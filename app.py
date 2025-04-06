import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import japanize_matplotlib  # 日本語フォント対応

# 環境変数の読み込み
load_dotenv()

# YouTube APIの設定
API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=API_KEY)

def parse_date(date_str):
    """日付文字列を解析する関数"""
    try:
        # ミリ秒を含むフォーマットを試す
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        try:
            # ミリ秒を含まないフォーマットを試す
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # その他のフォーマットを試す
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

def search_channels(query, max_results=50, min_date=None, max_date=None):
    """検索ワードに基づいてチャンネルを検索"""
    channels = []
    
    # チャンネル検索
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="channel",
        maxResults=max_results
    )
    response = request.execute()
    
    for item in response['items']:
        channel_id = item['id']['channelId']
        channel_info = get_channel_stats(channel_id)
        if channel_info:
            # 開設日のフィルタリング
            published_at = parse_date(channel_info['published_at'])
            if min_date and published_at < min_date:
                continue
            if max_date and published_at > max_date:
                continue
            channels.append(channel_info)
    
    return channels

def get_channel_stats(channel_id):
    """チャンネルの統計情報を取得"""
    request = youtube.channels().list(
        part="statistics,snippet",
        id=channel_id
    )
    response = request.execute()
    
    if not response['items']:
        return None
    
    stats = response['items'][0]['statistics']
    snippet = response['items'][0]['snippet']
    
    return {
        'channel_id': channel_id,
        'title': snippet['title'],
        'subscriber_count': int(stats['subscriberCount']),
        'view_count': int(stats['viewCount']),
        'video_count': int(stats['videoCount']),
        'published_at': snippet['publishedAt']
    }

def analyze_channels_growth(channels, days=30):
    """複数のチャンネルの成長率を分析"""
    results = []
    
    for channel in channels:
        # チャンネル開設からの経過日数を計算
        published_at = parse_date(channel['published_at'])
        days_since_creation = (datetime.now() - published_at).days
        
        # 1日あたりの平均値を計算
        daily_subs = channel['subscriber_count'] / days_since_creation
        daily_views = channel['view_count'] / days_since_creation
        
        # 成長率の計算（日数で正規化）
        growth_rate = (channel['subscriber_count'] / days_since_creation) * 100
        
        results.append({
            'channel_name': channel['title'],
            'channel_id': channel['channel_id'],
            'current_subs': channel['subscriber_count'],
            'current_views': channel['view_count'],
            'published_at': channel['published_at'],
            'days_since_creation': days_since_creation,
            'daily_subs': daily_subs,
            'daily_views': daily_views,
            'growth_rate': growth_rate
        })
    
    # 成長率でソート
    results.sort(key=lambda x: x['growth_rate'], reverse=True)
    return results

def plot_growth_comparison(results):
    """成長率の比較グラフを作成"""
    plt.style.use('default')  # デフォルトスタイルを使用
    plt.rcParams['font.family'] = 'IPAexGothic'  # 日本語フォントを指定
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))
    
    # チャンネル名のリスト
    channel_names = [r['channel_name'] for r in results]
    
    # 登録者数のバーグラフ
    subs = [r['current_subs'] for r in results]
    ax1.bar(range(1, len(channel_names) + 1), subs)
    ax1.set_title('チャンネル別登録者数', fontsize=12, pad=10)
    ax1.set_xticks(range(1, len(channel_names) + 1))
    ax1.set_xticklabels(channel_names, rotation=45, ha='right')
    
    # 成長率のバーグラフ
    growth_rates = [r['growth_rate'] for r in results]
    ax2.bar(range(1, len(channel_names) + 1), growth_rates)
    ax2.set_title('チャンネル別成長率（1日あたり）', fontsize=12, pad=10)
    ax2.set_xticks(range(1, len(channel_names) + 1))
    ax2.set_xticklabels(channel_names, rotation=45, ha='right')
    
    # 開設からの経過日数のバーグラフ
    days = [r['days_since_creation'] for r in results]
    ax3.bar(range(1, len(channel_names) + 1), days)
    ax3.set_title('チャンネル開設からの経過日数', fontsize=12, pad=10)
    ax3.set_xticks(range(1, len(channel_names) + 1))
    ax3.set_xticklabels(channel_names, rotation=45, ha='right')
    
    plt.tight_layout()
    return fig

