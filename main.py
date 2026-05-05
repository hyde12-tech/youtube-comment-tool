import os
import sys
from dotenv import load_dotenv
from googleapiclient.errors import HttpError
from youtube import extract_video_id, fetch_video_title, fetch_all_comments
from sheets import get_google_creds, write_comments_to_sheet


def handle_youtube_error(error: HttpError) -> None:
    reason = str(error)
    if 'quotaExceeded' in reason or 'dailyLimitExceeded' in reason:
        print('エラー: 本日のAPI使用量の上限に達しました。明日再試行してください')
    elif 'commentsDisabled' in reason:
        print('エラー: この動画はコメントが無効です')
    elif 'videoNotFound' in reason or error.status_code == 404:
        print('エラー: 動画が見つかりません。URLを確認してください')
    else:
        print(f'エラー: YouTube APIでエラーが発生しました: {error}')


def main() -> None:
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print('エラー: .envファイルにYOUTUBE_API_KEYが設定されていません')
        sys.exit(1)

    url = input('YouTubeの動画URLを入力してください: ').strip()
    video_id = extract_video_id(url)
    if not video_id:
        print('エラー: 正しいYouTube URLを入力してください')
        print('例: https://www.youtube.com/watch?v=XXXXX')
        sys.exit(1)

    print('動画情報を取得中...')
    try:
        title = fetch_video_title(api_key, video_id)
    except HttpError as e:
        handle_youtube_error(e)
        sys.exit(1)
    print(f'動画タイトル: {title}')

    print('')
    try:
        comments = fetch_all_comments(api_key, video_id)
    except HttpError as e:
        handle_youtube_error(e)
        sys.exit(1)

    if not comments:
        print('コメントが見つかりませんでした')
        sys.exit(0)

    print(f'\n{len(comments)}件のコメントを取得しました')

    spreadsheet_url = input('\nスプレッドシートのURLを入力してください（新規作成はそのままEnter）: ').strip() or None

    print('Googleアカウントの認証を行います...')
    try:
        creds = get_google_creds()
    except Exception as e:
        print(f'エラー: Google認証に失敗しました: {e}')
        sys.exit(1)

    print('スプレッドシートに書き込み中...')
    try:
        result_url = write_comments_to_sheet(creds, spreadsheet_url, title, comments)
    except Exception as e:
        print(f'エラー: スプレッドシートへの書き込みに失敗しました: {e}')
        sys.exit(1)

    print('\n完了しました！')
    print(f'スプレッドシート: {result_url}')


if __name__ == '__main__':
    main()
