import os
import argparse
from groq import Groq
import fulltext
import time

# Parse command line args
parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Function to extract text with retries
def extract_text_with_retries(filename, retries=2, delay=3):
    text = None
    for attempt in range(retries):
        text = fulltext.get(filename)
        if text:
            break
        else:
            print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
            time.sleep(delay)
    return text

# Function to chunk text into token-sized pieces
def chunk_text(text, chunk_size=3500):  # Adjust chunk_size based on model token limit
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield ' '.join(words[i:i + chunk_size])

# Function to estimate tokens from text
def estimate_tokens(text):
    return len(text) // 4  # Rough estimate: 1 token ≈ 4 characters

# Use fulltext to extract content from the file with retries
text = extract_text_with_retries(args.filename)

if not text:
    raise ValueError("Unsupported file type or unable to extract text after multiple attempts")

# Chunk the text and summarize each chunk
summaries = []
chunk_size = 3500  # Start with an estimated safe chunk size
for chunk_index, chunk in enumerate(chunk_text(text, chunk_size)):
    print(f"Processing chunk {chunk_index + 1}")
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Summarize the text below. Limit it to 1 paragraph, at a first-grade reading level.",
                },
                {
                    "role": "user",
                    "content": chunk,
                }
            ],
            model="llama3-8b-8192",
        )
        summary = chat_completion.choices[0].message.content
        print(f"Summary for chunk {chunk_index + 1}: {summary}")
        summaries.append(summary)
    except groq.RateLimitError as e:
        print(f"Rate limit error: {e}. Waiting to retry...")
        time.sleep(120)  # Wait 2 minutes before retrying
        continue

final_summary = " ".join(summaries)
print(final_summary)


