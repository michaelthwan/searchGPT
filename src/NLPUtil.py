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
