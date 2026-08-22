import os
import json
import tempfile
from html import escape
from datetime import date, timedelta

import streamlit as st
import streamlit.components.v1 as components

from backend.important_topics import generate_important_topics
from backend.summarizer import generate_summary
from backend.quiz_ui import show_quiz
from backend.dashboard import show_dashboard
from backend.flashcards import generate_flashcards
from backend.pdf_loader import extract_text
from backend.chunker import split_into_chunks
from backend.embedder import generate_embeddings
from backend.vectordb import store_chunks, reset_database
from backend.quiz_generator import generate_quiz
from backend.rag import ask_question
from backend.weak_topic_helper import generate_weak_topic_solution
from backend.weak_topic_practice import generate_topic_practice
from config import GROQ_API_KEY


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Lecturn",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# LOAD CSS
# =========================================================

def load_css():
    try:
        with open(
            "assets/style.css",
            encoding="utf-8"
        ) as file:

            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )

    except FileNotFoundError:
        pass


load_css()


# =========================================================
# PROGRESS STORAGE
# =========================================================

PROGRESS_FILE = "data/user_progress.json"


def load_progress():
    default_progress = {
        "xp": 0,
        "study_streak": 1,
        "last_study_date": "",
        "quiz_completed": 0,
        "flashcards_reviewed": 0,
        "weak_topics": {}
    }

    # Progress is intentionally session-only. A shared server-side JSON file
    # would mix the data of unrelated visitors on a public Streamlit app.
    return default_progress


def save_progress():
    # Kept as a compatibility hook for quiz modules. State already lives in
    # st.session_state and is private to the current browser session.
    return None


saved_progress = load_progress()


# =========================================================
# SESSION STATE
# =========================================================

defaults = {

    # Main
    "indexed": False,
    "messages": [],
    "last_uploaded_files": [],
    "source_files": [],

    # Navigation
    "scroll_target": None,

    # Gamification
    "xp": saved_progress["xp"],
    "study_streak": saved_progress["study_streak"],
    "last_study_date": saved_progress["last_study_date"],
    "quiz_completed": saved_progress["quiz_completed"],
    "flashcards_reviewed": (
        saved_progress["flashcards_reviewed"]
    ),

    # Weak Topics
    "weak_topics": saved_progress["weak_topics"],

    # Quiz
    "quiz": [],
    "quiz_version": 0,
    "current_question": 0,
    "score": 0,
    "show_result": False,
    "selected_option": None,
    "quiz_bonus_given": False,

    # Flashcards
    "flashcards": [],
    "current_flashcard": 0,
    "show_answer": False,

    # Weak Topic Practice
    "practice_questions": [],
    "practice_topic": "",
    "practice_index": 0,
    "practice_result": False,
    "practice_selected": None,
    "practice_xp_awarded": False,

    # Dashboard
    "total_pdfs": 0,
    "total_pages": 0,
    "total_chunks": 0,

    # Generated Content
    "summary": "",
    "important_topics": ""
}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# STUDY STREAK
# =========================================================

today = date.today()

last_date = (
    st.session_state.last_study_date
)

if not last_date:

    st.session_state.study_streak = 1

    st.session_state.last_study_date = (
        today.isoformat()
    )

    save_progress()

else:

    try:

        previous_date = date.fromisoformat(
            last_date
        )

        if previous_date == today:
            pass

        elif previous_date == today - timedelta(days=1):

            st.session_state.study_streak += 1

            st.session_state.last_study_date = (
                today.isoformat()
            )

            save_progress()

        elif previous_date < today - timedelta(days=1):

            st.session_state.study_streak = 1

            st.session_state.last_study_date = (
                today.isoformat()
            )

            save_progress()

    except Exception:
        pass


# =========================================================
# HERO
# =========================================================

hero_html = (
    '<div class="hero-card">'
    '<div class="hero-title">📚 Lecturn</div>'
    '<div class="hero-text">'
    'Upload your PDF notes, then learn with cited answers, quizzes, '
    'flashcards and focused revision—all in one private session.'
    '</div>'
    '</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True
)


