import os
from datetime import datetime

import pandas as pd
import pyterrier as pt

from Util import setup_logger

logger = setup_logger('PyTerrierService')


class PyTerrierService:
    def __init__(self):
        self.cwd = os.getcwd()

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
        df_indexer_path = os.path.join(self.cwd, f"var/{indexref_folder_name}_" + datetime_str)
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

    def retrieve_search_query_in_dfindexer(self, search_text, text_df):
        logger.info(f"PyTerrierService.retrieve_search_query_in_dfindexer. search_text: {search_text}, text_df.shape: {text_df.shape}")
        text_df = self.create_index_column_in_df(text_df)
        indexref = self.index_text_df(text_df, 'df_index')
        result_df: pd.DataFrame = pt.BatchRetrieve(indexref).search(search_text)
        return result_df.merge(text_df, on="docno", how="left")


if __name__ == '__main__':
    pyterrier_service = PyTerrierService()
    search_text = ""
    # print(pyterrier_service.text_retrieve_in_files(search_text))
