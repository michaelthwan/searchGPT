import os
from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd
import pyterrier as pt
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

from Util import setup_logger

logger = setup_logger('PyTerrierService')


class SemanticSearchService(ABC):
    def __init__(self):
        self.cwd = os.getcwd()
        self.index = None
        self.provider = ''

    @abstractmethod
    def index_text_df(self, text_df: pd.DataFrame, indexref_folder_name: str):
        pass

    @abstractmethod
    def retrieve_result_by_search_text_from_text_df(self, search_text, text_df) -> pd.DataFrame:
        pass

    @staticmethod
    def use_index_to_search(index, search_text):
        pass

    def clean_sentence_to_avoid_lexical_error(self, text):
        """
        Clean sentence. Pyterrier will throw error if the search query contains some special characters shown below
            jnius.JavaException: JVM exception occurred: Failed to process qid 1 '
            <search query>' -- Lexical error at line 3, column 90.  Encountered: "\'" (39), after : "" org.terrier.querying.parser.QueryParserException
            python-BaseException
        :return:
        """
        # TODO: good way to clean
        return text.replace("'", "").replace("?", "").replace("!", "").replace(":", "").replace(";", "")


class PyTerrierService(SemanticSearchService):
    def __init__(self):
        super().__init__()
        self.provider = 'pyterrier'

    def create_index_column_in_df(self, text_df: pd.DataFrame) -> pd.DataFrame:
        """
        add a docno column (primary key / index column) to the dataframe
        :param text_df:
        :return: text_df with docno column
        """
        text_df["docno"] = text_df.index + 1
        text_df["docno"] = text_df["docno"].astype(str)
        return text_df

    def index_text_df(self, text_df: pd.DataFrame, indexref_folder_name: str) -> pt.IndexRef:
        """
        index the text_df to get a indexref
        :param text_df:
            required columns:
                docno: as primary key for later process to retrieve back the row
                text: the text to be indexed
        :return:
            indexref:
        """
        if not pt.started():
            pt.init()
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        df_indexer_path = os.path.join(self.cwd, f".index/{indexref_folder_name}_" + datetime_str)
        if not os.path.exists(df_indexer_path):
            os.makedirs(df_indexer_path)

        # TODO: using overwrite?
        # Currently I cannot use overwrite=True to directly overwrite the existing index folder
        #   when I index for the second time, it will throw error. Therefore need to create a new folder
        #   I also cannot delete it in the last step, because the process is still running and consuming the index files inside.

        # TODO: using a better wmodel than Tf?
        pd_indexer = pt.DFIndexer(df_indexer_path, wmodel="Tf")
        indexref = pd_indexer.index(text_df["text"], text_df["docno"])
        return indexref

    @staticmethod
    def use_index_to_search(index, search_text):
        result_df: pd.DataFrame = pt.BatchRetrieve(index).search(search_text)
        return result_df

    def retrieve_result_by_search_text_from_text_df(self, search_text, text_df):
        logger.info(f"PyTerrierService.retrieve_result_by_search_text_from_text_df. search_text: {search_text}, text_df.shape: {text_df.shape}")
        text_df = self.create_index_column_in_df(text_df)
        index = self.index_text_df(text_df, 'df_index')
        result_df: pd.DataFrame = self.use_index_to_search(index, search_text)
        return result_df.merge(text_df, on="docno", how="left")


class LangChainFAISSService(SemanticSearchService):
    def __init__(self):
        super().__init__()
        self.provider = 'faiss'

    def index_text_df(self, text_df: pd.DataFrame, indexref_folder_name: str):
        text_df['docno'] = text_df.index.tolist()
        texts, docno_list = text_df['text'].tolist(), text_df['docno'].tolist()
        docno_dict = [{'docno': docno} for docno in docno_list]
        embeddings = HuggingFaceEmbeddings()  # OpenAIEmbeddings() cost money (OPENAI_API_KEY)
        faiss_index = FAISS.from_texts(texts, embeddings, metadatas=docno_dict)
        return faiss_index

    @staticmethod
    def use_index_to_search(index, search_text):
        index: FAISS
        # k: Number of Documents to return. Defaults to 4.
        # fetch_k: Number of Documents to fetch to pass to MMR algorithm.

        # k = 15
        # # Cons: you can only pick k, but you cannot filter by score
        # tuples = index.similarity_search_with_score(search_text, k=k)
        # docno_list = [t[0].metadata['docno'] for t in tuples]
        # score_list = [t[1] for t in tuples]
        # result_df = pd.DataFrame({'docno': docno_list, 'score': score_list})
        # result_df['rank'] = result_df.index

        k = 10
        docs = index.max_marginal_relevance_search(search_text, k=k, fetch_k=999)
        docno_list = [doc.metadata['docno'] for doc in docs]
        result_df = pd.DataFrame({'docno': docno_list})
        result_df['rank'] = result_df.index
        result_df['score'] = 999

        return result_df

    def retrieve_result_by_search_text_from_text_df(self, search_text, text_df):
        logger.info(f"LangChainFAISSService.retrieve_result_by_search_text_from_text_df. search_text: {search_text}, text_df.shape: {text_df.shape}")
        faiss_index = self.index_text_df(text_df, '')
        result_df = self.use_index_to_search(faiss_index, search_text)
        return result_df.merge(text_df, on="docno", how="left")


class SemanticSearchServiceFactory:
    @staticmethod
    def create_semantic_search_service(config) -> SemanticSearchService:
        provider = config.get('semantic_search').get('provider')
        if provider == 'pyterrier':
            return PyTerrierService()
        elif provider == 'faiss':
            return LangChainFAISSService()
        else:
            logger.error(f'SemanticSearchService for {provider} is not yet implemented.')
            raise NotImplementedError(f'SemanticSearchService - {provider} - is not supported')


if __name__ == '__main__':
    pyterrier_service = PyTerrierService()
    search_text = ""
    # print(pyterrier_service.text_retrieve_in_files(search_text))
