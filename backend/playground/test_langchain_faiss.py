import pandas as pd
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

if __name__ == '__main__':
    search_text = 'the source of dark energy'
    index_path = r"C:\xxx\searchGPT\backend\src\.index"
    text_df = pd.read_csv(rf'C:\xxx\text_df.csv')
    text_df['docno'] = text_df.index.tolist()
    print(text_df.shape)
    print(text_df)
    texts, docno_list = text_df['text'].tolist(), text_df['docno'].tolist()
    docno_dict = [{'docno': docno} for docno in docno_list]
    embeddings = HuggingFaceEmbeddings()  # OpenAIEmbeddings() cost money (OPENAI_API_KEY)
    faiss_index = FAISS.from_texts(texts, embeddings, metadatas=docno_dict)

    # k: Number of Documents to return. Defaults to 4.
    # fetch_k: Number of Documents to fetch to pass to MMR algorithm.
    k, fetch_k = 10, 999
    # docs = faiss_index.max_marginal_relevance_search(search_text, k=k, fetch_k=fetch_k)
    docs = faiss_index.similarity_search_with_score(search_text, k=k)
    text_list, docno_list, score_list = [], [], []
    for t in docs:
        doc, score = t
        print(doc)
        text_list.append(doc.page_content)
        docno_list.append(doc.metadata['docno'])
        score_list.append(score)
    gpt_df = pd.DataFrame({'text': text_list, 'docno': docno_list, 'score': score_list})
    print("=====gpt_df====")
    print(gpt_df.shape)
    print(gpt_df)
