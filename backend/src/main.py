from SearchGPTService import SearchGPTService

if __name__ == '__main__':
    search_text = 'the source of dark energy'
    load_from_cache = False  # set to True to load bing result and llm result from cache (if available)

    search_gpt_service = SearchGPTService()
    response_text, response_text_with_footnote, source_text, data_json = search_gpt_service.query_and_get_answer(search_text, load_from_cache)
    print()
