from youtube import extract_video_id


def test_extract_standard_watch_url():
    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    assert extract_video_id(url) == 'dQw4w9WgXcQ'


def test_extract_short_url():
    url = 'https://youtu.be/dQw4w9WgXcQ'
    assert extract_video_id(url) == 'dQw4w9WgXcQ'


def test_extract_url_with_extra_params():
    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123&list=PLxxx'
    assert extract_video_id(url) == 'dQw4w9WgXcQ'


def test_extract_mobile_url():
    url = 'https://m.youtube.com/watch?v=dQw4w9WgXcQ'
    assert extract_video_id(url) == 'dQw4w9WgXcQ'


def test_extract_invalid_url_returns_none():
    assert extract_video_id('https://example.com') is None


def test_extract_non_url_returns_none():
    assert extract_video_id('not-a-url') is None


def test_extract_empty_string_returns_none():
    assert extract_video_id('') is None


from unittest.mock import patch, MagicMock
from youtube import fetch_all_comments, fetch_video_title


def test_fetch_video_title_returns_title():
    mock_response = {
        'items': [{'snippet': {'title': 'テスト動画タイトル'}}]
    }
    with patch('youtube.build') as mock_build:
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        mock_youtube.videos.return_value.list.return_value.execute.return_value = mock_response

        result = fetch_video_title('fake_key', 'dQw4w9WgXcQ')

    assert result == 'テスト動画タイトル'


def test_fetch_video_title_returns_video_id_when_not_found():
    mock_response = {'items': []}
    with patch('youtube.build') as mock_build:
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        mock_youtube.videos.return_value.list.return_value.execute.return_value = mock_response

        result = fetch_video_title('fake_key', 'dQw4w9WgXcQ')

    assert result == 'dQw4w9WgXcQ'


def test_fetch_all_comments_returns_correct_structure():
    mock_response = {
        'items': [
            {
                'snippet': {
                    'topLevelComment': {
                        'snippet': {
                            'textDisplay': 'テストコメント',
                            'authorDisplayName': 'テストユーザー',
                            'publishedAt': '2024-01-15T03:34:56.000Z',
                            'likeCount': 5,
                        }
                    }
                }
            }
        ]
        # nextPageToken なし → 1ページで終了
    }
    with patch('youtube.build') as mock_build:
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        mock_youtube.commentThreads.return_value.list.return_value.execute.return_value = mock_response

        result = fetch_all_comments('fake_key', 'dQw4w9WgXcQ')

    assert len(result) == 1
    assert result[0]['text'] == 'テストコメント'
    assert result[0]['author'] == 'テストユーザー'
    assert result[0]['published_at'] == '2024-01-15 12:34:56'
    assert result[0]['like_count'] == 5


def test_fetch_all_comments_handles_pagination():
    page1 = {
        'items': [
            {
                'snippet': {
                    'topLevelComment': {
                        'snippet': {
                            'textDisplay': 'コメント1',
                            'authorDisplayName': 'ユーザー1',
                            'publishedAt': '2024-01-15T03:34:56.000Z',
                            'likeCount': 1,
                        }
                    }
                }
            }
        ],
        'nextPageToken': 'token_page2',
    }
    page2 = {
        'items': [
            {
                'snippet': {
                    'topLevelComment': {
                        'snippet': {
                            'textDisplay': 'コメント2',
                            'authorDisplayName': 'ユーザー2',
                            'publishedAt': '2024-01-16T03:34:56.000Z',
                            'likeCount': 2,
                        }
                    }
                }
            }
        ]
        # nextPageToken なし → 終了
    }
    with patch('youtube.build') as mock_build:
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        mock_youtube.commentThreads.return_value.list.return_value.execute.side_effect = [page1, page2]

        result = fetch_all_comments('fake_key', 'dQw4w9WgXcQ')

    assert len(result) == 2
    assert result[0]['text'] == 'コメント1'
    assert result[0]['published_at'] == '2024-01-15 12:34:56'
    assert result[1]['text'] == 'コメント2'
    assert result[1]['published_at'] == '2024-01-16 12:34:56'


def test_fetch_all_comments_calls_on_progress_with_running_total():
    mock_response = {
        'items': [
            {
                'snippet': {
                    'topLevelComment': {
                        'snippet': {
                            'textDisplay': 'コメント',
                            'authorDisplayName': 'ユーザー',
                            'publishedAt': '2024-01-15T03:34:56.000Z',
                            'likeCount': 1,
                        }
                    }
                }
            }
        ]
    }
    progress_calls = []
    with patch('youtube.build') as mock_build:
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        mock_youtube.commentThreads.return_value.list.return_value.execute.return_value = mock_response

        fetch_all_comments('fake_key', 'dQw4w9WgXcQ', on_progress=lambda n: progress_calls.append(n))

    assert progress_calls == [1]
