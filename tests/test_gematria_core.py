"""Regression fixtures for historical and explicitly experimental mappings."""
from __future__ import annotations

import unittest

from scripts.gematria_core import load_ciphers, normalize_letters, score_text


class TestScoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tables = load_ciphers()

    def score(self, value: str, cipher: str, script: str) -> int:
        return score_text(value, cipher, script, self.tables)

    def test_standard_hebrew_hearing(self) -> None:
        self.assertEqual(self.score("שְׁמ֥וּעַ", "standard", "hebrew"), 416)
        self.assertEqual(self.score("שמעו", "biblical", "hebrew"), 119)

    def test_hebrew_final_forms(self) -> None:
        self.assertEqual(self.score("מלך", "standard", "hebrew"), 90)
        self.assertEqual(self.score("מלכ", "standard", "hebrew"), 90)

    def test_greek_traditional_jesus(self) -> None:
        self.assertEqual(self.score("Ἰησοῦς", "greek_isopsephy", "greek"), 888)
        self.assertEqual(self.score("ΙΗΣΟΥΣ", "greek_isopsephy", "greek"), 888)
        self.assertEqual(self.score("Ἰησοῦϲ", "greek_isopsephy", "greek"), 888)

    def test_greek_model_jesus(self) -> None:
        self.assertEqual(self.score("Ἰησοῦς", "greek_transposition", "greek"), 492)
        self.assertEqual(self.score("Ἰησοῦσ", "greek_transposition", "greek"), 492)

    def test_greek_archaic_numerals(self) -> None:
        self.assertEqual(self.score("ϡ", "greek_isopsephy", "greek"), 900)
        self.assertEqual(self.score("ϡ", "greek_transposition", "greek"), 90)
        self.assertEqual(self.score("ϙ", "greek_isopsephy", "greek"), 90)

    def test_syriac(self) -> None:
        self.assertEqual(self.score("ܐܣܐ", "syriac_standard", "syriac"), 62)

    def test_reject_unknown_letter(self) -> None:
        with self.assertRaises(ValueError):
            self.score("Ἰησοῦς", "standard", "greek")
        with self.assertRaises(ValueError):
            self.score("abc", "standard", "hebrew")

    def test_normalization(self) -> None:
        self.assertEqual(normalize_letters("Σ ς ϲ", "greek"), "σ σ σ")
        self.assertEqual(normalize_letters("מָלָךְ", "hebrew"), "מלכ")


if __name__ == "__main__":
    unittest.main()
