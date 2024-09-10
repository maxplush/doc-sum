"""
docsum - A script for summarizing documents using the Groq API.

This module provides functions to import documents, split them into manageable chunks, and summarize
them using the Groq API. It is designed to handle various file types including plain text, HTML,
and PDFs in multiple utf encodings. It processes large documents by splitting them into smaller
chunks to comply with API constraints and context window limitations.

Functions:
- import_doc(filename: str) -> str
    Imports a document and converts it to plain text. Supports plain text and HTML files, with
    automatic encoding detection.

- split_document_into_chunks(text: str, max_chunk_size: int=4000) -> list[str]
    Splits the input text into chunks of specified maximum size to ensure compatibility with the
    Groq API's token and context window limits.

- groq_query(input_text: str, client, delay: int=5) -> groq.ChatCompletion
    Queries the Groq API to summarize the input text. Handles common API errors by retrying or
    splitting the text into smaller chunks as needed.

Usage:
    $ python docsum.py <filename>
    
    The script expects a file path as a command-line argument, imports the text from the file, and
    outputs a summarized version using the Groq API.

>>> with open('sample.txt', 'w', encoding='utf-8') as f:
...     f.write('This is a sample document.')
26
>>> import_doc('sample.txt')
'This is a sample document.'

$ split_document_into_chunks('This is a long document.' * 1000, max_chunk_size=500)
['This is a long document.' * 500, ...]

$ groq_query('This is a long document.', groq_client)
<groq.ChatCompletion object>

$  python3 docsum.py docs/declaration.txt
A long time ago, a group of countries called the United States of America decided to break away from
another country called Great Britain. They wrote a special paper called the Declaration of
Independence to explain why they wanted to be free. They said that all people are equal and have the
right to be happy and live free. They also said that the king of Great Britain had been very mean to
them and didn't listen to their problems. So, they decided to make their own country and take care
of themselves. The people who wrote this paper promised to work together and protect each other to
make their new country strong.
"""

import os
import argparse
import re
import time
import fulltext
import groq
from bs4 import BeautifulSoup
import chardet

def import_doc(filename):
    r"""
    Import a file a convert it to plain text.
    
    Arguments:
        filename (str): Path to the file.
    
    Returns:
        text (str): The plain text of the file.

    >>> with open('sample.txt', 'w', encoding='utf-8') as f:
    ...     f.write('This is a plain text file.')
    26
    >>> import_doc('sample.txt')
    'This is a plain text file.'
    
    >>> with open('sample.html', 'w', encoding='utf-8') as f:
    ...     f.write('<html><body><p>This is an HTML file.</p></body></html>')
    54
    >>> import_doc('sample.html')
    'This is an HTML file.'
    
    >>> import_doc('nonexistent_file.txt')
    Traceback (most recent call last):
    ...
    FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent_file.txt'
    """
    # Get the full text from the document
    with open(filename, 'rb') as f: # Open the file for read in binary mode
        # Use chardet library to find encoding
        result = chardet.detect(f.read())
        utf = result['encoding']

        # print(f"DEBUG: encoding: {utf}")

    if filename.endswith('.html'):
        # print("DEBUG: html file, using BeautifulSoup")

        with open(filename, 'r', encoding=utf) as f:
            soup = BeautifulSoup(f, 'html.parser')
            text = soup.get_text()
    else:
        try:
            # print("DEBUG: Trying open()")

            with open(filename, 'r', encoding=utf) as f:
                text = f.read()

        except UnicodeDecodeError:
            # print(f"DEBUG: open() didn't work, trying fulltext")

            text = fulltext.get(filename)

    # print(f"DEBUG: length of text: {len(text)}")

    return text

def split_document_into_chunks(text, max_chunk_size=4000):
    r"""
    Split the input text into a list of smaller chunks of text so that an LLM
    can process the chunks individually.

    Arguments:
        text (str): The original document to split up.
        max_chunk_size (int): The number of words in a chunk.
    
    Returns:
        chunks (list): The document as a series of strings in a list.

    >>> split_document_into_chunks('This is a paragraph.')
    ['This is a paragraph.']

    >>> split_document_into_chunks('This is a paragraph.\n\nThis is another paragraph.')
    ['This is a paragraph.\n\nThis is another paragraph.']

    >>> split_document_into_chunks('This is a paragraph.\n\nThis is another paragraph.\n\nThis is yet another paragraph.')
    ['This is a paragraph.\n\nThis is another paragraph.\n\nThis is yet another paragraph.']

    >>> doc = split_document_into_chunks('This is a paragraph.\n\nThis is another paragraph.\n\nThis is yet another paragraph.\n\nThis is too long to fit in one chunk.' * 1000, max_chunk_size=500)
    >>> len(doc[0])
    496
    >>> len(doc)
    250

    >>> split_document_into_chunks('')
    []

    >>> split_document_into_chunks('This is a paragraph.\n\n', max_chunk_size=10)
    ['This is a paragraph.']

    >>> split_document_into_chunks('Short text', max_chunk_size=10)
    ['Short text']
    """
    # Return empty list if the input text is empty
    if not text:
        return []

    # Split the document by two or more newlines
    paragraphs = re.split(r'\n{2,}', text)
    # print(f"DEBUG: paragraphs: {paragraphs}")

    # Remove leading/trailing newlines and spaces from each paragraph
    cleaned_paragraphs = [para.strip() for para in paragraphs if para.strip()]
    # print(f"DEBUG: cleaned_paragraphs: {cleaned_paragraphs}")

    chunks = []
    # print(f"DEBUG: chunks: {chunks}")
    current_chunk = ""
    # print(f"DEBUG: current_chunk: {current_chunk}")

    for para in cleaned_paragraphs:
        # print(f"DEBUG: para: {para}")
        if len(current_chunk) + len(para) + 2 > max_chunk_size:
            # If too long, add the current chunk to the list and move on
            # +2 for potential newlines
            # print("DEBUG: too long")
            if current_chunk:
                # Don't add an empty string
                chunks.append(current_chunk.strip())
            # print(f"DEBUG: chunks: {chunks}")
            current_chunk = para
        else:
            # print("DEBUG: keep adding")
            # Otherwise, keep adding to the current chunk
            if current_chunk:
                current_chunk += "\n\n"  # Add a separator between paragraphs
                # print(f"DEBUG: current_chunk: {current_chunk}")
            current_chunk += para
            # print(f"DEBUG: current_chunk: {current_chunk}")

    # If anything got added to the current chunk string
    if current_chunk:
        # print(f"DEBUG: current_chunk exists: {current_chunk}")
        # Add it to the chunks list
        chunks.append(current_chunk.strip())
        # print(f"DEBUG: chunks: {chunks}")

    # Return the document as the series of chunks
    return chunks

