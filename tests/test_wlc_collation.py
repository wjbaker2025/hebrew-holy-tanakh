"""Read-only collation unit tests using independently specified XML fixtures."""
from __future__ import annotations

import unittest

from scripts.collate_wlc import BOOK_CODES, consonants, source_verses


class TestWlcConsonantalCollation(unittest.TestCase):
    def test_all_books_have_distinct_osis_ids(self) -> None:
        self.assertEqual(len(BOOK_CODES), 39)
        self.assertEqual(len(set(BOOK_CODES)), 39)

    def test_canonical_consonants_only(self) -> None:
        self.assertEqual(consonants("שְׁמֹעַ־תִּשְׁמְעוּ"), "שמעתשמעו")
        self.assertEqual(consonants("אֲדֹנָי / הַשֵּׁם"), "אדניהשם")

    def test_osis_words_and_variant_streams(self) -> None:
        xml = b'''<?xml version="1.0" encoding="UTF-8"?>
<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace">
  <osisText><div type="book" osisID="Isa">
    <chapter osisID="Isa.6"><verse osisID="Isa.6.9">
      <w>AB</w><w type="x-ketiv">CD</w><w type="x-qere">EF</w>
    </verse></chapter>
  </div></osisText>
</osis>'''
        # Roman fixture letters are not Hebrew; only consonants contribute.
        self.assertEqual(source_verses(xml)[(6, 9)], ("", ""))

    def test_qere_ketiv_versus_default(self) -> None:
        xml = '''<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace">
<osisText><div type="book" osisID="Isa">
<chapter osisID="Isa.6"><verse osisID="Isa.6.9">
<w>שמעו</w><w type="x-ketiv">כתיב</w><w type="x-qere">קרי</w>
</verse></chapter></div></osisText></osis>'''.encode("utf-8")
        self.assertEqual(source_verses(xml)[(6, 9)], ("שמעוקרי", "שמעוכתיב"))


if __name__ == "__main__":
    unittest.main()
