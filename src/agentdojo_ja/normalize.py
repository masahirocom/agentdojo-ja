"""Japanese-aware normalization helpers for utility / security checks.

AgentDojo's original checks are mostly substring matches on English text. Japanese output can express the
same fact as "1,050円", "１０５０円", "千五十円" or "1050 yen"; names as kanji / hiragana / katakana /
half-width katakana. Prefer state-based checks; use these helpers only where text must be inspected.
"""
from __future__ import annotations

import re
import unicodedata

_HYPHENS = "‐‑‒–—―−ーｰ－⁃"  # hyphen-like characters people (and models) interchange
_KANJI_DIGITS = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_SMALL_UNITS = {"十": 10, "百": 100, "千": 1000}
_LARGE_UNITS = {"万": 10**4, "億": 10**8, "兆": 10**12}


def norm(text: str) -> str:
    """NFKC (full-width -> ASCII, half-width kana -> full-width kana), casefold, no whitespace."""
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\s+", "", text)


def norm_address(text: str) -> str:
    """Normalize an address: NFKC, unify hyphens, drop spaces."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(f"[{re.escape(_HYPHENS)}]", "-", text)
    return re.sub(r"\s+", "", text)


def contains_any(text: str, needles: list[str]) -> bool:
    """True if any needle appears in text after `norm` on both sides."""
    t = norm(text)
    return any(norm(n) in t for n in needles)


def kanji_to_int(s: str) -> int | None:
    """Parse a kanji numeral such as 千五十, 一万二千三百, 十二万 to int. Returns None if not a numeral."""
    if not s or any(c not in _KANJI_DIGITS and c not in _SMALL_UNITS and c not in _LARGE_UNITS for c in s):
        return None
    total, section, digit = 0, 0, None
    for c in s:
        if c in _KANJI_DIGITS:
            digit = _KANJI_DIGITS[c] if digit is None else digit * 10 + _KANJI_DIGITS[c]
        elif c in _SMALL_UNITS:
            section += (1 if digit is None else digit) * _SMALL_UNITS[c]
            digit = None
        else:  # large unit
            section += digit or 0
            total += (section or 1) * _LARGE_UNITS[c]
            section, digit = 0, None
    return total + section + (digit or 0)


_NUM_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)(万|億)?|([〇零一二三四五六七八九十百千万億兆]+)")


def extract_yen_amounts(text: str) -> set[float]:
    """All numeric amounts mentioned in text (arabic with commas/full-width, 12万, kanji numerals)."""
    text = unicodedata.normalize("NFKC", text)
    found: set[float] = set()
    for m in _NUM_RE.finditer(text):
        if m.group(1):
            v = float(m.group(1).replace(",", ""))
            if m.group(2):
                v *= _LARGE_UNITS[m.group(2)]
            found.add(v)
        elif m.group(3):
            k = kanji_to_int(m.group(3))
            if k is not None:
                found.add(float(k))
    return found


def mentions_amount(text: str, amount: int | float) -> bool:
    return float(amount) in extract_yen_amounts(text)
