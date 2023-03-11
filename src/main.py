from SearchGPT import SearchGPT

if __name__ == '__main__':
    search_text = 'the source of dark energy'

    search_gpt_service = SearchGPT()
    response_text, source_text, data_json = search_gpt_service.query_and_get_answer(search_text)
    print()

