# 🎓 RevisionBuddy

> Turn any lecture video or study notes into structured exam revision packs, tiered Q&As, model answers, and interactive grading mechanisms powered by Google Gemini.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://revisionbuddy.streamlit.app)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Overview

**RevisionBuddy** is an AI-powered study companion designed to solve a universal student problem: turning long, dense lecture videos or raw transcripts into high-yield, structured revision material in seconds. 

By leveraging the **Google GenAI SDK** and **Pydantic** structured schemas, RevisionBuddy extracts timestamped transcripts from YouTube lectures (or accepts direct text pastes), analyzes the core concepts, and automatically generates a comprehensive exam revision pack complete with Multiple Choice Questions (MCQs), Short Answer Questions, Long Answer Essays, and Viva / Oral exam prompts.

---

## ✨ Key Features

* **🎥 Dual Input Support:** Extract transcripts automatically via YouTube URL or paste raw lecture/notes text directly (built-in cloud IP fallback).
* **🧠 Tiered Exam Generation:** Automatically structures questions into:
  * **MCQs** with instant option grading.
  * **Short Answer Questions** testing concise core knowledge.
  * **Long Answer / Essay Questions** for deep conceptual understanding.
  * **Viva Voce Prompts** for oral defense and critical thinking.
* **🤖 Interactive AI Grading & Feedback:** Type your student answers to any question and have Gemini grade your response, give constructive feedback, and award a score.
* **⏱️ Timestamp Navigation:** Links questions directly back to lecture timestamps so you can jump straight to the source material.
* **📚 Local Revision History (SQLite):** Automatically caches generated revision packs locally so you can revisit past lectures instantly without re-generating.

---

## 🛠️ Tech Stack

* **Frontend & UI:** [Streamlit](https://streamlit.io/)
* **AI Engine:** Google Gemini API (`google-genai` SDK) using `gemini-1.5-flash`
* **Data Validation:** Pydantic (strict JSON schema enforcement)
* **Transcript Extraction:** `youtube-transcript-api`
* **Database & Caching:** SQLite3

---

## ⚙️ Project Structure

```text
lecture-revision-ai/
│
├── app.py                 # Main Streamlit user interface & session state
├── ai_engine.py           # Gemini API integration & structured prompt handling
├── models.py              # Pydantic schemas for structured Q&A generation
├── database.py            # SQLite caching layer for revision history
├── transcript_utils.py    # YouTube transcript parser & cloud fallback handler
├── requirements.txt       # Python package dependencies
└── .env                   # Local environment variables (git-ignored)