# =========================================================
# FEATURE CARDS
# =========================================================

feature_columns = st.columns(4)

features = [
    (
        "💬",
        "Ask Questions",
        "Chat with your uploaded study notes."
    ),
    (
        "📝",
        "Take Quizzes",
        "Test yourself using AI-generated MCQs."
    ),
    (
        "🃏",
        "Flashcards",
        "Revise important concepts quickly."
    ),
    (
        "⭐",
        "Exam Focus",
        "Generate summaries and key topics."
    )
]


for column, feature in zip(
    feature_columns,
    features
):

    icon, title, description = feature

    card_html = (
        '<div class="feature-card">'
        f'<div class="feature-icon">{icon}</div>'
        f'<div class="feature-title">{title}</div>'
        f'<div class="feature-text">{description}</div>'
        '</div>'
    )

    with column:

        st.markdown(
            card_html,
            unsafe_allow_html=True
        )


st.write("")


# =========================================================
# LEARNING PROGRESS
# =========================================================

st.subheader(
    "🌱 Your Learning Progress"
)

p1, p2, p3, p4 = st.columns(4)


with p1:

    st.metric(
        "⭐ XP",
        st.session_state.xp
    )


with p2:

    st.metric(
        "🔥 Study Streak",
        f"{st.session_state.study_streak} days"
    )


with p3:

    st.metric(
        "📝 Quizzes",
        st.session_state.quiz_completed
    )


with p4:

    st.metric(
        "🃏 Cards Reviewed",
        st.session_state.flashcards_reviewed
    )


# =========================================================
# CONTINUE STUDYING
# =========================================================

st.subheader(
    "🚀 Continue Studying"
)

c1, c2, c3, c4 = st.columns(4)


with c1:

    if st.button(
        "💬 Ask AI",
        use_container_width=True
    ):

        st.session_state.scroll_target = (
            "chat-section"
        )

        st.rerun()


with c2:

    if st.button(
        "📝 Continue Quiz",
        use_container_width=True
    ):

        if st.session_state.quiz:

            st.session_state.scroll_target = (
                "quiz-section"
            )

            st.rerun()

        else:

            st.info(
                "Generate a quiz first."
            )


with c3:

    if st.button(
        "🃏 Review Flashcards",
        use_container_width=True
    ):

        if st.session_state.flashcards:

            st.session_state.scroll_target = (
                "flashcards-section"
            )

            st.rerun()

        else:

            st.info(
                "Generate flashcards first."
            )


with c4:

    if st.button(
        "⚠ Weak Topics",
        use_container_width=True
    ):

        st.session_state.scroll_target = (
            "weak-topics-section"
        )

        st.rerun()


st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "📂 Study Workspace"
)

uploaded_files = st.sidebar.file_uploader(
    "Upload your PDF notes",
    type=["pdf"],
    accept_multiple_files=True,
    help=(
        "Upload one or more PDFs. "
        "They will be indexed automatically."
    )
)

st.sidebar.caption(
    "PDF only · up to 20 MB each · text is removed after indexing"
)

if not GROQ_API_KEY:
    st.sidebar.error(
        "AI features are not configured. Add GROQ_API_KEY to "
        "Streamlit Secrets or a local .env file."
    )

with st.sidebar.expander("How your data is handled"):
    st.write(
        "Your PDFs are processed for this browser session. Temporary files "
        "are deleted after text extraction and each session uses a separate "
        "search collection. Starting a new session clears your workspace."
    )

