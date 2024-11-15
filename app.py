import streamlit as st
from langchain.chains import ConversationChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory

# Load API key from Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Initialize memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Initialize conversation chain with memory
conversation = ConversationChain(
    llm=OpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key),
    memory=memory,
)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display logo
st.image("logo.jpg", width=600)

# Capture user input
user_input = st.chat_input("Type your requirement here...")

if user_input:
    # Add user input to session state messages
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate a response using the conversation chain
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
    st.download_button(
        label="Download Last Response as Text", 
        data=last_response, 
        file_name="response.txt", 
        mime="text/plain"
    )

    # Save as Word document
    from docx import Document
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
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
