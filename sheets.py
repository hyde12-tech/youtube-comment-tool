import os
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]
MAX_SHEET_NAME_LEN = 100


def get_unique_sheet_name(existing_names: list[str], desired_name: str) -> str:
    name = desired_name[:MAX_SHEET_NAME_LEN]
    if name not in existing_names:
        return name
    counter = 2
    while True:
        suffix = f'_{counter}'
        candidate = desired_name[:MAX_SHEET_NAME_LEN - len(suffix)] + suffix
        if candidate not in existing_names:
            return candidate
        counter += 1


def get_google_creds() -> Credentials:
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w', encoding='utf-8') as token_file:
            token_file.write(creds.to_json())
    return creds


def write_comments_to_sheet(
    creds: Credentials,
    spreadsheet_url: str | None,
    video_title: str,
    comments: list[dict],
) -> str:
    gc = gspread.authorize(creds)

    if spreadsheet_url:
        spreadsheet = gc.open_by_url(spreadsheet_url)
    else:
        spreadsheet = gc.create(f'YouTube コメント - {video_title[:50]}')

    existing_names = [ws.title for ws in spreadsheet.worksheets()]
    sheet_name = get_unique_sheet_name(existing_names, video_title)

    worksheet = spreadsheet.add_worksheet(
        title=sheet_name,
        rows=len(comments) + 1,
        cols=4,
    )

    header = [['コメント本文', '投稿者名', '投稿日時', 'いいね数']]
    rows = [[c['text'], c['author'], c['published_at'], c['like_count']] for c in comments]
    worksheet.update('A1', header + rows)

    return spreadsheet.url
