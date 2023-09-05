import streamlit as st
from quiz import Quiz, User


def main():
    if "user" not in st.session_state:
        user = User()
        user.login()
        if user.logged_in:
            st.session_state["user"] = user
            st.experimental_rerun()
    elif "quiz" not in st.session_state:
        quiz = Quiz(st.session_state["user"])
        quiz.get_quiz()
        if int(quiz.quiz_id) > 0:
            st.session_state["quiz"] = quiz
            st.experimental_rerun()
    else:
        st.session_state.quiz.show_quiz()


if __name__ == "__main__":
    main()
