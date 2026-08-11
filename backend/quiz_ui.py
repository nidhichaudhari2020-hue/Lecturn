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

        # Give completion bonus only once
        if not st.session_state.get(
            "quiz_bonus_given",
            False
        ):
            st.session_state.xp += 25
            st.session_state.quiz_completed += 1
            st.session_state.quiz_bonus_given = True

        col1, col2, col3 = st.columns(3)

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

        with col3:
            st.metric(
                "XP Earned",
                "+25 Bonus"
            )

        st.info(
            f"⭐ Total XP: {st.session_state.xp}"
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

                topic = question.get(
                    "topic",
                    "General"
                )

                # Correct answer
                if selected == correct_answer:

                    st.session_state.score += 1

                    # +10 XP
                    st.session_state.xp += 10

                    # Reduce weak-topic count if it exists
                    if topic in st.session_state.weak_topics:

                        st.session_state.weak_topics[topic] -= 1

                        if (
                            st.session_state.weak_topics[topic]
                            <= 0
                        ):
                            del st.session_state.weak_topics[topic]

                # Incorrect answer
                else:

                    if topic not in st.session_state.weak_topics:
                        st.session_state.weak_topics[topic] = 0

                    st.session_state.weak_topics[topic] += 1

                st.session_state.selected_option = (
                    selected
                )

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

            st.success(
                "🎉 Correct! +10 XP"
            )

        else:

            st.error(
                "❌ Incorrect"
            )

            st.info(
                f"✅ Correct Answer: {correct_answer}"
            )

            topic = question.get(
                "topic",
                "General"
            )

            st.warning(
                f"⚠ Added to Weak Topics: {topic}"
            )

        st.caption(
            f"⭐ Total XP: {st.session_state.xp}"
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

            st.session_state.scroll_target = (
                "quiz-section"
            )

            st.rerun()