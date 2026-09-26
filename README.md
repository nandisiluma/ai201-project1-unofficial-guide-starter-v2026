# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

## Chunking Strategy

**Chunk size:**
**Overlap:**

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

======================================================================
Chunk 1 | source: guide_accessibility.md#0 | produced by: chunker.py::split_documents

```
======================================================================
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.

## Straightforward

**Thornby Wells** is the easiest town in the region. It is flat, compact, and
everything is within three minutes of everything else. Parking is free for two
hours anywhere in town and the station is central. The pump room and gardens
are level throughout.
```

======================================================================
Chunk 2 | source: guide_corry_vale.md#4 | produced by: chunker.py::split_documents
======================================================================

```
## What to see

The valley itself is the attraction. The footpath network is dense and well marked, and a circuit taking in three of the four villages is about nine miles with 500 metres of ascent. The chapel in the second village is 12th century and always unlocked.

## Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked monthsahead. Camping is permitted on two marked fields and nowhere else.

```

======================================================================
Chunk 3 | source: guide_givens_mill.md#2 | produced by: chunker.py::split_documents
======================================================================

```
## What to see

The mill runs tours on the hour from 11 to 3 and the machinery is operating during them, which is loud and much more impressive thana static exhibit. The church has a Saxon doorway. The river walk downstream reaches Brightwater in about three hours.

## Where to stay

Nothing in the village itself. The nearest rooms are in Brightwater, which is close enough that this is not really a problem — most people come for a half day.

## When to go

```

======================================================================
Chunk 4 | source: guide_marchwood.md#0 | produced by: chunker.py::split_documents
======================================================================

```
# Marchwood

Marchwood is the regional hub — 180,000 people, the junction everyone changes trains at, and a city most visitors pass through rather than stop in. That is a mistake, though an understandable one, since almost nothing of interest is near the station.

## Getting there
```

======================================================================
Chunk 5 | source: guide_regional_transport.md#2 | produced by: chunker.py::split_documents
======================================================================

```
## Buses

Three operators run in the region and they do not accept each other's tickets,
which is the single most common source of confusion for visitors. Services
concentrate on weekday daytimes. Sunday service is minimal to non-existent
outside the Brightwater town routes.

The Kestrelford service is hourly on weekdays, two-hourly on Saturdays, and
does not run on Sundays. The Halden Bay coast service runs four times daily
year-round.

## Driving

```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**
"How often does the tram in Marchwood run on weekdays?"

**Answer:**

```
#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.3170     guide_marchwood.md               ## Getting around  A tram network of four lines, run...
2   0.3632     guide_marchwood.md               ## Eat and drink  The best eating is in the Northgat...
3   0.3676     guide_accessibility.md           **Marchwood** has a modern tram network with level b...
4   0.4517     guide_eating.md                  Marchwood is the exception, in that the good distric...
5   0.4862     guide_kestrelford.md             ## When to go  Late spring and early autumn. The Sat...

Gate: best distance 0.317 is under the 0.6 cutoff

Lower is better. 0.3 is a close match, 0.9 is unrelated.
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

Gap is between 0.252 and 0.936 so my cutoff will be 0.65

| Question | In corpus? | Best distance |
| -------- | ---------- | ------------- |
| 1        | Y          | 0.317         |

     2             Y              0.252
     3             Y              0.608
     4             Y              0.285
     5             Y              0.464
     6              N              0.798
     7              N              0.908
     8              N              0.936
     9              N              0.850
     10             N              0.836

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**

**2.**

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion | Verdict | How I decided |
| --- | --------- | ------- | ------------- |
| 1   |           |         |               |
| 2   |           |         |               |
| 3   |           |         |               |
| 4   |           |         |               |
| 5   |           |         |               |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
