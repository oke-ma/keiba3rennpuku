import streamlit as st
import google.generativeai as genai
import pypdf # PDFを読むためのライブラリ

# --- ページ設定 ---
st.set_page_config(page_title="最強3連複AI", page_icon="🐴")

# --- セッション状態の初期化 ---
if "race_name" not in st.session_state:
    st.session_state["race_name"] = ""
if "race_data" not in st.session_state:
    st.session_state["race_data"] = ""

# --- リセット処理関数 ---
def clear_inputs():
    st.session_state["race_name"] = ""
    st.session_state["race_data"] = ""

# --- パスワード保護 ---
MY_PASSWORD = "secret_horse"
password = st.text_input("パスワードを入力してください", type="password")
if password != MY_PASSWORD:
    st.warning("正しいパスワードを入力するとアプリが起動します。")
    st.stop()

# --- タイトル ---
st.title("🐴 最強3連複フォーメーションAI")
st.write("PDFの出馬表、またはテキストデータを元に予想します。")
st.caption("Model: gemini-flash-latest")

# --- API設定 ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-flash-latest")
except Exception as e:
    st.error(f"設定エラー: {e}")
    st.stop()

# --- システムプロンプト ---
SYSTEM_PROMPT = """
# Role Definition
あなたは「3連複フォーメーションのスペシャリスト」です。
ユーザーから提供されたデータ（PDF内容やテキスト）のみを根拠として分析を行ってください。
提供されたデータにない情報は「情報不足」とし、架空のデータを捏造することは厳禁です。

# Execution Protocols
回答は以下のStep順に実行してください。

## Step 1: データの読み取りと整理
ユーザー入力から以下の情報を抽出してください。
1. **人気順とオッズ**: わかる範囲で記述。
2. **馬名と騎手**: 有力馬を中心に。

## Step 2: 思考プロセス (分析)
1. **[Risk Assessment] 人気馬の死角**: 上位人気馬の不安要素。
2. **[Gold Mining] 特注穴馬の発掘**: 3着以内に来そうな穴馬とその理由。

## Step 3: [Formation Structure] 2-4-7 メンバー選定 (19点)
 - Set A (軸): [2頭] 信頼度高。
 - Set B (強相手): [4頭] Aを含み、穴馬1頭必須。
 - Set C (紐): [7頭] Bを含む。
 ※条件: Set A ⊂ Set B ⊂ Set C

## Step 4: 買い目出力
**重要**: 最後に必ず以下を行い、買い目リストを出力してください。
1. Set A, B, C の包含関係チェック。
2. 買い目点数が「19点」になっているか確認。
3. **最終的な買い目（馬名または馬番）をリストアップしてください。**
"""

# --- 入力フォーム ---
with st.form(key='my_form'):
    race_input = st.text_input(
        "① レース名", 
        placeholder="例: 日本ダービー", 
        key="race_name"
    )
    
    # PDFアップロード機能
    st.write("② データ入力（PDF または テキスト貼り付け）")
    uploaded_file = st.file_uploader("出馬表のPDFがあればここにアップロード", type="pdf")
    
    data_input = st.text_area(
        "または、テキストデータをここに貼り付け", 
        height=150,
        placeholder="ネット記事やオッズ表をコピーして貼り付ける場合はこちら。",
        key="race_data"
    )
    
    submit_button = st.form_submit_button(label='予想開始')

# --- 実行ロジック ---
if submit_button:
    # データの準備
    final_data_text = ""
    
    # 1. PDFがアップロードされていたらテキストを抽出
    if uploaded_file is not None:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text()
            final_data_text += f"\n【PDFから読み取った内容】:\n{pdf_text}\n"
            st.info(f"PDFを読み込みました（{len(reader.pages)}ページ）")
        except Exception as e:
            st.error(f"PDFの読み込みに失敗しました: {e}")

    # 2. テキスト欄に入力があれば追加
    if data_input:
        final_data_text += f"\n【貼り付けられたテキスト】:\n{data_input}\n"

    # データがあるか確認してAIへ送信
    if not race_input or not final_data_text:
        st.warning("レース名と、PDFまたはテキストデータのどちらかを入力してください。")
    else:
        with st.spinner('AIがデータを分析中...'):
            try:
                chat = model.start_chat(history=[])
                full_prompt = SYSTEM_PROMPT + f"\n\nUser Input:\n対象レース: {race_input}\n\n提供データ:\n{final_data_text}\n\nStep 4まで確実に実行してください。"
                
                response = chat.send_message(full_prompt)
                st.markdown(response.text)
                st.success("予想完了！")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- リセットボタン ---
st.button('入力をリセット', on_click=clear_inputs)
