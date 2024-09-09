import time
import os
import argparse
import chardet
import fulltext
from groq import Groq
from groq import InternalServerError, BadRequestError

# Constants
TOKEN_LIMIT = 4000  # Groq API token limit
CHUNK_SIZE = 3500   # Chunk size to leave room for system and user messages
SUMMARY_PROMPT = 'Summarize the input text below and give me a summary of what it says on a 5th grade level'
RETRY_LIMIT = 3     # Number of retry attempts
RETRY_DELAY = 5     # Delay between retries in seconds
FINAL_SUMMARY_CHUNK_SIZE = 2000  # Final summary chunk size

# Load environment variables and filename
parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

# Function to detect file encoding and read text
def detect_encoding_and_read(filename):
    with open(filename, 'rb') as f:
        result = chardet.detect(f.read())
        charenc = result['encoding']
    with open(filename, 'r', encoding=charenc) as f:
        return f.read()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Function to chunk text into smaller parts
def chunk_text(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Function to summarize each chunk with retry logic
def summarize_chunk(chunk):
    attempts = 0
    while attempts < RETRY_LIMIT:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {'role': 'system', 'content': SUMMARY_PROMPT},
                    {'role': 'user', 'content': chunk},
                ],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
        except (InternalServerError, BadRequestError) as e:
            attempts += 1
            print(f"Attempt {attempts} failed with error: {e}. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    raise Exception("Failed to get a response from the Groq API after multiple attempts.")

# Function to summarize final summary chunks
def summarize_final_chunks(summaries):
    final_summaries = []
    summary_text = " ".join(summaries)
    chunks = chunk_text(summary_text, FINAL_SUMMARY_CHUNK_SIZE)
    
    for chunk in chunks:
        final_summaries.append(summarize_chunk(chunk))
    
    return " ".join(final_summaries)

# Main processing function
def process_file(filename):
    text = detect_encoding_and_read(filename)
    chunks = chunk_text(text, CHUNK_SIZE)
    
    chunk_summaries = []
    for chunk in chunks:
        print(f"Processing chunk: {chunk[:50]}...")  # Debugging step to print first 50 characters of the chunk
        summary = summarize_chunk(chunk)
        chunk_summaries.append(summary)
    
    final_summary = summarize_final_chunks(chunk_summaries)
    
    print("\nFinal Summary:")
    print(final_summary.strip())

# Run the script
if __name__ == "__main__":
    process_file(args.filename)

