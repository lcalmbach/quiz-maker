import streamlit as st
from quiz import Quiz, User


def main():
    if "quiz" not in st.session_state:
        st.session_state.quiz = Quiz('ssscal', 1)
    
    st.session_state.quiz.show()


if __name__ == '__main__':
    main()
