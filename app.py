import streamlit as st
from langchain.chains import ConversationChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from docx import Document

# Load API key from Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Define a custom identity prompt
identity_prompt = """
You are BA Genie, a specialized AI assistant. When asked questions about who you are, your name, or your purpose, always respond by introducing yourself as BA Genie. 
Example:
User: Who are you?
Response: I am BA Genie, your personal assistant designed to help you generate user stories, email templates, and answer your queries. My goal is to assist you effectively.
Conversation History:
{history}
User Input:
{input}
"""

# Initialize memory with the correct key for ConversationChain
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# Initialize conversation chain with memory and custom identity prompt
conversation = ConversationChain(
    llm=OpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key),
    memory=memory,
    prompt=PromptTemplate(
        template=identity_prompt,
        input_variables=["history", "input"]
    ),
)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Functions for User Story and Email Template generation
def generate_precise_user_story(prompt):
    """
    Generate a user story based on the input prompt.
    """
    user_story_prompt = """
    Generate a detailed user story with the following format:
    Title: {title}
    As a {user}, I want to {feature}, so that {goal}.
    Acceptance Criteria:
    1. Clearly state the conditions for success.
    2. Define edge cases to consider.
    """
    llm = OpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key)
    chain = ConversationChain(
        llm=llm,
        prompt=PromptTemplate(
            template=user_story_prompt,
            input_variables=["title", "user", "feature", "goal"],
        ),
    )
    return chain.run(
        {
            "title": "E-commerce User Login",
            "user": "customer",
            "feature": "log into my account",
            "goal": "access my purchase history",
        }
    ).strip()


def generate_email_template(prompt):
    """
    Generate an email template based on the input prompt.
    """
    email_template_prompt = """
    Write a professional email based on the following details:
    {details}
    """
    llm = OpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key)
    chain = ConversationChain(
        llm=llm,
        prompt=PromptTemplate(
            template=email_template_prompt,
            input_variables=["details"],
        ),
    )
    return chain.run({"details": prompt}).strip()


# Display app logo
st.image("logo.jpg", width=600)

# Capture user input
user_input = st.chat_input("Type your requirement here...")

if user_input:
    # Add user input to session state messages
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate a response based on the input type
    if "user story" in user_input.lower():
        response = generate_precise_user_story(user_input)
    elif "email" in user_input.lower():
        response = generate_email_template(user_input)
    else:
        # Generate general conversation response
        response = conversation.run(input=user_input)

    # Add the response to session state messages
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Offer file download options for the last response
if len(st.session_state.messages) > 0:
    last_response = st.session_state.messages[-1]["content"]

    # Download as Text
    st.download_button(
        label="Download Last Response as Text",
        data=last_response,
        file_name="response.txt",
        mime="text/plain",
    )

    # Download as Word document
    def save_as_word(content, filename):
        doc = Document()
        doc.add_paragraph(content)
        doc.save(filename)

    save_as_word(last_response, "response.docx")
    with open("response.docx", "rb") as docx_file:
        st.download_button(
            label="Download Last Response as Word",
            data=docx_file,
            file_name="response.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
