# YouTube コメント取得ツール

YouTubeの動画URLを入力するだけで、全コメントをGoogle スプレッドシートに自動書き出しするデスクトップアプリです。

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 機能

- YouTube動画のコメントを全件取得
- Google スプレッドシートへ自動書き出し（新規作成 or 既存シートに追記）
- シンプルなGUI操作（ダークモード対応）
- 取得進捗をリアルタイム表示

---

## 画面イメージ

| 項目 | 内容 |
|------|------|
| YouTube URL | 取得したい動画のURLを貼り付ける |
| スプレッドシートURL | 省略すると新規作成、入力すると既存シートに書き出し |
| 取得開始ボタン | クリックするだけで自動処理 |
| スプレッドシートを開くボタン | 完了後に表示、クリックで直接開く |

---

## 事前準備

以下の2つが必要です。詳しい取得手順は [設定手順書.md](設定手順書.md) をご覧ください。

1. **YouTube APIキー** — Google Cloud Console で取得
2. **credentials.json** — Google OAuth認証ファイル（Google Cloud Console からダウンロード）

---

## 使い方

### .exe で使う場合（推奨）

```
📁 配布フォルダ/
├── youtube_comment_tool.exe
├── .env               ← YouTube APIキーを記載
└── credentials.json   ← Google認証ファイル
```

1. `.env` ファイルにAPIキーを設定
2. `credentials.json` を同フォルダに配置
3. `youtube_comment_tool.exe` をダブルクリックして起動
4. YouTube URLを入力 →「取得開始」をクリック
5. 初回のみブラウザでGoogleアカウントにログイン
6. 完了後「スプレッドシートを開く」をクリック

### Pythonで直接実行する場合

```bash
# 依存ライブラリをインストール
pip install -r requirements.txt

# GUIアプリとして起動
python gui_main.py

# CLIとして起動
python main.py
```

`.env` ファイルを作成し、以下を記載してください：

```
YOUTUBE_API_KEY=ここにAPIキーを貼り付け
```

---

## よくあるエラー

| エラーメッセージ | 対処法 |
|--------------|--------|
| `YOUTUBE_API_KEYが設定されていません` | `.env` ファイルのAPIキーを確認 |
| `credentials.jsonが見つかりません` | `.exe` と同じフォルダに配置されているか確認 |
| `本日のAPI使用量の上限に達しました` | YouTube APIの無料枠（1日10,000クォータ）超過。翌日再試行 |
| `この動画はコメントが無効です` | コメント欄が閉じられている動画のため取得不可 |

---

## 使用技術

| 技術 | 用途 |
|------|------|
| Python 3.10+ | メイン言語 |
| CustomTkinter | GUIフレームワーク |
| YouTube Data API v3 | コメント取得 |
| Google Sheets API | スプレッドシート書き出し |
| PyInstaller | .exeビルド |

---

## ライセンス

MIT License
