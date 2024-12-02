import streamlit as st
import boto3
import json
from docx import Document
from io import BytesIO

# Bedrock Configuration
class BedrockConfig:
    MODEL_ID = "amazon.titan-text-premier-v1:0"
    AWS_REGION = st.secrets["AWS_REGION"]
    AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]

# Initialize Bedrock client
def get_bedrock_client():
    return boto3.client(
        "sagemaker-runtime",
        region_name=BedrockConfig.AWS_REGION,
        aws_access_key_id=BedrockConfig.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=BedrockConfig.AWS_SECRET_ACCESS_KEY,
    )

# Generate content using Bedrock
def generate_content(prompt, task):
    client = get_bedrock_client()
    task_prompt = f"{task}: {prompt}"
    
    # Invoke Bedrock endpoint
    response = client.invoke_endpoint(
        EndpointName=BedrockConfig.ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps({"inputText": task_prompt}),
    )
    
    # Parse response
    response_body = json.loads(response["Body"].read())
    return response_body.get("results", "Error: No output from Bedrock")

# Save content as a Word document
def save_as_word(content):
    doc = Document()
    doc.add_paragraph(content)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit App Configuration
st.set_page_config(page_title="BA Genie", page_icon="🤖", layout="wide")

# Header Section
st.image("logo.jpg", width=600)  # Replace with your logo path
st.title("🤖 BA Genie")
st.markdown("""
Welcome to **BA Genie**, your AI-powered assistant for generating:
- 📖 **User Stories** 
- 📧 **Email Templates**
- ✍️ **Grammarly-like Writing Enhancements** 
- 📝 **Content Summaries and Paraphrasing**
""")

# Sidebar Navigation
st.sidebar.header("Navigation")
task = st.sidebar.selectbox(
    "Choose a task",
    ["Grammar Check", "Paraphrase", "Summarize", "Generate User Story", "Generate Email"]
)
st.sidebar.write("Select a task to begin. Customize your text and download the results!")

# Text Input Section
st.subheader("🔍 Input Area")
user_input = st.text_area(
    "Type or paste your content here:",
    placeholder="Enter your text, user story description, or email content...",
    height=200
)

# Generate Button
if st.button("Generate"):
    if user_input:
        # Dynamically generate content based on task
        result = generate_content(user_input, task)

        # Display Generated Content
        st.subheader("✨ Generated Output")
        st.write(result)

        # Download Options
        st.markdown("#### 📥 Download Your Result")
        st.download_button(
            label="Download as Text File",
            data=result,
            file_name="output.txt",
            mime="text/plain"
        )
        word_file = save_as_word(result)
        st.download_button(
            label="Download as Word File",
            data=word_file,
            file_name="output.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.warning("⚠️ Please enter text to generate results.")
else:
    st.info("👈 Select a task and input text to get started.")

# Footer Section
st.markdown("---")
st.markdown("© 2024 BA Genie - Powered by Amazon Bedrock and Streamlit")
