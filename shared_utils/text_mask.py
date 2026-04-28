# Text masking functions - mask strings for different views (LLM vs render)
import re

# Special markers for masked content
MASK_TAG_LLM_START = "<gptac_mask_llm>"
MASK_TAG_LLM_END = "</gptac_mask_llm>"
MASK_TAG_RENDER_START = "<gptac_mask_render>"
MASK_TAG_RENDER_END = "</gptac_mask_render>"
MASK_TAG_ENGLISH_START = "<gptac_mask_english>"
MASK_TAG_ENGLISH_END = "</gptac_mask_english>"
MASK_TAG_CHINESE_START = "<gptac_mask_chinese>"
MASK_TAG_CHINESE_END = "</gptac_mask_chinese>"


def build_gpt_academic_masked_string(text_show_llm=None, text_show_render=None):
    """Build a masked string with both LLM and render variants."""
    parts = []
    if text_show_llm:
        parts.append(f"{MASK_TAG_LLM_START}{text_show_llm}{MASK_TAG_LLM_END}")
    if text_show_render:
        parts.append(f"{MASK_TAG_RENDER_START}{text_show_render}{MASK_TAG_RENDER_END}")
    return "".join(parts)


def apply_gpt_academic_string_mask(text, mode):
    """Apply mask to extract specific content based on mode.

    Args:
        text: The masked string to process
        mode: One of "show_llm", "show_render", "show_all"

    Returns:
        The unmasked text appropriate for the mode

    Raises:
        ValueError: If mode is not valid
    """
    if text is None:
        return None
    if text == "":
        return ""

    # Check if text contains mask tags
    has_mask_tags = (MASK_TAG_LLM_START in text or MASK_TAG_RENDER_START in text)

    if not has_mask_tags:
        return text

    if mode == "show_llm":
        # Extract LLM content, remove render tags and content
        result = text
        # Remove render content entirely
        result = re.sub(
            f"{re.escape(MASK_TAG_RENDER_START)}.*?{re.escape(MASK_TAG_RENDER_END)}",
            "",
            result,
            flags=re.DOTALL
        )
        # Remove LLM tags but keep content
        result = result.replace(MASK_TAG_LLM_START, "").replace(MASK_TAG_LLM_END, "")
        return result

    elif mode == "show_render":
        # Extract render content, remove LLM tags and content
        result = text
        # Remove LLM content entirely
        result = re.sub(
            f"{re.escape(MASK_TAG_LLM_START)}.*?{re.escape(MASK_TAG_LLM_END)}",
            "",
            result,
            flags=re.DOTALL
        )
        # Remove render tags but keep content
        result = result.replace(MASK_TAG_RENDER_START, "").replace(MASK_TAG_RENDER_END, "")
        return result

    elif mode == "show_all":
        # Remove all tags, keep all content
        result = text
        result = result.replace(MASK_TAG_LLM_START, "").replace(MASK_TAG_LLM_END, "")
        result = result.replace(MASK_TAG_RENDER_START, "").replace(MASK_TAG_RENDER_END, "")
        return result

    else:
        raise ValueError(f"Invalid mode: {mode}")


def build_gpt_academic_masked_string_langbased(text_show_english=None, text_show_chinese=None):
    """Build a language-based masked string."""
    parts = []
    if text_show_english:
        parts.append(f"{MASK_TAG_ENGLISH_START}{text_show_english}{MASK_TAG_ENGLISH_END}")
    if text_show_chinese:
        parts.append(f"{MASK_TAG_CHINESE_START}{text_show_chinese}{MASK_TAG_CHINESE_END}")
    return "".join(parts)


def _contains_chinese(text):
    """Check if text contains Chinese characters."""
    if not text:
        return False
    # Chinese Unicode ranges: CJK Unified Ideographs
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False


def apply_gpt_academic_string_mask_langbased(text, reference):
    """Apply language-based mask.

    Args:
        text: The masked string to process
        reference: Reference text to detect language from

    Returns:
        Text appropriate for detected language (Chinese or English)
    """
    if text is None:
        return None
    if text == "":
        return ""

    # Check if reference contains Chinese
    is_chinese = _contains_chinese(reference)

    result = text
    if is_chinese:
        # Remove English content, keep Chinese
        result = re.sub(
            f"{re.escape(MASK_TAG_ENGLISH_START)}.*?{re.escape(MASK_TAG_ENGLISH_END)}",
            "",
            result,
            flags=re.DOTALL
        )
        # Remove Chinese tags but keep content
        result = result.replace(MASK_TAG_CHINESE_START, "").replace(MASK_TAG_CHINESE_END, "")
    else:
        # Remove Chinese content, keep English
        result = re.sub(
            f"{re.escape(MASK_TAG_CHINESE_START)}.*?{re.escape(MASK_TAG_CHINESE_END)}",
            "",
            result,
            flags=re.DOTALL
        )
        # Remove English tags but keep content
        result = result.replace(MASK_TAG_ENGLISH_START, "").replace(MASK_TAG_ENGLISH_END, "")

    return result
