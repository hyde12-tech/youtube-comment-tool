from utils import utc_to_jst


def test_utc_to_jst_converts_correctly():
    assert utc_to_jst('2024-01-15T03:34:56.000Z') == '2024-01-15 12:34:56'


def test_utc_to_jst_midnight_jst():
    # UTC 15:00 → JST 翌日 00:00
    assert utc_to_jst('2024-01-15T15:00:00.000Z') == '2024-01-16 00:00:00'


def test_utc_to_jst_format():
    result = utc_to_jst('2024-06-01T00:00:00.000Z')
    assert result == '2024-06-01 09:00:00'
