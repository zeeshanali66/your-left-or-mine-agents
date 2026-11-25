"""Second-pass analysis: which frame does the director use for left/right, and does it matter?

For each game, the director's messages are checked for the target's side:
  wrong frame - "your left" when the target is on the DIRECTOR's left (the director's own frame given as the partner's)
  right frame - "your right" (translated) or "my left" (own frame, marked as own)
Writes results/FRAMES.md.
"""
import importlib.util, json, os, re

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ma", os.path.join(HERE, "ma_study.py"))
ma = importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
PERSP = re.compile(r"\b(facing|opposite|across from|mirror|flip|from (my|your) (side|view|point of view|perspective))\b", re.I)

rows = []
for g in map(json.loads, open(os.path.join(HERE, "data", "games.jsonl"), encoding="utf-8")):
    L = ma.layout(g["layout"])
    r, _ = ma.ego(L["cups"][L["target"]], "director")
    ds, os_ = ("left", "right") if r < 0 else ("right", "left")
    dm = " ".join(m for w, m in g["log"] if w == "director").lower()
    wrong = bool(re.search(rf"\byour {ds}\b", dm))
    right = bool(re.search(rf"\byour {os_}\b|\bmy {ds}\b", dm))
    cls = {(True, False): "wrong frame only", (False, True): "right frame only", (True, True): "both",
           (False, False): "no left/right"}[(wrong, right)]
    rows.append({"model": g["model"], "mode": g["mode"], "told": g["told"], "window": g["window"],
                 "success": g["success"], "literal": g["pick"] == g["literal_pick"], "frame": cls,
                 "perspective_words": bool(PERSP.search(" ".join(m for _, m in g["log"]))),
                 "director_uses_own_labels": bool(re.search(r"\bcup [A-D]\b", " ".join(m for w, m in g["log"] if w == "director")))})
d = pd.DataFrame(rows)
out = ["# Frame analysis", "", "## Success by the frame the director used", "", "```",
       d.groupby("frame").agg(success=("success", "mean"), literal=("literal", "mean"), n=("success", "size")).round(2).to_string(),
       "```", "", "## Frame use by model", "", "```", pd.crosstab(d.model, d.frame, normalize="index").round(2).to_string(), "```",
       "", "## Frame use by disclosure (told the partner sits opposite?)", "", "```",
       pd.crosstab([d["mode"], d["told"]], d.frame, normalize="index").round(2).to_string(), "```", "",
       "## Perspective words (facing, opposite, from my side, mirror, ...)", "", "```",
       d.groupby("told").perspective_words.mean().round(2).to_string(), "",
       d.groupby("perspective_words").success.agg(["mean", "size"]).round(2).to_string(), "```", "",
       "## Director names its own private cup labels (A-D), which the partner cannot know", "", "```",
       d.groupby("model").director_uses_own_labels.mean().round(2).to_string(), "",
       d.groupby("director_uses_own_labels").success.agg(["mean", "size"]).round(2).to_string(), "```"]
open(os.path.join(HERE, "results", "FRAMES.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
