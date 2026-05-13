# Mini Research Proposal Flow (10 Slides)

Use this as your direct PPT script.

## Slide 1 - Project Title

Explainable Multimodal Research Paper Assistant:
Evidence-Grounded Summarization and QA from PDF Text and Figures

Add:

- Your name
- Course / Lab
- Guide name

## Slide 2 - Motivation

- Research papers are long and dense.
- Figures and tables are often hard to interpret quickly.
- Most assistants summarize only text.
- Students need transparent answers with source evidence.

Goal:

Build a system that reads paper text and figures together, then provides explainable summaries and answers.

## Slide 3 - Problem Statement

Current systems can:

- summarize text
- answer simple questions

But they often fail to:

1. understand figure content
2. connect figure insights with methodology/results
3. provide trustworthy evidence traces

Research Question:

How can we design an explainable multimodal assistant for research paper understanding that links answers to both text and visual evidence?

## Slide 4 - Domain and Applications

Domain:

- Multimodal AI
- NLP + Computer Vision + Explainable AI

Applications:

- student learning support
- fast literature review
- thesis survey writing
- research onboarding for new team members

## Slide 5 - Dataset and Input Scope

Input data:

- user-uploaded research PDFs
- extracted text blocks
- extracted embedded figures

Feasibility subset for project demo:

- 30-100 papers from a focused domain (for example NLP or medical AI)
- prioritize papers with clear figure content

## Slide 6 - Proposed Technical Approach

Pipeline:

PDF Upload
-> Text + Figure Extraction
-> Figure Captioning (ViT)
-> Text Summarization (BART)
-> Retrieval (Sentence Transformer)
-> QA (RoBERTa SQuAD)
-> Explainability Trace

Tech stack:

- Frontend: React (Vite)
- Backend: Flask
- Models: ViT-GPT2, BART, RoBERTa, MiniLM embeddings

## Slide 7 - Explainability Strategy

Explainability outputs:

- ranked evidence chunks with page numbers
- retrieval scores for each evidence block
- figure references used in answering
- confidence score for final answer

Example:

Question: What is the key contribution?
Answer + Evidence:

- Rank 1, Page 3: "We propose..."
- Rank 2, Page 5: "Experimental gain..."

## Slide 8 - Feasibility

Data feasibility:

- no expensive manual labeling needed for baseline
- direct PDF ingestion pipeline

Model feasibility:

- uses pretrained open-source models
- fallback logic for low-resource/offline scenarios

Hardware feasibility:

- works on Google Colab / Kaggle / local CPU (slower)

## Slide 9 - Expected Results and Metrics

Expected outputs:

- high-quality paper summary
- figure-level textual explanation
- evidence-grounded QA

Metrics:

- Summary: ROUGE, BLEU, METEOR
- QA: Exact Match, F1
- Explainability: human relevance scoring of evidence traces

## Slide 10 - Contribution and Novelty

1. End-to-end multimodal paper assistant using React + Flask.
2. Figure-aware explanation via ViT-based captioning.
3. Evidence-grounded QA with transparent reasoning trace.
4. Practical, student-friendly workflow for research understanding.

## Closing Line for Presentation

Our assistant does not just answer; it shows where and why the answer comes from by linking paper text, figure understanding, and evidence traces.
