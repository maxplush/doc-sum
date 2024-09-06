import os
import argparse
from groq import Groq
import fulltext
import time

# next steps are try and add all of the docs files bac into this folder
# add the .github/workspaces/test.yml to this and see if this code works?

# for the terminal side code - do that chatgpt steps?

# next step is chunking

# Parse command line args
parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

file_ext = os.path.splitext(args.filename)[1].lower()
# print(f"args.filename={args.filename}")

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

# Use fulltext to extract content from the file with retries
text = extract_text_with_retries(args.filename)

# print(text)

if not text:
    raise ValueError("Unsupported file type or unable to extract text after multiple attempts")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Summarize the text below. Limit it to 1 paragraph, at a first grade reading level.",
        },
        {
            "role": "user",
            "content": text,
        }
    ],
    model="llama3-8b-8192",
)

print(chat_completion.choices[0].message.content)


# is able to print the text extracted but 
