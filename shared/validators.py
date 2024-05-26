import re

def vulgarity_validator(text):
    vulgarities = ["fuck", "dick", "pussy", "nigger"]

    for word in vulgarities:
        pattern = rf'\b{re.escape(word)}\b'
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise ValidationError(f"the text contains a prohibited word: {word}.")
            break
