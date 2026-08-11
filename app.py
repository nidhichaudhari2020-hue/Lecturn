import os
import json
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
# PROGRESS FILE
# =========================================================

PROGRESS_FILE = "data/user_progress.json"


def load_progress():

    os.makedirs(
        "data",
        exist_ok=True
    )

    default_progress = {
        "xp": 0,
        "study_streak": 1,
        "last_study_date": "",
        "quiz_completed": 0,
        "flashcards_reviewed": 0,
        "weak_topics": {}
    }

    if not os.path.exists(PROGRESS_FILE):
        return default_progress

    try:

        with open(
            PROGRESS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            saved = json.load(file)

            default_progress.update(saved)

            return default_progress

    except Exception:

        return default_progress


def save_progress():

    data = {
        "xp": st.session_state.xp,
        "study_streak": st.session_state.study_streak,
        "last_study_date": st.session_state.last_study_date,
        "quiz_completed": st.session_state.quiz_completed,
        "flashcards_reviewed": (
            st.session_state.flashcards_reviewed
        ),
        "weak_topics": st.session_state.weak_topics
    }

    try:

        with open(
            PROGRESS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    except Exception:
        pass


# =========================================================
# LOAD SAVED PROGRESS
# =========================================================

saved_progress = load_progress()


# =========================================================
# SESSION STATE
# =========================================================

defaults = {

    # Main
    "indexed": False,
    "messages": [],
    "last_uploaded_files": [],

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
# UPDATE STUDY STREAK
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
# HERO SECTION
# =========================================================

hero_html = (
    '<div class="hero-card">'
    '<div class="hero-title">📚 Lecturn</div>'
    '<div class="hero-text">'
    'Turn your study notes into answers, quizzes, '
    'flashcards, summaries and smarter revision sessions.'
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
# LEARNING DASHBOARD
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

continue1, continue2, continue3, continue4 = (
    st.columns(4)
)


with continue1:

    if st.button(
        "💬 Ask AI",
        use_container_width=True
    ):

        st.session_state.scroll_target = (
            "chat-section"
        )

        st.rerun()


with continue2:

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


with continue3:

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


with continue4:

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
        "Upload one or more PDF files. "
        "They will be indexed automatically."
    )
)


st.sidebar.caption(
    "✨ Notes are indexed automatically after upload."
)


st.sidebar.divider()


# =========================================================
# AUTOMATIC PDF INDEXING
# =========================================================

if uploaded_files:

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
                    "uploads",
                    exist_ok=True
                )

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


                # -----------------------------------------
                # PROCESS PDF FILES
                # -----------------------------------------

                for index, uploaded_file in enumerate(
                    uploaded_files
                ):

                    save_path = os.path.join(
                        "uploads",
                        uploaded_file.name
                    )


                    with open(
                        save_path,
                        "wb"
                    ) as file:

                        file.write(
                            uploaded_file.getbuffer()
                        )


                    pages = extract_text(
                        save_path
                    )


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

                            (
                                (index + 1)
                                / total_files
                            )

                            * 50

                        )

                    )


                # -----------------------------------------
                # EMBEDDINGS
                # -----------------------------------------

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


                    embeddings = (
                        generate_embeddings(
                            texts
                        )
                    )


                    progress.progress(85)


                    store_chunks(
                        all_chunks,
                        embeddings
                    )


                    progress.progress(100)


                    # -------------------------------------
                    # SAVE INDEX STATE
                    # -------------------------------------

                    st.session_state.indexed = True


                    st.session_state.total_pdfs = len(
                        uploaded_files
                    )


                    st.session_state.total_pages = (
                        total_pages
                    )


                    st.session_state.total_chunks = (
                        len(all_chunks)
                    )


                    st.session_state.last_uploaded_files = (
                        current_files
                    )


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
# GENERATE QUIZ
# =========================================================

if st.sidebar.button(
    "📝 Generate Quiz",
    use_container_width=True
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
# GENERATE FLASHCARDS
# =========================================================

if st.sidebar.button(
    "🃏 Generate Flashcards",
    use_container_width=True
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
# GENERATE SUMMARY
# =========================================================

if st.sidebar.button(
    "📚 Generate Summary",
    use_container_width=True
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
    use_container_width=True
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
# ORIGINAL DOCUMENT DASHBOARD
# =========================================================

show_dashboard()


# =========================================================
# QUIZ
# =========================================================

st.markdown(
    '<div id="quiz-section"></div>',
    unsafe_allow_html=True
)


show_quiz()


# =========================================================
# FLASHCARDS
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

        '<div class="feature-icon">'
        '🧠'
        '</div>'

        f'<div class="feature-title">'
        f'{card["question"]}'
        '</div>'

        '</div>'

    )


    st.markdown(
        flashcard_html,
        unsafe_allow_html=True
    )


    st.write("")


    # -----------------------------------------
    # REVEAL ANSWER
    # -----------------------------------------

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


    # -----------------------------------------
    # PREVIOUS CARD
    # -----------------------------------------

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


    # -----------------------------------------
    # NEXT CARD
    # -----------------------------------------

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

        st.warning(
            f"📌 {topic} — "
            f"{mistakes} mistake(s)"
        )


else:

    st.success(
        "🎉 No weak topics yet. "
        "Keep practicing!"
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
# AI CHAT
# =========================================================

st.markdown(
    '<div id="chat-section"></div>',
    unsafe_allow_html=True
)


st.header(
    "💬 AI Study Assistant"
)


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


# =========================================================
# CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(

    "Ask anything from your notes...",

    disabled=(
        not st.session_state.indexed
    )

)


# =========================================================
# PROCESS CHAT
# =========================================================

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


            pages = result.get(
                "pages",
                []
            )


            st.markdown(
                answer
            )


            if pages:

                st.caption(
                    "📄 Source Pages: "
                    + ", ".join(
                        map(
                            str,
                            pages
                        )
                    )
                )


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