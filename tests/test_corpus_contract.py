"""Contract tests for the existing data format and experimental script mapper."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestDataContracts(unittest.TestCase):
    def test_cipher_metadata_and_duplicate_beta(self) -> None:
        data = json.loads(
            (ROOT / "gemantria/mappings/gemantria_ciphers.json").read_text("utf-8")
        )
        greek = data["ciphers"]["greek_transposition"]["mapping"]
        self.assertEqual(greek["σ"], greek["ς"])
        self.assertEqual(greek["ϲ"], greek["ς"])
        self.assertEqual(data["ciphers"]["greek_isopsephy"]["mapping"]["ϡ"], 900)
        self.assertEqual(data["ciphers"]["greek_transposition"]["mapping"]["ϡ"], 90)
        g = next(v for v in data["languages"]["greek"] if v["letter"] == "β")
        item = next(v for v in data["ciphers"]["greek_letters"]
                    if v["greek_letter"] == "β")
        self.assertEqual(item["reversal_cipher"], g["values"]["reversal"])
        self.assertEqual(item["reversal_cipher"], 200)

    def test_obadiah_json_contract(self) -> None:
        path = ROOT / "Tanakh/2. Nevi'im - Prophets/3. Minor Prophets/18_obadiah.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        word = data["Obadiah"]["chapters"]["1"]["1"][0]
        self.assertIsInstance(word["hebrew"], str)
        self.assertIn("hebrew_greek", word)
        self.assertIsInstance(word["strongs"], str)
        self.assertIsInstance(word["morphology"], str)

    def test_reader_cipher_path(self) -> None:
        html = (ROOT / "bible_app.html").read_text(encoding="utf-8")
        self.assertIn('fetch("gemantria/mappings/gemantria_ciphers.json"', html)
        self.assertNotIn("FALLBACK_GREEK_MAP", html)
        self.assertNotIn("gemantria/definitions/gemantria_ciphers.json", html)


if __name__ == "__main__":
    unittest.main()
