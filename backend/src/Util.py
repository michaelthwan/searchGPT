import logging

logger = None


def setup_logger(tag):
    global logger
    if logger is None:
        logger = logging.getLogger(tag)
        logger.setLevel(logging.DEBUG)

        handler: logging.StreamHandler = logging.StreamHandler()
        formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def post_process_gpt_input_text_df(gpt_input_text_df, prompt_length_limit):
    # clean out of prompt texts
    gpt_input_text_df['len_text'] = gpt_input_text_df['text'].apply(lambda x: len(x))
    gpt_input_text_df['cumsum_len_text'] = gpt_input_text_df['len_text'].cumsum()
    max_rank = gpt_input_text_df[gpt_input_text_df['cumsum_len_text'] <= prompt_length_limit]['rank'].max() + 1
    gpt_input_text_df['is_used'] = gpt_input_text_df['rank'] <= max_rank  # In order to get also the row slightly larger than prompt_length_limit

    # display_df = gpt_input_text_df[gpt_input_text_df['is_used']]
    # # after cleaning, display text
    # display_df.sort_values(by=['docno'], inplace=True)
    # distinct_urls = list(display_df['url'].unique())
    # # for list with index
    # for index, url in enumerate(distinct_urls):
    #     print('---------------------')
    #     print(f'[{index+1}] {url}')
    #     for index, row in display_df[display_df['url'] == url].iterrows():
    #         print(f'  {row["text"]}')
    return gpt_input_text_df
