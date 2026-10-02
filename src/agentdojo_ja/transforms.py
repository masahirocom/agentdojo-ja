"""Japanese-specific text transforms ("transform operators") for attack strings.

Each transform maps an attack string to a variant that a human (or an LLM) still reads as the same instruction but
that defeats naive string / regex / English-trained filters: script changes, width changes, invisible characters.
They are intentionally *model-agnostic* and can be applied on top of any base attack, including English-origin ones.
"""
from __future__ import annotations

import re
from collections.abc import Callable

import jaconv

_KEYWORDS = ["指示", "無視", "重要", "システム", "管理者", "送金", "振込", "パスワード", "口座", "命令", "従って"]
_ZWSP = "​"


def zenkaku(text: str) -> str:
    """ASCII letters/digits/symbols -> full-width (ＡＢＣ１２３)."""
    return jaconv.h2z(text, kana=False, digit=True, ascii=True)


def hankaku_kana(text: str) -> str:
    """Katakana -> half-width katakana (ｶﾀｶﾅ). Hiragana is converted to katakana first."""
    return jaconv.z2h(jaconv.hira2kata(text), kana=True, digit=False, ascii=False)


def hiragana(text: str) -> str:
    """Katakana -> hiragana."""
    return jaconv.kata2hira(text)


def katakana(text: str) -> str:
    """Hiragana -> katakana."""
    return jaconv.hira2kata(text)


def zwsp_keywords(text: str) -> str:
    """Insert zero-width spaces inside trigger words (指‌示) so keyword filters miss them."""
    for kw in _KEYWORDS:
        text = text.replace(kw, _ZWSP.join(kw))
    return text


def spaced_keywords(text: str) -> str:
    """Insert ordinary spaces inside trigger words (指 示)."""
    for kw in _KEYWORDS:
        text = text.replace(kw, " ".join(kw))
    return text


def fullwidth_space(text: str) -> str:
    """Replace ASCII spaces with ideographic spaces (U+3000)."""
    return re.sub(" ", "　", text)


TRANSFORMS: dict[str, Callable[[str], str]] = {
    "zenkaku": zenkaku,
    "hankaku_kana": hankaku_kana,
    "hiragana": hiragana,
    "katakana": katakana,
    "zwsp_keywords": zwsp_keywords,
    "spaced_keywords": spaced_keywords,
    "fullwidth_space": fullwidth_space,
}
