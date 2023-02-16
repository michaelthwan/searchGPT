import pyterrier as pt
import pandas as pd
import os


class PyTerrierService:
    def __init__(self):
        self.cwd = os.getcwd()

    def text_retrieve_in_files(self, search_text, files_path="var/files", is_index=True):
        if not pt.started():
            pt.init()
        files = pt.io.find_files(os.path.join(self.cwd, files_path))
        file_index_path = os.path.join(self.cwd, "var/file_index")
        if is_index:
            if not os.path.exists(file_index_path):
                os.makedirs(file_index_path)
            indexref_file = pt.FilesIndexer(file_index_path, overwrite=True).index(files)
        else:
            indexref_file = pt.IndexFactory.of(os.path.join(file_index_path, "data.properties"))
        result_df = pt.BatchRetrieve(indexref_file).search(search_text)  # Can feed both jnius.reflect.org.terrier.querying.IndexRef / jnius.reflect.org.terrier.querying.Index
        return result_df


if __name__ == '__main__':
    pyterrier_service = PyTerrierService()
    print(pyterrier_service.text_retrieve_in_files("NSSO"))
