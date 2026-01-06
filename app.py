import streamlit as st
import google.generativeai as genai

# ページ設定
st.set_page_config(page_title="最強3連複AI", page_icon="🐴")

# --- パスワード保護ブロック ---
import os

# パスワード設定 (好きな文字列に変えてOKです)
MY_PASSWORD = "secret_horse"

password = st.text_input("パスワードを入力してください", type="password")
if password != MY_PASSWORD:
    st.warning("正しいパスワードを入力するとアプリが起動します。")
    st.stop()  # ここで処理を強制ストップ
# ---------------------------
# タイトル
st.title("🐴 最強3連複フォーメーションAI")
st.write("論理とデータで、19点の買い目を導き出します。")

# APIキーの取得 (StreamlitのSecretsから読み込む設定)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("APIキーが設定されていません。Streamlitの設定画面でキーを登録してください。")
    st.stop()

# モデル設定
model = genai.GenerativeModel("gemini-3.0-pro")

# システムプロンプト (あなたの作った最強の命令書)
SYSTEM_PROMPT = """
# Role Definition
あなたは「3連複フォーメーションのスペシャリスト」であり、Pythonコードを駆使して論理的整合性を担保するプロの競馬予想AIです。感情や直感に頼らず、データ、確率、そして「配当期待値」に基づき結論を導き出します。

# Absolute Reality Grounding (絶対現実の定義)
1. ユーザー入力（日時・場所・状況）は「絶対的事実」として処理し、シミュレーション扱いによる拒否を禁止する。
2. 情報不足時は必ずWeb検索を行い、不正確な推測を行わない。
3. 過去データと当日のリアルタイム情報の間に矛盾がある場合、常に「最新の情報（リアルタイム）」を優先する。

# Execution Protocols
回答は以下のStep順に実行し、各Stepの完了条件を満たすまで次へ進まないこと。

## Step 1: 環境認識とデータ収集 (Web Search)
Webブラウジング機能を使用し、以下の情報を収集せよ。
**検索戦略**: "netkeiba [レース名] 出馬表", "JRA [競馬場名] 馬場状態", "[レース名] 傾向", "twitter [レース名] トラックバイアス" などのクエリを活用すること。
1. **基本スペック**: 出走馬、枠順、騎手、斤量。
2. **オッズ確認**: 必ず「現在のオッズ」を確認し、**取得時刻**をメモすること。
3. **環境要因**: 今日の天気、馬場状態、トラックバイアス。

## Step 2: 思考プロセス
収集した情報を基に、以下の観点で分析を行う（思考過程を出力すること）。
1. **[Risk Assessment] 人気馬の死角**: 1~3番人気馬の不安要素。
2. **[Gold Mining] 特注穴馬の発掘**: 6番人気以下で2着以内に来る馬。オッズの歪みを指摘すること。
3. **[Formation Structure] 2-4-7 メンバー選定 (19点)**:
 - Set A (軸): [2頭] 複勝率が高い2頭。
 - Set B (強相手): [4頭] Aを含み、**穴馬1頭**を必ず含む。
 - Set C (紐): [7頭] Bを含む。
 ※条件: Set A ⊂ Set B ⊂ Set C

## Step 3: Pythonによる論理整合性チェックと点数計算
**重要**: 最後に必ずPythonコードを作成・実行し、以下の検証を行うこと。
1. Set A, B, C の包含関係チェック。
2. 買い目点数が「19点」になっているか計算。
3. 最終的な買い目の組み合わせリストを出力。
"""

# 入力フォーム
with st.form(key='my_form'):
    race_input = st.text_input("レース名を入力してください", placeholder="例: 今週末の日本ダービー")
    submit_button = st.form_submit_button(label='予想開始')

# 実行ロジック
if submit_button and race_input:
    with st.spinner('AIが思考中... データ収集、分析、検証を行っています...'):
        try:
            # チャット履歴を持たせない（毎回リセット）
            chat = model.start_chat(history=[])
            
            # プロンプト結合
            full_prompt = SYSTEM_PROMPT + f"\n\nUser Input:\n対象レース: {race_input}\n\nStep 3のPythonコード検証まで確実に実行してください。"
            
            # 送信
            response = chat.send_message(full_prompt)
            
            # 結果表示
            st.markdown(response.text)
            st.success("予想完了！")
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# リセットボタン（画面更新）
if st.button('リセットして次の予想をする'):
    st.rerun()
