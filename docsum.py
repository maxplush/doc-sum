import argparse
import chardet
import os
import fulltext
from groq import Groq  # Assuming you have a Groq client library
import PyPDF2  # For PDF extraction


# Collaborated with Alex
# Function to detect encoding using chardet
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

# Function to read the file with detected encoding
def read_file_with_encoding(file_path):
    encoding = detect_encoding(file_path)
    if encoding is None:
        raise ValueError("Could not detect file encoding.")
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()

# Function to extract text from PDF using PyPDF2
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text.strip() if text else None
    except Exception as e:
        print(f"PyPDF2 failed to extract text from PDF: {e}")
        return None

# Function to extract text from the file using fulltext and fallback to PyPDF2 and chardet
def extract_text(file_path):
    # Try using fulltext to extract text
    try:
        return fulltext.get(file_path)
    except Exception as e:
        print(f"fulltext failed: {e}")

    # If it's a PDF, try extracting the text using PyPDF2
    if file_path.endswith('.pdf'):
        print("Attempting to extract text using PyPDF2...")
        pdf_text = extract_text_from_pdf(file_path)
        if pdf_text:
            return pdf_text

    # Fallback to using chardet to detect encoding and read the file
    print("Attempting to detect encoding with chardet...")
    try:
        return read_file_with_encoding(file_path)
    except Exception as e:
        print(f"Failed to read the file even after detecting encoding: {e}")
        exit(1)

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

# Read the document text using fulltext or fallback to PyPDF2 and chardet
text = extract_text(args.filename)

if not text:
    print("No text could be extracted from the document.")
    exit(1)

# Initialize the Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Define CHUNK_SIZE for splitting the text
CHUNK_SIZE = 3000  # You can adjust this value based on your needs

# Define the summary prompt
SUMMARY_PROMPT = "Please summarize this text."

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
