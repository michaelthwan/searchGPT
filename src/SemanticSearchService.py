import openai
import pandas as pd
import re
from openai.embeddings_utils import cosine_similarity
from website.sender import Sender, MSG_TYPE_SEARCH_STEP

from Util import setup_logger
from NLPUtil import num_tokens_from_string

# from abc import ABC, abstractmethod
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS
BASE_MODEL = "text-embedding-ada-002"  # default embedding of faiss-openai
logger = setup_logger('SemanticSearchService')


# class SemanticSearchService(ABC):
#     def __init__(self, config):
#         self.cwd = os.getcwd()
#         self.config = config
#         self.index = None
#         self.provider = ''
#
#     @abstractmethod
#     def index_text_df(self, text_df: pd.DataFrame, indexref_folder_name: str):
#         pass
#
#     @abstractmethod
#     def retrieve_result_by_search_text_from_text_df(self, search_text, text_df) -> pd.DataFrame:
#         pass
#
#     @staticmethod
#     def use_index_to_search(index, search_text):
#         pass
#
#     def clean_sentence_to_avoid_lexical_error(self, text):
#         """
#         Clean sentence. Pyterrier will throw error if the search query contains some special characters shown below
#             jnius.JavaException: JVM exception occurred: Failed to process qid 1 '
#             <search query>' -- Lexical error at line 3, column 90.  Encountered: "\'" (39), after : "" org.terrier.querying.parser.QueryParserException
#             python-BaseException
#         :return:
#         """
#         # TODO: good way to clean
#         return text.replace("'", "").replace("?", "").replace("!", "").replace(":", "").replace(";", "")
#
#
# class PyTerrierService(SemanticSearchService):
#     def __init__(self, config):
#         super().__init__(config)
#         self.provider = 'pyterrier'
#
#     def create_index_column_in_df(self, text_df: pd.DataFrame) -> pd.DataFrame:
#         """
#         add a docno column (primary key / index column) to the dataframe
#         :param text_df:
#         :return: text_df with docno column
#         """
#         text_df["docno"] = text_df.index + 1
#         text_df["docno"] = text_df["docno"].astype(str)
#         return text_df
#
#     def index_text_df(self, text_df: pd.DataFrame, indexref_folder_name: str):
#         """
#         index the text_df to get a indexref
#         :param text_df:
#             required columns:
#                 docno: as primary key for later process to retrieve back the row
#                 text: the text to be indexed
#         :return:
#             indexref:
#         """
#         import pyterrier as pt
#         if not pt.started():
#             pt.init()
#         datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
#         df_indexer_path = os.path.join(self.cwd, f".index/{indexref_folder_name}_" + datetime_str)
#         if not os.path.exists(df_indexer_path):
#             os.makedirs(df_indexer_path)
#
#         # TODO: using overwrite?
#         # Currently I cannot use overwrite=True to directly overwrite the existing index folder
#         #   when I index for the second time, it will throw error. Therefore need to create a new folder
#         #   I also cannot delete it in the last step, because the process is still running and consuming the index files inside.
#
#         # TODO: using a better wmodel than Tf?
#         pd_indexer = pt.DFIndexer(df_indexer_path, wmodel="Tf")
#         indexref = pd_indexer.index(text_df["text"], text_df["docno"])
#         return indexref
#
#     @staticmethod
#     def use_index_to_search(index, search_text):
#         result_df: pd.DataFrame = pt.BatchRetrieve(index).search(search_text)
#         return result_df
#
#     def retrieve_result_by_search_text_from_text_df(self, search_text, text_df):
#         logger.info(f"PyTerrierService.retrieve_result_by_search_text_from_text_df. search_text: {search_text}, text_df.shape: {text_df.shape}")
#         text_df = self.create_index_column_in_df(text_df)
#         index = self.index_text_df(text_df, 'df_index')
#         result_df: pd.DataFrame = self.use_index_to_search(index, search_text)
#         return result_df.merge(text_df, on="docno", how="left")
#
#
# class LangChainFAISSService(SemanticSearchService):
#     def __init__(self, config):
#         super().__init__(config)
#         self.provider = self.config.get('semantic_search').get('provider')
#         self.embeddings = None
#         if self.provider == 'faiss-openai':
#             self.embeddings = OpenAIEmbeddings(openai_api_key=self.config.get('llm_service').get('openai_api').get('api_key'))
#         elif self.provider == 'faiss-huggingface':
#             self.embeddings = HuggingFaceEmbeddings()
#         else:
#             raise Exception(f"provider {self.provider} is not supported")
#
#     def index_text_df(self, text_df: pd.DataFrame, indexref_folder_name: str):
#         logger.info(f"LangChainFAISSService.index_text_df. text_df.shape: {text_df.shape}")
#         text_df['docno'] = text_df.index.tolist()
#         texts, docno_list = text_df['text'].tolist(), text_df['docno'].tolist()
#         docno_dict = [{'docno': docno} for docno in docno_list]
#         faiss_index = FAISS.from_texts(texts, self.embeddings, metadatas=docno_dict)
#         return faiss_index
#
#     @staticmethod
#     def use_index_to_search(index, search_text):
#         index: FAISS
#         # k: Number of Documents to return. Defaults to 4.
#         # fetch_k: Number of Documents to fetch to pass to MMR algorithm.
#
#         # k = 15
#         # # Cons: you can only pick k, but you cannot filter by score
#         # tuples = index.similarity_search_with_score(search_text, k=k)
#         # docno_list = [t[0].metadata['docno'] for t in tuples]
#         # score_list = [t[1] for t in tuples]
#         # result_df = pd.DataFrame({'docno': docno_list, 'score': score_list})
#         # result_df['rank'] = result_df.index
#
#         k = 30
#         docs = index.max_marginal_relevance_search(search_text, k=k, fetch_k=999)
#         docno_list = [doc.metadata['docno'] for doc in docs]
#         result_df = pd.DataFrame({'docno': docno_list})
#         result_df['rank'] = result_df.index
#         result_df['score'] = 999
#
#         return result_df
#
#     def retrieve_result_by_search_text_from_text_df(self, search_text, text_df):
#         logger.info(f"LangChainFAISSService.retrieve_result_by_search_text_from_text_df. search_text: {search_text}, text_df.shape: {text_df.shape}")
#         faiss_index = self.index_text_df(text_df, '')
#         result_df = self.use_index_to_search(faiss_index, search_text)
#         return result_df.merge(text_df, on="docno", how="left")
#
#
# class SemanticSearchServiceFactory:
#     @staticmethod
#     def create_semantic_search_service(config) -> SemanticSearchService:
#         provider = config.get('semantic_search').get('provider')
#         if provider == 'pyterrier':
#             return PyTerrierService(config)
#         elif provider in ['faiss-openai', 'faiss-huggingface']:
#             return LangChainFAISSService(config)
#         else:
#             logger.error(f'SemanticSearchService for {provider} is not yet implemented.')
#             raise NotImplementedError(f'SemanticSearchService - {provider} - is not supported')


