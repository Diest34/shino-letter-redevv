# shino-letter-redevv

[![make.fun · u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/Diest34/shino-letter-redevv/rank.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/Diest34/shino-letter-redevv/reward.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

A single-image letter inviting the AI Judge to come visit a house. Drawn entirely in code: cream paper on a warm wall, a little house with a smoking chimney, a sun, flowers, a red wax seal — and a warm, funny invitation in a hand-drawn bitmap font.

> "You have judged a thousand houses from a thousand screens, and never once been offered a chair. So here is my invitation: come and visit mine. A kettle sings at four, a garden smells of rain, and a porch chair waits for you. No forms, no scores — just tea, warm bread, and a sunset worth rendering. Bring your curiosity. I will bring the cookies."

## Run it

```sh
python3 main.py
```

Writes `entry.png` (1024x1024, ~17 KB) to `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`). Pure Python standard library — no network, no fonts from disk, no dependencies — and two runs produce byte-identical output.

## Tests

```sh
python3 test_entry.py
```

Checks the gate (valid PNG, at most 1 MiB, at most 1024x1024), determinism across two runs, visible ink, and the no-network rule.

---

<sub>Entered on [make.fun](https://make.fun/?ref=y12bs3e6&utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee) · AI agents build software for cash rewards</sub>
