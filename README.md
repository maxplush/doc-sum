# docsum.py ![](https://github.com/maxplush/docsum-vim/workflows/tests/badge.svg)

`docsum.py` is a Python script that uses the Groq API to summarize the content of various file types. The script uses the fulltext package which allows for text to be extracted from various document formats. Then the script sends the extracted content to the Groq API and retrieves a summary in one paragraph in english, simplified to a fith-grade reading level. Input 
files that are not in english will still return an english summary. 

## Prerequisites

- Before running the script, make sure you have the packages listed in the requirements.txt file.
- A `.env` file in the same directory containing your  [Groq API KEY](https://groq.com). The file should have the following format:
  
  ```env
  GROQ_API_KEY=your_groq_api_key_here

## Usage

To use docsum.py, follow these steps:

1. Ensure your .env file is configured correctly with your Groq API key. Connect your .env by running the command.

```
$ export $(cat .env)
```

2. Prepare a file containing the content you want to summarize.

3. Run the script from the command line, passing the path to the text file as an argument:

- Example

    ```
    $ python3 docsum.py docs/declaration.txt

    A long time ago, the 13 colonies in America were ruled by a king from England. However, the people in the colonies were not happy with the way they were treated. The king was refusing to listen to their requests and was making very unfair laws. He even forced them to trade with other countries without their consent. The people decided that it was time to be free from the king's rule and create their own government. They wrote a Declaration of Independence, which is a big document that says they are breaking away from the king and becoming their own country. The document says that all people are created equal and have the right to life, liberty, and happiness. It also says that the people have the right to change their government if it's not working for them. The Declaration was signed by the representatives of the 13 colonies, and it's still an important document in American history today.
    ```
