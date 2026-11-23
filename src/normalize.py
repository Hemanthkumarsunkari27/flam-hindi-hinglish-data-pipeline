
import unicodedata
import re


def normalize_text(text):
    """
    Normalize Hindi and Hinglish text.
    """

    if not isinstance(text, str):
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFC", text)

    # Remove invisible characters
    invisible_chars = [
        "\u200b",
        "\ufeff"
    ]

    for char in invisible_chars:
        text = text.replace(char, "")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove unnecessary spaces
    text = text.strip()

    return text


if __name__ == "__main__":

    samples = [
        "नमस्ते   दोस्तों",
        "मेरा नाम   हेमंत है",
        "Hello    dosto kaise ho"
    ]

    for sample in samples:
        print("Original:", sample)
        print("Normalized:", normalize_text(sample))
        print("-" * 40)
