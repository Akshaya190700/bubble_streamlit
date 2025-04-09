import streamlit as st
from langdetect import detect
from textblob import TextBlob
from spellchecker import SpellChecker
from streamlit_modal import Modal

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
    spell = SpellChecker()
    words = text.split()
    corrected_text = []

    for word in words:
        corrected_word = spell.correction(word)
        corrected_text.append(corrected_word if corrected_word else word)

    corrected_sentence = " ".join(corrected_text)

    # Use TextBlob for grammar correction
    blob = TextBlob(corrected_sentence)
    fully_corrected_sentence = str(blob.correct())

    # Improve sentence coherence and formatting
    return improve_suggestion(fully_corrected_sentence)

# Function to check if the text is in English
def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False

# Function to validate and suggest corrections
def validate_idea(text):
    # First apply spelling and grammar corrections
    corrected_sentence = suggest_corrections(text)

    # Check if the corrected sentence is in English
    if not is_english(corrected_sentence):
        return "The text is not in English.", text

    # Compare original and corrected sentence
    if corrected_sentence.strip() != text.strip():
        return corrected_sentence, text
    return "No changes required. Your text is correct.", text

# Initialize session state for user input and modal
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "validation_status" not in st.session_state:
    st.session_state.validation_status = None
if "modal_open" not in st.session_state:
    st.session_state.modal_open = False
if "sentence" not in st.session_state:
    st.session_state.sentence = ""
if "suggested_sentence" not in st.session_state:  # Initialize the key
    st.session_state.suggested_sentence = ""
if "original_sentence" not in st.session_state:  # Initialize the key
    st.session_state.original_sentence = ""

# Streamlit UI
st.title("Sentence Validator")

# Text input for the user to enter a sentence
sentence = st.text_input("Enter a sentence:", value=st.session_state.sentence, key="sentence_input")

# Modal instance with a title
modal = Modal("Validation Modal", key="validation_modal")

# Validate Button
if st.button("Validate the Text"):
    if sentence.strip():  # Check if the input is not empty
        st.session_state["sentence"] = sentence  # Store the sentence in session state
        # Validate the sentence for spelling, grammar, and language
        suggestion, original_text = validate_idea(sentence)

        # If there is a suggestion, show the modal for confirmation
        if suggestion != original_text:
            st.session_state["suggested_sentence"] = suggestion  # Store suggested sentence in session state
            st.session_state["original_sentence"] = original_text  # Store original sentence
            modal.open()  # Open the modal for user confirmation
            st.session_state["modal_open"] = True
        else:
            st.success("Your sentence is correct!")  # No corrections needed
    else:
        st.warning("Please enter a sentence before validating!")

# Modal content
if modal.is_open():
    with modal.container():
        # Display the corrected sentence in uppercase
        st.subheader(st.session_state["suggested_sentence"].upper())
        st.write("Would you like to accept the suggested changes?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, apply suggestion"):
                st.session_state["sentence"] = st.session_state["suggested_sentence"].upper()  # Update the sentence
                st.session_state["modal_open"] = False  # Close modal
                modal.close()
                st.success("Validation Successful! The sentence has been updated.")
            with col2:
                if st.button("No, keep original"):
                    st.session_state["sentence"] = st.session_state["original_sentence"]  # Keep original sentence
                    st.session_state["modal_open"] = False  # Close modal
                    modal.close()
                    st.info("The original sentence has been kept.")

# Display validation status message
if not st.session_state["modal_open"] and st.session_state["validation_status"]:
    if st.session_state["validation_status"] == "success":
        st.success("Validation Successful!")
    elif st.session_state["validation_status"] == "failure":
        st.error("Validation Failed!")
