import streamlit as st
import google.generativeai as genai

st.title("🛠 API接続診断")

# 1. APIキーの確認
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success("✅ APIキーは認識されています")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"❌ APIキーの設定エラー: {e}")
    st.stop()

# 2. 利用可能なモデル一覧を取得
st.write("---")
st.write("Googleのサーバーに「使えるモデル」を問い合わせ中...")

try:
    # モデル一覧を取得して表示
    models = genai.list_models()
    
    found_models = []
    st.write("▼ 取得できたモデル一覧:")
    
    for m in models:
        # コンテンツ生成（文章作成）に対応しているモデルだけを表示
        if 'generateContent' in m.supported_generation_methods:
            st.code(m.name) # 画面にモデル名を表示
            found_models.append(m.name)
            
    if not found_models:
        st.warning("⚠️ 接続はできましたが、利用可能なモデルが1つも返ってきませんでした。")
        st.info("可能性: APIキーを作成したGoogleアカウントで、Generative AIの利用規約に同意していない可能性があります。Google AI Studioを開き直してみてください。")
    else:
        st.balloons()
        st.success("🎉 接続成功！ 上記のリストにある名前を使えば必ず動きます。")

except Exception as e:
    st.error("❌ Googleサーバーとの通信エラー")
    st.write(f"エラー詳細: {e}")