if st.sidebar.button(
    "Try a demo lesson", use_container_width=True,
    disabled=st.session_state.indexed
):
    demo_pages = [{
        "page": 1,
        "source": "Demo lesson: The scientific method",
        "text": (
            "The scientific method is an iterative process for building "
            "reliable knowledge. It commonly includes observation, a testable "
            "question, a falsifiable hypothesis, an experiment with controlled "
            "variables, analysis of results, and a conclusion. The independent "
            "variable is deliberately changed; the dependent variable is "
            "measured. Repetition and peer review improve reliability. A result "
            "that does not support a hypothesis is still useful evidence."
        )
    }]
    with st.spinner("Preparing the demo lesson..."):
        reset_database()
        demo_chunks = split_into_chunks(demo_pages)
        store_chunks(
            demo_chunks,
            generate_embeddings([chunk["text"] for chunk in demo_chunks])
        )
    st.session_state.indexed = True
    st.session_state.total_pdfs = 0
    st.session_state.total_pages = 1
    st.session_state.total_chunks = len(demo_chunks)
    st.session_state.source_files = ["Demo lesson: The scientific method"]
    st.sidebar.success("Demo ready—try asking a question.")
    st.rerun()

if st.sidebar.button(
    "Clear this workspace", use_container_width=True,
    disabled=not st.session_state.indexed
):
    reset_database()
    for key in (
        "messages", "last_uploaded_files", "source_files", "quiz",
        "flashcards", "practice_questions"
    ):
        st.session_state[key] = []
    for key in ("summary", "important_topics"):
        st.session_state[key] = ""
    st.session_state.indexed = False
    st.session_state.total_pdfs = 0
    st.session_state.total_pages = 0
    st.session_state.total_chunks = 0
    st.sidebar.success("Workspace cleared.")
    st.rerun()

st.sidebar.divider()


# =========================================================
# AUTO INDEX PDF
# =========================================================

if uploaded_files:

    oversized = [file.name for file in uploaded_files if file.size > 20 * 1024 * 1024]
    if oversized:
        st.sidebar.error(
            "These files exceed the 20 MB limit: " + ", ".join(oversized)
        )
        uploaded_files = []

    current_files = [
        f"{uploaded_file.name}-{uploaded_file.size}"
        for uploaded_file in uploaded_files
    ]

    if (
        st.session_state.last_uploaded_files
        != current_files
    ):

        try:

            with st.spinner(
                "🧠 Reading and preparing your notes..."
            ):

                os.makedirs(
                    "data",
                    exist_ok=True
                )

                reset_database()

                progress = (
                    st.sidebar.progress(0)
                )

                all_chunks = []
                total_pages = 0
                total_files = len(
                    uploaded_files
                )

                for index, uploaded_file in enumerate(
                    uploaded_files
                ):

                    with tempfile.NamedTemporaryFile(
                        suffix=".pdf", delete=False
                    ) as temporary_file:
                        temporary_file.write(uploaded_file.getbuffer())
                        save_path = temporary_file.name

                    try:
                        pages = extract_text(save_path)
                    finally:
                        try:
                            os.remove(save_path)
                        except OSError:
                            pass

                    for page in pages:
                        page["source"] = uploaded_file.name

                    total_pages += len(
                        pages
                    )

                    chunks = split_into_chunks(
                        pages
                    )

                    all_chunks.extend(
                        chunks
                    )

                    progress.progress(
                        int(
                            ((index + 1) / total_files)
                            * 50
                        )
                    )

                if not all_chunks:

                    st.sidebar.error(
                        "No readable text was found."
                    )

                else:

                    progress.progress(60)

                    texts = [
                        chunk["text"]
                        for chunk in all_chunks
                    ]

                    embeddings = generate_embeddings(
                        texts
                    )

                    progress.progress(85)

                    store_chunks(
                        all_chunks,
                        embeddings
                    )

                    progress.progress(100)

                    st.session_state.indexed = True

                    st.session_state.total_pdfs = len(
                        uploaded_files
                    )

                    st.session_state.total_pages = (
                        total_pages
                    )

                    st.session_state.total_chunks = len(
                        all_chunks
                    )

                    st.session_state.last_uploaded_files = (
                        current_files
                    )
                    st.session_state.source_files = [
                        file.name for file in uploaded_files
                    ]

                    # Reset generated content
                    st.session_state.quiz = []
                    st.session_state.current_question = 0
                    st.session_state.score = 0
                    st.session_state.show_result = False
                    st.session_state.selected_option = None
                    st.session_state.quiz_bonus_given = False

                    st.session_state.flashcards = []
                    st.session_state.current_flashcard = 0
                    st.session_state.show_answer = False

                    st.session_state.practice_questions = []
                    st.session_state.practice_topic = ""
                    st.session_state.practice_index = 0
                    st.session_state.practice_result = False
                    st.session_state.practice_selected = None
                    st.session_state.practice_xp_awarded = False

                    st.session_state.summary = ""
                    st.session_state.important_topics = ""
                    st.session_state.messages = []

                    st.sidebar.success(
                        "✅ Notes indexed automatically!"
                    )

        except Exception as error:

            st.session_state.indexed = False

            st.sidebar.error(
                f"Automatic indexing failed: {error}"
            )

