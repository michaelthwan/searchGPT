searchGPT - An Open-Source RAG-based LLM Search Engine
==================================================

**searchGPT** is an open-source project to build a search engine based on Large Language Model (LLM) technology to give natural language answers.

You may take this is a **minimal implementation of new Bing mainly for search engine and question answering**. 

It supports answers based on web search content or file content.

Please give me a star if you like it! 🌟

### **(Demo page link is available below!)**

![webui](/img/webui.png)
![explainability](/img/explainability.png)

Features
--------

* Source:
  * Web search with real-time results
  * File content search (PPT/DOC/PDF, etc.)
* Sematic search from source ([FAISS](https://github.com/facebookresearch/faiss) / [pyterrier](https://github.com/terrier-org/pyterrier))
* LLM integration: ([OpenAI](https://platform.openai.com/docs/api-reference?lang=python) / [GooseAI](https://goose.ai/), etc.)
* Frontend: Easy-to-use and intuitive user interface

Demo page
---------------
https://searchgpt-demo.herokuapp.com/index
- Please do not abuse it with any programs.
- Please be patient with the loading time, which usually takes ~10 seconds.

Architecture and roadmap
------------------------
![architecture_roadmap](/img/architecture_roadmap.png)

Why RAG?
---------------
Because it is impossible for the LLM to learn everything during the training, thus real-time factual information is needed for reference.

Example of ungrounded false answers (both using `text-curie-001` model):

**Prompt: what is ghost kitchen**

| Original answer                                                                                                                                                                                                           | RAG-based answer (SearchGPT)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| The Ghost Kitchen is a place where the departed spirits of cooks and dishwashers can cook and wash dishes with ease. The kitchen is said to be especially busy on Full Moon nights                                        | A ghost kitchen is a physical space for operators to create food for off-premises consumption. [1] This type of kitchen doesn't have waiters, no dining room, and no parking lot – really, no public presence whatsoever. [1] This kitchen is designed to cut unnecessary costs, allowing a restaurant to expand easily with low capital. [2] With apps like GrubHub and DoorDash, restaurant owners can easily find orders and exceed their expected revenue. [3]                                                                                                                                                                                                                                                |
| Ghost Kitchen is a pop-up restaurant in London that is completely without food. Instead, the restaurant is filled with spirits, who banish negative energy and help to make the guests' dining experience more enjoyable. | A ghost kitchen is a professional kitchen that is set up to cook food for delivery or take-out but does not have a dine-in option. [1] Ghost kitchens are often located in areas with high foot traffic and are used by multiple restaurants. [1] This allows restaurant chains to test new menu items without the investment of a brick-and-mortar location. [2] By having all of your orders in one place, a ghost kitchen can minimize the chances of errors and increase efficiency. [3] Additionally, by being located close to customers, a ghost kitchen can increase revenue. [4] While ghost kitchens are here to stay, they will likely face competition from other restaurants in the near future. [1] |

**Prompt: what is the meaning of wwww in Japanese**

| Original answer                                                                                                                                                                                                           | RAG-based answer (SearchGPT)                                                                                                                                                                                                                                                                                  |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Japanese "www" is typically used as a placeholder for "www." For example, "This is www." is typically translated to "Kore wa www.". Japanese "www" is also used to indicate that a webpage is not currently being viewed. | The meaning of "www" in Japanese is typically used to show amusement or to convey sarcasm. [1] It can also be used as a casual way to say "yes" or "okay." Additionally, speakers of Japanese may use "w" to represent the kana "笑" in online chat because it looks similar to the character for "laugh." [2] | 


Getting Started
---------------

### Prerequisites

To run `searchGPT`, you'll need:

* [Python 3.10.8](https://www.python.org/downloads/)
* [OpenAI API Key](https://beta.openai.com/signup) or [GooseAI API Key](https://goose.ai/)
    * OpenAI: First $18 is free (enough for 3000+ searches)
    * GooseAI: First $10 is free
* [Azure Bing Search Subscription Key](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api/)
    * Free version is available (3 searches per second, 1000 searches per month

### Installation

1. Create your python or anaconda env and install python packages

Native
```
# using python=3.10.8
pip install -r requirements.txt
```

Anaconda
```
conda create --name searchgpt python=3.10.8
conda activate searchgpt
pip install -r requirements.txt
```

2. Input API keys (OpenAI/Azure Bing Search) in `backend/src/config/config.yaml` (or via UI if web app is used)
3. Run `app.py`, (or `flask_app.py`) for frontend web app launching.
4. For quick testing, run `main.py`. Stdout output only.

Contributing
------------

We welcome contributions to **searchGPT**! (Especially frontend developers)

If you're interested in contributing, please take a look at our [contributing guidelines](./CONTRIBUTING.md) for more information.

License
-------

`searchGPT` is licensed under the [MIT License](./LICENSE).
