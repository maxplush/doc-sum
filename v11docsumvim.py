def split_document_into_chunks(text, chunk_size=5000):
    """
    Split text into smaller chunks so an LLM can process those chunks individually.

    Args:
        text (str): The input text to split into chunks.
        chunk_size (int): The maximum size of each chunk in terms of characters.

    Returns:
        List[str]: A list of text chunks.
    """
    # Split the text by paragraphs (assuming paragraphs are separated by double newlines)
    #paragraphs = text.split('\n\n')

    # Further split paragraphs into smaller chunks if they exceed the chunk size
    #chunks = []
    #for paragraph in text:
    #    start = 0
    #    while start < len(paragraph):
    #        chunks.append(paragraph[start:start + chunk_size].strip())
    #        start += chunk_size

    #return chunks
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

import os
from groq import Groq
#from dotenv import load_dotenv
import argparse
import fulltext
import chardet
#filename = 'docs/declaration'
#with open(args.filename) as f:
#    text = f.read()
# Load environment variables from .env file
# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

# Use fulltext to extract text from the file
try:
    # Try using fulltext to extract text from the file
    text = fulltext.get(args.filename)
except (UnicodeDecodeError, Exception) as e:
    print(f"fulltext failed: {e}")
    print("Attempting to detect encoding with chardet...")

    # Fallback to using chardet to detect encoding and read the file
    try:
        with open(args.filename, 'rb') as f:
            result = chardet.detect(f.read())
            charenc = result['encoding']
            print(f"Detected encoding: {charenc}")

            # Read the file with the detected encoding
            with open(args.filename, 'r', encoding=charenc) as f:
                text = f.read()
    except Exception as e:
        print(f"Failed to read the file even after detecting encoding: {e}")
        exit(1)

#print(os.environ.get("GROQ_API_KEY"))
# Initialize Groq client with API key
client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)


# Split the document into smaller chunks
chunks = split_document_into_chunks(text)

# Initialize an empty list to hold individual summaries
summaries = []

# Iterate over each chunk and generate a summary for each
for chunk in chunks:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "summarize input text below. limit summary to 1 sentence and use a 1st grade reading level",
            },
            {
                "role": "user",
                "content": chunk,
            }
        ],
        model="llama3-8b-8192",
    )
    
    # Append the generated summary to the list
    summaries.append(chat_completion.choices[0].message.content)

# Join all summaries into one final summary
# Join all summaries into one final summary
final_summary = f"This is a summary of the file '{args.filename}': " + " ".join(summaries)
print(final_summary)
