# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in week 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next week costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

80% correctness is a resonable ask as we dont have anything between 80 and 100. Ideally  I wouuld like about 85% to 90% and I cant go for 100% as there will be few questions whose vector distance may not be within limits . The reason at least this is thawe want a grounded response based ont he documents we have chunked and vectorized and saved in the Chroma vector DB 
---     

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**


The Prompt builder in our system has specific rules which says "Name the document your answer came from, using the filename given in each excerpt"  and another rule "If the documents don't cover the question, say you don't have enough information. Do not guess"

This target is of very high importance as we want reponses to be grounded to facts available. 

--- 

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.


**Why this target:**

The Prompt builder in our system has specific rules :  "If the documents don't cover the question, say you don't have enough information. Do not guess". But there will be occurance that the vector dimension was not big enough and some of the projections overlapped due to lower dimension. The distance criteria should help us filter anything that is above 0.6 is what the defaults setting is

--- 

## 4. Something about your chunks

Within a sample of 5 chunks 4 or more chunks should be:
- Do not span the paragraph boundary
- Begin and end sentence boundary
- Chunks size is not longer than 900 characters which with an average token size of 4 charater gives us about 225 tokens  which is below the vector size for the embedding for the one we are using(limit is 256 for Mini LLM -L6-V2) 

**Why this target:**
Any AI based application that we build shoiuld give helpful answers which means should be with context. If the chunks size is not good enough we may not be able have enough context captured. If the chunk size is too big we will have context dilution as context is captured through attention mechanism. So we need to have a balance and the vector dimention of the embedding model needs to be taken into consideration . If the embedding model supports larger vector(higher dimension) then we will be able to capture the context better.

- Staying within the paragraph will help us from getting context dillution

- Begin and end sentence boundary will make sure we have proper context and its not truncating and causing confugion with LLM for its generation

- Chunk size is not longer than 900 characters which with an average token size of 4 charater gives us about 225 tokens  which is below the vector size for the embedding for the one we are using(limit is 256 for Mini LLM -L6-V2)
---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->
- Accuracy  of response- I would like the score to be preferably below 0.5 and as near to 0.3 as possible
- No non relevant answer and low halucination- If there is no content for a specific question the retreival should say not found and LLM should not respond with a cooked up answer (i.e low halucination)


**Why this target:**

I care about accuracy of information and that would mean relevant, having context, not hallunicanated  and within a reasonable amount of wait time.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     WEEK 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in week 2:** For at least 4 of 5 questions, the top three
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
