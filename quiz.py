import streamlit as st
from questions import quizzes
from datetime import datetime
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
        self.usr_key = ""

    def get_user_info(self):
        usr = self.all_users_df[self.all_users_df["login"] == self.usr_key]
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
                self.usr_key = login
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
    
    def save_quiz(self, count):
        line = f"""{self.user.usr_key},{self.quiz_id},{datetime.now()},{count},{NUM_QUESTIONS * REQUIRED},{count >= NUM_QUESTIONS * REQUIRED}\n"""
        with open(RESULT_FILE, 'a') as file:
            file.write(line)
    
    def show_correct_answers(self):
        st.subheader("Folgende Fragen wurden von dir falsch beantwortet:")
        st.markdown("""Untenstehend werden alle Fragen aufgelistet, welche von dir falsch beantwortet 
                    wurden. Deine Antwort ist mit einem ❌, die richtige Antwort mit einem ✔️ gekennzeichnet. 
                    Wo vorhanden, verlinkt das 🔗-Symbol rechts von der Frage mit weiteren Infos betreffend diese Frage.\n\n
                    """)

        for question in self.questions:
            if question["user"] != question["r"]:
                link = f"[🔗]({question['url']})" if "url" in question else ""
                st.markdown(f"**{question['q']}** {link}")
                for key, value in question["a"].items():
                    if key == question["user"] and key != question["r"]:
                        mark = "❌ "
                    elif key == question["r"]:
                        mark = "✔️ "
                    else:
                        mark = "⚪ "
                    st.markdown(mark + value)
            
            st.markdown("")

    def show_result(self):
        count = sum(1 for item in self.questions if item["user"] == item["r"])
        st.markdown(f"Deine Punktezahl: {count}/{NUM_QUESTIONS}")
        if count / NUM_QUESTIONS < REQUIRED:
            st.warning(
                "Leider hat es diesmal nicht gereicht, überprüfe bitte deine falschen Antworten im untenstehenden Abschnitt und versuche es anschliessend nochmals."
            )
            self.index = 0
            self.finished = False
        else:
            st.success("Herzliche Gratulation, du hast den Test bestanden")
            st.balloons()
        self.save_quiz(count)

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
            response_options = list(self.question["a"].keys())
            if "user" not in self.question:
                self.question["user"] = "A"
            id = response_options.index(self.question["user"])
            response = st.radio(
                "Antwort",
                options=response_options,
                format_func=self.question["a"].get,
                index=id
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
