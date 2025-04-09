# from transformers import BartForConditionalGeneration, BartTokenizer

# # Load pre-trained BART model and tokenizer
# model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
# tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

# def summarize_text(text):
#     # Tokenize input text and get model output
#     inputs = tokenizer(text, return_tensors='pt', max_length=1024, truncation=True)
#     summary_ids = model.generate(inputs['input_ids'], num_beams=4, min_length=30, max_length=200, early_stopping=True)
    
#     # Decode and return the summary
#     summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
#     return summary

# # Example text to summarize
# text = """
# Climate change is one of the most pressing issues facing humanity today. 
# It is caused by the buildup of greenhouse gases in the atmosphere, primarily from burning fossil fuels and deforestation. 
# The consequences of climate change include rising global temperatures, melting ice caps, and more frequent extreme weather events.
#  To combat this crisis, governments, businesses, and individuals must work together to reduce carbon emissions, adopt renewable energy sources, and promote sustainable practices
# """

# # Get the summary of the text
# summary = summarize_text(text)
# print(summary)


from pymongo import MongoClient
from transformers import pipeline, BartTokenizer, BartForConditionalGeneration
from sentence_transformers import SentenceTransformer

# MongoDB connection setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["bubble_db"]
post_collection = db["bubble_posts"]

# Load pre-trained BART model and tokenizer
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

# Summarization pipeline setup (using Hugging Face Transformers with BART)
bart_summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# model = SentenceTransformer('all-MiniLM-L6-v2')

def summarize_and_store():
    try:
        # Fetch all posts from the post collection
        posts = post_collection.find()
        
        for post in posts:
            text = post.get("processed_text", "")
            if not text:
                continue

            # Tokenize input text and summarize using BART
            inputs = tokenizer(text, return_tensors='pt', max_length=1024, truncation=True)
            summary_ids = model.generate(inputs['input_ids'], num_beams=4, min_length=10, max_length=50, early_stopping=True)
            
            # Decode the summary
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            # Update the document with summarized text and flag
            post_collection.update_one(
                {"_id": post["_id"]},
                {"$set": {"summarized_text": summary, "summarized": True}}
            )
            print(f"Updated post with _id {post['_id']}")

    except Exception as e:
        print("An error occurred:", str(e))

# Example usage
if __name__ == "__main__":
    summarize_and_store()

