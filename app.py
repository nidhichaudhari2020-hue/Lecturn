import os
import streamlit as st

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
        with open("assets/style.css", encoding="utf-8") as file:
            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )

    except FileNotFoundError:
        st.warning("Custom style file was not found.")


load_css()


# =========================================================
# SESSION STATE
# =========================================================

defaults = {

    # Main app
    "indexed": False,
    "messages": [],

    # Prevent repeated auto-indexing
    "last_uploaded_files": [],

    # Quiz
    "quiz": [],
    "current_question": 0,
    "score": 0,
    "show_result": False,
    "selected_option": None,

    # Flashcards
    "flashcards": [],
    "current_flashcard": 0,
    "show_answer": False,

    # Dashboard
    "total_pdfs": 0,
    "total_pages": 0,
    "total_chunks": 0,

    # Generated study content
    "summary": "",
    "important_topics": ""
}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero-card">

        <div class="hero-title">
            📚 Lecturn
        </div>

        <div class="hero-text">
            Turn your study notes into answers, quizzes,
            flashcards, summaries and smarter revision sessions.
        </div>

    </div>
    """,
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

    with column:

        st.markdown(
            f"""
            <div class="feature-card">

                <div class="feature-icon">
                    {icon}
                </div>

                <div class="feature-title">
                    {title}
                </div>

                <div class="feature-text">
                    {description}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


st.write("")


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📂 Study Workspace")


uploaded_files = st.sidebar.file_uploader(

    "Upload your PDF notes",

    type=["pdf"],

    accept_multiple_files=True,

    help=(
        "You can upload one or multiple PDF files. "
        "Lecturn will index them automatically."
    )
)


st.sidebar.caption(
    "✨ Your notes will be indexed automatically after upload."
)


st.sidebar.divider()


# =========================================================
# AUTOMATIC PDF INDEXING
# =========================================================

if uploaded_files:

    # Create a signature for the currently uploaded files.
    # This prevents Streamlit from indexing the same PDFs
    # again whenever the app reruns.

    current_files = [

        f"{uploaded_file.name}-{uploaded_file.size}"

        for uploaded_file in uploaded_files
    ]


    # Only index if the uploaded files changed

    if (
        st.session_state.last_uploaded_files
        != current_files
    ):

        try:

            with st.spinner(
                "🧠 Lecturn is reading, understanding "
                "and indexing your notes..."
            ):

                # Ensure folders exist

                os.makedirs(
                    "uploads",
                    exist_ok=True
                )

                os.makedirs(
                    "data",
                    exist_ok=True
                )


                # Remove previous ChromaDB collection

                reset_database()


                # Progress bar

                progress = st.sidebar.progress(0)


                all_chunks = []

                total_pages = 0

                total_files = len(
                    uploaded_files
                )


                # =========================================
                # PROCESS EACH PDF
                # =========================================

                for index, uploaded_file in enumerate(
                    uploaded_files
                ):

                    save_path = os.path.join(
                        "uploads",
                        uploaded_file.name
                    )


                    # Save uploaded PDF

                    with open(
                        save_path,
                        "wb"
                    ) as file:

                        file.write(
                            uploaded_file.getbuffer()
                        )


                    # Extract PDF text

                    pages = extract_text(
                        save_path
                    )


                    total_pages += len(
                        pages
                    )


                    # Split text into chunks

                    chunks = split_into_chunks(
                        pages
                    )


                    all_chunks.extend(
                        chunks
                    )


                    # First half of progress = PDF processing

                    progress.progress(

                        int(

                            (
                                (index + 1)
                                / total_files
                            )

                            * 50

                        )

                    )


                # =========================================
                # CHECK IF TEXT WAS FOUND
                # =========================================

                if not all_chunks:

                    st.sidebar.error(
                        "No readable text was found "
                        "inside the uploaded PDFs."
                    )

                else:

                    # =====================================
                    # GENERATE EMBEDDINGS
                    # =====================================

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


                    # =====================================
                    # STORE IN CHROMADB
                    # =====================================

                    store_chunks(
                        all_chunks,
                        embeddings
                    )


                    progress.progress(100)


                    # =====================================
                    # UPDATE SESSION STATE
                    # =====================================

                    st.session_state.indexed = True


                    st.session_state.total_pdfs = (
                        len(uploaded_files)
                    )


                    st.session_state.total_pages = (
                        total_pages
                    )


                    st.session_state.total_chunks = (
                        len(all_chunks)
                    )


                    # Remember which files were indexed

                    st.session_state.last_uploaded_files = (
                        current_files
                    )


                    # =====================================
                    # RESET OLD GENERATED CONTENT
                    # =====================================

                    st.session_state.quiz = []

                    st.session_state.current_question = 0

                    st.session_state.score = 0

                    st.session_state.show_result = False


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


