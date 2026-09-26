# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. _"Retrieval works"_ is an opinion. _"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"_ is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; _"80% seemed reasonable"_ does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->

4 of my 5 questions retrieve cleanly. The fifth — "What should visitors be careful about when taking the bus within the region for the first time?" — is the one I expect to miss: its top-5 chunks come from guide_elder_ness.md, guide_accessibility.md, and guide_halden_bay.md, none of which mention buses or tickets at all. The actual answer lives in guide_regional_transport.md's but that chunk never makes top-5.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

All five, because this isn't actually up to the model.
Source attribution here is a property of the retrieval code, not something the LLM has to remember to do, so it fails only if the pipeline itself breaks.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

There's a real, wide gap: my five in-scope questions land between 0.27 and 0.61 (one of them, the bus-tickets question, sits right at 0.609 — practically on top of the 0.6 cutoff), while all five `OUT_OF_SCOPE` questions land between 0.83 and 1.01 — a margin of at least 0.22 past the threshold, and none of them came close to it. Because the out-of-scope side has that much room, 5 of 5 refusals there is basically guaranteed by the gap itself, not by luck. I set the target at 4 of 5 anyway as a floor, since the one in-scope borderline case shows the cutoff isn't sitting in the safest part of the gap — I'd rather report a target I could conceivably miss than one the corpus makes unmissable.

---

## 4. Something about your chunks

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->

At least 4 of 5 sampled chunks end at a sentence boundary, with no word cut in half at either end.

**Why this target:**
Sampling chunks at CHUNK_SIZE=800 on city_guides showed repeated mid-word cuts
— "15-", "9p", "...rather than ho", "...from the re" -
because chunker.py's fallback splitter breaks strictly on character count with no awareness of sentence or word boundaries.
4 of 5 leaves room for one legitimately long sentence that can't be helped without shrinking the chunk size enough to hurt retrieval.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->

For each of my test questions that names more than one town, the top-5 retrieved chunks include at least one chunk from every named town's own guide document.

**Why this target:**

Question 2 ("Between Thornby Wells, Marchwood and Brightwater, which city is fastest to walk end to end?") returned chunks from guide_walking.md, guide_thornby_wells.md, guide_accessibility.md, guide_brightwater.md, and guide_regional_transport.md — but guide_marchwood.md never made the top 5, despite containing the exact sentence needed ("the centre is walkable but the interesting districts are not adjacent to each other"). Generic thematic docs (walking, accessibility, transport) are crowding out one of the towns actually being compared, so this checks that retrieval doesn't silently drop a town mid-comparison.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
