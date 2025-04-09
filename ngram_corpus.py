import spacy
from nltk.util import ngrams
from nltk.corpus import stopwords
import nltk

# Download NLTK stopwords if not already downloaded
nltk.download('stopwords')

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to check if a word is a stopword
def check_stopword(word):
    return word in stopwords.words('english')

# Function to check if a word is in the dictionary (OOV check)
def check_in_dictionary(word):
    # `is_oov` checks if the word is Out Of Vocabulary
    return not nlp.vocab[word].is_oov

# Function to create n-grams from text
def generate_ngrams(text, n=2):
    """Generate n-grams from a text string."""
    tokens = text.split()
    return [" ".join(ngram) for ngram in ngrams(tokens, n)]

# Example sentence
user_sentence = "Quantum entanglement and blockchain technology are emerging fields revolutionizing industries, with concepts like cryptocurrency and decentralized finance (DeFi) gaining traction globally."

# Tokenize the sentence
doc = nlp(user_sentence)

# Process words and create n-grams if not in the corpus (stopwords or dictionary)
words_in_corpus = []
words_not_in_corpus = []
ngrams_created = []

for token in doc:
    # Lemmatize the token (convert to base form)
    lemma = token.lemma_

    if check_stopword(lemma) or check_in_dictionary(lemma):
        words_in_corpus.append(lemma)
    else:
        words_not_in_corpus.append(lemma)

# Generate n-grams for the unfamiliar words
if words_not_in_corpus:
    ngrams_created = generate_ngrams(" ".join(words_not_in_corpus), n=2)


# Save results to a JSON file
import json
with open("unfamiliar_words.json", "w") as f:
    json.dump(words_not_in_corpus,f,indent=4)

# Output the results
print("Words in Corpus (Stopwords or Dictionary):", words_in_corpus)
print("Words NOT in Corpus (Unfamiliar words):", words_not_in_corpus)
print("Generated N-grams:", ngrams_created)
