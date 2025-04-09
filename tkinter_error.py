# # import torch
# # from transformers import BertTokenizer, BertForMaskedLM
# # import language_tool_python
# # from symspellpy import SymSpell, Verbosity
# # import os

# # # Initialize SymSpell
# # def initialize_symspell():
# #     symspell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
# #     dictionary_path = os.path.join(os.path.dirname(__file__), "frequency_dictionary_en_82_765.txt")
# #     if os.path.exists(dictionary_path):
# #         symspell.load_dictionary(dictionary_path, term_index=0, count_index=1)
# #     else:
# #         raise FileNotFoundError(f"Dictionary file not found at {dictionary_path}")
# #     return symspell

# # # Initialize BERT model and tokenizer
# # tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# # model = BertForMaskedLM.from_pretrained('bert-base-uncased')

# # # Function to use BERT for correcting words in context
# # def correct_spelling_with_bert(sentence):
# #     # Tokenize the sentence and replace misspelled words with [MASK]
# #     tokens = tokenizer.tokenize(sentence)
# #     masked_sentence = []
# #     mask_positions = []
    
# #     # Masking words we assume are misspelled
# #     for idx, word in enumerate(tokens):
# #         if word in ['tody', 'mrning', 'anwesome']:  # Example words to mask
# #             masked_sentence.append('[MASK]')
# #             mask_positions.append(idx)
# #         else:
# #             masked_sentence.append(word)
    
# #     # Reconstruct the sentence with masked words
# #     masked_input = tokenizer.convert_tokens_to_string(masked_sentence)
    
# #     # Encode the masked sentence
# #     input_ids = tokenizer.encode(masked_input, return_tensors='pt')
    
# #     # Get BERT's predictions for the masked tokens
# #     with torch.no_grad():
# #         output = model(input_ids)
# #         predictions = output.logits
    
# #     # Replace masked tokens with BERT's predicted words
# #     predicted_tokens = tokenizer.convert_ids_to_tokens(input_ids[0].tolist())
    
# #     for pos in mask_positions:
# #         predicted_token = tokenizer.convert_ids_to_tokens(torch.argmax(predictions[0, pos]).item())
# #         predicted_tokens[pos] = predicted_token
    
# #     # Remove the special tokens [CLS] and [SEP]
# #     predicted_sentence = tokenizer.convert_tokens_to_string(predicted_tokens)
    
# #     # Clean up the sentence by removing any extra spaces or special tokens
# #     corrected_sentence = predicted_sentence.replace('[CLS] ', '').replace(' [SEP]', '').strip()
    
# #     return corrected_sentence

# # # Function to detect spelling and grammar errors
# # def correct_sentence(sentence, symspell):
# #     # Step 1: Use SymSpell for spelling correction
# #     corrected_words = []

# #     for word in sentence.split():
# #         suggestions = symspell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)
# #         print(f"Word: {word}, Suggestions: {[s.term for s in suggestions]}")  # Debug log

# #         if not suggestions:
# #             corrected_words.append(word)
# #             continue
        
# #         best_suggestion = suggestions[0].term
# #         if len(best_suggestion) > 2 and best_suggestion != word:
# #             corrected_words.append(best_suggestion)
# #         else:
# #             corrected_words.append(word)

# #     corrected_spelling = " ".join(corrected_words)

# #     # Step 2: Grammar correction using LanguageTool
# #     tool = language_tool_python.LanguageTool('en-US')
# #     matches = tool.check(corrected_spelling)
# #     corrected_grammar = corrected_spelling
# #     for match in matches:
# #         corrected_grammar = corrected_grammar.replace(
# #             match.context[match.offset:match.offset + match.errorLength], match.replacements[0]
# #         )

# #     # Step 3: Check if the corrected sentence makes sense in context using BERT-based correction
# #     final_sentence = correct_spelling_with_bert(corrected_grammar)

# #     return final_sentence

