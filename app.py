import streamlit as st
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(page_title="最強3連複AI", page_icon="🐴")

# --- セッション状態の初期化（リセット機能用） ---
if "race_name" not in st.session_state:
    st.session_state["race_name"] = ""
if "race_data" not in st.session_state:
    st.session_state["race_data"] = ""

# --- リセット処理関数 ---
def clear_inputs():
    st.session_state["race_name"] = ""
    st.session_state["race_data"] = ""

# --- パスワード保護ブロック ---
MY_PASSWORD = "secret_horse"
password = st.text_input("パスワードを入力してください", type="password")
if password != MY_PASSWORD:
    st.warning("正しいパスワードを入力するとアプリが起動します。")
    st.stop()

# --- タイトルと説明 ---
st.title("🐴 最強3連複フォーメーションAI")
st.write("データ（出馬表・オッズ）を貼り付けることで、AIが論理的に19点の買い目を導き出します。")
st.caption("Model: gemini-flash-latest")

# --- APIキーの設定 ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("APIキー設定エラー。Secretsを確認してください。")
    st.stop()

# --- モデル設定 ---
try:
    model = genai.GenerativeModel("gemini-flash-latest")
except Exception as e:
    st.error(f"モデル設定エラー: {e}")
    st.stop()

# --- システムプロンプト (データ分析特化型) ---
SYSTEM_PROMPT = """
# Role Definition
あなたは「3連複フォーメーションのスペシャリスト」です。
ユーザーから提供された「レース情報（出馬表・オッズなど）」のみを根拠（Absolute Fact）として分析を行ってください。
インターネット検索はできないため、提供されたテキストデータだけを頼りに論理を展開してください。
提供されたデータにない情報は「情報不足」として扱ってください。架空の馬名やデータを捏造することは厳禁です。

# Execution Protocols
回答は以下のStep順に実行してください。

## Step 1: データの読み取りと整理
ユーザーが入力したテキストデータから、以下の情報を整理して抽出してください。
1. **人気順とオッズ**: 1番人気〜下位人気までの並び。
2. **馬名と騎手**: 主要な有力馬。

## Step 2: 思考プロセス (分析)
1. **[Risk Assessment] 人気馬の死角**: 上位人気（1~3番人気）の中で、オッズの割に不安がある馬、またはデータ上で強調材料が少ない馬を指摘。
2. **[Gold Mining] 特注穴馬の発掘**: 中位〜下位人気の中で、3着以内に食い込む可能性がある馬を選定し、その理由（オッズ妙味など）を述べる。

## Step 3: [Formation Structure] 2-4-7 メンバー選定 (19点)
論理に基づき、以下の枠組みで馬を選定してください。
 - Set A (軸): [2頭] 最も信頼できる2頭。
 - Set B (強相手): [4頭] Aを含み、**穴馬1頭**以上を必ず含む。
 - Set C (紐): [7頭] Bを含む。
 ※条件: Set A ⊂ Set B ⊂ Set C

## Step 4: 買い目出力
**重要**: 最後に必ず以下の検証を行い、買い目リストを出力してください。
1. Set A, B, C の包含関係チェック。
2. 買い目点数が「19点」になっているか確認。
3. **最終的な買い目（数字の組み合わせではなく、馬名または馬番）をリストアップしてください。**
"""

# --- 入力フォーム ---
with st.form(key='my_form'):
    # session_stateを使って値を管理（key引数を指定）
    race_input = st.text_input(
        "① レース名", 
        placeholder="例: 日本ダービー", 
        key="race_name"
    )
    
    data_input = st.text_area(
        "② 出馬表・オッズデータをここに貼り付け（重要！）", 
        height=200,
        placeholder="ここにnetkeibaやJRAのサイトから、出馬表やオッズのテキストをコピーして貼り付けてください。\n情報が多いほど精度が上がります。",
        key="race_data"
    )
    
    submit_button = st.form_submit_button(label='予想開始')

# --- 実行ロジック ---
if submit_button:
    if not race_input or not data_input:
        st.warning("レース名とデータの両方を入力してください。")
    else:
        with st.spinner('AIが提供データを分析中...'):
            try:
                chat = model.start_chat(history=[])
                
                # ユーザーの入力データをすべてプロンプトに含める
                full_prompt = SYSTEM_PROMPT + f"\n\nUser Input Data:\n【レース名】: {race_input}\n\n【提供データ】:\n{data_input}\n\nStep 4まで確実に実行してください。"
                
                response = chat.send_message(full_prompt)
                
                st.markdown(response.text)
                st.success("分析完了！")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- リセットボタン ---
# on_click引数で、ボタンを押した瞬間に中身を空にする関数を呼び出す
st.button('入力をリセット', on_click=clear_inputs)
