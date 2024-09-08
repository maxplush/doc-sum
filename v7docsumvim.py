import os
import argparse
import chardet
import fulltext
from groq import Groq

# Constants
TOKEN_LIMIT = 4000  # Groq API token limit
CHUNK_SIZE = 3500   # Chunk size to leave room for system and user messages
SUMMARY_PROMPT = 'Summarize the input text below and give me a summary of what it says on a 5th grade level'

# Load environment variables
# api_key = os.getenv('GROQ_API_KEY')

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

# Detect encoding using chardet
with open(args.filename, 'rb') as f:
    result = chardet.detect(f.read())
    charenc = result['encoding']

# Read the document text using the detected encoding
with open(args.filename, 'r', encoding=charenc) as f:
    text = f.read()

# Initialize the Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Function to chunk text into smaller parts
def chunk_text(text, chunk_size):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])

# Summarize each chunk
def summarize_chunk(chunk):
    chat_completion = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': SUMMARY_PROMPT},
            {'role': 'user', 'content': chunk},
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Break the text into chunks
chunks = list(chunk_text(text, CHUNK_SIZE))

# Summarize each chunk
chunk_summaries = []
for chunk in chunks:
    summary = summarize_chunk(chunk)
    chunk_summaries.append(summary)

# Combine chunk summaries into a single paragraph summary
final_summary_prompt = "Summarize the following summaries into a single paragraph:\n" + " ".join(chunk_summaries)
final_summary = summarize_chunk(final_summary_prompt)

# Print the final single-paragraph summary
print("\nFinal Summary:")
print(final_summary.strip())

