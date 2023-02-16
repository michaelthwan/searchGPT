import pyterrier as pt
import pandas as pd
import os


def pd_indexer():
    df = pd.DataFrame({
        'docno':
            ['1', '2', '3'],
        'url':
            ['url1', 'url2', 'url3'],
        'text':
            ['He ran out of money, so he had to stop playing',
             'The waves were crashing on the shore; it was a',
             'The body may perhaps compensates for the loss']
    })
    files = pt.io.find_files("./var/files")

    indexref_file = pt.FilesIndexer("./file_index", overwrite=True).index(files)

    # pd_indexer = pt.DFIndexer("./var")
    # indexref2 = pd_indexer.index(df["text"], df["docno"])
    index = pt.IndexFactory.of(indexref_file)
    print(index.getCollectionStatistics().toString())
    # pt.BatchRetrieve(indexref2).search("waves")
    return


if __name__ == '__main__':

    if not pt.started():
        pt.init()
    # dataset = pt.datasets.get_dataset("vaswani")
    # index_path = "./index"
    print(os.getcwd())

    # files = pt.io.find_files("./var/files")
    files = pt.io.find_files(os.path.join(os.getcwd(), "var/files"))
    indexref_file = pt.FilesIndexer(os.path.join(os.getcwd(), "var/file_index"), overwrite=True).index(files)
    # indexref_file = pt.IndexFactory.of(os.path.join(os.getcwd(), "var/file_index/data.properties"))
    print(type(indexref_file))
    result_df = pt.BatchRetrieve(indexref_file).search("NSSO")  # Can feed both jnius.reflect.org.terrier.querying.IndexRef / jnius.reflect.org.terrier.querying.Index
    print(result_df)

    # index = pt.IndexFactory.of(indexref_file)
    # print(index.getCollectionStatistics().toString())
