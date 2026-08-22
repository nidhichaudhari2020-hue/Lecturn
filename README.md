# Lecturn

Lecturn turns PDF study notes into a private, session-based AI tutor. Upload one
or more PDFs, ask grounded questions with document and page citations, generate
quizzes and flashcards, identify weak topics, and export the session as Markdown.

## Highlights

- Cited Q&A grounded in the uploaded notes
- AI-generated summaries, important topics, quizzes, and flashcards
- Weak-topic practice and lightweight progress tracking
- Demo lesson for first-time visitors
- Per-session vector collections to prevent visitors sharing document indexes
- Temporary PDF deletion immediately after extraction
- Markdown export and one-click workspace clearing
- Responsive layout, keyboard focus styles, and reduced-motion support

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Add `GROQ_API_KEY=your-key` to a local `.env` file.
4. Run `streamlit run app.py`.

The landing screen and PDF indexing work without a Groq key, but generative AI
features remain disabled until the key is configured.

## Deploy on Streamlit Community Cloud

Deploy `app.py`, then add `GROQ_API_KEY` under **App settings → Secrets**. Make
the app public if it should be accessible without Streamlit authentication.

## Privacy notes

Uploaded PDFs are written only to a temporary file for text extraction and are
then deleted. Extracted chunks use a unique collection for each browser session.
Progress is intentionally session-only because a shared JSON file is unsafe in a
multi-user deployment. Production-grade persistence should use authenticated
accounts and a database with row-level user isolation.