# =========================================================
# NO FILES UPLOADED
# =========================================================

else:

    st.sidebar.info(
        "📄 Upload PDF notes to start studying."
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
            "Please upload notes first."
        )

    else:

        try:

            with st.spinner(
                "📝 Creating a fresh quiz "
                "from your notes..."
            ):

                quiz = generate_quiz()


            if quiz:

                st.session_state.quiz = quiz

                st.session_state.current_question = 0

                st.session_state.score = 0

                st.session_state.show_result = False


                st.sidebar.success(
                    "Quiz generated!"
                )


            else:

                st.sidebar.error(
                    "The quiz could not be generated. "
                    "Please try again."
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
            "Please upload notes first."
        )

    else:

        try:

            with st.spinner(
                "🃏 Turning key concepts "
                "into flashcards..."
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


                st.sidebar.success(
                    "Flashcards generated!"
                )


            else:

                st.sidebar.error(
                    "The flashcards could not be "
                    "generated. Please try again."
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
            "Please upload notes first."
        )

    else:

        try:

            with st.spinner(
                "✨ Creating your revision-friendly "
                "summary..."
            ):

                st.session_state.summary = (
                    generate_summary()
                )


            st.sidebar.success(
                "Summary generated!"
            )


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
            "Please upload notes first."
        )

    else:

        try:

            with st.spinner(
                "🔍 Finding the most important "
                "exam topics..."
            ):

                st.session_state.important_topics = (
                    generate_important_topics()
                )


            st.sidebar.success(
                "Important topics generated!"
            )


        except Exception as error:

            st.sidebar.error(

                "Important topics generation "
                f"failed: {error}"

            )


# =========================================================
# DASHBOARD
# =========================================================

show_dashboard()


# =========================================================
# QUIZ
# =========================================================

show_quiz()


# =========================================================
# FLASHCARDS DISPLAY
# =========================================================

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


    # Flashcard progress

    st.progress(

        (card_index + 1)
        / len(cards)

    )


    st.caption(

        f"Card {card_index + 1} "
        f"of {len(cards)}"

    )


    # Flashcard question

    st.markdown(

        f"""
        <div class="feature-card">

            <div class="feature-icon">
                🧠
            </div>

            <div class="feature-title">
                {card["question"]}
            </div>

        </div>
        """,

        unsafe_allow_html=True
    )


    st.write("")


    # Reveal answer

    if st.button(
        "👁 Reveal Answer",
        key="show_flashcard_answer"
    ):

        st.session_state.show_answer = True


    if st.session_state.show_answer:

        st.success(
            card["answer"]
        )


    # Navigation

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

            st.rerun()


    st.divider()


# =========================================================
# DISPLAY SUMMARY
# =========================================================

if st.session_state.summary:

    with st.expander(
        "📚 Open Study Summary",
        expanded=True
    ):

        st.markdown(
            st.session_state.summary
        )


# =========================================================
# DISPLAY IMPORTANT TOPICS
# =========================================================

if st.session_state.important_topics:

    with st.expander(
        "⭐ Open Important Topics",
        expanded=True
    ):

        st.markdown(
            st.session_state.important_topics
        )


# =========================================================
# AI CHAT
# =========================================================

st.divider()


st.header(
    "💬 AI Study Assistant"
)


if not st.session_state.indexed:

    st.info(

        "📄 Upload your PDF notes. "
        "Lecturn will automatically index them "
        "and prepare your study workspace."

    )

else:

    st.success(

        "✅ Your notes are ready. "
        "Ask anything from the uploaded material."

    )


# =========================================================
# DISPLAY CHAT HISTORY
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
# PROCESS QUESTION
# =========================================================

if prompt:

    # Save user message

    st.session_state.messages.append(

        {
            "role": "user",
            "content": prompt
        }

    )


    # Display user message

    with st.chat_message(
        "user"
    ):

        st.markdown(
            prompt
        )


    # Assistant response

    with st.chat_message(
        "assistant"
    ):

        try:

            with st.spinner(
                "🤖 Lecturn is searching your notes..."
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


            # Display answer

            st.markdown(
                answer
            )


            # Display source pages

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


    # Save assistant response

    st.session_state.messages.append(

        {
            "role": "assistant",
            "content": answer
        }

    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        Built with 🧠 RAG, Python,
        ChromaDB and Groq

        <br>

        Lecturn — Study smarter,
        not harder.

    </div>
    """,

    unsafe_allow_html=True
)