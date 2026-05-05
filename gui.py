import os
import sys
import threading
import webbrowser
from pathlib import Path

import customtkinter as ctk
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from youtube import extract_video_id, fetch_video_title, fetch_all_comments
from sheets import get_google_creds, write_comments_to_sheet


def _get_base_path(filename: str) -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / filename
    return Path(__file__).parent / filename


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title('YouTube コメント取得ツール')
        self.geometry('620x560')
        self.resizable(False, False)
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')
        self._result_url: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text='YouTube URL').grid(row=0, column=0, padx=20, pady=(20, 0), sticky='w')
        self.youtube_entry = ctk.CTkEntry(self, width=580, placeholder_text='https://www.youtube.com/watch?v=...')
        self.youtube_entry.grid(row=1, column=0, padx=20, pady=(4, 0))

        ctk.CTkLabel(self, text='スプレッドシートURL（省略で新規作成）').grid(row=2, column=0, padx=20, pady=(16, 0), sticky='w')
        self.sheets_entry = ctk.CTkEntry(self, width=580, placeholder_text='省略するとスプレッドシートを新規作成します')
        self.sheets_entry.grid(row=3, column=0, padx=20, pady=(4, 0))

        self.start_btn = ctk.CTkButton(self, text='取得開始', command=self._on_start, width=200, height=40)
        self.start_btn.grid(row=4, column=0, pady=20)

        self.progress_bar = ctk.CTkProgressBar(self, width=580)
        self.progress_bar.grid(row=5, column=0, padx=20)
        self.progress_bar.set(0)

        self.log_box = ctk.CTkTextbox(self, width=580, height=180, state='disabled')
        self.log_box.grid(row=6, column=0, padx=20, pady=(16, 0))

        self.open_btn = ctk.CTkButton(
            self, text='スプレッドシートを開く', command=self._on_open,
            width=200, height=40, fg_color='#2e8b57', hover_color='#1e6b37',
        )

    def _log(self, msg: str) -> None:
        self.log_box.configure(state='normal')
        self.log_box.insert('end', msg + '\n')
        self.log_box.see('end')
        self.log_box.configure(state='disabled')

    def _on_start(self) -> None:
        youtube_url = self.youtube_entry.get().strip()
        sheets_url = self.sheets_entry.get().strip() or None

        if not youtube_url:
            self._log('❌ YouTubeのURLを入力してください')
            return

        self.start_btn.configure(state='disabled')
        self.open_btn.grid_forget()
        self.progress_bar.set(0)
        self.log_box.configure(state='normal')
        self.log_box.delete('1.0', 'end')
        self.log_box.configure(state='disabled')

        threading.Thread(target=self._run, args=(youtube_url, sheets_url), daemon=True).start()

    def _run(self, youtube_url: str, sheets_url: str | None) -> None:
        try:
            load_dotenv(_get_base_path('.env'))
            api_key = os.getenv('YOUTUBE_API_KEY')
            if not api_key:
                self.after(0, self._log, '❌ .envファイルにYOUTUBE_API_KEYが設定されていません')
                self.after(0, self.start_btn.configure, {'state': 'normal'})
                return

            video_id = extract_video_id(youtube_url)
            if not video_id:
                self.after(0, self._log, '❌ 正しいYouTube URLを入力してください')
                self.after(0, self.start_btn.configure, {'state': 'normal'})
                return

            self.after(0, self._log, '動画情報を取得中...')
            title = fetch_video_title(api_key, video_id)
            self.after(0, self._log, f'✅ 動画タイトル：{title}')
            self.after(0, self.progress_bar.set, 0.2)

            self.after(0, self._log, 'コメントを取得中...')

            def on_progress(count: int) -> None:
                self.after(0, self._log, f'  {count} 件取得中...')

            comments = fetch_all_comments(api_key, video_id, on_progress=on_progress)
            self.after(0, self._log, f'✅ {len(comments)} 件のコメントを取得しました')
            self.after(0, self.progress_bar.set, 0.6)

            if not comments:
                self.after(0, self._log, '❌ この動画にはコメントがありません')
                self.after(0, self.start_btn.configure, {'state': 'normal'})
                return

            self.after(0, self._log, 'Googleアカウントの認証を行います...')
            creds = get_google_creds()
            self.after(0, self.progress_bar.set, 0.8)

            self.after(0, self._log, '📝 スプレッドシートに書き込み中...')
            result_url = write_comments_to_sheet(creds, sheets_url, title, comments)
            self.after(0, self.progress_bar.set, 1.0)
            self.after(0, self._log, '✅ 完了しました！')
            self._result_url = result_url
            self.after(0, self._on_complete)

        except FileNotFoundError:
            self.after(0, self._log, '❌ credentials.json が見つかりません。.exeと同じフォルダに置いてください')
            self.after(0, self.start_btn.configure, {'state': 'normal'})
        except HttpError as e:
            reason = e.reason or ''
            if 'quotaExceeded' in reason or 'dailyLimitExceeded' in reason:
                msg = '❌ 本日のAPI使用量の上限に達しました。明日再試行してください'
            elif 'commentsDisabled' in reason:
                msg = '❌ この動画はコメントが無効です'
            elif 'videoNotFound' in reason or e.status_code == 404:
                msg = '❌ 動画が見つかりません。URLを確認してください'
            else:
                msg = f'❌ YouTube APIエラー：{e}'
            self.after(0, self._log, msg)
            self.after(0, self.start_btn.configure, {'state': 'normal'})
        except Exception as e:
            self.after(0, self._log, f'❌ エラーが発生しました：{e}')
            self.after(0, self.start_btn.configure, {'state': 'normal'})

    def _on_complete(self) -> None:
        self.start_btn.configure(state='normal')
        self.open_btn.grid(row=7, column=0, pady=16)

    def _on_open(self) -> None:
        if self._result_url:
            webbrowser.open(self._result_url)


if __name__ == '__main__':
    app = App()
    app.mainloop()