def main():
    st.title('YouTubeチャンネル成長分析')
    
    # サイドバーで設定
    st.sidebar.header('分析設定')
    search_query = st.sidebar.text_input('検索ワードを入力')
    max_results = st.sidebar.slider('取得するチャンネル数', 5, 50, 20)
    
    # 開設日の範囲設定
    st.sidebar.subheader('チャンネル開設日の範囲')
    min_date = st.sidebar.date_input('開始日', datetime.now() - timedelta(days=365*5))
    max_date = st.sidebar.date_input('終了日', datetime.now())
    
    if st.sidebar.button('分析開始'):
        if search_query:
            with st.spinner('チャンネルを検索中...'):
                channels = search_channels(
                    search_query, 
                    max_results,
                    min_date=datetime.combine(min_date, datetime.min.time()),
                    max_date=datetime.combine(max_date, datetime.max.time())
                )
                
                if channels:
                    st.success(f'{len(channels)}個のチャンネルが見つかりました')
                    
                    with st.spinner('成長率を分析中...'):
                        results = analyze_channels_growth(channels)
                        
                        # 結果の表示
                        st.subheader('チャンネル成長率ランキング')
                        
                        # データフレームで表示
                        df = pd.DataFrame(results)
                        df['published_at'] = pd.to_datetime(df['published_at']).dt.strftime('%Y-%m-%d')
                        df.index = range(1, len(df) + 1)  # インデックスを1から開始
                        
                        # チャンネルリンクを追加
                        df['channel_link'] = df['channel_id'].apply(
                            lambda x: f'https://www.youtube.com/channel/{x}'
                        )
                        
                        # カラム名を日本語に変更
                        df = df.rename(columns={
                            'channel_name': 'チャンネル名',
                            'published_at': '開設日',
                            'days_since_creation': '経過日数',
                            'current_subs': '登録者数',
                            'current_views': '再生回数',
                            'daily_subs': '1日あたりの平均登録者数',
                            'daily_views': '1日あたりの平均再生回数',
                            'growth_rate': '成長率（1日あたり）',
                            'channel_link': 'チャンネルリンク'
                        })
                        
                        # 数値のフォーマットを設定
                        df['1日あたりの平均登録者数'] = df['1日あたりの平均登録者数'].round(2)
                        df['1日あたりの平均再生回数'] = df['1日あたりの平均再生回数'].round(2)
                        df['成長率（1日あたり）'] = df['成長率（1日あたり）'].round(2)
                        
                        # リンク付きのチャンネル名を作成
                        df['チャンネル名'] = df.apply(
                            lambda x: f'<a href="{x["チャンネルリンク"]}" target="_blank">{x["チャンネル名"]}</a>',
                            axis=1
                        )
                        
                        # HTMLとして表示
                        st.write(
                            df[[
                                'チャンネル名', 
                                '開設日',
                                '経過日数',
                                '登録者数', 
                                '再生回数',
                                '1日あたりの平均登録者数',
                                '1日あたりの平均再生回数',
                                '成長率（1日あたり）'
                            ]].to_html(escape=False, index=True),
                            unsafe_allow_html=True
                        )
                        
                        # グラフの表示
                        st.subheader('成長率比較グラフ')
                        fig = plot_growth_comparison(results)
                        st.pyplot(fig)
                        
                        # 急成長チャンネルの表示
                        st.subheader('急成長チャンネル')
                        top_growth = results[:5]  # 上位5チャンネル
                        for i, channel in enumerate(top_growth, 1):  # 1から始まるインデックス
                            st.write(
                                f"{i}. 📈 [{channel['channel_name']}](https://www.youtube.com/channel/{channel['channel_id']}): "
                                f"成長率 {channel['growth_rate']:.2f}% "
                                f"(開設日: {channel['published_at'][:10]}, "
                                f"経過日数: {channel['days_since_creation']}日)"
                            )
                else:
                    st.error('チャンネルが見つかりませんでした。')
        else:
            st.warning('検索ワードを入力してください。')

if __name__ == '__main__':
    main() 