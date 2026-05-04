from sheets import get_unique_sheet_name


def test_no_conflict_returns_name_as_is():
    assert get_unique_sheet_name(['Sheet1'], '動画タイトル') == '動画タイトル'


def test_conflict_appends_2():
    assert get_unique_sheet_name(['動画タイトル'], '動画タイトル') == '動画タイトル_2'


def test_multiple_conflicts_increments():
    existing = ['動画タイトル', '動画タイトル_2', '動画タイトル_3']
    assert get_unique_sheet_name(existing, '動画タイトル') == '動画タイトル_4'


def test_long_name_truncated_to_100():
    long_name = 'あ' * 150
    result = get_unique_sheet_name([], long_name)
    assert len(result) == 100


def test_long_name_with_conflict_stays_within_100():
    long_name = 'あ' * 150
    truncated = 'あ' * 100
    result = get_unique_sheet_name([truncated], long_name)
    assert len(result) <= 100
    assert result != truncated


def test_empty_existing_returns_name():
    assert get_unique_sheet_name([], 'テスト') == 'テスト'
