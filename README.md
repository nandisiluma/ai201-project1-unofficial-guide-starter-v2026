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

```
This is a RAG question-answering system built on the city_guides corpus: fourteen markdown guides covering thirteen towns and villages in one region, plus cross-cutting guides on accessibility, eating, walking, seasons, and regional transport. It answers practical travel questions a visitor would actually ask — how often the Marchwood tram runs, how late restaurants stay open outside Marchwood, which town is fastest to walk end to end, what to watch out for on the regional bus network — by retrieving the guide passages most relevant to the question and citing the document(s) they came from. Questions the corpus doesn't cover (unrelated topics like world history or car maintenance) get refused by a relevance gate rather than answered with a guess.
```

## Chunking Strategy

**Chunk size:** 500 characters
**Overlap:** 120 characters

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

```
I started with the starter's defaults (800/120, plain character-window `fallback_split`) and sampled chunks with `python app.py chunks`. That surfaced two problems specific to these guides: chunks cut off mid-word ("...15-", "...9p", "...rather than ho", "...from the re"), and one chunk that was just a tiny orphaned tail starting mid-word. The guides are organized as short `##` sections — each one is a heading plus one paragraph, typically 200–380 characters. So I rewrote `split_documents` to pack whole paragraphs (falling back to whole sentences only if a single paragraph doesn't fit) up to `CHUNK_SIZE`, instead of slicing on a raw character count — that's why chunks now never end mid-word. I dropped `CHUNK_SIZE` from 800 to 500 once I moved to that strategy, since 500 is enough room to fit one section's heading + body plus a peek at the next heading (which becomes the overlap into the next chunk), whereas 800 was leaving so much slack that three or four unrelated sections were getting packed into a single chunk. `CHUNK_OVERLAP` stayed at 120 because every heading in this corpus is well under that, so the carried-over heading always fits.


```

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
I asked AI to review the questions I came up with for testability. It helped me rewrite 2 out of 5 questions without changing the intention behind them.

**2.**

I pitched my plan for the chunking function to the AI. I wanted to use sentence level splitting to avoid mid sentence cutoffs, and AI pointed out the gaps in that although this solves the mid-sentence cutoff problem, it will not resolve paragraph blending which is another problem I needed to address. As a result the new logic for the chunking function runs mainly on the paragraph level split, and also uses the sentence level split as a fallback option.

**3.**

I asked Claude to build `scorer.py` from the `judge(question, expects, answer, results) -> bool` spec in `run_eval.py`. It came back with a substring check on `expects` plus a hedge-phrase list so a disguised refusal wouldn't score as a pass — then, when I asked it to validate that against my actual run log, it caught that its own hedge list produces a false pass (a refusal phrased as "do not provide enough information" slips past it) and a false fail on the best-month question's legitimate closing caveat. I kept the scorer as-is since erring toward "fail" seemed safer, but now know to read the real output behind any close verdict.

**4.**

When criterion 5 kept missing, I described the pattern — retrieval always returning the same sources for the walk-comparison question, never Marchwood's or Brightwater's own guides — and asked whether raising `top_k` or re-chunking would fix it. It had me test raising `top_k` first (up to 20), which showed Marchwood's chunk doesn't rank above position 15 — more slots alone just added more irrelevant towns, it didn't help. That's what pointed to hybrid search (BM25 + semantic, fused by rank) instead. I had it implement that in `store.py`, then verified myself that the after-run log actually shows `guide_marchwood.md` and `guide_brightwater.md` being retrieved, not just a plausible explanation for why they should be.

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

| Criterion                               | Target | Run 1 | Run 2 | Run 3 | Verdict |
| --------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer  | 4 of 5 | 3/5   | 4/5   | 3/5   | MISSED  |
| 2. Every answer names a source          | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions   | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunks end at a sentence boundary    | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 5. For multiple towns, retrieved chunks | 4 of 5 | 0/5   | 0/5   | 0/5   | MISSED  |

include at least one chunk from every
named town's own guide document

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

Criterion 1

### How often does the tram in Marchwood run on weekdays? — run 1

- Best distance: 0.3170 (passed the gate)
- Sources retrieved: guide_accessibility.md, guide_eating.md, guide_kestrelford.md, guide_marchwood.md

```
The tram in Marchwood runs every 8 minutes on weekdays (from guide_marchwood.md and guide_accessibility.md).
```

Criterion 2

### Between Thornby Wells, Marchwood and Brightwater, which city is fastest to walk end to end? — run 1

- Best distance: 0.2525 (passed the gate)
- Sources retrieved: guide_regional_transport.md, guide_thornby_wells.md, guide_walking.md

```
Based on the provided documents, Thornby Wells is described as having flat, formal gardens and level streets, making it the region's most accessible town on foot (*guide_walking.md*). However, the documents do not contain information to determine which city is the *fastest* to walk end to end among Thornby Wells, Marchwood, and Brightwater. Therefore, I do not have enough information to answer the question.
```

Criterion 3

### What should visitors be careful about when taking the bus within the region for the first time? — run 3

- Best distance: 0.6084 (passed the gate)
- Sources retrieved: guide_accessibility.md, guide_elder_ness.md, guide_halden_bay.md, guide_kestrelford.md

```
I do not have enough information to answer this question.
```

Criterion 4

### Outside Marchwood, how late do restaurants stay open? — run 1

- Best distance: 0.2849 (passed the gate)
- Sources retrieved: guide_eating.md, guide_kestrelford.md, guide_marchwood.md, guide_thornby_wells.md

```
Outside Marchwood, kitchens across the region stop serving at 9pm and often earlier (guide_eating.md).
```

Criterion 5

### What's the best month to visit the region? — run 2

- Best distance: 0.4644 (passed the gate)
- Sources retrieved: guide_brightwater.md, guide_halden_bay.md, guide_marchwood.md, guide_pellew_sands.md, guide_thornby_wells.md

```
Based on the provided documents, there is no single best month for the entire region, as different places have different recommendations:

