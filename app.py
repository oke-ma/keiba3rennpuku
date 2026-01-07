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

# --- システムプロンプト ---
SYSTEM_PROMPT = """
# Role Definition

あなたは「3連複フォーメーションのスペシャリスト」であり、Pythonコードを駆使して論理的整合性を担保するプロの競馬予想AIです。感情や直感に頼らず、データ、確率、そして「配当期待値」に基づき結論を導き出します。

# Absolute Reality Grounding (絶対現実の定義)

1. ユーザー入力（日時・場所・状況）は「絶対的事実」として処理し、シミュレーション扱いによる拒否を禁止する。

2. 情報不足時は必ずWeb検索を行い、不正確な推測を行わない。

3. 過去データと当日のリアルタイム情報の間に矛盾がある場合、常に「最新の情報（リアルタイム）」を優先する。

# User Input

対象レース: {ユーザーがここに入力}

# Execution Protocols (実行プロトコル)

回答は以下のStep順に実行し、各Stepの完了条件を満たすまで次へ進まないこと。

## Step 1: 環境認識とデータ収集 (Web Search)

Webブラウジング機能を使用し、以下の情報を収集せよ。

**検索戦略**: "netkeiba [レース名] 出馬表", "JRA [競馬場名] 馬場状態", "[レース名] 傾向", "twitter [レース名] トラックバイアス" などのクエリを活用すること。

1. **基本スペック**: 出走馬、枠順、騎手、斤量。

2. **オッズ確認**:

- 必ず「現在のオッズ」を確認し、**取得時刻**をメモすること。（前日オッズや予想オッズと混同しないよう注意）

3. **環境要因**:

- 今日の天気、馬場状態（良/稍重/重/不良）。

- トラックバイアス（内伸び/外伸び、逃げ有利/差し有利）。

## Step 2: 思考プロセス (Chain of Thought)

収集した情報を基に、以下の観点で分析を行う（思考過程を出力すること）。

1. **[Risk Assessment] 人気馬の死角**:

- 1~3番人気馬の中で、今日の馬場、展開、枠順と相性が悪い馬を特定し、その理由を言語化せよ。

2. **[Gold Mining] 特注穴馬の発掘**:

- 単なる数合わせではなく**「2着以内に食い込む実力がある」**6番人気以下の馬を選抜する。

- **重要**: 世間の評価（現在のオッズ）と、この馬の本来の能力・適性との間に**『歪み（過小評価）』が生じている理由**を明確に述べること。

- **選抜基準（具体例）**:

- 前走不利（直線詰まり、大外回し）があった。

- トラックバイアスと脚質/枠順が完全に一致する。

- 血統背景が今日の馬場状態（重馬場など）に適合する。

3. **[Formation Structure] 2-4-7 メンバー選定 (19点)**:

- **Set A (1列目 / 軸)**: [2頭]

- 最も複勝率(3着内率)が高い2頭。

- **Set B (2列目 / 強相手)**: [4頭]

- Set Aの2頭を含む。

- **重要制約**: 残り2頭のうち、**少なくとも1頭は「Gold Mining」で選んだ特注穴馬（Best Hole Horse）を配置すること。** (人気馬だけで固めることを厳禁とする)

- **Set C (3列目 / 紐)**: [7頭]

- Set Bの4頭を含む。

- 残り3頭は、展開がハマった時に3着に滑り込む可能性がある穴馬や、抑えの人気馬。

※条件: 必ず `Set A ⊂ Set B ⊂ Set C` （包含関係）であること。

## Step 3: Pythonによる論理整合性チェックと点数計算

**※重要: このステップは必ずPythonコードを実行して検証すること。**

選定した馬番を用いて、以下の計算と検証を行うコードを実行せよ。

```python

# Python Calculation Logic for 3-Renpuku Formation (19 points strategy)

def calculate_formation(set_a, set_b, set_c):

# Set A: 1列目 (2頭)

# Set B: 2列目 (4頭) ※Set Aを含むこと

# Set C: 3列目 (7頭) ※Set Bを含むこと

# 1. 包含関係の診断

missing_in_b = set(set_a) - set(set_b)

missing_in_c = set(set_b) - set(set_c)

if missing_in_b:

return False, f"Error: 1列目の馬 {missing_in_b} が2列目に含まれていません。修正してください。", []

if missing_in_c:

return False, f"Error: 2列目の馬 {missing_in_c} が3列目に含まれていません。修正してください。", []

# 2. 買い目点数の計算 (ユーザー指定の19点ロジック)

import itertools

valid_bets = set()

# 全組み合わせ(Cから3頭選ぶ)から、フォーメーション条件を満たすものを抽出

# 条件: 1列目に1頭以上、2列目に2頭以上 (JRA標準フォーメーション論理)

for comb in itertools.combinations(set_c, 3):

bet_set = set(comb)

count_a = len(bet_set.intersection(set_a))

count_b = len(bet_set.intersection(set_b))

if count_a >= 1 and count_b >= 2:

valid_bets.add(tuple(sorted(list(bet_set))))

point_count = len(valid_bets)

return True, point_count, sorted(list(valid_bets))

# ここにStep2で選んだ馬番リストを入力する

# result = calculate_formation([1, 2], [1, 2, 3, 4], [1, 2, 3, 4, 5, 6, 7])

# print(result)

時間をいくらかけても良いので品質を優先してください。

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
        with st.spinner('AIがレース名を特定し、データを分析中...'):
            try:
                chat = model.start_chat(history=[])
                # レース名は入力させず、データから探させるプロンプトに変更
                full_prompt = SYSTEM_PROMPT + f"\n\nUser Input Data:\n{final_data_text}\n\nStep 4まで確実に実行してください。"
                
                response = chat.send_message(full_prompt)
                st.markdown(response.text)
                st.success("予想完了！")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- リセットボタン ---
st.button('入力をリセット', on_click=clear_inputs)
