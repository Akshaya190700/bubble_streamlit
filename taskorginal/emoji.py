import streamlit as st
from langdetect import detect
from textblob import TextBlob
from spellchecker import SpellChecker
from streamlit_modal import Modal
import re  # For regular expression based emoji removal

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

# Function to remove emojis from text
def remove_emojis(text):
    emoji_pattern = re.compile(
        "["  
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# Function to validate and suggest corrections
def validate_idea(text):
    # Remove emojis from the text for further validation and correction
    text_without_emojis = remove_emojis(text)
    
    # First, apply spelling and grammar corrections
    corrected_sentence = suggest_corrections(text_without_emojis)

    # Then check if the corrected sentence is in English
    if not is_english(corrected_sentence):
        return "The text is not in English.", text

    # Return the corrected sentence and the original text
    return corrected_sentence, text

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
st.title("Sentence and Idea Validator with Emoji Support")

# Dynamically creating a unique key for the text input field
sentence_key = f"sentence_input_{st.session_state.sentence}"  # Unique key based on the sentence content

# Text input for the user to enter a sentence (single input box)
sentence = st.text_input("Enter a sentence:", value=st.session_state.sentence, key=sentence_key)

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
