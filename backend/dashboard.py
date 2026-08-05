import streamlit as st


def show_dashboard():

    st.subheader("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📄 PDFs",
            st.session_state.get("total_pdfs", 0)
        )

    with col2:
        st.metric(
            "📖 Pages",
            st.session_state.get("total_pages", 0)
        )

    with col3:
        st.metric(
            "🧩 Chunks",
            st.session_state.get("total_chunks", 0)
        )

    st.divider()