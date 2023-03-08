import os

import openai
import pandas as pd
import yaml
from openai.embeddings_utils import get_embedding, cosine_similarity

from Util import get_project_root

BASE_MODEL = "text-embedding-ada-002"  # default embedding of faiss-openai


def search_using_cosine_similarity(df, query):
    query_embedding = get_embedding(query, engine=BASE_MODEL)
    df["similarity"] = df['embeddings'].apply(lambda x: cosine_similarity(x, query_embedding))

    results = df.sort_values("similarity", ascending=False, ignore_index=True)

    k = 5
    results = results.head(k)
    global sources
    sources = []
    for i in range(k):
        sources.append({'Page ' + str(results.iloc[i]['page']): results.iloc[i]['text'][:150] + '...'})
    print(sources)
    return results.head(k)


def compute_embeddings(text, model="text-embedding-ada-002"):
    print(f'compute_embeddings() text: {text}')
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']


def search_similar(df: pd.DataFrame, target_text, n=3, pprint=True):
    print(f'search_similar() text: {target_text}')
    embedding = compute_embeddings(target_text, model=BASE_MODEL)
    df['similarities'] = df['embedding'].apply(lambda x: cosine_similarity(x, embedding))
    res = df.sort_values('similarities', ascending=False).head(n)
    return res, df


def compute_embeddings_2(text_df, model=BASE_MODEL, chunk_size=1000):
    print(f'compute_embeddings_2() len(texts): {len(df)}')
    text_df['text'] = text_df['text'].apply(lambda x: x.replace("\n", " "))
    embeddings = []
    for i in range(0, len(texts), chunk_size):
        response = openai.Embedding.create(
            input=texts[i: i + chunk_size], engine=model
        )
        embeddings += [r["embedding"] for r in response["data"]]
    text_df['embedding'] = embeddings
    return text_df


if __name__ == '__main__':
    # text_df = pd.read_csv(os.path.join(get_project_root(), 'src/text_df.csv'))
    texts = [
        "Discover the world of delicious beans with our premium selection.",
        "Try our savory bean soup recipe for a delicious and nutritious meal.",
        "Our roasted coffee beans are carefully selected for their rich and delicious flavor.",
        "Beans are not only delicious, but also a great source of protein and dietary fiber.",
        "Looking for a delicious vegan meal? Try our spicy black bean burger recipe.",

        "The sky is blue and the sun is shining today.",
        "I need to go grocery shopping after work to pick up some milk and bread.",
        "Did you hear about the new movie that just came out? It's supposed to be really good.",
        "I'm planning a trip to Europe next summer and I'm so excited.",
        "My cat keeps meowing at me for no reason and it's driving me crazy.",
    ]
    text_df = pd.DataFrame({'text': texts, 'docno': range(len(texts))})
    print(text_df.shape)

    with open(os.path.join(get_project_root(), 'src/config/config.yaml')) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        openai.api_key = config.get('openai_api').get('api_key')

        # text_df = compute_embeddings(text_df)
        # result_df = search_using_cosine_similarity(text_df, 'what is chatgpt?')
        # print(result_df)

        search_text = 'delicious beans'
        search_text = 'Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection Discover the world of delicious beans with our premium selection '

        from pyinstrument import Profiler

        profiler = Profiler()
        profiler.start()
        print("Sequential call mode:")
        text_df['embedding'] = text_df['text'].apply(lambda x: compute_embeddings(x, model=BASE_MODEL))
        res, text_df = search_similar(text_df, search_text, n=3)
        print(res)
        profiler.stop()
        profiler.print()

        profiler = Profiler()
        profiler.start()
        print("Batch call mode:")
        text_df = compute_embeddings_2(text_df)
        res, text_df = search_similar(text_df, search_text, n=3)
        print(res)
        profiler.stop()
        profiler.print()
