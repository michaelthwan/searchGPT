import logging
import os
import re
import pickle
import shutil
from hashlib import md5
from pathlib import Path


def setup_logger(tag):
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
    gpt_input_text_df['in_scope'] = gpt_input_text_df['rank'] <= max_rank  # In order to get also the row slightly larger than prompt_length_limit

    # display_df = gpt_input_text_df[gpt_input_text_df['in_scope']]
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


def save_result_cache(path: Path, search_text: str, cache_type: str = 'bing_search', **kwargs):
    cache_dir = path / md5(search_text.encode()).hexdigest()

    os.makedirs(cache_dir, exist_ok=True)
    path = Path(cache_dir, f'{cache_type}.pickle')
    with open(path, 'wb') as f:
        pickle.dump(kwargs, f)


def load_result_from_cache(path: Path, search_text: str, cache_type: str = 'bing_search'):
    path = path / f'{md5(search_text.encode()).hexdigest()}' / f'{cache_type}.pickle'
    with open(path, 'rb') as f:
        return pickle.load(f)


def check_result_cache_exists(path: Path, search_text: str, cache_type: str = 'bing_search') -> bool:
    path = path / f'{md5(search_text.encode()).hexdigest()}' / f'{cache_type}.pickle'
    if os.path.exists(path):
        return True
    else:
        return False


def check_max_number_of_cache(path: Path, max_number_of_cache: int = 10):
    if len(os.listdir(path)) >= max_number_of_cache:
        ctime_list = [(os.path.getctime(path / file), file) for file in os.listdir(path)]
        oldest_file = sorted(ctime_list)[0][1]
        shutil.rmtree(path / oldest_file)

def split_sentences_from_paragraph(text):
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    return sentences


if __name__ == '__main__':
    text = "There are many things you can do to learn how to run faster, Mr. Wan, such as incorporating speed workouts into your running schedule, running hills, counting your strides, and adjusting your running form. Lean forward when you run and push off firmly with each foot. Pump your arms actively and keep your elbows bent at a 90-degree angle. Try to run every day, and gradually increase the distance you run for long-distance runs. Make sure you rest at least one day per week to allow your body to recover. Avoid running with excess gear that could slow you down."
    sentences = split_sentences_from_paragraph(text)
    print(len(sentences))
    print(sentences)