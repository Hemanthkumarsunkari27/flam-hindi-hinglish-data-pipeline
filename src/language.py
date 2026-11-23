
import re

# Strong Hindi words commonly written in Latin script.
# Ambiguous English words such as "to", "me", "is" and "us"
# are deliberately excluded.

HINDI_LATIN_WORDS = {
    "hai", "hain", "tha", "thi", "the",
    "ho", "hoga", "hogi", "honge",
    "ka", "ki", "ke", "ko", "se",
    "mein", "mein", "aur", "par",
    "ye", "yeh", "woh", "vo",
    "kya", "kyun", "kaise", "kab",
    "nahi", "nahin", "haan",
    "mera", "meri", "mere",
    "tera", "teri", "tum", "aap",
    "hum", "ham", "main", "mai",
    "ise", "iska", "uska",
    "gaya", "gayi", "gaye",
    "kiya", "karna", "karo",
    "hota", "hoti", "hote",
    "liye", "bhi", "bahut",
    "accha", "achha", "wala",
    "wali", "wale", "raha",
    "rahe", "rahi", "ek",
    "toh", "pasand", "cheez",
    "khuda", "jan", "dil",
    "dukh", "pyar", "pyaar",
    "samajh", "samaj", "karoge",
    "samne", "samaksh", "prastut",
    "paarit", "gya", "gaya",
    "aavaj", "awaaz", "sunai",
    "kaum", "unhone", "hamare",
    "vishes", "sangaathan"
}

DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")


def identify_language(text):

    if not isinstance(text, str) or not text.strip():
        return "other"

    # Devanagari text
    if DEVANAGARI_PATTERN.search(text):
        return "hi"

    words = re.findall(r"[a-zA-Z]+", text.lower())

    if not words:
        return "other"

    hindi_count = sum(
        word in HINDI_LATIN_WORDS
        for word in words
    )

    hindi_ratio = hindi_count / len(words)

    # Require stronger Hindi evidence
    if hindi_count >= 3:
        return "hi-Latn"

    if hindi_count >= 2 and hindi_ratio >= 0.08:
        return "hi-Latn"

    return "en"


if __name__ == "__main__":

    samples = [
        "नमस्ते दोस्तों कैसे हो",
        "Ise 1856 mein present kiya gaya",
        "Hello everyone, how are you?",
        "भारत में technology तेजी से बढ़ रही है",
        "12345 !!!",
        "Our Lord, we have heard the caller calling to belief",
        "That you will be granted woh cheez jo tum pasand karoge",
        "And ye khuda ke liye difficult nhi hai"
    ]

    for sample in samples:
        print("Text:", sample)
        print("Language:", identify_language(sample))
        print("-" * 40)

