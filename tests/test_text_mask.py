"""Tests for the text masking utilities module."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.text_mask import (
    build_masked_string,
    apply_mask,
    detect_language,
    apply_mask_langbased,
    build_masked_string_langbased,
    is_masked_string,
    unmask_all,
)


class TestBuildMaskedString(unittest.TestCase):
    """Test cases for building masked strings."""

    def test_build_masked_string_creates_valid_format(self):
        """Test that masked string contains both versions."""
        result = build_masked_string("Hello", "你好")
        self.assertIn("Hello", result)
        self.assertIn("你好", result)
        self.assertIn("<<<GPT_ACADEMIC_MASK_BEGIN>>>", result)
        self.assertIn("<<<GPT_ACADEMIC_MASK_END>>>", result)

    def test_build_masked_string_langbased_alias(self):
        """Test the langbased alias works the same."""
        result1 = build_masked_string("Hello", "你好")
        result2 = build_masked_string_langbased("Hello", "你好")
        self.assertEqual(result1, result2)


class TestApplyMask(unittest.TestCase):
    """Test cases for applying masks to extract language versions."""

    def test_apply_mask_show_english(self):
        """Test extracting English version from masked string."""
        masked = build_masked_string("Hello World", "你好世界")
        result = apply_mask(masked, mode="show_english")
        self.assertEqual(result, "Hello World")

    def test_apply_mask_show_chinese(self):
        """Test extracting Chinese version from masked string."""
        masked = build_masked_string("Hello World", "你好世界")
        result = apply_mask(masked, mode="show_chinese")
        self.assertEqual(result, "你好世界")

    def test_apply_mask_nonmasked_passes_through(self):
        """Test that non-masked strings pass through unchanged."""
        text = "This is a regular string"
        result = apply_mask(text, mode="show_english")
        self.assertEqual(result, text)

    def test_apply_mask_none_returns_none(self):
        """Test that None input returns None."""
        result = apply_mask(None)
        self.assertIsNone(result)

    def test_apply_mask_non_string_passes_through(self):
        """Test that non-string inputs pass through."""
        result = apply_mask(123)
        self.assertEqual(result, 123)

    def test_apply_mask_multiple_masks(self):
        """Test handling multiple masks in one string."""
        part1 = build_masked_string("Hello", "你好")
        part2 = build_masked_string("World", "世界")
        combined = f"{part1} {part2}"
        result = apply_mask(combined, mode="show_english")
        self.assertEqual(result, "Hello World")


class TestDetectLanguage(unittest.TestCase):
    """Test cases for language detection."""

    def test_detect_english_text(self):
        """Test detection of English text."""
        result = detect_language("Hello World")
        self.assertEqual(result, "en")

    def test_detect_chinese_text(self):
        """Test detection of Chinese text."""
        result = detect_language("你好世界")
        self.assertEqual(result, "zh")

    def test_detect_mixed_mostly_english(self):
        """Test mixed text that is mostly English."""
        result = detect_language("Hello 你好 World test")
        self.assertEqual(result, "en")

    def test_detect_mixed_mostly_chinese(self):
        """Test mixed text that is mostly Chinese."""
        result = detect_language("你好世界测试 Hi")
        self.assertEqual(result, "zh")

    def test_detect_none_returns_unknown(self):
        """Test that None returns unknown."""
        result = detect_language(None)
        self.assertEqual(result, "unknown")

    def test_detect_empty_string_returns_unknown(self):
        """Test that empty string returns unknown."""
        result = detect_language("")
        self.assertEqual(result, "unknown")

    def test_detect_numbers_only_returns_unknown(self):
        """Test that numbers only returns unknown."""
        result = detect_language("12345")
        self.assertEqual(result, "unknown")


class TestApplyMaskLangbased(unittest.TestCase):
    """Test cases for language-based mask application."""

    def test_applies_english_for_english_reference(self):
        """Test auto-selecting English based on reference text."""
        masked = build_masked_string("Hello", "你好")
        result = apply_mask_langbased(masked, lang_reference="This is English text")
        self.assertEqual(result, "Hello")

    def test_applies_chinese_for_chinese_reference(self):
        """Test auto-selecting Chinese based on reference text."""
        masked = build_masked_string("Hello", "你好")
        result = apply_mask_langbased(masked, lang_reference="这是中文文本")
        self.assertEqual(result, "你好")

    def test_uses_text_as_reference_when_not_provided(self):
        """Test using the text itself as reference when none provided."""
        # This would fail to match since the masked string has markers
        masked = build_masked_string("Hello", "你好")
        result = apply_mask_langbased(masked)
        # Should default to English since markers are not Chinese/English
        self.assertIn(result, ["Hello", "你好"])

    def test_none_returns_none(self):
        """Test that None input returns None."""
        result = apply_mask_langbased(None)
        self.assertIsNone(result)


class TestIsMaskedString(unittest.TestCase):
    """Test cases for checking if string is masked."""

    def test_masked_string_detected(self):
        """Test that masked strings are detected."""
        masked = build_masked_string("Hello", "你好")
        self.assertTrue(is_masked_string(masked))

    def test_regular_string_not_detected(self):
        """Test that regular strings are not detected as masked."""
        self.assertFalse(is_masked_string("Hello World"))

    def test_none_not_detected(self):
        """Test that None is not detected as masked."""
        self.assertFalse(is_masked_string(None))

    def test_non_string_not_detected(self):
        """Test that non-strings are not detected as masked."""
        self.assertFalse(is_masked_string(123))


class TestUnmaskAll(unittest.TestCase):
    """Test cases for unmasking all content."""

    def test_unmask_all_english(self):
        """Test unmasking with English preference."""
        masked = build_masked_string("Hello", "你好")
        result = unmask_all(masked, preferred_language="en")
        self.assertEqual(result, "Hello")

    def test_unmask_all_chinese(self):
        """Test unmasking with Chinese preference."""
        masked = build_masked_string("Hello", "你好")
        result = unmask_all(masked, preferred_language="zh")
        self.assertEqual(result, "你好")

    def test_unmask_all_defaults_to_english(self):
        """Test that unmask_all defaults to English."""
        masked = build_masked_string("Hello", "你好")
        result = unmask_all(masked)
        self.assertEqual(result, "Hello")


if __name__ == '__main__':
    unittest.main()