else:

    st.sidebar.info(
        "📄 Upload PDF notes to begin."
    )


# =========================================================
# STUDY TOOLS
# =========================================================

st.sidebar.subheader(
    "🎓 Study Tools"
)


# =========================================================
# QUIZ
# =========================================================

if st.sidebar.button(
    "📝 Generate Quiz",
    use_container_width=True,
    disabled=not bool(GROQ_API_KEY)
):

    if not st.session_state.indexed:

        st.sidebar.warning(
            "Please upload your notes first."
        )

    else:

        try:

            with st.spinner(
                "📝 Creating a fresh quiz..."
            ):

                quiz = generate_quiz()

            if quiz:

                st.session_state.quiz = quiz
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.show_result = False
                st.session_state.selected_option = None
                st.session_state.quiz_bonus_given = False
                st.session_state.quiz_version += 1

                st.session_state.scroll_target = (
                    "quiz-section"
                )

                st.sidebar.success(
                    "Quiz generated!"
                )

                st.rerun()

            else:

                st.sidebar.error(
                    "Quiz generation failed."
                )

        except Exception as error:

            st.sidebar.error(
                f"Quiz generation failed: {error}"
            )


# =========================================================
# FLASHCARDS
# =========================================================

if st.sidebar.button(
    "🃏 Generate Flashcards",
    use_container_width=True,
    disabled=not bool(GROQ_API_KEY)
):

    if not st.session_state.indexed:

        st.sidebar.warning(
            "Please upload your notes first."
        )

    else:

        try:

            with st.spinner(
                "🃏 Creating flashcards..."
            ):

                flashcards = (
                    generate_flashcards()
                )

            if flashcards:

                st.session_state.flashcards = (
                    flashcards
                )

                st.session_state.current_flashcard = 0
                st.session_state.show_answer = False

                st.session_state.scroll_target = (
                    "flashcards-section"
                )

                st.sidebar.success(
                    "Flashcards generated!"
                )

                st.rerun()

            else:

                st.sidebar.error(
                    "Flashcard generation failed."
                )

        except Exception as error:

            st.sidebar.error(
                f"Flashcard generation failed: {error}"
            )


# =========================================================
# SUMMARY
# =========================================================

if st.sidebar.button(
    "📚 Generate Summary",
    use_container_width=True,
    disabled=not bool(GROQ_API_KEY)
):

    if not st.session_state.indexed:

        st.sidebar.warning(
            "Please upload your notes first."
        )

    else:

        try:

            with st.spinner(
                "✨ Creating your summary..."
            ):

                st.session_state.summary = (
                    generate_summary()
                )

            st.session_state.xp += 5

            save_progress()

            st.session_state.scroll_target = (
                "summary-section"
            )

            st.sidebar.success(
                "Summary generated! +5 XP"
            )

            st.rerun()

        except Exception as error:

            st.sidebar.error(
                f"Summary generation failed: {error}"
            )


# =========================================================
# IMPORTANT TOPICS
# =========================================================

