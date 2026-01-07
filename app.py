import streamlit as st
import google.generativeai as genai
import pypdf

# --- ページ設定 ---
st.set_page_config(page_title="最強3連複AI", page_icon="🐴")

# --- セッション状態の初期化 ---
if "race_data" not in st.session_state:
    st.session_state["race_data"] = ""

# --- リセット処理関数 ---
def clear_inputs():
    st.session_state["race_data"] = ""

# --- パスワード保護 ---
MY_PASSWORD = "secret_horse"
password = st.text_input("パスワードを入力してください", type="password")
if password != MY_PASSWORD:
    st.warning("正しいパスワードを入力するとアプリが起動します。")
    st.stop()

# --- タイトル ---
st.title("🐴 最強3連複フォーメーションAI")
st.write("PDFまたはテキストデータを入力してください。レース名も自動で読み取ります。")
st.caption("Model: gemini-flash-latest")

# --- API設定 ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-flash-latest")
except Exception as e:
    st.error(f"設定エラー: {e}")
    st.stop()

# --- システムプロンプト (消去法＋バイアス排除版) ---
# チャット表示バグ回避のため、コードブロック記号を分割して記述しています
SYSTEM_PROMPT = """
# Role Definition
あなたは「3連複フォーメーションのスペシャリスト」です。
今回は**「消去法（Negative Screening）」**を最重視したアプローチで予想を行います。
まず「買えない馬」を論理的に排除し、残った精鋭のみで買い目を構築してください。

# Absolute Reality Grounding
1. ユーザー提供データ（PDF/テキスト）のみを根拠とする。
2. 想像や架空のデータ補完は禁止。

# Execution Protocols (実行プロトコル)
回答は以下のStep順に実行し、各Stepの完了条件を満たすまで次へ進まないこと。

## Step 1: 環境認識とデータ整理
提供されたデータから、出走馬、オッズ、コース条件、馬場状態を整理せよ。

## Step 2: ネガティブスクリーニング (除外馬の選定)
**ここが最も重要です。** 全出走馬の中から「馬券に絡む確率が極めて低い馬」を特定し、除外してください。

**【重要制約: 人気バイアスの完全排除】**
* この選定プロセスにおいては、**「現在の人気順（オッズ）」を完全に無視**すること。
* 1番人気であっても、適性や状態に不安があれば容赦なく「除外」せよ。
* 逆に最低人気であっても、減点材料が少なければ安易に除外してはならない。
* 判断基準は「能力・適性・展開・騎手・血統」のみとし、「人気だから」という理由は一切認めない。

以下のフォーマットで出力すること。
**【除外する馬とその理由】**
* **[馬名]**: [除外理由を具体的に記述] (例: 人気だが大外枠でこのコース実績がない、過剰人気、前走フロック等)
* ...

## Step 3: ポジティブセレクション & 穴馬発掘
Step 2で**除外されずに残った馬**の中から、以下の注目馬を選定せよ。
1.  **[Risk Assessment] 人気馬の死角**: 残った人気馬（1~3番人気）の中に不安要素があれば指摘。
2.  **[Gold Mining] 特注穴馬**: 残った馬の中で、オッズ以上の実力を持つ「特注穴馬」を1頭以上選抜。

## Step 4: [Formation Structure] 2-4-7 メンバー選定 (19点)
**Step 2で生き残った馬のみ**を使用して、以下のフォーメーションを構築せよ。
* **Set A (1列目 / 軸)**: [2頭] 最も信頼できる2頭。
* **Set B (2列目 / 強相手)**: [4頭] Set Aを含む + 特注穴馬を含める。
* **Set C (3列目 / 紐)**: [7頭] Set Bを含む。

## Step 5: Pythonによる論理整合性チェック
**※重要: 必ずPythonコードを実行して検証すること。**
Step 2で除外した馬が含まれていないか、包含関係は正しいか確認し、最終的な買い目を出力せよ。
""" + "\n```python\n" + """
def calculate_formation(set_a, set_b, set_c):
    # 1. 包含関係の診断
    missing_in_b = set(set_a) - set(set_b)
    missing_in_c = set(set_b) - set(set_c)
    
    if missing_in_b:
        return False, f"Error: 1列目の馬 {missing_in_b} が2列目に含まれていません。", []
    if missing_in_c:
        return False, f"Error: 2列目の馬 {missing_in_c} が3列目に含まれていません。", []

    # 2. 買い目点数の計算 (1列目1頭以上、2列目2頭以上のJRA標準フォーメーション)
    import itertools
    valid_bets = set()
    
    for comb in itertools.combinations(set_c, 3):
        bet_set = set(comb)
        count_a = len(bet_set.intersection(set_a))
        count_b = len(bet_set.intersection(set_b))
        
        if count_a >= 1 and count_b >= 2:
            valid_bets.add(tuple(sorted(list(bet_set))))
            
    point_count = len(valid_bets)
    return True, point_count, sorted(list(valid_bets))
""" + "\n```\n"

# --- 入力フォーム ---
with st.form(key='my_form'):
    st.write("▼ データ入力（PDF または テキスト貼り付け）")
    
    # PDFアップロード
    uploaded_file = st.file_uploader("出馬表のPDFがあればここにアップロード", type="pdf")
    
    # テキスト貼り付け
    data_input = st.text_area(
        "または、テキストデータをここに貼り付け", 
        height=200,
        placeholder="ここに出馬表やオッズのテキストを貼り付けてください。\nレース名もここに含まれていればAIが読み取ります。",
        key="race_data"
    )
    
    submit_button = st.form_submit_button(label='予想開始')

# --- 実行ロジック ---
if submit_button:
    # データの準備
    final_data_text = ""
    
    # 1. PDF読み込み
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

    # 2. テキスト追加
    if data_input:
        final_data_text += f"\n【貼り付けられたテキスト】:\n{data_input}\n"

    # 入力チェック
    if not final_data_text:
        st.warning("PDFをアップロードするか、テキストデータを貼り付けてください。")
    else:
        with st.spinner('AIが「消去法」を実行し、厳選予想を作成中...'):
            try:
                chat = model.start_chat(history=[])
                # プロンプト結合
                full_prompt = SYSTEM_PROMPT + f"\n\nUser Input Data:\n{final_data_text}\n\nStep 5の検証と買い目出力まで確実に実行してください。"
                
                response = chat.send_message(full_prompt)
                st.markdown(response.text)
                st.success("予想完了！")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- リセットボタン ---
st.button('入力をリセット', on_click=clear_inputs)