# # if __name__ == "__main__":
# #     symspell = initialize_symspell()

# #     # Input sentence
# #     sentence = "tody was a awesome day. What a great mrning"
# #     corrected = correct_sentence(sentence, symspell)

# #     # Output
# #     print("Original:", sentence)
# #     print("Corrected:", corrected)


# from transformers import GPT2LMHeadModel, GPT2Tokenizer

# # Load the GPT-2 model and tokenizer
# model = GPT2LMHeadModel.from_pretrained('gpt2')
# tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# def correct_sentence_with_gpt2(sentence):
#     # Tokenize the input sentence
#     input_ids = tokenizer.encode(sentence, return_tensors='pt')

#     # Generate corrected text
#     output = model.generate(input_ids, max_length=100, num_return_sequences=1, no_repeat_ngram_size=2, early_stopping=True)

#     # Decode the output to get the corrected sentence
#     corrected_sentence = tokenizer.decode(output[0], skip_special_tokens=True)
    
#     return corrected_sentence

# if __name__ == "__main__":
#     sentence = "tody was a awesome day. What a great mrning"
#     corrected = correct_sentence_with_gpt2(sentence)

#     # Output
#     print("Original:", sentence)
#     print("Corrected:", corrected)


# import re
# import tkinter as tk
# from tkinter.scrolledtext import ScrolledText
# import nltk
# from nltk.corpus import words

# nltk.download("words")

# class SpellingChecker:

#     def _init_(self):

#         self.root=tk.Tk()
#         self.root.geometry("600x500")
#         self.text=ScrolledText(self.root, font=("Arial", 14))
#         self.text.bind("<KeyRelease>", self.check)
#         self.text.pack()
#         self.old_spaces=0
#         self.root.mainloop()

#     def check(self, event):

#         content = self.text.get("1.0", tk.END)
#         space_count = content.count(" ")
#         if space_count != self.old_spaces:
#             self.old_spaces = space_count

#             for tag in self.text.tag_names():
#                 self.text.tag_delete(tag)

#             for word in content.split(" "):
#                 if re.sub(r"[^\w]", "", word.lower()) not in words.words():
#                     position = content.find(word)
#                     self.text.tag_add(word, f"1.{position}", f"1.{position + len (word)}")
#                     self.text.tag_config(word, foreground="red")

# SpellingChecker()





import re
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import nltk
from nltk.corpus import words

nltk.download("words")


class SpellingChecker:

    def __init__(self):
        self.word_list = set(words.words())  # Use a set for faster lookup
        self.root = tk.Tk()
        self.root.geometry("600x500")
        self.root.title("Spelling Checker")

        # Create a ScrolledText widget
        self.text = ScrolledText(self.root, font=("Arial", 14), wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True)

        # Bind key release to check spelling
        self.text.bind("<KeyRelease>", self.check)

        self.root.mainloop()

    def check(self, event=None):
        # Remove all previous tags
        for tag in self.text.tag_names():
            self.text.tag_delete(tag)

        # Get the content of the text widget
        content = self.text.get("1.0", tk.END).strip()

        # Split content into lines and words
        lines = content.split("\n")
        for line_idx, line in enumerate(lines):
            words_in_line = line.split(" ")
            char_idx = 0

            for word in words_in_line:
                # Clean the word to remove punctuation
                clean_word = re.sub(r"[^\w]", "", word).lower()
                if clean_word and clean_word not in self.word_list:
                    # Highlight misspelled words
                    start_idx = f"{line_idx + 1}.{char_idx}"
                    end_idx = f"{line_idx + 1}.{char_idx + len(word)}"
                    self.text.tag_add("misspelled", start_idx, end_idx)

                # Update character index for the next word
                char_idx += len(word) + 1  # +1 for the space

        # Configure the tag to show misspelled words in red
        self.text.tag_config("misspelled", foreground="red")


# Run the Spelling Checker
SpellingChecker()
