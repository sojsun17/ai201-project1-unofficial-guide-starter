# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Student reviews of Computer Science professors at Queens College, CUNY. This knowledge is valuable because official course descriptions and faculty pages tell you nothing about teaching style, exam difficulty, grading fairness, or how approachable a professor is outside of class. The only way to find this information is to dig through RateMyProfessors individually for each professor — there is no single place to ask a plain-language question and get a grounded answer drawn from real student experiences.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | RateMyProfessors | Student reviews | documents/prof_bojana_obrenic.txt |
| 2 | RateMyProfessors | Student reviews | documents/prof_gaurish_telang.txt |
| 3 | RateMyProfessors | Student reviews | documents/prof_delaram_kahrobaei.txt |
| 4 | RateMyProfessors | Student reviews | documents/prof_john_svadlenka.txt |
| 5 | RateMyProfessors | Student reviews | documents/prof_oren_teinberg.txt |
| 6 | RateMyProfessors | Student reviews | documents/prof_alex_ryba.txt |
| 7 | RateMyProfessors | Student reviews | documents/prof_cuneyt_akinlar.txt |
| 8 | RateMyProfessors | Student reviews | documents/prof_kent_boklan.txt |
| 9 | RateMyProfessors | Student reviews | documents/prof_joseph_svitak.txt |
| 10 | RateMyProfessors | Student reviews | documents/prof_tsaiyun_phillips.txt |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** Each document contains short student reviews, typically 2–5 sentences per review. A 400-character chunk is large enough to capture one complete review or one coherent opinion without merging unrelated reviews together. The 50-character overlap ensures that if a review happens to split across a chunk boundary, the key point is not lost — a sentence that starts at the end of one chunk also appears at the start of the next. Before chunking, documents were cleaned by stripping blank lines and collapsing extra whitespace so that the chunker works on clean, continuous text rather than fragmented lines.

**Final chunk count:** 47 chunks across 10 documents

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (runs locally, no API key or rate limits required)

**Production tradeoff reflection:** For a real deployment serving many users, I would evaluate OpenAI's text-embedding-3-small. It produces higher-accuracy embeddings on domain-specific text and supports longer context windows (up to 8191 tokens vs. 256 for all-MiniLM-L6-v2), which matters if documents contain longer reviews. The tradeoff is cost — it charges per token — and API dependency, meaning retrieval breaks if the API goes down. I would also consider a multilingual model if the student body writes reviews in languages other than English, since all-MiniLM-L6-v2 performs poorly on non-English text. For latency-sensitive production systems, a locally hosted model like all-MiniLM-L6-v2 has an advantage because inference happens on-device with no network round trip.

---

## Grounded Generation

**System prompt grounding instruction:**

The following instruction is passed to the LLM with every query:

> "You are a helpful assistant that answers questions about CS professors at Queens College, CUNY. Answer the question using ONLY the information provided in the documents below. Do not use any outside knowledge. If the documents do not contain enough information to answer the question, say exactly: 'I don't have enough information in my documents to answer that.'"

The retrieved chunks are formatted as:

```
[Source: prof_cuneyt_akinlar.txt]
<chunk text>

[Source: prof_john_svadlenka.txt]
<chunk text>
```

This structure makes the source of each piece of context explicit to the model, encouraging it to attribute its answer to the right document.

**How source attribution is surfaced in the response:** After generation, the app programmatically extracts the source filenames from the retrieved chunks and displays them in a separate "Retrieved from" field in the Gradio interface. This means source attribution is guaranteed by the pipeline structure, not left to the LLM to include voluntarily.

---

## Sample Chunks

**Chunk 1 (source: prof_cuneyt_akinlar.txt)**
> Professor: Cuneyt Akinlar Department: Computer Science University: Queens College, CUNY Courses: CS 316, CS 416 Source: RateMyProfessors.com --- Review 1 --- This professor is very beginner friendly and explains programming concepts in a clear and approachable way. Students new to CS tend to do well here.

**Chunk 2 (source: prof_cuneyt_akinlar.txt)**
> nd to do very well. The environment is supportive and structured. --- Review 8 --- Difficult concepts are explained in a simplified way that is easy to understand. Good pacing for beginners.

**Chunk 3 (source: prof_john_svadlenka.txt)**
> Professor: John Svadlenka Department: Computer Science University: Queens College, CUNY Courses: CS 111, CS 112 --- Review 1 --- Very heavy workload with frequent assignments and strict grading. --- Review 2 --- Lectures are dense and require strong attention to keep up.

**Chunk 4 (source: prof_delaram_kahrobaei.txt)**
> Exams require deep conceptual understanding rather than memorization. You need to fully grasp the material. --- Review 4 --- Lectures are dense but informative if you pay close attention. Staying engaged is important.

**Chunk 5 (source: prof_alex_ryba.txt)**
> Professor: Alex Ryba Department: Computer Science University: Queens College, CUNY --- Review 1 --- Strong theoretical background. Lectures are challenging but rewarding for students who enjoy math-heavy CS.

---

## Retrieval Test Results

