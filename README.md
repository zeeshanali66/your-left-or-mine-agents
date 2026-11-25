# Your left or mine? Two LLM agents across a table cannot agree on a cup

Two agents sit on opposite sides of a table with four identical cups. The **director** knows which cup is the
target; the **matcher** has to pick it. Each agent sees the cups only in its own frame ("23 cm to your left, 31 cm
away from you") and under its own private names. The task is trivial for two people who know they face each other.
It needs one step of perspective-taking: my left is your right.

## Design
- **20 layouts** (a 2 × 2 grid of cups with jitter). The same model plays both roles (self-play), local via Ollama,
  temperature 0.
- **Conditions**:
  - `dialogue` (up to 6 turns, the matcher may ask questions) or `one_shot` (one director message, then a forced pick).
  - `told`: both agents are told the partner sits opposite, facing them; `not_told`: only "your partner is also at
    the table".
  - In dialogue: with or without a shared landmark (a window, described to each agent in its own frame).
- **Models**: Gemma 4 12B, Qwen 3.5 9B, Gemma 3 12B, Qwen 2.5 7B and Llama 3.1 8B. 600 games.
- **Self-test**: the seats mirror both axes, and a matcher that takes the director's words literally (no change of
  perspective) **always picks a wrong cup**. So `literal` picks show exactly when perspective-taking failed.

## Results (chance = 0.25)
**1. Agents do worse than chance.** Overall success is 0.17 (binomial test vs 0.25, p < 0.0001). The strongest model,
Gemma 4, is the worst: **0.05**, with 60% of its picks being the literal (wrong) cup.

| model | success | literal (wrong-frame) pick |
|---|---|---|
| Gemma 3 12B | 0.24 | 0.37 |
| Llama 3.1 8B | 0.24 | 0.26 |
| Qwen 2.5 7B | 0.17 | 0.49 |
| Qwen 3.5 9B | 0.15 | 0.57 |
| Gemma 4 12B | **0.05** | **0.60** |

**2. The cause: the director hands over its own frame as the partner's.** In 36% of games the director says the
target is on "your left" when it is on the director's own left. Those games succeed **5%** of the time (70% literal
picks). A typical Gemma 4 director message: *"It is located 23 cm to your left and 31 cm away from you"*, which copies
its own coordinates word for word.

| what the director said about left/right | success | literal pick | games |
|---|---|---|---|
| own frame given as the partner's ("your left") | **0.05** | 0.70 | 216 |
| no left/right | 0.21 | 0.27 | 143 |
| translated ("your right" or "my left") | 0.28 | 0.33 | 198 |

Even a translated left/right only brings success to chance, because the near/far part ("31 cm away from you") is
still copied, and it is also mirrored across the table.

**3. Talking more does not help.** Dialogue (up to 6 turns) succeeds 0.17, one message 0.17. The agents almost never
negotiate the frame: words like "facing", "opposite" or "from my side" appear in **4%** of games. Instead they ask
each other which cup is "closest" or "furthest left", and each answers in its own frame.

**4. Saying "your partner is facing you" helps a little.** Success rises by +0.06 (paired sign-flip test over
model × layout × condition, p = 0.03), and wrong-frame directions drop from 0.44 to 0.30 in dialogue. Most errors
remain.

**5. Weaker models leak private names.** Llama 3.1 and Qwen 2.5 often tell the partner "pick cup B", a name only the
director knows (42% and 52% of games). Gemma 4 and Qwen 3.5 never do, but they make the frame error instead.

**6. The shared window did not help** (dialogue success 0.17 with a window, 0.18 without).

## What this means
Multi-agent systems that coordinate about physical space, such as robots, a robot and a phone assistant, or agents
working from different camera views, cannot be left to "just talk it out". The fix used in every study in this
series applies here too: **give the agents one shared frame** (table coordinates or shared object IDs), or have the
sender convert its description into the receiver's frame with code before sending it.

## Related work
Closest: COSMIC (arXiv 2603.27183), which finds that multimodal agents with partial views fail at frame
conversion and do not settle on shared anchors the way humans do. This pilot isolates the same failure in a minimal
text game with a literal-reading check.

## Limitations
Self-play only (no mixed pairs, no human partner); text descriptions, not images; one table geometry; small open
models; a regex-based frame classifier (checked on examples, not hand-labelled in full).

## Run
```
python ma_study.py selftest | run | results
python frames.py          # second-pass frame analysis
```
Tables: [`results/RESULTS.md`](results/RESULTS.md), [`results/FRAMES.md`](results/FRAMES.md). Log:
[`docs/RESEARCH_LOG.md`](docs/RESEARCH_LOG.md). All 600 dialogues are in `data/games.jsonl`.

## Disclosure
Code and documentation were written with the help of an AI assistant; the research design, checking and decisions
are the author's.

## License
MIT
