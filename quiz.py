import streamlit as st
from questions import questions
import random
import time

NUM_QUESTIONS = 10
REQUIRED = 0.8

class User:
    def __init__(self):
        self.name = "Lukas"
        self.last_name = "Calmbach"


class Quiz:
    def __init__(self, user, quiz_id):
        self.questions = random.sample(questions, NUM_QUESTIONS)
        self.answers = {}
        self.index = 0
        self.finished = False
        self.title = "StatA Sicherheitscheck 🔐"

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value
        self.question = self.questions[self.index]

    def show_result(self):
        count = sum(
            1 for item in self.answers.values() if item["user"] == item["result"]
        )
        st.markdown(f"Deine Punktezahl: {count}/{NUM_QUESTIONS}")
        if count/NUM_QUESTIONS < REQUIRED:
            st.warning("Leider hat es diesmal nicht gereicht, bitte versuch es nochmals.")
            self.index = 0
            self.finished = False
        else:
            st.success("Herzliche Gratulation, du hast den Test bestanden")
            st.balloons()

    def show(self):
        st.header(self.title)
        if self.finished:
            self.show_result()
        else:
            st.progress((self.index) / NUM_QUESTIONS)

            st.subheader(f"Frage {self.index + 1}")
            st.markdown(self.question["q"])
            response = st.radio(
                "Antwort",
                options=list(self.question["a"].keys()),
                format_func=self.question["a"].get,
            )

            self.answers[self.index] = {"user": response, "result": self.question["r"]}

            cols = st.columns([1, 1, 4])
            with cols[0]:
                if st.button("<Zurück", disabled=(self.index == 0)):
                    self.index -= 1
                    st.experimental_rerun()
            with cols[1]:
                if st.button("Nächste", disabled=(self.index >= len(self.questions) - 1)):
                    self.index += 1
                    st.experimental_rerun()
            with cols[2]:
                if self.index == len(self.questions) - 1:
                    if st.button("Abschicken", disabled=self.finished):
                        self.finished = True
                        st.experimental_rerun()
