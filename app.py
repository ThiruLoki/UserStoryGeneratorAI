import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from docx import Document

# Load API key from Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Display the app logo
st.image("logo.jpg", width=600)

def generate_precise_user_story(prompt):
    """
    Generate a user story based on the input prompt.
    """
    if "existing customer" in prompt.lower() or "login" in prompt.lower():
        user_role = "existing customer"
    elif "new customer" in prompt.lower() or "sign up" in prompt.lower():
        user_role = "new customer"
    else:
        user_role = "user"  # Default to a generic "user" if no specific role is detected

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
    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["feature_name", "title", "user", "feature", "goal"],
            template=user_story_template
        )
    )

    # Run chain with dynamic user role
    user_story = chain.run({
        "feature_name": "E-commerce Website Login Page",
        "title": f"{user_role.capitalize()} Login to Access Profile",
        "user": user_role,
        "feature": "log into the e-commerce website" if user_role == "existing customer" else "sign up for an account",
        "goal": "access my profile and manage my account details" if user_role == "existing customer" else "create a new account and start shopping"
    })
    return user_story.strip()

def generate_email_template(prompt):
    """
    Generate an email template based on the input prompt.
    """
    llm = OpenAI(temperature=0.5, model_name="gpt-3.5-turbo", openai_api_key=api_key)
    email_template = """
        Write a formal email based on the following details:
        {details}
    """
    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(input_variables=["details"], template=email_template)
    )
    email_response = chain.run({"details": prompt})
    return email_response.strip()

def generate_general_query_response(prompt):
    """
    Generate a response for general queries.
    """
    llm = OpenAI(temperature=0.7, model_name="gpt-3.5-turbo", openai_api_key=api_key)
    general_template = """
        Respond thoughtfully to the following query:
        {query}
    """
    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(input_variables=["query"], template=general_template)
    )
    general_response = chain.run({"query": prompt})
    return general_response.strip()

def detect_response_type(prompt):
    """
    Detect the type of response based on keywords.
    """
    keywords_user_story = ["user story", "acceptance criteria", "feature", "As a", "so that"]
    keywords_email = ["email", "subject", "greeting", "template"]

    if any(keyword in prompt.lower() for keyword in keywords_user_story):
        return "User Story"
    elif any(keyword in prompt.lower() for keyword in keywords_email):
        return "Email Template"
    return "General"

def generate_response(prompt, response_type):
    """
    Generate a response based on the detected response type.
    """
    if response_type == "User Story":
        return generate_precise_user_story(prompt)
    elif response_type == "Email Template":
        return generate_email_template(prompt)
    else:
        # For all other queries, use a general-purpose prompt
        return generate_general_query_response(prompt)

def save_as_word(content, filename):
    """
    Save the generated response as a Word document.
    """
    doc = Document()
    doc.add_paragraph(content)
    doc.save(filename)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Capture user input
user_input = st.chat_input("Type your requirement here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Detect response type and generate the response
    response_type = detect_response_type(user_input)
    response = generate_response(user_input, response_type)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat messages
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
    save_as_word(last_response, "response.docx")
    with open("response.docx", "rb") as docx_file:
        st.download_button(
            label="Download Last Response as Word",
            data=docx_file,
            file_name="response.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
