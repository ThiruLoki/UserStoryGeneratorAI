import streamlit as st
import boto3
import json
from docx import Document

# Bedrock Configuration
class BedrockConfig:
    MODEL_ID = "amazon.titan-text-premier-v1:0"
    AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
    AWS_REGION = st.secrets["AWS_REGION"]

# Initialize Bedrock Client
def get_bedrock_client():
    return boto3.client(
        "bedrock",
        region_name=BedrockConfig.AWS_REGION,
        aws_access_key_id=BedrockConfig.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=BedrockConfig.AWS_SECRET_ACCESS_KEY,
    )

# Generate Precise User Story
def generate_precise_user_story(prompt, user_role="user"):
    template = f"""
    Generate a detailed user story for an e-commerce website.
    Title: {user_role.capitalize()} Login to Access Profile
    As an {user_role}, I want to {"log into the e-commerce website" if user_role == "existing customer" else "sign up for an account"}, so that {"I can access my profile and manage my account details" if user_role == "existing customer" else "I can create a new account and start shopping"}.
    Include acceptance criteria, input validation, session management, and security measures.
    """
    client = get_bedrock_client()
    response = client.invoke_model(
        modelId=BedrockConfig.MODEL_ID,
        body=json.dumps({"inputText": template}),
        accept="application/json",
        contentType="application/json",
    )
    output = json.loads(response["body"].read())
    return output["results"]

# Generate Email Template
def generate_email_template(prompt):
    template = f"""
    Write a professional email based on the following details:
    {prompt}
    """
    client = get_bedrock_client()
    response = client.invoke_model(
        modelId=BedrockConfig.MODEL_ID,
        body=json.dumps({"inputText": template}),
        accept="application/json",
        contentType="application/json",
    )
    output = json.loads(response["body"].read())
    return output["results"]

# Save Content as Word Document
def save_as_word(content, filename):
    doc = Document()
    doc.add_paragraph(content)
    doc.save(filename)

# Input Validation
def is_valid_input(prompt):
    return len(prompt) >= 10

# Streamlit App
st.image("logo.jpg", width=600)
st.title("BA Genie")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat Input
user_input = st.chat_input("Type your requirement here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if is_valid_input(user_input):
        # Determine response type
        if "user story" in user_input.lower():
            response = generate_precise_user_story(user_input, user_role="existing customer")
        elif "email" in user_input.lower():
            response = generate_email_template(user_input)
        else:
            response = "I can assist with user stories or email templates. Please provide a valid input."
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Input must be at least 10 characters long."})

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Download Buttons for Last Response
if len(st.session_state.messages) > 0:
    last_response = st.session_state.messages[-1]["content"]
    st.download_button("Download Last Response as Text", last_response, file_name="response.txt", mime="text/plain")
    save_as_word(last_response, "response.docx")
    with open("response.docx", "rb") as docx_file:
        st.download_button("Download Last Response as Word", docx_file, file_name="response.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
