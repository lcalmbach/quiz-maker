import streamlit as st
from questions import quizzes
import random
import pandas as pd
import time

NUM_QUESTIONS = 10
REQUIRED = 0.8
USERS_FILE = "./users.csv"
RESULT_FILE = "./results.csv"


class User:
    def __init__(self):
        self.all_users_df = users_df = pd.read_csv(USERS_FILE)
        self.name = ""
        self.last_name = ""
        self.logged_in = False

    def get_user_info(self):
        usr = self.all_users_df[self.all_users_df["login"] == self.login]
        usr = usr.iloc[0].to_dict()
        self.name = usr["name"]
        self.first_name = usr["first_name"]
        self.email = usr["email"]

    def login(self):
        def check_password(login, pwd):
            user = self.all_users_df[self.all_users_df["login"] == login]
            return pwd == str(user.iloc[0]["password"])

        st.subheader("👤 StatA Quiz login")
        login = st.text_input("Kürzel")
        pwd = st.text_input("Passwort", type="password")

        if st.button("Login"):
            if check_password(login, pwd):
                self.logged_in = True
                self.login = login
                self.get_user_info()
                st.success(f"Willkommen {self.first_name} beim StatA Quiz")
            else:
                st.warning("Leider hat etwas nicht geklappt, versuch es nochmals")
            time.sleep(3)


class Quiz:
    def __init__(self, user):
        self.user = user
        self._quiz_id = "0"
        self._index = 0
        self.quiz_dict = {}
        self.questions = []
        self.question = {}
        self.answers = {}
        self.finished = False
        self.title = ""

    def __repr__(self):
        return self.title

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value
        self.question = self.questions[self.index]

    @property
    def quiz_id(self):
        return self._quiz_id

    @quiz_id.setter
    def quiz_id(self, value):
        my_quiz = quizzes[value]
        self._quiz_id = value
        st.session_state["quiz_id"] = value
        self.title = my_quiz["title"]
        self.questions = random.sample(my_quiz["questions"], NUM_QUESTIONS)
        self.index = 0

    def get_quizzes_dict(self):
        return {k: v["title"] for k, v in quizzes.items()}

    def get_quiz(self):
        options = self.get_quizzes_dict()
        id = st.selectbox(
            label="Quiz", options=list(options.keys()), format_func=options.get
        )
        if st.button("Quiz Starten"):
            self.quiz_id = id

    def show_correct_answers(self):
        st.subheader("Folgende Fragen wruden von dir falsch beantwortet:")
        st.markdown("❌ deine falsche Antwort")
        st.markdown("✔️ richtige Antwort\n")
        for question in self.questions:
            st.markdown(f"*{question['q']}*")
            if question["user"] != question["r"]:
                for key, value in question["a"].items():
                    if key == question["user"] and key != question["r"]:
                        mark = "❌ "
                    elif key == question["r"]:
                        mark = "✔️ "
                    else:
                        mark = "⚪ "
                    st.markdown(mark + value)
            if "url" in question:
                st.markdown(f"[Weitere Infos]({question['url']})")
            st.markdown("")

    def show_result(self):
        count = sum(1 for item in self.questions if item["user"] == item["r"])
        st.markdown(f"Deine Punktezahl: {count}/{NUM_QUESTIONS}")
        if count / NUM_QUESTIONS < REQUIRED:
            st.warning(
                "Leider hat es diesmal nicht gereicht, bitte versuch es nochmals."
            )
            self.index = 0
            self.finished = False
        else:
            st.success("Herzliche Gratulation, du hast den Test bestanden")
            st.balloons()

        if count < NUM_QUESTIONS:
            self.show_correct_answers()

    def show_quiz(self):
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
            self.question["user"] = response
            self.answers[self.index] = {"user": response, "result": self.question["r"]}

            cols = st.columns([1, 1, 4])
            with cols[0]:
                if st.button("<Zurück", disabled=(self.index == 0)):
                    self.index -= 1
                    st.experimental_rerun()
            with cols[1]:
                if st.button(
                    "Nächste", disabled=(self.index >= len(self.questions) - 1)
                ):
                    self.index += 1
                    st.experimental_rerun()
            with cols[2]:
                if self.index == len(self.questions) - 1:
                    if st.button("Abschicken", disabled=self.finished):
                        self.finished = True
                        st.experimental_rerun()