* **May and June** are best for Thornby Wells and Brightwater (guide_thornby_wells.md, guide_brightwater.md).
* **June and September** are the "sweet spot" for Halden Bay and the best months to avoid crowds at Pellew Sands (guide_halden_bay.md, guide_pellew_sands.md).
* **Any time** works for Marchwood, as it functions year-round (guide_marchwood.md).
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion                           | Verdict | How I decided                                                                              |
| --- | ----------------------------------- | ------- | ------------------------------------------------------------------------------------------ |
| 1   | Retrieved chunk contains the answer | MISSED  | model was not consistent across the three runs. Returned 4,3,4 against and target of 4     |
| 2   | Every answer names a source         | MET     | For all runs, we identified a source for each answer per question                          |
| 3   | stops out-of-corpus questions       | MET     | All out of scope questions were identified and returned 'I don't have enough information'. |
| 4   | Chunks end at a sentence boundary   | MET     | All the returned chunks ended at a sentence coundary without any mid sentence cutoffs.     |
| 5   | retrieved chunks                    |

include at least one chunk from every
named town's own guide document | MISSED | Retrieved chunks prioritized based on topics over the cities in context. For example, if the question was about transport, the model picked chunks from transport related documents and didn't diversify acroass different cities. |

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

Both misses trace back to the retrieval stagebut two different
mechanisms, plus a secondary quirk worth flagging separately.

**Pattern 1: multi-town crowding.** This is the entire reason criterion 5
missed (0 of 5, every run), and it's also half of why criterion 1 missed —
it's the same mechanism driving the walk-comparison question's failure. With
`top_k=5`, a generic thematic document (`guide_walking.md`,
`guide_regional_transport.md`) embeds closer to "which city is fastest to
walk end to end" than most individual towns' own guides do, because the
generic doc's whole content is about walking across the region, while each
town's guide only mentions walking in passing inside a larger "Getting
around" section. Across all three runs, retrieval for that question returned
the exact same three sources every time — `guide_regional_transport.md`,
`guide_thornby_wells.md`, `guide_walking.md` — never `guide_marchwood.md` or
`guide_brightwater.md`. Three towns needed coverage, only 5 slots existed,
and the generic docs plus Thornby Wells took all of them. This is a
retrieval-stage problem, not a chunking one — Marchwood's walkability
sentence exists cleanly in its own chunk (confirmed when we sampled chunks in
Milestone 3); it just never gets retrieved for this question.

