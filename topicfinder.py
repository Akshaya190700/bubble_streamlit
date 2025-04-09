import streamlit as st
from transformers import pipeline
import language_tool_python

# Load the zero-shot classification pipeline
@st.cache_resource
def load_model():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli",device=-1)

# Initialize the LanguageTool for grammar checking
@st.cache_resource
def load_language_tool():
    return language_tool_python.LanguageTool("en-US")

# Predefined topics for zero-shot classification
TOPICS = [
    "technology",
    "sports",
    "health",
    "education",
    "finance",
    "entertainment",
    "travel",
    "politics",
    "science",
    "environment",
    "business",
    "fashion",
    "art",
    "music",
    "movies",
    "history",
    "food",
    "philosophy",
    "religion",
    "psychology",
    "social media",
    "literature",
    "gaming",
    "space",
    "cryptocurrency",
    "programming",
    "artificial intelligence",
    "machine learning",
    "cybersecurity",
    "marketing",
    "relationships",
    "parenting",
    "fitness",
    "real estate",
    "law",
    "economics",
    "medicine",
    "biology",
    "physics",
    "chemistry",
    "mathematics",
    "current events",
    "startups",
    "mental health",
    "wellness",
    "e-commerce",
    "news",
    "photography",
    "animals",
    "DIY",
    "gardening",
    "technology trends",
    "entrepreneurship",
    "leadership",
    "public speaking",
    "self-improvement",
    "career development",
    "automation",
    "blockchain",
    "augmented reality",
    "virtual reality",
    "quantum computing",
    "robotics",
    "nanotechnology",
    "sustainability",
    "climate change",
    "renewable energy",
    "electric vehicles",
    "astrophysics",
    "geology",
    "oceanography",
    "forestry",
    "urban planning",
    "civil engineering",
    "mechanical engineering",
    "aerospace engineering",
    "chemical engineering",
    "data science",
    "statistics",
    "analytics",
    "ethics",
    "cultural studies",
    "linguistics",
    "theology",
    "travel tips",
    "hospitality",
    "luxury lifestyle",
    "budget travel",
    "personal finance",
    "investing",
    "stock market",
    "cryptocurrency trading",
    "insurance",
    "retirement planning",
    "taxation",
    "charity",
    "volunteering",
    "social issues",
    "human rights",
    "diversity and inclusion",
    "gender equality",
    "education policy",
    "teaching",
    "online learning",
    "student life",
    "scholarships",
    "exams",
    "study tips",
    "creative writing",
    "poetry",
    "novels",
    "biographies",
    "memoirs",
    "film reviews",
    "TV shows",
    "celebrity gossip",
    "music genres",
    "classical music",
    "pop music",
    "jazz",
    "rock music",
    "hip hop",
    "electronic music",
    "video production",
    "podcasting",
    "vlogging",
    "streaming",
    "esports",
    "board games",
    "card games",
    "outdoor activities",
    "hiking",
    "camping",
    "fishing",
    "cycling",
    "running",
    "team sports",
    "individual sports",
    "athletics",
    "yoga",
    "meditation",
    "nutrition",
    "dieting",
    "veganism",
    "vegetarianism",
    "mindfulness",
    "spirituality",
    "alternative medicine",
    "pharmaceuticals",
    "cosmetics",
    "skincare",
    "haircare",
    "home decor",
    "interior design",
    "real estate investing",
    "construction",
    "smart homes",
    "wearable technology",
    "drones",
    "military technology",
    "space exploration",
    "astronomy",
    "zoology",
    "botany",
    "aquatic life",
    "wildlife conservation",
    "farming",
    "agriculture",
    "food security",
    "supply chain",
    "logistics",
    "transportation",
    "aviation",
    "shipping",
    "ride-sharing",
    "electric bikes",
    "autonomous vehicles",
    "public transportation",
    "global events",
    "local news",
    "breaking news",
    "cultural festivals",
    "holidays",
    "fashion trends",
    "sustainable fashion",
    "jewelry",
    "accessories",
    "luxury brands",
    "budget shopping",
    "crafting",
    "sewing",
    "knitting",
    "woodworking",
    "home improvement",
    "home appliances",
    "pet care",
    "dog training",
    "cat behavior",
    "exotic pets",
    "gardening tools",
    "landscaping",
    "horticulture",
    "plant care",
    "succulents",
    "bonsai trees",
]

def correct_grammar(sentence, topic):
    """
    Fix grammar or spelling issues unrelated to the topic using LanguageTool.
    """
    tool = load_language_tool()
    matches = tool.check(sentence)

    corrected_sentence = language_tool_python.utils.correct(sentence, matches)
    return corrected_sentence

def main():
    st.title("Topic Identifier with Grammar Correction")

    st.write(
        "Enter a sentence, and this app will identify its topic and correct grammar/spelling errors if unrelated to the topic."
    )

    # User input
    user_input = st.text_input("Enter your sentence here:")

    if st.button("Validate"):
        if not user_input.strip():
            st.warning("Please enter a valid sentence.")
        else:
            # Load model
            classifier = load_model()

            # Perform zero-shot classification
            with st.spinner("Identifying topic..."):
                results = classifier(user_input, TOPICS)

            # Extract the most probable topic
            top_topic = results["labels"][0]
            confidence = results["scores"][0] * 100

            st.success(
                f"The sentence most likely belongs to the topic: **{top_topic}** with a confidence of {confidence:.2f}%."
            )

            # Correct grammar or spelling
            with st.spinner("Correcting grammar/spelling..."):
                corrected_sentence = correct_grammar(user_input, top_topic)

            st.write("### Corrected Sentence:")
            st.write(corrected_sentence)

if __name__ == "__main__":
    main()
