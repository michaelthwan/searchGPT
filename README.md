searchGPT - An Open-Source LLM-based Search Engine
==================================================

**searchGPT** is an open-source project to build a search engine based on Large Language Model (LLM) technology. 

It leverages the power of OpenAI's ChatGPT and its API to provide fast and accurate search results for web searches, file content searches, and more.

You may imagine that it is New Bing that supports file content search.

Features
--------

*   Web search with real-time results
*   File content search
*   Accurate results powered by OpenAI's ChatGPT technology
*   Easy-to-use and intuitive user interface

Getting Started
---------------

### Prerequisites

To run `searchGPT`, you'll need:

* [Python 3.10.8](https://www.python.org/downloads/)
* [OpenAI API Key](https://beta.openai.com/signup)
* [Java >= 11](https://www.oracle.com/tw/java/technologies/downloads/#jdk19-windows)

### Installation (users)


### Installation (developer, backend)

1. Create your conda env and install python packages
```
conda create --name searchgpt python=3.10.8
conda activate searchgpt
pip install -r requirements.txt
```
2. Install JAVA >= 11

Related linkes
- https://www.oracle.com/tw/java/technologies/downloads/#jdk19-windows
- https://download.oracle.com/java/19/latest/jdk-19_windows-x64_bin.exe

Then set your JAVA_HOME environment variable

`JAVA_HOME="C:\Program Files\Java\jdk-19"`

3. Download Punkt Sentence Tokenizer data for nltk, a NLP toolkit used in the footnote service, via its data downloader.

In Python, import nltk and run the following command:
```
import nltk
nltk.download('punkt')
```

4. Input API keys (OpenAI/Azure Bing Search) in `backend/src/config/config.yaml`
5. Run `main.py`

### Installation (developer, frontend)

Contributing
------------

We welcome contributions to **searchGPT**! 

If you're interested in contributing, please take a look at our [contributing guidelines](./CONTRIBUTING.md) for more information.

License
-------

`searchGPT` is licensed under the [MIT License](./LICENSE).

Acknowledgments
---------------

`searchGPT` wouldn't be possible without the support of the OpenAI community and the amazing technology provided by OpenAI.