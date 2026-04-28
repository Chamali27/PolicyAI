# PolicyAI System

AI-powered system that summarises real-world policy documents and generates scenario-based policy drafts using Generative AI.

---

## Project Overview

This project presents an AI-assisted web application built to analyse and adapt real-world policy documents for different scenarios and audiences.

The analysis focuses on:

- Policy summarisation using NLP techniques
- Scenario-based policy draft generation
- Interactive web interface for policy exploration

---

## Policy Document Used

- **Source:** SriLankan Airlines — Conditions of Carriage & Online Booking Terms
- **Type:** Real-world published aviation policy
- **Format:** PDF / Text

---

## Technologies Used

- **Python** — Core programming language
- **Ollama (llama3.2)** — Local LLM for generative policy drafting
- **Streamlit** — Web application framework
- **NLTK** — Text preprocessing and TF-IDF summarisation
- **PyPDF2 / python-docx** — Document parsing
- **GitHub** — Version control and project documentation
---

---

## How to Run

**Step 1 – Install Ollama and pull the model**

Go to [ollama.com](https://ollama.com) and install Ollama, then run:

```bash
ollama pull llama3.2
ollama serve
```

**Step 2 – Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 3 – Run the app**

```bash
streamlit run policy_app.py
```

The app will open at `http://localhost:8501`

---

## Key Features

- NLP-based summarisation of complex policy documents
- TF-IDF extractive summarisation with Brief, Standard and Detailed depth levels
- Minimum 2 scenario-based adapted policy drafts
- Free Draft mode — generate any policy from a plain description
- Interactive left/right panel web interface
- Supports multiple scenarios from the same summary
- Upload PDF, DOCX, or TXT — or paste text directly
- Download summaries and drafts as `.txt` files

---

## Project Structure
