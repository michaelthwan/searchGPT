import abc


class AbstractDocExtractSvc(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def extract_from_doc(self, path: str):
        pass
