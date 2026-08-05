import streamlit as st
from backend.quiz_generator import generate_quiz


def show_quiz():

    if len(st.session_state.quiz) == 0:
        return

    st.header("📝 AI Quiz")

    q_index = st.session_state.current_question

    if q_index < len(st.session_state.quiz):

        question = st.session_state.quiz[q_index]

        st.progress((q_index + 1) / len(st.session_state.quiz))

        st.subheader(
            f"Question {q_index + 1} of {len(st.session_state.quiz)}"
        )

        st.write(question["question"])

        selected = st.radio(
            "Choose an answer",
            question["options"],
            key=f"question_{q_index}"
        )

        if st.button("✅ Submit Answer"):

            correct = question["options"][question["answer"]]

            if selected == correct:

                st.success("🎉 Correct!")

                st.session_state.score += 1

            else:

                st.error("❌ Incorrect")

                st.info(f"Correct Answer: {correct}")

            st.session_state.show_result = True

        if st.session_state.show_result:

            if st.button("➡ Next Question"):

                st.session_state.current_question += 1

                st.session_state.show_result = False

                st.rerun()

    else:

        st.balloons()

        score = st.session_state.score

        total = len(st.session_state.quiz)

        percentage = round(score / total * 100)

        st.success("🎉 Quiz Completed!")

        st.metric("Score", f"{score}/{total}")

        st.metric("Percentage", f"{percentage}%")

        if st.button("🔄 Generate New Quiz"):

            st.session_state.quiz = generate_quiz()

            st.session_state.current_question = 0

            st.session_state.score = 0

            st.session_state.show_result = False

            st.rerun()

    st.divider()