def groq_query(input_text, client, delay=5):
    """
    Wrapper for the Groq API query that handles common errors like a query
    maxing out the rate limit, a query being too long individually, or the
    Groq API being unstable. Recursively calls itself until it gets back a
    response.
    
    Arguments:
        input_text (str): Text to be submitted as query. Might be too long.
        client (Groq API client)
        delay (int): Seconds to wait before retrying API call.
    
    Returns:
        final_chat (groq.ChatCompletion): The chat completion object from the
            Groq API that does finally summarize the document in its entirety.
    """
    try:
        final_chat = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Summarize the input text below. " \
                            "Limit the summary to 1 paragraph and use a 1st grade reading level.",
                },
                {
                    "role": "user",
                    "content": input_text,
                }
            ],
            model="llama3-8b-8192",
        )

    except groq.InternalServerError:
        # Situations where the probably is just the Groq API being unstable
        # print("DEBUG: Groq broke, try again")
        # The solution is just to wait and try again
        time.sleep(delay)
        final_chat = groq_query(input_text, client)

    except (groq.RateLimitError, groq.BadRequestError) as e:
        # Situations where either
        #   The individual query itself is too long (BadRequestError)
        #   The individual query itself (and possibly the previous queries
        #       from the last minute) are cumulatively too long
        #       (RateLimitError, 'Tokens Per Minute (TMP)')
        #   There have been too many queries in the past minute
        #       (RateLimitError, 'Requests Per Minute (RMP)')
        # In the first two situations, the solution is to break up the current
        #   query into smaller chunks and recursively query the API again.
        # In the last situation, the solution is to wait and query the API
        #   again.

        error_message = str(e)

        if 'RMP' in error_message:
            # Situations where the there have been too many queries in the
            # past minute
            # print(f"DEBUG: Too many queries, waiting {delay} seconds")
            time.sleep(delay)
            final_chat = groq_query(input_text, client)

        else:
            # Split the document into chunks
            chunked_text = split_document_into_chunks(input_text)
            # print(f"DEBUG: number of chunks: {len(chunked_text)}")

            # Initialize an empty list for storing individual summaries
            summarized_chunks = []

            # Summarize each paragraph
            for chunk in chunked_text:
                # print(f"DEBUG: chunk {i}")
                # print(f"DEBUG: length of chunk: {len(chunk)}")
                # print(f"DEBUG: chunk: {chunk}")

                # Get the query object (this function only returns the object)
                chunk_chat = groq_query(chunk, client)

                # Get the message text from the query object
                chunk_txt = chunk_chat.choices[0].message.content

                # print(f"DEBUG: internal response: {chunk_txt}")

                # Add it to the summaries list
                summarized_chunks.append(chunk_txt)

            # Concatenate all summarized paragraphs into a smaller document
            summarized_document = " ".join(summarized_chunks)

            # print(f"DEBUG: len big summary: {len(summarized_document)}")
            # print(f"DEBUG: summarized_document: {summarized_document}")
            # Submit the concatenated summary for summary itself

            final_chat = groq_query(summarized_document, client)

    # Return the API chat object for the summary of the full text
    return final_chat

if __name__ == '__main__':
    # Initialize the Groq API client
    groq_api = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Get the file path to the doc to summarize from the command line call
    parser = argparse.ArgumentParser(description='Summarizes a document with groq.')
    parser.add_argument('filename', help='Provide the path to a document to summarize.')
    args = parser.parse_args()

    # print(f"DEBUG: summarizing {args.filename}")

    # Import plain text from document regardless of file type
    file_text = import_doc(args.filename)

    # Get the summary chat API object from Groq API and select the message
    summary_chat = groq_query(file_text, groq_api)
    summary_txt = summary_chat.choices[0].message.content

    # Output summary
    # print("DEBUG: final response:")
    print(summary_txt)
