"""
Unit 2's scorer.

`run_eval.py` looks for a function here called `judge(question, expects,
answer, results) -> bool` and, if it finds one, calls it once per run to fill
in the Run columns instead of leaving them blank.

The judgment call this makes: an answer counts as correct only if it
actually states the expected fact, not just if the expected words happen to
appear somewhere in it. Two cases justify that distinction, both seen
directly in this project's own results/run_*.md:

  - The gate's own refusal, "I don't have enough information about that.",
    is the easy case — it never reaches the model, and the answer is nothing
    but that sentence.
  - Harder: the model sometimes writes a real paragraph, drops the expected
    place name in passing, and then says outright that it doesn't know the
    answer. For "Between Thornby Wells, Marchwood and Brightwater, which
    city is fastest to walk end to end?" (expects "Thornby Wells"), one run
    produced: "Thornby Wells has flat, formal gardens... however, the
    documents do not contain information to determine which of the three
    cities is fastest to walk end to end." That contains "Thornby Wells" and
    is still not a correct answer to the question that was asked.

So a hedge phrase anywhere in the answer overrides a substring match — the
answer has to both contain what's expected AND not contradict itself.

This isn't airtight in the other direction either. "What's the best month
to visit the region?" gets answered thoroughly, town by town, and then
closes with "the documents do not specify a single best month for the
entire region as a whole" — a genuine, useful answer that this scorer will
still fail, because that closing line matches the same hedge pattern. I
decided that was the safer side to be wrong on: a scorer that's too lenient
hides real misses silently, one that's too strict just means I read a few
"fail" verdicts myself before trusting them at face value.
"""

_HEDGES = (
    "i do not have enough information",
    "i don't have enough information",
    "do not contain information",
    "does not contain information",
    "do not specify",
    "does not specify",
    "cannot determine",
    "not enough information",
)


def judge(question: str, expects: str, answer: str, results) -> bool:
    """True if `answer` actually delivers `expects`, not just mentions it."""
    if not expects:
        return False

    lowered = answer.lower()

    if any(hedge in lowered for hedge in _HEDGES):
        return False

    return expects.lower() in lowered
