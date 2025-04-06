# YouTubeチャンネル成長分析アプリ

このアプリは、特定の期間におけるYouTubeチャンネルの成長率を分析し、視覚的に表示するツールです。

## 機能

- 検索ワードに基づくチャンネル検索
- チャンネル開設日によるフィルタリング
- 登録者数、再生回数の推移を分析
- 1日あたりの平均成長率の計算と可視化
- チャンネルへの直接リンク
- 複数チャンネルの比較分析

## セットアップ手順

1. リポジトリをクローン
```bash
git clone [repository_url]
cd youtube_channel_survey
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
- `.env.example`を`.env`にコピー
- YouTube Data APIのAPIキーを取得し、`.env`ファイルに設定
```bash
YOUTUBE_API_KEY=your_api_key_here
```

5. アプリの起動
```bash
streamlit run app.py
```

## 使用方法

1. サイドバーで検索ワードを入力
2. 取得するチャンネル数を選択（5-50の範囲）
3. チャンネル開設日の範囲を設定
4. 「分析開始」ボタンをクリック

## 注意事項

- YouTube Data APIの使用制限に注意してください
- APIキーは安全に管理してください
- 実際の成長率の計算には、過去のデータの保存が必要です

## 技術スタック

- Python 3.x
- Streamlit
- Pandas
- Matplotlib
- Google YouTube Data API v3

## ライセンス

MIT License 