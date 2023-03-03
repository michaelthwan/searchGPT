searchGPT - An Open-Source LLM-based Grounded Search Engine
==================================================

**searchGPT** is an open-source project to build a search engine based on Large Language Model (LLM) technology to give natural language answers.

This is a minimal implementation with modular plugin design, meaning you can choose different tech for different components.

You may imagine that it is like ChatGPT but supports file content search and latest web search.

Features
--------

* Source: Web search with real-time results
* Source: File content search (PPT/DOC/PDF, etc.)
* Sematic search from source ([FAISS](https://github.com/facebookresearch/faiss) / [pyterrier](https://github.com/terrier-org/pyterrier))
* LLM integration: ([OpenAI](https://platform.openai.com/docs/api-reference?lang=python) / [GooseAI](https://goose.ai/), etc.)
* Frontend: Easy-to-use and intuitive user interface

Architecture and roadmap
------------------------
![architecture_roadmap](/img/architecture_roadmap.png)

Why Grounded?
---------------
TODO

Demo page
---------------
Coming soon...

Getting Started
---------------

### Prerequisites

To run `searchGPT`, you'll need:

* [Python 3.10.8](https://www.python.org/downloads/)
* [OpenAI API Key](https://beta.openai.com/signup) or [GooseAI API Key](https://goose.ai/)
    * OpenAI: First $18 is free
    * GooseAI: First $10 is free
* [Azure Bing Search API Key](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api/)
    * Free version is available

### Installation

1. Create your conda env and install python packages

```
conda create --name searchgpt python=3.10.8
conda activate searchgpt
pip install -r requirements.txt
```

2. Input API keys (OpenAI/Azure Bing Search) in `backend/src/config/config.yaml`
3. Run `flask_app.py` for frontend web app launching. `main.py` for stdout output.
4. (optional, if you use pyterrier) Install JAVA >= 11
    * Related linkes
        - https://www.oracle.com/tw/java/technologies/downloads/#jdk19-windows
        - https://download.oracle.com/java/19/latest/jdk-19_windows-x64_bin.exe
    - Then set your JAVA_HOME environment variable
        - `JAVA_HOME="C:\Program Files\Java\jdk-19"`

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