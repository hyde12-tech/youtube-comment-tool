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
