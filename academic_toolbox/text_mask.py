"""
Text masking utilities module.
Provides language-based string transformation for conditional text rendering.
Allows embedding both English and Chinese versions in a single string with markers.
"""
import re


# Markers for masked string sections
MASK_BEGIN = "<<<GPT_ACADEMIC_MASK_BEGIN>>>"
MASK_MIDDLE = "<<<GPT_ACADEMIC_MASK_MIDDLE>>>"
MASK_END = "<<<GPT_ACADEMIC_MASK_END>>>"

# Pattern to match masked strings
MASK_PATTERN = re.compile(
    rf'{re.escape(MASK_BEGIN)}(.*?){re.escape(MASK_MIDDLE)}(.*?){re.escape(MASK_END)}',
    re.DOTALL
)


def build_masked_string(text_english, text_chinese):
    """
    Build a masked string containing both English and Chinese versions.

    Args:
        text_english: The English version of the text
        text_chinese: The Chinese version of the text

    Returns:
        A masked string that can be later extracted based on language preference
    """
    return f"{MASK_BEGIN}{text_english}{MASK_MIDDLE}{text_chinese}{MASK_END}"


def apply_mask(text, mode="show_english"):
    """
    Apply mask to extract the appropriate language version from a masked string.

    Args:
        text: The masked string or regular string
        mode: Either "show_english" or "show_chinese"

    Returns:
        The extracted text in the requested language, or original text if not masked
    """
    if text is None:
        return None

    if not isinstance(text, str):
        return text

    def replace_masked(match):
        english_text = match.group(1)
        chinese_text = match.group(2)
        if mode == "show_english":
            return english_text
        elif mode == "show_chinese":
            return chinese_text
        else:
            return english_text  # Default to English

    return MASK_PATTERN.sub(replace_masked, text)


def detect_language(text):
    """
    Detect whether text is primarily English or Chinese.

    Args:
        text: The text to analyze

    Returns:
        "en" for English, "zh" for Chinese, "unknown" otherwise
    """
    if text is None or not isinstance(text, str) or len(text) == 0:
        return "unknown"

    # Count Chinese characters (CJK Unified Ideographs range)
    chinese_chars = len(re.findall(r'[一-鿿]', text))

    # Count ASCII letters
    ascii_chars = len(re.findall(r'[a-zA-Z]', text))

    # Determine based on ratio
    if chinese_chars > ascii_chars:
        return "zh"
    elif ascii_chars > 0:
        return "en"
    elif chinese_chars > 0:
        return "zh"
    else:
        return "unknown"


def apply_mask_langbased(text, lang_reference=None):
    """
    Apply mask based on detected language of reference text.

    Args:
        text: The masked string to process
        lang_reference: Reference text to detect language from (if None, uses text itself)

    Returns:
        The extracted text in the detected language
    """
    if text is None:
        return None

    if lang_reference is None:
        lang_reference = text

    language = detect_language(lang_reference)

    if language == "zh":
        return apply_mask(text, mode="show_chinese")
    else:
        return apply_mask(text, mode="show_english")


def build_masked_string_langbased(text_show_english, text_show_chinese):
    """
    Alias for build_masked_string with clearer parameter names.

    Args:
        text_show_english: Text to show when English is detected
        text_show_chinese: Text to show when Chinese is detected

    Returns:
        A masked string
    """
    return build_masked_string(text_show_english, text_show_chinese)


def apply_mask_show_render(text):
    """
    Apply mask for rendering display (shows the appropriate language version).

    Args:
        text: The masked string

    Returns:
        The rendered text with language appropriately selected
    """
    return apply_mask_langbased(text)


def is_masked_string(text):
    """
    Check if a string contains masked content.

    Args:
        text: The string to check

    Returns:
        True if the string contains masked content
    """
    if text is None or not isinstance(text, str):
        return False
    return MASK_BEGIN in text and MASK_END in text


def unmask_all(text, preferred_language="en"):
    """
    Remove all masks from a string, extracting preferred language.

    Args:
        text: The text potentially containing masks
        preferred_language: "en" for English, "zh" for Chinese

    Returns:
        Text with all masks resolved
    """
    mode = "show_chinese" if preferred_language == "zh" else "show_english"
    return apply_mask(text, mode=mode)
