import pyterrier as pt
from datetime import datetime
import pandas as pd
import os


class PyTerrierService:
    def __init__(self):
        self.cwd = os.getcwd()

    # def text_retrieve_in_files(self, search_text, files_path="var/files", is_index=True):
    #     if not pt.started():
    #         pt.init()
    #     files = pt.io.find_files(os.path.join(self.cwd, files_path))
    #     file_index_path = os.path.join(self.cwd, "var/file_index")
    #     if is_index:
    #         if not os.path.exists(file_index_path):
    #             os.makedirs(file_index_path)
    #         indexref_file = pt.FilesIndexer(file_index_path, overwrite=True).index(files)
    #     else:
    #         indexref_file = pt.IndexFactory.of(os.path.join(file_index_path, "data.properties"))
    #     result_df = pt.BatchRetrieve(indexref_file).search(search_text)  # Can feed both jnius.reflect.org.terrier.querying.IndexRef / jnius.reflect.org.terrier.querying.Index
    #     return result_df

    def create_index_column_in_df(self, text_df):
        text_df["docno"] = text_df.index + 1
        text_df["docno"] = text_df["docno"].astype(str)
        return text_df

    def retrieve_search_query_in_dfindexer(self, search_text, text_df):
        text_df = self.create_index_column_in_df(text_df)
        if not pt.started():
            pt.init()
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        df_indexer_path = os.path.join(self.cwd, "var/df_index_" + datetime_str)
        if not os.path.exists(df_indexer_path):
            os.makedirs(df_indexer_path)
        pd_indexer = pt.DFIndexer(df_indexer_path, wmodel="Tf")
        indexref = pd_indexer.index(text_df["text"], text_df["docno"])
        result_df = pt.BatchRetrieve(indexref).search(search_text)
        return result_df.merge(text_df, on="docno", how="left")


if __name__ == '__main__':
    pyterrier_service = PyTerrierService()
    search_text = ""
    print(pyterrier_service.text_retrieve_in_files(search_text))
