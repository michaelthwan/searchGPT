import tiktoken


def remove_substrings(strings):
    """
    Remove any string that is a substring of another string
    Input ["abc", "ab", "c"]
    Output ["abc", "c"]
    """
    # Sort the strings by length in descending order
    strings_sorted = sorted(strings, key=len, reverse=False)

    # Remove any string that is a substring of another string
    result = []
    for i in range(len(strings_sorted)):
        is_substring = False
        for j in range(i + 1, len(strings_sorted)):
            if strings_sorted[i] in strings_sorted[j]:
                is_substring = True
                break
        if not is_substring:
            result.append(strings_sorted[i])

    return result


def get_longest_common_word_sequences(paragraph1, paragraph2, k=10):
    """
    Find the longest common subsequences of words between two paragraphs
    Input: p1: "The quick brown fox jumps over the lazy dog", p2: "The quick brown dog jumps over the lazy fox"
    Output: ["jumps over the lazy", "the quick brown"]
    """
    # Tokenize the paragraphs into lists of words
    word_lists1 = [word.lower() for word in paragraph1.split()]
    word_lists2 = [word.lower() for word in paragraph2.split()]

    # Initialize a table to store the lengths of common subsequences
    table = [[0] * (len(word_lists2) + 1) for _ in range(len(word_lists1) + 1)]

    # Fill in the table by comparing each pair of words
    common_sequences = []
    for i in range(1, len(word_lists1) + 1):
        for j in range(1, len(word_lists2) + 1):
            if word_lists1[i - 1] == word_lists2[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
                sequence_len = table[i][j]
                # if sequence_len >= k:
                sequence = ' '.join(word_lists1[i - sequence_len:i])
                if sequence not in common_sequences:
                    common_sequences.append(sequence)
            else:
                table[i][j] = 0

    # Sort the common sequences by length in descending order and return the top k longest sequences
    common_sequences = remove_substrings(common_sequences)
    longest_sequences = sorted(common_sequences, key=len, reverse=True)[:k]
    min_sequence_len = 10
    longest_sequences = [sequence for sequence in longest_sequences if len(sequence) >= min_sequence_len]
    return longest_sequences


def split_with_delimiters(string, delimiter_list):
    """
    Key point if this function is it will preserve the delimiters to serve the purpose
    Input: ("is fine-tuned from a gpt-3.5 series", ["fine-tuned", "gpt-3.5"])
    Output: ['is ', 'fine-tuned', ' from a ', 'gpt-3.5', ' series']
    """
    result = []
    start = 0
    for i in range(len(string)):
        for delimiter in delimiter_list:
            delimiter_len = len(delimiter)
            if string[i:i + delimiter_len] == delimiter:
                if i > start:
                    result.append(string[start:i])
                result.append(delimiter)
                start = i + delimiter_len
                break
        else:
            continue
    if start < len(string):
        result.append(string[start:])
    return result


def num_tokens_from_string(string: str) -> int:
    """
    Returns the number of tokens in a text string.
    https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    """
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens


if __name__ == '__main__':
    paragraph1 = "ChatGPT is an AI chatbot that can understand and generate human-like answers to text prompts, as well as create code from natural speech [3]. It is built on a family of large language models collectively called GPT-3, which is trained on huge amounts of data [3][1]. The model is fine-tuned from a model in the GPT-3.5 series, which finished training in early 2022 and trained on an Azure AI supercomputing infrastructure [1]. ChatGPT is also sensitive to tweaks to the input phrasing or attempting the same prompt multiple times [1]. The objective of ChatGPT is to predict the next word in a sentence based on what it has learned [3]. The research release of ChatGPT in November 2022 is among OpenAI's iterative deployment of increasingly safe and useful AI systems [1]. ChatGPT Plus also exists, which brings a few benefits over the free tier [3]."
    paragraph2 = """
Source (1)
ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response.
- ChatGPT is sensitive to tweaks to the input phrasing or attempting the same prompt multiple times. For example, given one phrasing of a question, the model can claim to not know the answer, but given a slight rephrase, can answer correctly.
ChatGPT is fine-tuned from a model in the GPT-3.5 series, which finished training in early 2022. You can learn more about the 3.5 series here. ChatGPT and GPT-3.5 were trained on an Azure AI supercomputing infrastructure.
Todayâs research release of ChatGPT is the latest step in OpenAI iterative deployment of increasingly safe and useful AI systems. Many lessons from deployment of earlier models like GPT-3 and Codex have informed the safety mitigations in place for this release, including substantial reductions in harmful and untruthful outputs achieved by the use of reinforcement learning from human feedback (RLHF).

Source (3)
ChatGPT is an AI chatbot that's built on a family of large language models (LLMs) that are collectively called GPT-3. These models can understand and generate human-like answers to text prompts, because they've been trained on huge amounts of data.
But ChatGPT is also equally talented at coding and productivity tasks. For the former, its ability to create code from natural speech makes it a powerful ally for both new and experienced coders who either aren't familiar with a particular language or want to troubleshoot existing code. Unfortunately, there is also the potential for it to be misused to create malicious emails and malware.
ChatGPT stands for "Chat Generative Pre-trained Transformer". Let's take a look at each of those words in turn.
But the short answer? ChatGPT works thanks to a combination of deep learning algorithms, a dash of natural language processing, and a generous dollop of generative pre-training, which all combine to help it produce disarmingly human-like responses to text questions. Even if all it's ultimately been trained to do is fill in the next word, based on its experience of being the world's most voracious reader.
ChatGPT has been created with one main objective to predict the next word in a sentence, based on what's typically happened in the gigabytes of text data that it's been trained on.
ChatGPT was released as a "research preview" on November 30, 2022. A blog post (opens in new tab) casually introduced the AI chatbot to the world, with OpenAI stating that "we’ve trained a model called ChatGPT which interacts in a conversational way".
ChatGPT Plus costs $20 p/month (around £17 / AU$30) and brings a few benefits over the free tier. It promises to give you full access to ChatGPT even during peak times, which is when you'll otherwise frequently see "ChatGPT is at capacity right now messages during down times.
ChatGPT has been trained on a vast amount of text covering a huge range of subjects, so its poss
    """

    # common_stems = FrontendService.longest_common_word_sequences(paragraph1, paragraph2)
    # # print(common_stems)
    # for common_stem in common_stems:
    #     print(common_stem)

    # text_list = ["is fine-tuned from a model in the gpt-3.5 series, which finished training in early",
    #              "sensitive to tweaks to the input phrasing or attempting the same prompt multiple",
    #              "is fine-tuned from a model in the gpt-3.5 series, which finished training in",
    #              "is fine-tuned from a model in the gpt-3.5 series, which finished training",
    #              "sensitive to tweaks to the input phrasing or attempting the same prompt",
    #              "is fine-tuned from a model in the gpt-3.5 series, which finished",
    #              "sensitive to tweaks to the input phrasing or attempting the same",
    #              "sensitive to tweaks to the input phrasing or attempting the",
    #              "is fine-tuned from a model in the gpt-3.5 series, which"]
    # text_list = FrontendService.remove_substrings(text_list)
    # for text in text_list:
    #     print(text)

    # response_text = "is fine-tuned from a gpt-3.5 series"
    # split_list = split_with_delimiters(response_text, ["fine-tuned", "gpt-3.5"])
    # print(split_list)

    s = "OpenAI 推出了一個新型聊天機器人模型ChatGPT"
    print(num_tokens_from_string(s))
