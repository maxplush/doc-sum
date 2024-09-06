import os
import argparse
from groq import Groq
import fulltext
import time

# Parse command line args
parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

file_ext = os.path.splitext(args.filename)[1].lower()

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

# Function to chunk text
def chunk_text(text, chunk_size):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

# Extract text from the file
text = extract_text_with_retries(args.filename)

if not text:
    raise ValueError("Unsupported file type or unable to extract text after multiple attempts")

# Define chunk size based on token limit
chunk_size = 3500  # Adjust if necessary

summaries = []
chunks = chunk_text(text, chunk_size)

for chunk_index, chunk in enumerate(chunks):
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

