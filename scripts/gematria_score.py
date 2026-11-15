"""Score exact original-language transcriptions using a named mapping."""
from __future__ import annotations

import argparse
from scripts.gematria_core import load_ciphers, score_text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", help="Original-script text; do not substitute translation")
    parser.add_argument("--cipher", default="standard",
                        help="Cipher key, e.g. standard, greek_isopsephy, syriac_standard")
    parser.add_argument("--script", choices=["hebrew", "greek", "syriac"],
                        default="hebrew")
    args = parser.parse_args()
    tables = load_ciphers()
    try:
        value = score_text(args.text, args.cipher, args.script, tables)
    except (ValueError, TypeError) as exc:
        parser.error(str(exc))
    print(f"{args.cipher} ({args.script}): {value}")


if __name__ == "__main__":
    main()
