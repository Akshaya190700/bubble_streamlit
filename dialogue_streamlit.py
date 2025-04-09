import streamlit as st
from streamlit_modal import Modal

# Title of the application
st.title("Sentence Validator")

# Initialize session state variables
if "validation_status" not in st.session_state:
    st.session_state["validation_status"] = None
if "modal_open" not in st.session_state:
    st.session_state["modal_open"] = False
if "sentence" not in st.session_state:
    st.session_state["sentence"] = ""

# Text input for the user to enter a sentence
sentence = st.text_input("Enter a sentence:", value=st.session_state["sentence"], key="sentence_input")

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
