# Research log: your left or mine?

### 1. Why
The single-agent studies in this series showed that LLMs handle spatial tasks well when given explicit geometry and
poorly when they must infer it. With two agents, each one has explicit geometry, but only in its own frame. A novelty
search found close work: COSMIC (arXiv 2603.27183), where multimodal agents with partial views fail at frame
conversion and, unlike humans, do not settle on anchors; and multi-perspective referential communication (arXiv
2410.03959, EMNLP 2024). Still open: identical objects where only the frame can disambiguate, a literal-reading check
that marks every perspective error, and the told / landmark / one-message conditions.

### 2. The literal-pick check
The self-test verifies that a matcher that reads the director's left/right and near/far without translating always
lands on a wrong cup. This makes "picked the literal cup" a direct measure of a perspective failure rather than a
guess.

### 3. The first frame measure was misleading
The planned `frame_talk` measure counted phrases like "your left". It was true in 85% of games, yet success was the
same with and without it. Reading the dialogues showed why: "your left" was usually the error itself (the director
giving its own frame as the partner's). `frames.py` was added to split these phrases by whether they match the
director's side or the translated side, and to count real perspective words (facing, opposite, from my side)
separately.

### 4. Results that surprised us
- The strongest model (Gemma 4) did worst, because it reliably gives precise but untranslated coordinates.
- Dialogue did not beat one message: the agents' questions ("which cup is closest to you?") are also answered in
  their own frames.

## Next
Mixed pairs (strong director, weak matcher and the reverse); a prompt that asks the director to describe the target
from the partner's seat; a shared-coordinate tool; a human-human and human-model baseline on the same layouts.
