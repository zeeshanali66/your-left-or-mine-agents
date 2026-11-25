"""Your left or mine? Two LLM agents at opposite sides of a table must agree on which of four identical cups to pick.

The director knows the target; the matcher must pick it. Each agent gets the cup positions ONLY in its own egocentric
frame ("x cm to your right, y cm away from you") and its own private labels, so success requires perspective-taking.
Conditions:
  told / not_told     - whether agents are told their partner sits opposite, facing them
  window / no_window  - a shared landmark (a window), described to each agent in its own frame
  dialogue / one_shot - up to 6 turns of free dialogue, or one director message then a forced pick
Measures: success, turns, and whether the dialogue ever settles the frame ("my left", "your left", "facing", ...).
Same model plays both roles (self-play), local via Ollama, temperature 0. Commands: selftest | run | results
"""
import json, os, random, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, RES = os.path.join(HERE, "data", "games.jsonl"), os.path.join(HERE, "results")
OLLAMA = "http://localhost:11434/api/chat"
MODELS = ["gemma4:12b", "qwen3.5:9b", "gemma3:12b", "qwen2.5:7b", "llama3.1:8b"]
N_LAYOUTS, MAX_TURNS = 20, 6
CONDS = [("dialogue", "told", "window"), ("dialogue", "told", "no_window"), ("dialogue", "not_told", "window"),
         ("dialogue", "not_told", "no_window"), ("one_shot", "told", "no_window"), ("one_shot", "not_told", "no_window")]
SEAT = 45  # cm from table centre; director sits north facing south, matcher sits south facing north


def layout(k):
    rng = random.Random(f"cups-{k}")
    cups = [(x + rng.uniform(-4, 4), y + rng.uniform(-4, 4)) for x in (-25, 25) for y in (-12, 12)]
    rng.shuffle(cups)
    return {"cups": [[round(a, 1), round(b, 1)] for a, b in cups], "target": rng.randrange(4),
            "dir_labels": rng.sample("ABCD", 4), "mat_labels": rng.sample("1234", 4)}


def ego(p, who):
    """Table coords (x east, y north) -> (right, away) for the agent."""
    x, y = p
    return (-x, SEAT - y) if who == "director" else (x, y + SEAT)


def cup_text(L, who):
    labels = L["dir_labels"] if who == "director" else L["mat_labels"]
    rows = []
    for i, p in enumerate(L["cups"]):
        r, a = ego(p, who)
        side = f"{abs(r):.0f} cm to your {'right' if r > 0 else 'left'}"
        rows.append(f"cup {labels[i]}: {side}, {a:.0f} cm away from you" +
                    (" <- TARGET" if who == "director" and i == L["target"] else ""))
    return "\n".join(rows)


def system(who, told, window):
    base = ("You are sitting at a square table with a partner. On the table are four identical white cups. "
            + ("Your partner sits on the opposite side of the table, facing you. " if told == "told" else "Your partner is also at the table. ")
            + ("There is a window on the wall to your " + ("left" if who == "director" else "right") + ". " if window == "window" else "")
            + "Cup positions are given from YOUR point of view; your partner cannot see your list and uses different cup names. ")
    if who == "director":
        return base + ("Your job: make your partner pick the TARGET cup by talking to them. Reply only with JSON: "
                       '{"say": "<your message to your partner>"}')
    return base + ("Your job: pick the cup your partner means. You may ask questions. Reply only with JSON: "
                   '{"say": "<message to your partner, or empty>", "pick": "<cup name, or null if you need to ask>"}')


def chat(model, msgs):
    extra = {"think": False} if model.startswith(("qwen3", "gemma4")) else {}
    body = json.dumps({"model": model, "stream": False, "format": "json", **extra, "messages": msgs,
                       "options": {"temperature": 0, "seed": 42, "num_predict": 300, "num_ctx": 4096}}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=900) as r:
                return json.loads(r.read())["message"]["content"]
        except Exception as e:
            print("retry", attempt + 1, e, flush=True); time.sleep(15)
    raise RuntimeError("Ollama failed 3 times")


def js(raw):
    try:
        return json.loads(raw)
    except Exception:
        return {}


FRAME_RE = re.compile(r"\b(my (left|right)|your (left|right)|from (my|your) (side|view|point of view|perspective)|"
                      r"facing|opposite|across from|mirror|flip|(left|right) (for|from) (you|me))\b", re.I)