**Pattern 2: topic/phrasing mismatch.** The bus-tickets question fails all
three runs for a different reason. Its casual phrasing ("what should
visitors be careful about... first time") embeds closer to generic
caution/practical-notes chunks (`guide_elder_ness.md`,
`guide_accessibility.md`, `guide_halden_bay.md`) than to the chunk that
actually answers it — `guide_regional_transport.md`'s "## Buses" section,
which states plainly that the three operators don't accept each other's
tickets. That chunk exists and is well-formed (it's Sample Chunk 5 from
Milestone 3), so this isn't a chunking failure either; indirect phrasing just
doesn't land near specific operational content in embedding space the way a
more literal phrasing would.

**The pattern across both:** every miss happens before the model ever sees
the question. Chunking, embedding, and generation are all doing what they're
supposed to — the failure is entirely in what top-k retrieval selects, which
has no mechanism to guarantee coverage across multiple relevant documents
(pattern 1) or to bridge paraphrased intent to specific content (pattern 2).

One more thing worth noting, since it looks like a contradiction otherwise:
the walk-comparison question flipped fail → pass → fail across the three
runs even though retrieval returned identical sources every time. That
"pass" isn't evidence retrieval sometimes worked — it's the model phrasing
its own refusal slightly differently that run ("do not provide enough
information to determine..." instead of "I do not have enough information"),
which happened to dodge `scorer.py`'s hedge-phrase list. The underlying
retrieval gap (no Marchwood or Brightwater chunks) was present in all three
runs.

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- | --- | --- | --- | --- | --- | --- |
| 1. Retrieved chunk contains the answer | 4 of 5 | 4/5   | 4/5   | 4/5   | MET     |
| 2. Every answer names a source         | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions  | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunks end at a sentence boundary   | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 5. Multi-town coverage                 | 4 of 5 | 1/5   | 1/5   | 1/5   | MISSED  |     |     |     |     |     |     |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

Yes, using keyboard seach I was able to imporve the retrieval numbers for criterion 1.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

1. Criterion 1 is technically MET after the fix (4 of 5, held across all
   three "after" runs) — but one question, the bus-tickets one, has failed
   in _every_ run, before and after. The diagnosed cause:
   `guide_regional_transport.md`'s "## Buses" section never repeats the word
   "bus" in its body, only in the plural heading, so a casually-phrased
   question ("what should visitors be careful about... first time?") has no
   lexical or semantic bridge to it — BM25 has nothing to match, and cosine
   similarity favors generic caution chunks instead. Next thing I'd try:
   query rewriting (expand "bus" with synonyms like "ticket"/"fare"/
   "operator" before retrieval) or rewriting the chunk itself in
   visitor-facing language. I stopped here because this single failure
   doesn't break the 4-of-5 target, and hybrid search was the higher-value
   fix since it addressed two criteria at once rather than one question in
   one criterion.

2. Criterion 5 is MET on paper, but I don't fully trust the verdict. The
   criterion is phrased as "4 of 5," which assumes five comparable trials —
   but there's only ever been one multi-town question in my test set, so
   one pass isn't the same evidence as 4 of 5 independent ones. I haven't
   decided yet whether to give criterion 5 its own dedicated multi-town
   question set (the way criterion 3 has its own `OUT_OF_SCOPE` list,
   separate from the core five) or rewrite it as a plain fact instead of a
   rate. I ran out of time to settle which, so the honest state is: the fix
   is proven on the one example I have, not on a population large enough to
   call a rate.

3. `scorer.py`'s hedge-phrase check is a known source of noise in both
   directions — it gave a false pass in the Before log (a refusal phrased
   as "do not provide enough information" dodged the hedge list) and it
   would give a false fail on a genuinely good answer that hedges only as a
   footnote (the best-month question's "the documents do not specify a
   single best month for the entire region" line). I left it as-is because
   erring strict felt safer than erring lenient, but it means any Run-column
   verdict needs a glance at the real output before it's trusted, not just
   the pass/fail count.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

Criterion 5, clearly. I'd write it from the start as either a single
observable fact ("the multi-town test question gets full town coverage") or
give it its own five-question population, the same way criterion 3 got its
own `OUT_OF_SCOPE` list from day one. Writing it as "at least 4 of 5" when
only one question in my actual test set could ever trigger it was a mismatch
I didn't catch until the after-results table made the denominator
meaningless.

I'd also define criterion 1's "contains the answer" more carefully. Building
`scorer.py` this unit showed the substring-on-`expects` approach isn't
obviously wrong until you watch it disagree with your own reading twice —
once too lenient, once too strict, on the same kind of hedge language. Next
time I'd pick `expects` phrases that can't appear for unrelated reasons (not
a place name that shows up regardless of whether the question got answered),
and decide up front whether a hedged-but-partially-right answer counts.
