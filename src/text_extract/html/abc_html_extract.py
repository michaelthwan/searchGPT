import abc


class AbstractHtmlExtractSvc(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def extract_from_html(self, text: str):
        pass