**Query 1:** "Which professor is good for beginners?"
- Top chunk returned: prof_cuneyt_akinlar.txt — "This professor is very beginner friendly and explains programming concepts in a clear and approachable way."
- Distance score: 0.96
- The returned chunks are relevant because the query uses the word "beginners" and the Akinlar document explicitly contains the phrase "beginner friendly" and "good pacing for beginners."

**Query 2:** "What do students say about Professor Svadlenka's exams?"
- Top chunk returned: prof_john_svadlenka.txt — "Exams are significantly harder than expected based on lecture material."
- Distance score: 1.12
- The returned chunks are partially relevant — they mention exams but the short, generic nature of the reviews limits how much detail is retrievable.

**Query 3:** "What do students think of Professor Kahrobaei's workload?"
- Top chunk returned: prof_delaram_kahrobaei.txt — "The workload is significant but manageable for motivated students. It requires discipline."
- Distance score: 1.04
- The returned chunks are relevant — multiple chunks from the Kahrobaei file contain workload-related language.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Professor Svadlenka's teaching style? | Reviews mentioning dense lectures, strict grading, difficulty following material | System said it did not have enough information | Off-target | Inaccurate |
| 2 | Which Queens College CS professor is recommended for students taking CS 111 for the first time? | Should name Akinlar or another professor with positive beginner reviews | Correctly recommended Akinlar, citing beginner-friendly teaching and clear explanations | Relevant | Accurate |
| 3 | How difficult are Professor Telang's exams? | Student mentions of exam difficulty, curve, study tips | System said it did not have enough information | Off-target | Inaccurate |
| 4 | What do students think of Professor Obrenic's grading? | Reviews mentioning grading fairness or strictness | Returned a partial answer about strict grading standards with some source attribution | Partially relevant | Partially accurate |
| 5 | What do students say about Professor Kahrobaei's workload? | Reviews mentioning significant workload, theory-heavy, needs discipline | Correctly described significant workload, cited that it is rewarding for motivated students | Relevant | Accurate |

---

## Failure Case Analysis

**Question that failed:** "What do students say about Professor Svadlenka's teaching style?" and "How difficult are Professor Telang's exams?"

**What the system returned:** "I don't have enough information in my documents to answer that."

**Root cause (tied to a specific pipeline stage):** The failure occurs at the chunking and embedding stages. The reviews in each document are very short — typically one sentence per review — which means each chunk carries very little semantic signal after embedding. When the query asks specifically about "teaching style" or "exam difficulty," the embedding model cannot find a strong enough similarity match between the query vector and any chunk vector because the chunks are too brief and generic to represent specific concepts clearly. The distance scores on retrieved chunks are above 1.0, indicating weak matches. Additionally, the reviews were not sourced from real RateMyProfessors pages — they were short placeholder-style sentences rather than the detailed, opinionated student writing that would produce more semantically rich embeddings.

**What you would change to fix it:** Replace the placeholder reviews with real, longer student reviews from RateMyProfessors (target 2000+ characters per professor file). Longer, more specific reviews would produce chunks that carry enough semantic content for the embedding model to find strong matches on specific queries about teaching style or exam difficulty.

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing the chunking strategy section of planning.md before writing any code forced me to think about chunk size before seeing how the data actually looked. When I later inspected real chunks and found that 400 characters was capturing roughly one review per chunk, it confirmed that the reasoning in the spec was sound. Having the architecture diagram in the spec also made it straightforward to explain to Claude what each script needed to do — the diagram served as shared context for every code generation prompt.

**One way your implementation diverged from the spec, and why:** The spec anticipated collecting real, opinionated student reviews from RateMyProfessors. In practice, the reviews collected were short and generic (1–2 sentences each) rather than the detailed multi-sentence reviews that exist on the site. This meant the final chunk count (47) was lower than anticipated, and retrieval quality was weaker than planned. The chunking parameters stayed the same, but the document quality was lower than the spec assumed, which directly caused several evaluation failures.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Documents section and Chunking Strategy section from planning.md, plus the requirement that the script load all .txt files from a local folder, clean whitespace, and split into 400-character chunks with 50-character overlap.
- *What it produced:* A complete ingest.py with load_documents(), clean_text(), and chunk_text() functions that matched the spec exactly, plus a __main__ block that printed 5 sample chunks for inspection.
- *What I changed or overrode:* The folder name — the generated code used "qc_documents" but my actual folder was named "documents", so I updated the DOCUMENTS_DIR constant. I also verified the chunk output by reading the printed samples and confirmed the sizes looked right before moving on.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from planning.md (model name: all-MiniLM-L6-v2, top-k: 5) and the full pipeline architecture diagram, plus the grounding requirement that the LLM answer only from retrieved context and include source attribution.
- *What it produced:* A complete app.py with retrieve(), generate(), and ask() functions, plus a Gradio interface with an answer box and a sources box. The system prompt included the grounding instruction and the context was formatted with source labels.
- *What I changed or overrode:* The generated code used load_dotenv() without the override=True parameter, which caused the API key to load from a cached version of the .env file rather than the current one. I added override=True to fix this. I also verified grounding by asking an out-of-scope question ("What is the best restaurant near Queens College?") and confirming the system refused rather than hallucinating.