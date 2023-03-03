from FootnoteService import FootnoteService
from website import create_app

app = create_app()

if __name__ == '__main__':
    FootnoteService.download_nltk_data_if_not()
    app.run(debug=True)
