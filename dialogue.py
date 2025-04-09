import streamlit as st 
from pymongo import MongoClient
from streamlit_option_menu import option_menu
from datetime import datetime
from langdetect import detect
from textblob import TextBlob
from streamlit_modal import Modal
import re  # For regular expression-based emoji and special character removal
# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['user_db']
users_collection = db['bubble_users']
posts_collection = db['bubble_posts']
# Function to verify credentials
def login_user(email, password):
    user = users_collection.find_one({"email": email})
    if user and user['password'] == password:  # Plain text password check
        return user
    return None
# Function to improve corrections by ensuring coherence
def improve_suggestion(corrected_text):
    sentences = corrected_text.split(". ")
    improved_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:  # Avoid empty sentences
            if not sentence.endswith('.'):
                sentence += '.'
            improved_sentences.append(sentence[0].upper() + sentence[1:])
    return " ".join(improved_sentences)
# Function to suggest corrections for spelling and grammar
def suggest_corrections(text):
    # Use TextBlob for grammar correction
    blob = TextBlob(text)
    corrected_sentence = str(blob.correct())
# Improve sentence coherence and formatting
    return improve_suggestion(corrected_sentence)
# Function to check if the text is in English
def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False
# Function to remove emojis and special characters from text
def remove_special_characters(text):
    # Remove emojis
    emoji_pattern = re.compile(
        "["  
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F700-\U0001F77F"  # Alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric shapes extended
        "\U0001F800-\U0001F8FF"  # Supplemental arrows
        "\U0001F900-\U0001F9FF"  # Supplemental symbols & pictographs
        "\U0001FA00-\U0001FA6F"  # Chess symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and pictographs extended
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "\U0000200D"  # Zero width joiner
        "\U00002600-\U000026FF"  # Misc symbols
        "\U00002B05-\U00002B07"  # Arrows
        "]+", 
        flags=re.UNICODE)
# Remove special characters and emojis
    return re.sub(r'[^A-Za-z0-9\s]+', '', emoji_pattern.sub(r'', text))
# Function to validate and suggest corrections
def validate_idea(text):
 # Remove emojis and special characters from the text for further validation and correction
    text_cleaned = remove_special_characters(text)
# Apply grammar corrections
    corrected_sentence = suggest_corrections(text_cleaned)
# Then check if the corrected sentence is in English
    if not is_english(corrected_sentence):
        return "The text is not in English.", text
# Return the corrected sentence and the original text
    return corrected_sentence, text
# Initialize session state variables
if "user" not in st.session_state:
    st.session_state["user"] = None
if "validation_status" not in st.session_state:
    st.session_state["validation_status"] = None
if "modal_open" not in st.session_state:
    st.session_state["modal_open"] = False
if "sentence" not in st.session_state:
    st.session_state["sentence"] = ""
# Streamlit page configuration
st.set_page_config(
    page_title="My Streamlit App",
    page_icon="🤖")
# Main Login Page
if "user" not in st.session_state or not st.session_state["user"]:
    st.title("Login Page")
    email = st.text_input("📧 Email")
    password = st.text_input("🔒 Password", type="password")
    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state["user"] = user
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")
else:
    user = st.session_state["user"]
# Dashboard with Navigation
    st.title("Dashboard")
    selected = option_menu(
        menu_title=None,
        options=["My Profile", "Create Post", "My Posts"], 
        icons=["person-circle", "plus-square", "chat-square-text"], 
        menu_icon=None,default_index=0,orientation="horizontal")
    if selected == "My Profile":
        st.subheader("Profile")
        st.write(f"*Name:* {user.get('name', 'N/A')}")
        st.write(f"*Email:* {user.get('email', 'N/A')}")
        st.write(f"*Role:* {user.get('role', 'N/A')}")
          # Address (Formatted)
        address = user.get('address', {})
        street = address.get('street', 'N/A')
        city = address.get('city', 'N/A')
        zip_code = address.get('zip', 'N/A')
        st.write("*Address:*")
        st.markdown(
            f"""
            <div style="margin-left: 20px;">
                <p><b>Street:</b> {street}</p>
                <p><b>City:</b> {city}</p>
                <p><b>ZIP:</b> {zip_code}</p>
            </div>
            """,
            unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    elif selected == "Create Post":
        st.subheader("Create Post")
        # Text input for the user to enter a sentence
        sentence = st.text_input("Enter your post (25-400 characters)", max_chars=400,value=st.session_state["sentence"], key="sentence_input")
        if len(sentence) >= 25:   
            post_data = {
                    "user_id": user.get("_id"),
                    "name": user.get("name"),
                    "content": sentence,
                    "created_at": datetime.now()}
            posts_collection.insert_one(post_data)
            st.success("Post submitted successfully!")
            st.session_state["sentence"]=""
        elif len(sentence)>0:
            st.error("Post must be at least 25 characters long.")           
# Modal instance with a title
        modal = Modal("Validation Modal", key="validation_modal")
 # Validate Button
        if st.button("Validate the Text"):
            if sentence.strip():  # Check if the input is not empty
                st.session_state["sentence"] = sentence  # Store the sentence in session state
                modal.open()  # Open the modal
                st.session_state["modal_open"] = True
            else:
                st.warning("Please enter a sentence before validating!")
   # Modal content
        if modal.is_open():
            with modal.container():
                # Replace the modal header with the uppercase version of the user's input
                st.subheader(st.session_state["sentence"].upper())
                st.write("Do you confirm the validation of this sentence?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes"):
                        st.session_state["validation_status"] = "success"
                        st.session_state["sentence"] = st.session_state["sentence"].upper()  # Update input with uppercase text
                        st.session_state["modal_open"] = False  # Close modal
                        modal.close()
                with col2:
                    if st.button("No"):
                        st.session_state["validation_status"] = "failure"
                        st.session_state["sentence"] = ""  # Clear the input box content
                        st.session_state["modal_open"] = False  # Close modal
                        modal.close()
   # Display validation status message
        if not st.session_state["modal_open"]:
            if st.session_state["validation_status"] == "success":
                st.success("Validation Successful!")
            elif st.session_state["validation_status"] == "failure":
                st.error("Validation Failed!")
      # Clear or update the input field content based on user action
        if not st.session_state["modal_open"]:
            sentence = st.session_state["sentence"]  # Update the text input with the updated sentence
       # Post Button
        if st.session_state.get("sentence", "").strip():
            if st.button("Post"):
                try:
                    post_data = {
                        "user_id": user.get("_id"),
                        "name": user.get("name"),
                        "content": st.session_state["sentence"],
                        "created_at": datetime.now()
                    }
                    posts_collection.insert_one(post_data)
                    st.success("Post submitted successfully!")
                    st.session_state.sentence = ""  # Clear the post content after submission
                except Exception as e:
                    st.error(f"Failed to post due to:{str(e)}")
    elif selected == "My Posts":
        st.subheader("My Posts")
        user_posts = list(posts_collection.find({"user_id": user.get("_id")}))
        user_posts.sort(key=lambda post: post.get('created_at'), reverse=True)

        if not user_posts:
            st.info("You have not created any posts yet.")
        else:
            for post in user_posts:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"*Post ID:* {post.get('_id')}")
                with col2:
                    st.write(f"*Posted On:* {post.get('created_at').strftime('%d-%m-%Y %H:%M:%S')}")

                st.write(f"*Post:*  \n{post.get('content')}")
                st.markdown("---")
