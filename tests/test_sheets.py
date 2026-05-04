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


from unittest.mock import patch, MagicMock
from sheets import write_comments_to_sheet

SAMPLE_COMMENTS = [
    {
        'text': 'テストコメント',
        'author': 'テストユーザー',
        'published_at': '2024-01-15 12:34:56',
        'like_count': 5,
    }
]


def test_write_to_existing_spreadsheet():
    mock_creds = MagicMock()
    with patch('sheets.gspread') as mock_gspread:
        mock_gc = MagicMock()
        mock_gspread.Client.return_value = mock_gc
        mock_spreadsheet = MagicMock()
        mock_gc.open_by_url.return_value = mock_spreadsheet
        mock_spreadsheet.worksheets.return_value = []
        mock_worksheet = MagicMock()
        mock_spreadsheet.add_worksheet.return_value = mock_worksheet
        mock_spreadsheet.url = 'https://docs.google.com/spreadsheets/d/existing'

        result = write_comments_to_sheet(
            mock_creds,
            'https://docs.google.com/spreadsheets/d/existing',
            '動画タイトル',
            SAMPLE_COMMENTS,
        )

    assert result == 'https://docs.google.com/spreadsheets/d/existing'
    mock_gc.open_by_url.assert_called_once_with('https://docs.google.com/spreadsheets/d/existing')
    mock_spreadsheet.add_worksheet.assert_called_once()
    mock_worksheet.update.assert_called_once()


def test_write_creates_new_spreadsheet_when_no_url():
    mock_creds = MagicMock()
    with patch('sheets.gspread') as mock_gspread:
        mock_gc = MagicMock()
        mock_gspread.Client.return_value = mock_gc
        mock_spreadsheet = MagicMock()
        mock_gc.create.return_value = mock_spreadsheet
        mock_spreadsheet.worksheets.return_value = []
        mock_worksheet = MagicMock()
        mock_spreadsheet.add_worksheet.return_value = mock_worksheet
        mock_spreadsheet.url = 'https://docs.google.com/spreadsheets/d/new'

        result = write_comments_to_sheet(
            mock_creds,
            None,
            '動画タイトル',
            SAMPLE_COMMENTS,
        )

    assert result == 'https://docs.google.com/spreadsheets/d/new'
    mock_gc.create.assert_called_once()
    mock_gc.open_by_url.assert_not_called()


def test_write_data_includes_header_and_comments():
    mock_creds = MagicMock()
    with patch('sheets.gspread') as mock_gspread:
        mock_gc = MagicMock()
        mock_gspread.Client.return_value = mock_gc
        mock_spreadsheet = MagicMock()
        mock_gc.create.return_value = mock_spreadsheet
        mock_spreadsheet.worksheets.return_value = []
        mock_worksheet = MagicMock()
        mock_spreadsheet.add_worksheet.return_value = mock_worksheet
        mock_spreadsheet.url = 'https://docs.google.com/spreadsheets/d/new'

        write_comments_to_sheet(mock_creds, None, '動画', SAMPLE_COMMENTS)

    call_args = mock_worksheet.update.call_args
    written_data = call_args[0][0]
    assert written_data[0] == ['コメント本文', '投稿者名', '投稿日時', 'いいね数']
    assert written_data[1] == ['テストコメント', 'テストユーザー', '2024-01-15 12:34:56', 5]
