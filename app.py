import streamlit as st
import boto3
import json
from docx import Document
from io import BytesIO

# Bedrock Configuration
class BedrockConfig:
    MODEL_ID = "amazon.titan-text-premier-v1:0"  # Adjust model ID as per your Bedrock setup
    AWS_REGION = st.secrets["AWS_REGION"]
    AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]

# Initialize Bedrock client
def get_bedrock_client():
    return boto3.client(
        "bedrock",
        region_name=BedrockConfig.AWS_REGION,
        aws_access_key_id=BedrockConfig.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=BedrockConfig.AWS_SECRET_ACCESS_KEY,
    )

# Generate content using Bedrock
def generate_content(prompt, task):
    client = get_bedrock_client()
    task_prompt = f"{task}: {prompt}"
    
    response = client.invoke_model(
        modelId=BedrockConfig.MODEL_ID,
        body=json.dumps({"inputText": task_prompt}),
        accept="application/json",
        contentType="application/json",
    )
    response_body = json.loads(response["body"].read())
    return response_body["results"]

# Save content as a Word document
def save_as_word(content):
    doc = Document()
    doc.add_paragraph(content)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("AI-Powered Writing Assistant (Bedrock)")

# Sidebar for task selection
task = st.sidebar.selectbox("Choose a task", ["Grammar Check", "Paraphrase", "Summarize", "Generate User Story", "Generate Email"])

# Text input area
user_input = st.text_area("Enter your text here:")

if st.button("Generate"):
    if user_input:
        # Generate content based on selected task
        result = generate_content(user_input, task)
        st.subheader("Generated Content")
        st.write(result)

        # Provide download options
        st.download_button(
            label="Download as Text",
            data=result,
            file_name="output.txt",
            mime="text/plain",
        )

        word_file = save_as_word(result)
        st.download_button(
            label="Download as Word",
            data=word_file,
            file_name="output.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    else:
        st.warning("Please enter some text to proceed.")
