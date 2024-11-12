import streamlit as st
from io import StringIO
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from docx import Document
import os

api_key = st.secrets["OPENAI_API_KEY"]

def generate_precise_user_story(prompt, brd_content=None):
    llm = OpenAI(temperature=0.5, model_name="gpt-3.5-turbo", openai_api_key=api_key)
    user_story_template = """
        Generate a detailed user story with the following format:
        User Story for {feature_name}
        Title: {title}
        As an {user}, I want to {feature}, so that {goal}.
        Acceptance Criteria:
        1. Login Form: The login page should have both email and password fields, along with a submit button.
        2. Input Validation: Ensure users receive an error for incorrect email or password. Validate email format.
        3. Forgot Password Option: Provide a link to initiate password recovery.
        4. Session Management: Users should stay logged in unless they explicitly log out.
        5. Redirect on Successful Login: After login, users should be redirected to their profile or last visited page.
        6. Access Control: Users must log in before accessing any account-related features.
        7. Responsive Design: Ensure login works seamlessly on both desktop and mobile.
        8. Security Measures: Implement CAPTCHA after multiple login attempts, and ensure secure password handling.
        """
    
    chain = LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["feature_name", "title", "user", "feature", "goal"], template=user_story_template))

    user_story = chain.run({
        "feature_name": "E-commerce Website Login Page",
        "title": "Existing Customer Login to Access Profile",
        "user": "existing customer",
        "feature": "log into the e-commerce website",
        "goal": "access my profile and manage my account details"
    })
    return user_story.strip()

def generate_email_template(prompt):
    llm = OpenAI(temperature=0.5, model_name="gpt-3.5-turbo", openai_api_key=api_key)
    email_template = """
        Write a formal email based on the following details:
        {details}
        """
    
    chain = LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["details"], template=email_template))
    email_response = chain.run({"details": prompt})
    return email_response.strip()

def detect_response_type(prompt):
    keywords_user_story = ["user story", "acceptance criteria", "feature", "As a", "so that"]
    keywords_email = ["email", "subject", "greeting", "template"]
    if any(keyword in prompt.lower() for keyword in keywords_user_story):
        return "User Story"
    elif any(keyword in prompt.lower() for keyword in keywords_email):
        return "Email Template"
    return "User Story"

def save_as_word(content, filename):
    doc = Document()
    doc.add_paragraph(content)
    doc.save(filename)

def is_valid_input(prompt):
    if len(prompt) < 10:
        return False
    keywords_user_story = ["user story", "acceptance criteria", "feature", "As a", "so that"]
    keywords_email = ["email", "subject", "greeting", "template"]
    return any(keyword in prompt.lower() for keyword in keywords_user_story + keywords_email)

st.title('BA Genie')

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Type your requirement here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    if is_valid_input(user_input):
        response_type = detect_response_type(user_input)
        response = generate_precise_user_story(user_input) if response_type == "User Story" else generate_email_template(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Please provide a more detailed requirement, such as a user story or email template request."})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if len(st.session_state.messages) > 0:
    last_response = st.session_state.messages[-1]["content"]
    st.download_button(f"Download Last Response as Text", last_response, file_name="response.txt", mime='text/plain')
    save_as_word(last_response, "response.docx")
    with open("response.docx", "rb") as docx_file:
        st.download_button(f"Download Last Response as Word", docx_file, file_name="response.docx", mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