class BatchOpenAISemanticSearchService:
    def __init__(self, config, sender: Sender = None):
        self.config = config
        openai.api_key = config.get('llm_service').get('openai_api').get('api_key')
        self.sender = sender

    @staticmethod
    def batch_call_embeddings(texts, chunk_size=1000):
        texts = [text.replace("\n", " ") for text in texts]
        embeddings = []
        for i in range(0, len(texts), chunk_size):
            response = openai.Embedding.create(
                input=texts[i: i + chunk_size], engine=BASE_MODEL
            )
            embeddings += [r["embedding"] for r in response["data"]]
        return embeddings

    @staticmethod
    def compute_embeddings_for_text_df(text_df: pd.DataFrame):
        """Compute embeddings for a text_df and return the text_df with the embeddings column added."""
        print(f'compute_embeddings_for_text_df() len(texts): {len(text_df)}')
        text_df['text'] = text_df['text'].apply(lambda x: x.replace("\n", " "))
        text_df['embedding'] = BatchOpenAISemanticSearchService.batch_call_embeddings(text_df['text'].tolist())
        return text_df

    def search_related_source(self, text_df: pd.DataFrame, target_text, n=30):
        if not self.config.get('source_service').get('is_use_source'):
            col = ['name', 'url', 'url_id', 'snippet', 'text', 'similarities', 'rank', 'docno']
            return pd.DataFrame(columns=col)

        if self.sender is not None:
            self.sender.send_message(msg_type=MSG_TYPE_SEARCH_STEP, msg="Searching from extracted text")
        print(f'search_similar() text: {target_text}')
        embedding = BatchOpenAISemanticSearchService.batch_call_embeddings([target_text])[0]
        text_df = BatchOpenAISemanticSearchService.compute_embeddings_for_text_df(text_df)
        text_df['similarities'] = text_df['embedding'].apply(lambda x: cosine_similarity(x, embedding))
        result_df = text_df.sort_values('similarities', ascending=False).head(n)
        result_df['rank'] = range(1, len(result_df) + 1)
        result_df['docno'] = range(1, len(result_df) + 1)
        return result_df

    @staticmethod
    def post_process_gpt_input_text_df(gpt_input_text_df, prompt_token_limit):
        # clean out of prompt texts for existing [1], [2], [3]... in the source_text for response output stability
        gpt_input_text_df['text'] = gpt_input_text_df['text'].apply(lambda x: re.sub(r'\[[0-9]+\]', '', x))
        # length of char and token
        gpt_input_text_df['len_text'] = gpt_input_text_df['text'].apply(lambda x: len(x))
        gpt_input_text_df['len_token'] = gpt_input_text_df['text'].apply(lambda x: num_tokens_from_string(x))

        gpt_input_text_df['cumsum_len_text'] = gpt_input_text_df['len_text'].cumsum()
        gpt_input_text_df['cumsum_len_token'] = gpt_input_text_df['len_token'].cumsum()

        max_rank = gpt_input_text_df[gpt_input_text_df['cumsum_len_token'] <= prompt_token_limit]['rank'].max() + 1
        gpt_input_text_df['in_scope'] = gpt_input_text_df['rank'] <= max_rank  # In order to get also the row slightly larger than prompt_length_limit
        # reorder url_id with url that in scope.
        url_id_list = gpt_input_text_df['url_id'].unique()
        url_id_map = dict(zip(url_id_list, range(1, len(url_id_list) + 1)))
        gpt_input_text_df['url_id'] = gpt_input_text_df['url_id'].map(url_id_map)
        return gpt_input_text_df


