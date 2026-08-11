import streamlit as st


def show_quiz():

    if not st.session_state.quiz:
        return

    st.header("📝 AI Quiz")

    quiz = st.session_state.quiz
    q_index = st.session_state.current_question

    # -----------------------------
    # QUIZ COMPLETED
    # -----------------------------

    if q_index >= len(quiz):

        st.success("🎉 Quiz Completed!")

        score = st.session_state.score
        total = len(quiz)

        percentage = round(
            (score / total) * 100
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Final Score",
                f"{score}/{total}"
            )

        with col2:
            st.metric(
                "Percentage",
                f"{percentage}%"
            )

        return

    # -----------------------------
    # CURRENT QUESTION
    # -----------------------------

    question = quiz[q_index]

    st.progress(
        (q_index + 1) / len(quiz)
    )

    st.subheader(
        f"Question {q_index + 1} of {len(quiz)}"
    )

    st.write(
        question["question"]
    )

    # No option selected initially
    selected = st.radio(
        "Choose your answer:",
        question["options"],
        index=None,
        key=(
            f"quiz_"
            f"{st.session_state.quiz_version}_"
            f"{q_index}"
        ),
        disabled=st.session_state.show_result
    )

    # -----------------------------
    # SUBMIT ANSWER
    # -----------------------------

    if not st.session_state.show_result:

        if st.button(
            "✅ Submit Answer",
            key=f"submit_{q_index}",
            use_container_width=True
        ):

            if selected is None:

                st.warning(
                    "Please select an answer first."
                )

            else:

                correct_index = question["answer"]

                correct_answer = (
                    question["options"][correct_index]
                )

                if selected == correct_answer:

                    st.session_state.score += 1

                st.session_state.selected_option = selected
                st.session_state.show_result = True

                st.rerun()

    # -----------------------------
    # RESULT
    # -----------------------------

    if st.session_state.show_result:

        correct_index = question["answer"]

        correct_answer = (
            question["options"][correct_index]
        )

        selected_answer = (
            st.session_state.selected_option
        )

        if selected_answer == correct_answer:

            st.success("🎉 Correct!")

        else:

            st.error("❌ Incorrect")

            st.info(
                f"✅ Correct Answer: {correct_answer}"
            )

        # -------------------------
        # NEXT QUESTION
        # -------------------------

        if st.button(
            "Next Question ➡",
            key=f"next_question_{q_index}",
            use_container_width=True
        ):

            st.session_state.current_question += 1
            st.session_state.show_result = False
            st.session_state.selected_option = None

            # Keep user at quiz section
            st.session_state.scroll_target = (
                "quiz-section"
            )

            st.rerun()