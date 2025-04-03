## In The Name Of GOD
## Filoger NLP Final Project
## Developed By Eiliya Mohebi
## Live Demo Link On Streamlit:
## https://eiliya-mohebi.streamlit.app/
import streamlit as st
import os
import ast
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from crewai import Agent, Task, Crew

# Load environment variables
load_dotenv()

st.set_page_config(page_title="AI MCQ Chatbot", layout="centered")

st.title("🤖 AI MCQ Chatbot")
st.write("Enter a text or topic to generate a multiple-choice question.")


st.sidebar.title("ℹ️ About This Bot")
st.sidebar.markdown("""
This chatbot generates **multiple-choice questions (MCQs)** based on a given topic.
It uses **CrewAI** and an **LLM (OpenAI API)** to create questions.
- It is the final project of **filoger NLP course**.
- It uses **avalai api**(3 request per minutes) and **gpt-4o-mini** as the base model.
- It supports **persian** input!  
- Developed by **eiliya mohebi** for educational purposes.
""")


if "question_data" not in st.session_state:
    st.session_state.question_data = None
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None
if "answer_submitted" not in st.session_state:
    st.session_state.answer_submitted = False
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = False  


user_input = st.text_input("Enter text or topic:", "")


def generate_mcq():
    if not user_input.strip():
        st.warning("Please enter a valid text or topic.")
        return

    try:
        # Initialize LLM
        custom_llm = ChatOpenAI(
            base_url=os.environ.get("OPENAI_API_BASE"),
            model=os.environ.get("OPENAI_MODEL_NAME")
        )

        # Define Agent
        main_agent = Agent(
            role="AI-powered chatbot responsible for generating structured multiple-choice questions (MCQs) based on given text or topics.",
            goal="Accurately create well-structured MCQs with one correct answer and three distractors from either a provided text or a general topic.",
            allow_delegation=False,
            verbose=True,
            backstory=(
                """
                Designed as an advanced AI assistant, the MCQ Generator Agent was built to streamline the process of educational content creation.
                With a deep understanding of language processing, question formulation, and distractor generation, it ensures that all questions maintain coherence, relevance, and difficulty balance.
                """
            ),
            llm = custom_llm
        )

        generate_questions_task = Task(
            description=("""
            The agent must take either an input text or a general topic and generate a properly formatted MCQ.
            The question should be relevant to the input, follow a structured format, and include a correct answer along with three distractors.
            Here is the user input:
            {user_input}

        """),
            expected_output="""
            Output must be a tuple in the following format:
            ("Generated question?", {"A) Answer 1": False, "B) Answer 2": False, "C) Correct Answer": True, "D) Answer 4": False})

            - Each option must be a complete phrase, not just "Option A", "Option B".
            - The correct answer should be randomly placed.
            - The format should remain strictly as a tuple without additional text.
        """,
            agent=main_agent
        )

        # Execute Task
        crew = Crew(agents=[main_agent], tasks=[generate_questions_task])
        raw_result = crew.kickoff(inputs={"user_input": user_input})

        try:
            
            question_tuple = ast.literal_eval(str(raw_result).strip())

            if isinstance(question_tuple, tuple) and isinstance(question_tuple[1], dict):
                question, options_dict = question_tuple

                
                ordered_options = sorted(options_dict.items(), key=lambda x: x[0])

                
                st.session_state.question_data = (question, ordered_options)
                st.session_state.selected_answer = None
                st.session_state.answer_submitted = False
                st.session_state.reset_trigger = False  

            else:
                st.error("⚠️ Failed to generate a valid MCQ. Please try again.")

        except Exception as e:
            st.error(f"⚠️ Error processing question: {e}")

    except Exception as e:
        st.error(f"🚨 Error occurred while generating the question: {e}")


def reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]  
    st.session_state.reset_trigger = True  


col1, col2 = st.columns([1, 1])
with col1:
    st.button("Generate Question", on_click=generate_mcq)
with col2:
    st.button("Reset", on_click=reset)


if st.session_state.question_data:
    question, options = st.session_state.question_data

    st.subheader(f"📝 {question}")

   
    selected_answer = st.radio(
        "Choose your answer:",
        [opt[0] for opt in options],
        index=None,
        key="selected_answer"
    )

    
    def check_answer():
        if selected_answer:
            correct_answer = [opt[0] for opt in options if opt[1] is True][0]
            if selected_answer == correct_answer:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. The correct answer is: **{correct_answer}**")
            st.session_state.answer_submitted = True

    
    if selected_answer:
        st.button("Submit Answer", on_click=check_answer)