if st.sidebar.button(
    "⭐ Important Topics",
    use_container_width=True,
    disabled=not bool(GROQ_API_KEY)
):

    if not st.session_state.indexed:

        st.sidebar.warning(
            "Please upload your notes first."
        )

    else:

        try:

            with st.spinner(
                "🔍 Finding important topics..."
            ):

                st.session_state.important_topics = (
                    generate_important_topics()
                )

            st.session_state.xp += 5

            save_progress()

            st.session_state.scroll_target = (
                "topics-section"
            )

            st.sidebar.success(
                "Topics generated! +5 XP"
            )

            st.rerun()

        except Exception as error:

            st.sidebar.error(
                "Important topics generation failed: "
                f"{error}"
            )


# =========================================================
# DOCUMENT DASHBOARD
# =========================================================

if not st.session_state.indexed:
    st.markdown(
        """
        <div class="empty-state">
          <div class="empty-icon">1 → 2 → 3</div>
          <h2>Start your first study session</h2>
          <p><strong>Upload</strong> PDF notes in the sidebar, wait for indexing,
          then <strong>ask</strong> a question or generate a study activity.</p>
          <p class="small-note">No PDF handy? Choose <strong>Try a demo lesson</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    source_label = ", ".join(st.session_state.source_files)
    st.success(f"Workspace ready: {source_label}")

show_dashboard()


# =========================================================
# QUIZ SECTION
# =========================================================

st.markdown(
    '<div id="quiz-section"></div>',
    unsafe_allow_html=True
)

show_quiz()


# =========================================================
# FLASHCARDS DISPLAY
# =========================================================

st.markdown(
    '<div id="flashcards-section"></div>',
    unsafe_allow_html=True
)

if st.session_state.flashcards:

    st.header(
        "🃏 Flashcards"
    )

    card_index = (
        st.session_state.current_flashcard
    )

    cards = (
        st.session_state.flashcards
    )

    card = cards[
        card_index
    ]

    st.progress(
        (card_index + 1)
        / len(cards)
    )

    st.caption(
        f"Card {card_index + 1} "
        f"of {len(cards)}"
    )

    flashcard_html = (
        '<div class="feature-card">'
        '<div class="feature-icon">🧠</div>'
        f'<div class="feature-title">{escape(str(card["question"]))}</div>'
        '</div>'
    )

    st.markdown(
        flashcard_html,
        unsafe_allow_html=True
    )

    st.write("")

    if st.button(
        "👁 Reveal Answer",
        key="show_flashcard_answer",
        use_container_width=True
    ):

        if not st.session_state.show_answer:

            st.session_state.flashcards_reviewed += 1
            st.session_state.xp += 2

            save_progress()

        st.session_state.show_answer = True

    if st.session_state.show_answer:

        st.success(
            card["answer"]
        )

        st.caption(
            "⭐ +2 XP for reviewing this card"
        )

    previous_column, next_column = (
        st.columns(2)
    )

    with previous_column:

        if st.button(
            "⬅ Previous",
            disabled=(
                card_index == 0
            ),
            key="previous_flashcard",
            use_container_width=True
        ):

            st.session_state.current_flashcard -= 1
            st.session_state.show_answer = False

            st.session_state.scroll_target = (
                "flashcards-section"
            )

            st.rerun()

    with next_column:

        if st.button(
            "Next ➡",
            disabled=(
                card_index
                == len(cards) - 1
            ),
            key="next_flashcard",
            use_container_width=True
        ):

            st.session_state.current_flashcard += 1
            st.session_state.show_answer = False

            st.session_state.scroll_target = (
                "flashcards-section"
            )

            st.rerun()

    st.divider()


# =========================================================
# WEAK TOPICS
# =========================================================

st.markdown(
    '<div id="weak-topics-section"></div>',
    unsafe_allow_html=True
)

st.subheader(
    "⚠ Topics To Revise"
)

if st.session_state.weak_topics:

    sorted_topics = sorted(
        st.session_state.weak_topics.items(),
        key=lambda item: item[1],
        reverse=True
    )

    for topic, mistakes in sorted_topics:

        with st.expander(
            f"📌 {topic} — {mistakes} mistake(s)"
        ):

            st.write(
                "Choose how you want to improve this topic."
            )

            # -----------------------------------------
            # TEACH ME
            # -----------------------------------------

            if st.button(
                f"🧠 Teach Me {topic}",
                key=f"teach_{topic}",
                use_container_width=True
            ):

                with st.spinner(
                    "Creating your learning solution..."
                ):

                    solution = (
                        generate_weak_topic_solution(
                            topic,
                            mistakes
                        )
                    )

                st.markdown(
                    solution
                )

            # -----------------------------------------
            # PRACTICE
            # -----------------------------------------

            if st.button(
                f"🎯 Practice {topic}",
                key=f"practice_{topic}",
                use_container_width=True
            ):

                with st.spinner(
                    "Creating practice questions..."
                ):

                    questions = generate_topic_practice(
                        topic
                    )

                if questions:

                    st.session_state.practice_questions = (
                        questions
                    )

                    st.session_state.practice_topic = topic
                    st.session_state.practice_index = 0
                    st.session_state.practice_result = False
                    st.session_state.practice_selected = None
                    st.session_state.practice_xp_awarded = False

                    st.session_state.scroll_target = (
                        "practice-section"
                    )

                    st.rerun()

else:

    st.success(
        "🎉 No weak topics yet. Keep practicing!"
    )


# =========================================================
# WEAK TOPIC PRACTICE
# =========================================================

st.markdown(
    '<div id="practice-section"></div>',
    unsafe_allow_html=True
)

if st.session_state.practice_questions:

    st.header(
        f"🎯 Practice: "
        f"{st.session_state.practice_topic}"
    )

    questions = (
        st.session_state.practice_questions
    )

    index = (
        st.session_state.practice_index
    )

    if index < len(questions):

        question = questions[
            index
        ]

        st.progress(
            (index + 1)
            / len(questions)
        )

        st.subheader(
            f"Practice Question "
            f"{index + 1} of {len(questions)}"
        )

        st.write(
            question["question"]
        )

        selected = st.radio(
            "Choose your answer:",
            question["options"],
            index=None,
            key=(
                f"practice_"
                f"{st.session_state.practice_topic}_"
                f"{index}"
            ),
            disabled=(
                st.session_state.practice_result
            )
        )

        if not st.session_state.practice_result:

            if st.button(
                "✅ Check Answer",
                key=f"check_practice_{index}",
                use_container_width=True
            ):

                if selected is None:

                    st.warning(
                        "Choose an answer first."
                    )

                else:

                    st.session_state.practice_selected = (
                        selected
                    )

                    st.session_state.practice_result = True

                    st.session_state.scroll_target = (
                        "practice-section"
                    )

                    st.rerun()

        if st.session_state.practice_result:

            correct_answer = (
                question["options"][
                    question["answer"]
                ]
            )

            if (
                st.session_state.practice_selected
                == correct_answer
            ):

                if not st.session_state.practice_xp_awarded:

                    st.session_state.xp += 10

                    st.session_state.practice_xp_awarded = True

                    save_progress()

                st.success(
                    "🎉 Correct! +10 XP"
                )

            else:

                st.error(
                    "❌ Incorrect"
                )

                st.info(
                    f"✅ Correct Answer: "
                    f"{correct_answer}"
                )

            if st.button(
                "Next Practice Question ➡",
                key=f"next_practice_{index}",
                use_container_width=True
            ):

                st.session_state.practice_index += 1

                st.session_state.practice_result = False

                st.session_state.practice_selected = None

                st.session_state.practice_xp_awarded = False

                st.session_state.scroll_target = (
                    "practice-section"
                )

                st.rerun()

    else:

        st.success(
            "🎉 Practice completed!"
        )

        st.write(
            "Great work. Keep revising this topic "
            "until it feels easy."
        )


# =========================================================
# SUMMARY
# =========================================================

st.markdown(
    '<div id="summary-section"></div>',
    unsafe_allow_html=True
)

if st.session_state.summary:

    st.header(
        "📚 Study Summary"
    )

    with st.expander(
        "Open Study Summary",
        expanded=True
    ):

        st.markdown(
            st.session_state.summary
        )

    st.divider()


# =========================================================
# IMPORTANT TOPICS
# =========================================================

st.markdown(
    '<div id="topics-section"></div>',
    unsafe_allow_html=True
)

if st.session_state.important_topics:

    st.header(
        "⭐ Important Topics"
    )

    with st.expander(
        "Open Important Topics",
        expanded=True
    ):

        st.markdown(
            st.session_state.important_topics
        )

    st.divider()


# =========================================================
# EXPORTS
# =========================================================

if st.session_state.indexed:
    export_parts = ["# Lecturn study session", ""]
    if st.session_state.summary:
        export_parts.extend(["## Summary", st.session_state.summary, ""])
    if st.session_state.important_topics:
        export_parts.extend([
            "## Important topics", st.session_state.important_topics, ""
        ])
    if st.session_state.messages:
        export_parts.append("## Q&A transcript")
        for item in st.session_state.messages:
            label = "Question" if item["role"] == "user" else "Answer"
            export_parts.extend([f"### {label}", item["content"], ""])

    with st.expander("Export this study session"):
        st.caption(
            "Download your generated summary, topics, and Q&A as Markdown."
        )
        st.download_button(
            "Download study notes (.md)",
            data="\n".join(export_parts),
            file_name="lecturn-study-session.md",
            mime="text/markdown",
            use_container_width=True
        )


# =========================================================
# AI CHAT
# =========================================================

st.markdown(
    '<div id="chat-section"></div>',
    unsafe_allow_html=True
)

st.header(
    "💬 AI Study Assistant"
)

if st.session_state.messages and st.button(
    "Clear conversation", key="clear_chat"
):
    st.session_state.messages = []
    st.rerun()

if not st.session_state.indexed:

    st.info(
        "📄 Upload your PDF notes. "
        "They will be indexed automatically."
    )

else:

    st.success(
        "✅ Your notes are ready. "
        "Ask anything from the uploaded material."
    )


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


prompt = st.chat_input(
    "Ask anything from your notes...",
    disabled=(
        not st.session_state.indexed or not GROQ_API_KEY
    )
)


if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            prompt
        )

    with st.chat_message(
        "assistant"
    ):

        try:

            with st.spinner(
                "🤖 Searching your notes..."
            ):

                result = ask_question(
                    prompt
                )

            answer = result[
                "answer"
            ]

            citations = result.get("citations", [])

            st.markdown(
                answer
            )

            if citations:
                citation_text = " · ".join(
                    f"{item['source']} — p. {item['page']}"
                    for item in citations
                )
                st.caption("Sources: " + citation_text)

        except Exception as error:

            answer = (
                "I couldn't generate an answer "
                "because an error occurred."
            )

            st.error(
                f"{answer}\n\n"
                f"Details: {error}"
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


# =========================================================
# AUTO SCROLL
# =========================================================

if st.session_state.scroll_target:

    target = (
        st.session_state.scroll_target
    )

    components.html(
        f"""
<script>

setTimeout(function() {{

    const element =
        parent.document.getElementById(
            "{target}"
        );

    if (element) {{

        element.scrollIntoView({{
            behavior: "smooth",
            block: "start"
        }});

    }}

}}, 500);

</script>
""",
        height=0
    )

    st.session_state.scroll_target = None


# =========================================================
# FOOTER
# =========================================================

footer_html = (
    '<div class="footer">'
    'Built with 🧠 RAG, Python, '
    'ChromaDB and Groq'
    '<br>'
    'Lecturn — Study smarter, not harder.'
    '</div>'
)

st.markdown(
    footer_html,
    unsafe_allow_html=True
)
