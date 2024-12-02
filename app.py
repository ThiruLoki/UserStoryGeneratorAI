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
def generate_content(prompt, task):
    """
    Sends the input prompt to the Bedrock model and retrieves the output text.
    """
    client = get_bedrock_client()
    task_prompt = f"{task}: {prompt}"  # Task-specific prompt formatting

    try:
        # Invoke the model through Bedrock
        response = client.invoke_model(
            modelId=BedrockConfig.MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": task_prompt}),
        )
        
        # Parse the response body
        response_body = json.loads(response["body"].read().decode("utf-8"))
        
        # Debugging: Log the raw response to Streamlit for troubleshooting
        st.write("Raw Bedrock Response:", response_body)

        # Extract the outputText from the results
        if (
            "results" in response_body
            and isinstance(response_body["results"], list)
            and len(response_body["results"]) > 0
        ):
            output_text = response_body["results"][0].get("outputText", "No output text found.")
            return output_text.strip()  # Clean up extra spaces/newlines
        else:
            return "Error: No valid output from Bedrock."
    except Exception as e:
        return f"Error invoking Bedrock: {str(e)}"

# Generate content with fallback templates
def generate_content_with_fallback(prompt, task):
    """
    Sends the input prompt to Bedrock and provides fallback content if the response is invalid.
    """
    predefined_templates = {
        "Grammar Check": "I couldn't process the request. Please ensure the input text is clear.",
        "Paraphrase": "I couldn't paraphrase the text. Try rephrasing your input.",
        "Summarize": "I couldn't summarize the content. Please provide a clearer context.",
        "Generate User Story": "Here is a basic user story: As a user, I want to perform a specific action, so that I can achieve a specific goal.",
        "Generate Email": "Here is a generic email template: Dear [Recipient], I hope this message finds you well. [Add details]. Best regards, [Your Name].",
    }

    # Attempt to generate content using Bedrock
    response = generate_content(prompt, task)

    # If the response contains an error or is empty, return the fallback template
    if response.startswith("Error") or response.strip() == "":
        return predefined_templates.get(task, "Sorry, I couldn't generate the requested content.")
    return response

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
        # Dynamically generate content based on task with fallback
        result = generate_content_with_fallback(user_input, task)
        
        # Display the generated or fallback content
        st.subheader("✨ Generated Output")
        st.write(result)

        # Allow downloads
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
