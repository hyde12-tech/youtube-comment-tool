from urllib.parse import urlparse, parse_qs
from typing import Callable
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm
from utils import utc_to_jst


class _NullContext:
    def __enter__(self): return self
    def __exit__(self, *_): pass


def extract_video_id(url: str) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.hostname == 'youtu.be':
        video_id = parsed.path.lstrip('/')
        return video_id if video_id else None
    if parsed.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        if parsed.path == '/watch':
            params = parse_qs(parsed.query)
            ids = params.get('v', [])
            return ids[0] if ids else None
    return None


def fetch_video_title(api_key: str, video_id: str) -> str:
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.videos().list(part='snippet', id=video_id).execute()
    items = response.get('items', [])
    if not items:
        return video_id
    return items[0]['snippet']['title']


def fetch_all_comments(
    api_key: str,
    video_id: str,
    on_progress: Callable[[int], None] | None = None,
) -> list[dict]:
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    next_page_token = None
    use_tqdm = on_progress is None

    with (tqdm(desc='コメントを取得中', unit='件') if use_tqdm else _NullContext()) as pbar:
        while True:
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat='plainText',
            ).execute()

            items = response.get('items', [])
            for item in items:
                snippet = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'text': snippet['textDisplay'],
                    'author': snippet['authorDisplayName'],
                    'published_at': utc_to_jst(snippet['publishedAt']),
                    'like_count': snippet['likeCount'],
                })

            if use_tqdm:
                pbar.update(len(items))
            elif on_progress is not None:
                on_progress(len(comments))

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

    return comments
