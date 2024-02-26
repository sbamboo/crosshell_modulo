from fuzzywuzzy import fuzz

def fuzzy_substring_search(substring, string_list):
    best_match_index = None
    highest_ratio = -1  # Initialize with a value less than the minimum ratio

    for index, string in enumerate(string_list):
        ratio = fuzz.partial_ratio(substring, string)
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match_index = index

    return best_match_index

# Example usage:
string_lines = [
    "apple pie",
    "banana split",
    "cherry tart",
    "blueberry muffin",
    "strawberry shortcake"
]

substring = "berry"

best_match_index = fuzzy_substring_search(substring, string_lines)
print(f"The best match index for '{substring}' is: {best_match_index}")
print(f"The best matching string is: {string_lines[best_match_index]}")
