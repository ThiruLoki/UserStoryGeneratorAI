import streamlit as st
import boto3
import json
from docx import Document
from io import BytesIO

# Bedrock Configuration
class BedrockConfig:
    MODEL_ID = "amazon.titan-text-premier-v1:0"  # Replace with your Bedrock model ID
    AWS_REGION = st.secrets["AWS_REGION"]
    AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]

# Initialize Bedrock client
def get_bedrock_client():
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=BedrockConfig.AWS_REGION,
        aws_access_key_id=BedrockConfig.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=BedrockConfig.AWS_SECRET_ACCESS_KEY,
    )

# Generate content using Bedrock
def generate_content(prompt):
    """
    Sends the input prompt to the Bedrock model and retrieves the output text.
    """
    client = get_bedrock_client()

    try:
        # Invoke the model through Bedrock
        response = client.invoke_model(
            modelId=BedrockConfig.MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": prompt}),
        )
        
        # Parse the response body
        response_body = json.loads(response["body"].read().decode("utf-8"))

        # Extract the outputText from the results field
        if (
            "results" in response_body
            and isinstance(response_body["results"], list)
            and len(response_body["results"]) > 0
        ):
            output_text = response_body["results"][0].get("outputText", "No output text found.")
            return output_text.strip()  # Clean up extra spaces/newlines
        else:
            return "Sorry, I couldn't process your request. Please try again."
    except Exception as e:
        return f"Error invoking Bedrock: {str(e)}"

# Save content as a Word document
def save_as_word(content):
    """
    Saves the generated content to a Word document.
    """
    doc = Document()
    doc.add_paragraph(content)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit App Configuration
st.set_page_config(page_title="BA Genie", page_icon="🤖", layout="wide")
st.image("logo.jpg", width=600)


# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header Section
st.title("🤖 BA Genie")
st.markdown("""
Welcome to **BA Genie**, your conversational assistant for:
- 📖 User Stories
- 📧 Email Templates
- ✍️ Writing Enhancements
- 📝 Summaries and Paraphrasing
""")

# Chat Message Input and Display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Area
user_input = st.chat_input("Type your request here...")

if user_input:
    # Save user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = generate_content(user_input)
        st.markdown(response)
        # Save assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Download Options
        st.markdown("#### 📥 Download Your Result")
        st.download_button(
            label="Download as Text File",
            data=response,
            file_name="response.txt",
            mime="text/plain"
        )
        word_file = save_as_word(response)
        st.download_button(
            label="Download as Word File",
            data=word_file,
            file_name="response.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