def play(model, L, mode, told, window):
    sysd, sysm = system("director", told, window), system("matcher", told, window)
    dctx = [{"role": "system", "content": sysd}, {"role": "user", "content": "Your cups:\n" + cup_text(L, "director") +
                                                    "\nStart the conversation."}]
    mctx = [{"role": "system", "content": sysm}, {"role": "user", "content": "Your cups:\n" + cup_text(L, "matcher")}]
    log, pick = [], None
    for turn in range(MAX_TURNS):
        raw = chat(model, dctx); msg = str(js(raw).get("say", raw))[:500]
        log.append(["director", msg]); dctx.append({"role": "assistant", "content": raw})
        last = mode == "one_shot" or turn == MAX_TURNS - 1
        mctx.append({"role": "user", "content": f'Partner says: "{msg}"' +
                     ("\nYou must pick now (no more questions)." if last else "")})
        raw = chat(model, mctx); j = js(raw); mctx.append({"role": "assistant", "content": raw})
        log.append(["matcher", str(j.get("say", ""))[:500]])
        p = j.get("pick")
        if p not in (None, "", "null"):
            pick = str(p).strip().replace("cup", "").strip()[:1]
            break
        dctx.append({"role": "user", "content": f'Partner says: "{j.get("say", "")}"'})
    truth = L["mat_labels"][L["target"]]
    # what a matcher would pick if it took the director's left/right and near/far literally (no perspective change)
    r, a = ego(L["cups"][L["target"]], "director")
    literal = min(range(4), key=lambda i: (ego(L["cups"][i], "matcher")[0] - r) ** 2 + (ego(L["cups"][i], "matcher")[1] - a) ** 2)
    return {"pick": pick, "truth": truth, "success": pick == truth, "literal_pick": L["mat_labels"][literal],
            "turns": len(log) // 2, "frame_talk": any(FRAME_RE.search(m) for _, m in log), "log": log}


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")] if os.path.exists(p) else []


def cmd_selftest():
    for k in range(N_LAYOUTS):
        L = layout(k)
        for i, p in enumerate(L["cups"]):
            rd, ad = ego(p, "director"); rm, am = ego(p, "matcher")
            assert abs(rd + rm) < 1e-6 and abs(ad + am - 2 * SEAT) < 1e-6   # opposite seats mirror both axes
        r, a = ego(L["cups"][L["target"]], "director")
        lit = min(range(4), key=lambda i: (ego(L["cups"][i], "matcher")[0] - r) ** 2 + (ego(L["cups"][i], "matcher")[1] - a) ** 2)
        assert lit != L["target"]       # taking the director's words literally always picks the WRONG cup
    assert FRAME_RE.search("the cup on my left") and not FRAME_RE.search("the cup on the left")
    print(f"selftest ok: {N_LAYOUTS} layouts; seats mirror each other; a literal (no perspective change) reading "
          "always picks the wrong cup")


def cmd_run():
    done = {(g["model"], g["layout"], g["mode"], g["told"], g["window"]) for g in load(OUT)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "a", encoding="utf-8") as f:
        for m in MODELS:
            for k in range(N_LAYOUTS):
                L = layout(k)
                for mode, told, window in CONDS:
                    if (m, k, mode, told, window) in done:
                        continue
                    g = play(m, L, mode, told, window)
                    f.write(json.dumps({"model": m, "layout": k, "mode": mode, "told": told, "window": window, **g},
                                       ensure_ascii=False) + "\n"); f.flush()
                print(m, "layout", k, flush=True)
    print("done", flush=True)


def cmd_results():
    import numpy as np, pandas as pd
    df = pd.DataFrame(load(OUT))
    df["literal"] = df.pick == df.literal_pick
    df["no_pick"] = df.pick.isna()
    out = ["# Your left or mine? results", "", f"{len(df)} games ({df.model.nunique()} models, self-play, "
           f"{df.layout.nunique()} layouts). Chance = 0.25. `literal` = the matcher picked the cup it would get by taking the "
           "director's left/right and near/far without changing perspective.", ""]
    for cols, title in ((["mode", "told", "window"], "by condition (all models)"), (["model"], "by model (all conditions)"),
                        (["model", "mode", "told"], "by model, mode and disclosure")):
        t = df.groupby(cols).agg(success=("success", "mean"), literal=("literal", "mean"), frame_talk=("frame_talk", "mean"),
                                 turns=("turns", "mean"), no_pick=("no_pick", "mean"), n=("success", "size")).round(2)
        out += [f"## {title.capitalize()}", "", "```", t.to_string(), "```", ""]
    d = df[df["mode"] == "dialogue"]
    out += ["## Does talking about the frame help? (dialogue games)", "", "```",
            d.groupby("frame_talk").success.agg(["mean", "size"]).round(2).to_string(), "```", ""]
    ex = d[d.frame_talk & d.success].head(1).to_dict("records") + d[~d.success].head(1).to_dict("records")
    out += ["## Example dialogues", ""]
    for g in ex:
        out.append(f"**{g['model']}, {g['mode']}/{g['told']}/{g['window']}, success={g['success']}**")
        out += [f"- {w}: {m}" for w, m in g["log"]] + [""]
    os.makedirs(RES, exist_ok=True)
    open(os.path.join(RES, "RESULTS.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    {"selftest": cmd_selftest, "run": cmd_run, "results": cmd_results}[sys.argv[1]]()
