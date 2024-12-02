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
def generate_content_with_context(conversation):
    """
    Sends the conversation history to the Bedrock model and retrieves the response.
    """
    client = get_bedrock_client()

    # Format the conversation for the prompt
    prompt = "You are BA Genie, an AI-powered assistant. Keep the conversation context and respond appropriately.\n\n"
    for turn in conversation:
        prompt += f"{turn['role'].capitalize()}: {turn['content']}\n"
    prompt += "BA Genie:"

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
st.set_page_config(page_title="BA Genie", page_icon="🤖", layout="centered")

# Apply Custom CSS for Center Alignment
st.markdown("""
    <style>
        .center-content {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        .chat-message {
            width: 80%;
            margin: auto;
            text-align: left;
            border-radius: 10px;
            padding: 10px;
            background-color: #f4f4f4;
        }
        .chat-message.user {
            background-color: #d4e6f1;
        }
        .chat-message.assistant {
            background-color: #f9ebea;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header Section
st.markdown('<div class="center-content">', unsafe_allow_html=True)
st.title("🤖 BA Genie")
st.markdown("""
Welcome to **BA Genie**, your conversational assistant for:
- 📖 User Stories
- 📧 Email Templates
- ✍️ Writing Enhancements
- 📝 Summaries and Paraphrasing
""")
st.markdown('</div>', unsafe_allow_html=True)

# Chat Message Input and Display
for message in st.session_state.messages:
    role_class = "user" if message["role"] == "user" else "assistant"
    st.markdown(f"""
        <div class="chat-message {role_class}">
            {message["content"]}
        </div>
    """, unsafe_allow_html=True)

# User Input Area
user_input = st.chat_input("Type your request here...")

if user_input:
    # Save user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"""
        <div class="chat-message user">
            {user_input}
        </div>
    """, unsafe_allow_html=True)

    # Generate response with context
    response = generate_content_with_context(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown(f"""
        <div class="chat-message assistant">
            {response}
        </div>
    """, unsafe_allow_html=True)

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
