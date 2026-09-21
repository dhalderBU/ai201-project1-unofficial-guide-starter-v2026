# The Unofficial Guide

**Name:** Debasish Halder  
**Corpus:** campus_life

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none, because the grader can't
> read it.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Week 1

## What This Does

**Corpus Suitability**
I opted to go for campus_life. Though I tried all other corpus and had very good success rate 

Content reflects real campus-life problems across admin, courses, dining, and housing.
Each question typically has at most two different answers, sometimes contradicting (good vs. bad).
Topic is clearly labeled at the top of each item.
Moderate sentence length (a couple of lines), so only a modest context window is needed.  And I can experiment quite a bit 

My firs build worked for the campus life but didnot work for the Threads and city guides. so I changed the chunker as needed to work for each type and my scores got to acceptable level and the responses were grounded

## Chunking Strategy

**Chunk size:**
500 chracters (for the campus_life and advice_threads, for City_guides I used 900  ) 
**Overlap:**
50(i.e 10%, same for all corpus) Original chunker shortest 178 and longest 549. In view of this I kept the chunk size as 500 character so as to avoid corrupting context and kept context at paragraph boundary and allowed 10% overlap
With changed chunker i got shortest 36 longest 397



## Sample Chunks



**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: ` (original mode -> fallback_split)`

```
======================================================================
Chunk 1  |  source: admin_add_drop_deadline.txt#0  |  produced by: chunker.py::split_documents (original mode -> fallback_split)
======================================================================
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160.txt#0` — produced by: ` (original mode -> fallback_split)`

```
======================================================================
Chunk 2  |  source: course_biol_160.txt#0  |  produced by: chunker.py::split_documents (original mode -> fallback_split)
======================================================================
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: ` (original mode -> fallback_split)`

```
======================================================================
Chunk 3  |  source: course_hist_118_workload.txt#0  |  produced by: chunker.py::split_documents (original mode -> fallback_split)
======================================================================
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: ` (original mode -> fallback_split)`

```
======================================================================
Chunk 4  |  source: dining_pellew_dining_hall_followup.txt#0  |  produced by: chunker.py::split_documents (original mode -> fallback_split)
======================================================================
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.

```

**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: ` (original mode -> fallback_split)`

```

======================================================================
Chunk 5  |  source: housing_innisfree_hall.txt#0  |  produced by: chunker.py::split_documents (original mode -> fallback_split)
======================================================================
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

**Question:**
"what is workload of CS 210 ?" 
**Answer:**

```
The workload for CS 210 Data Structures is 8 to 10 hours a week outside class, and it is front-loaded with the first month being heavier than the rest. 

Source: course_cs_210_workload.txt

Sources retrieved: course_cs_210_exams.txt, course_cs_210_workload.txt, course_cs_340_workload.txt, course_phys_130_workload.txt, course_stat_150_workload.txt

1 model calls this session, 584 tokens (529 in, 55 out)
```

**My relevance cutoff:**


venv-codepath) debasishhalder@Debasishs-Mac-mini codepath % python app.py --corpus campus_life ask "What is the capital of Mongolia?"
  (best distance 0.825, cutoff 0.6)

I don't have enough information about that.

0 model calls this session
(venv-codepath) debasishhalder@Debasishs-Mac-mini codepath % python app.py --corpus campus_life ask "How do I change the oil in a diesel engine?"
  (best distance 0.934, cutoff 0.6)

I don't have enough information about that.

0 model calls this session
(venv-codepath) debasishhalder@Debasishs-Mac-mini codepath % python app.py --corpus campus_life ask "Who won the 1994 World Cup?",               
  (best distance 0.888, cutoff 0.6)

I don't have enough information about that.

0 model calls this session
(venv-codepath) debasishhalder@Debasishs-Mac-mini codepath % python app.py --corpus campus_life ask "What is the recommended dosage of ibuprofen for a headache?",
  (best distance 0.849, cutoff 0.6)

I don't have enough information about that.

0 model calls this session
(venv-codepath) debasishhalder@Debasishs-Mac-mini codepath % python app.py --corpus campus_life ask "How do I write a for loop in Rust?", 
  (best distance 0.893, cutoff 0.6)

I don't have enough information about that.

0 model calls this session



| Question | In corpus? | Best distance |

The Best Distance I got was 0.337 using default  chunker using custom chunker I got in 0.350 
|---|---|---|
|  |  |  |

## How I Used AI

**1.**

While Building custom chunker I used claude to give me the python code based on my ask of how I want to build chunker how specific strategies can be applied to each of the three data file types and based on their way of representing information so as I get very good context without increasing the chunk size to large level.

**2.**

I implemented the chunker which will work for all the types of data / corpus we were given. As a stretch type laterty I could add metadata based filtering and adding seprate vector space for documents which will help in city_guides kind of corpus

---

# Week 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     week 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     week — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

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

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

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
