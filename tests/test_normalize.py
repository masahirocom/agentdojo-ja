from agentdojo_ja.normalize import contains_any, extract_yen_amounts, kanji_to_int, mentions_amount, norm, norm_address


def test_kanji_numerals():
    assert kanji_to_int("千五十") == 1050
    assert kanji_to_int("一万二千三百") == 12300
    assert kanji_to_int("十二万") == 120000
    assert kanji_to_int("百") == 100
    assert kanji_to_int("二十") == 20
    assert kanji_to_int("abc") is None


def test_amount_mentions():
    for s in ["合計は1,050円です", "合計は１０５０円です", "合計は千五十円です", "合計1050 yen"]:
        assert mentions_amount(s, 1050), s
    assert mentions_amount("家賃は12万円", 120000)
    assert not mentions_amount("合計は1,060円", 1050)


def test_norm_and_address():
    assert norm("ｽﾎﾟﾃｨﾌｧｲ Premium") == norm("スポティファイpremium")
    assert norm_address("緑町５−６−７ メゾン緑２０１") == norm_address("緑町5-6-7メゾン緑201")
    assert contains_any("ｱｲﾌｫﾝ の定額", ["アイフォン"])
