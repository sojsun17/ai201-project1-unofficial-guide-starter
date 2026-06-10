# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Student reviews of Computer Science professors at Queens College, CUNY. This knowledge is valuable because it reflects real student experiences with grading, teaching style, and workload — information that isn't available through any official Queens College channel. A prospective student has no way to find out which professors give useful feedback or which courses are manageable without digging through scattered RateMyProfessors pages themselves.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | RateMyProfessors | Student reviews of Bojana Obrenic | https://www.ratemyprofessors.com/professor/249702 |
| 2 | RateMyProfessors | Student reviews of Gaurish Telang |https://www.ratemyprofessors.com/professor/2937156 |
| 3 | RateMyProfessors | Student reviews of Delaram Kahrobaei | https://www.ratemyprofessors.com/professor/2870283 |
| 4 | RateMyProfessors | Student reviews of John Svadlenka | https://www.ratemyprofessors.com/professor/2485140 |
| 5 | RateMyProfessors | Student reviews of Oren Steinberg | https://www.ratemyprofessors.com/professor/2698138 |
| 6 | RateMyProfessors | Student reviews of Alex Ryba | https://www.ratemyprofessors.com/professor/44623|
| 7 | RateMyProfessors | Student reviews of Cuneyt Akinlar | https://www.ratemyprofessors.com/professor/2941773 |
| 8 | RateMyProfessors | Student reviews of Kent Boklan | https://www.ratemyprofessors.com/professor/629756|
| 9 | RateMyProfessors | Student reviews of Joseph Svitak | https://www.ratemyprofessors.com/professor/348234 |
| 10 | RateMyProfessors | Student reviews of Tsaiyun Phillips | https://www.ratemyprofessors.com/professor/1870716 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Reasoning:** Each document contains short student reviews, typically 2–5 sentences long. A 400-character chunk is large enough to capture one complete review or one coherent opinion, but small enough that unrelated reviews don't get merged together. The 50-character overlap ensures that if a review happens to split across a chunk boundary, the key point isn't lost — a sentence that starts at the end of one chunk will also appear at the start of the next. Larger chunks (e.g. 1000+ characters) would dilute individual opinions by mixing multiple reviews into one embedding, making it harder to match a specific query to the right student's experience.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers (runs locally, no API key or rate limits)

**Top-k:** 5 chunks per query

**Production tradeoff reflection:** For a real deployment I would consider OpenAI's text-embedding-3-small, which produces higher-accuracy embeddings on domain-specific text and supports longer context windows. The tradeoff is cost (charged per token) and API dependency — if the API goes down, retrieval breaks. I would also consider a multilingual model if the student body writes reviews in languages other than English. all-MiniLM-L6-v2 is the right choice here because it's free, fast, and requires no internet connection at inference time.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Professor Svadlenka's teaching style? | Reviews should mention poor clarity, difficulty following lectures, or specific complaints about how material is explained |
| 2 | Which Queens College CS professor is recommended for students taking CS 111 for the first time? | Should name a professor with positive reviews in intro-level courses and mention approachability or clear explanations |
| 3 | How difficult are Professor Telang's exams? | Student mentions of exam difficulty level, whether exams are curved, and any study tips reviewers suggest |
| 4 | What do students think of Professor Obrenic's grading? | Reviews mentioning grading fairness, strictness, rubric clarity, or how easy or hard it is to get a good grade |
| 5 | What do students say about Professor Kahrobaei's workload? | Reviews mentioning how much work is assigned, time commitment, or whether the course is manageable alongside other classes |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Very short reviews producing weak embeddings.** Some students write only one sentence (e.g. "Terrible professor, avoid."). A chunk this short carries almost no semantic signal, so the embedding model may not match it to relevant queries even when it's the most useful review. This could cause retrieval to return longer but less relevant chunks instead.

2. **Professor names referenced inconsistently.** Students often write just a last name, a nickname, or misspell the professor's name entirely. The embedding model has no way to know that "Svad" or "Svadlenka" refer to the same person, which means queries using the full name may miss reviews that use a shortened version, and vice versa.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         DOCUMENT INGESTION                  │
│  Load .txt files from qc_documents/         │
│  Library: Python open() / os.listdir()      │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         CHUNKING                            │
│  Split by 400 chars, 50 char overlap        │
│  Library: LangChain CharacterTextSplitter   │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│    EMBEDDING + VECTOR STORE                 │
│  Embed: sentence-transformers               │
│         (all-MiniLM-L6-v2)                 │
│  Store: ChromaDB (local)                    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         RETRIEVAL                           │
│  Semantic similarity search                 │
│  Top-k = 5 chunks returned per query        │
│  Library: ChromaDB query()                  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         GENERATION                          │
│  LLM: Groq (llama-3.3-70b-versatile)       │
│  Grounded prompt: answer from context only  │
│  Output: Answer + source file citations     │
└─────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         QUERY INTERFACE                     │
│  Library: Gradio                            │
│  Input: text box for question               │
│  Output: answer + sources displayed         │
└─────────────────────────────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I will use Claude. I'll provide the Documents table (file names and locations), the Chunking Strategy section (400 char chunks, 50 char overlap), and ask it to write `ingest.py` — a script that loads all .txt files from `qc_documents/`, strips blank lines and extra whitespace, splits each document into chunks using those exact parameters, and prints 5 sample chunks so I can verify the output looks correct. I'll verify by reading the printed chunks and checking they look like complete review sentences, not fragments or HTML.

**Milestone 4 — Embedding and retrieval:**
I will use Claude. I'll provide the Retrieval Approach section (model name, top-k value) and the Architecture diagram, and ask it to write `embed.py` (loads chunks from ingest.py, embeds with all-MiniLM-L6-v2, stores in ChromaDB with source filename as metadata) and `retrieve.py` (takes a query string, returns top-5 chunks with source names and distance scores). I'll verify by running 3 of my evaluation questions and checking that returned chunks visibly relate to each question and distance scores are below 0.5.

**Milestone 5 — Generation and interface:**
I will use Claude. I'll provide the full planning.md and ask it to write `app.py` — a Gradio interface that calls retrieve.py, passes the top-5 chunks into a Groq prompt that explicitly instructs the model to answer from the retrieved context only, and displays the answer plus source filenames. I'll verify grounding by asking a question my documents don't cover and confirming the system says it doesn't have enough information rather than making something up.