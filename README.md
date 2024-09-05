# docsum.py ![](https://github.com/maxplush/docsum-vim/workflows/tests/badge.svg)

`docsum.py` is a Python script that uses the Groq API to summarize the content of various file types. The script uses the fulltext package which allwos for text to be extracted from various document formats. Then the script sends the extracted content to the Groq API and retrieves a summary in one paragraph in english, simplified to a first-grade reading level. Input 
files that are not in english will still return a english summary. 

## Prerequisites

- Before running the script, make sure you have the packages listed in the requirements.txt file.
- A `.env` file in the same directory containing your Groq API key. The file should have the following format:
  
  ```env
  GROQ_API_KEY=your_groq_api_key_here

## Usage

To use docsum.py, follow these steps:

1. Ensure your .env file is configured correctly with your Groq API key.

2. Prepare a file containing the content you want to summarize.

3. Run the script from the command line, passing the path to the text file as an argument:

- Example

    ```
    python3 docsum.py docs/declaration.txt
    
