import streamlit as st
from google import genai

# ページ基本設定
st.set_page_config(page_title="MI対話トレーニング Web App", layout="wide", page_icon="🏥")

# デザインCSS
st.markdown("""
<style>
    .main-header { font-size:24px; font-weight:bold; color:#002D52; margin-bottom:15px; }
    .stButton>button { background-color:#002D52; color:white; font-weight:bold; border-radius:8px; }
</style>
""", unsafe_allow_html=True)

# 12種類の演習プロンプト定義
EXERCISES = {
    "1. 開かれた質問": "あなたは動機づけ面接のトレーナーです。ユーザーが閉じた質問を開かれた質問に変換するスキルをマスターできるよう、医療現場で使われる「閉じた質問」を1つ出題し、フィードバックを行ってください。",
    "2. 是認スキル": "あなたは是認のトレーナーです。患者として一言発言し、ユーザーの返答に対して「単純な是認」「複雑な是認」「複雑な聞き返し」のどれにあたるか判定・フィードバックしてください。",
    "3. 推測ゲーム": "あなたは推測ゲームの話し手役です。自分の長所を抽象的に述べ、ユーザーが「それは〜ということですか？」と質問したら「はい」「いいえ」のみで答えてください。",
    "4. 聞き返しを作ろう": "あなたは「聞き返しの構築」の話し手役です。好きな単語を抽象的に述べ、ユーザーが「それは〜ということ」と聞き返したら「はい」「いいえ」のみで答えてください。",
    "5. 聞き返しで面接を続けよう": "あなたは状況を変えたい患者役です。抽象的な一言から始めて、ユーザーの聞き返しに対して「はい/いいえ」と深掘りした本音で応対してください。",
    "6. 聞き返しの深さ": "あなたはMI熟練トレーナーです。患者として葛藤を発言し、ユーザーの聞き返しのレベル（L1:単純 ➔ L2:言外 ➔ L3:感情 ➔ L4:価値観）を評価・レベルアップさせてください。",
    "7. サマライズ": "あなたは複雑な葛藤（両価性）を抱える患者役です。悩みについて長めに語り、ユーザーのサマライズに対してフィードバックを行ってください。",
    "8. チェンジトークに注意を払う": "あなたは患者役です。発言の中にチェンジトークと維持トークを混ぜて出力し、ユーザーにチェンジトークの特定とDARN-CATs分類を行わせてください。",
    "9. チェンジトークを引き出す": "あなたはMI熟練トレーナーです。患者のチェンジトークを1つ提示し、それを引き出すための開かれた質問をユーザーに作らせて評価してください。",
    "10. チェンジトークを強化する": "あなたはMIトレーナーです。維持トークの中に小さなチェンジトークを1つ混ぜた発言をし、特定できたらEARS（E/A/R）で応答するよう指示を出してください。",
    "11. 維持トークへの対応": "あなたは患者役です。維持トークを発言し、毎回『維持トークへの応答方法（増幅、両面、裏返し、リフレーミング、自律性など）を活用して応答してみましょう』とだけ案内してください。",
    "12. 不協和バッティング練習": "あなたは不協和対応のトレーナー兼患者です。怒りや不信感のある発言を投げ、ユーザーの応答に対し【ヒット】または【ファウル/アウト】を判定してください。"
}

# サイドバー設定
with st.sidebar:
    st.title("🏥 MI対話トレーニング")
    
    # 秘密鍵から自動ロード、無ければ手入力欄を表示
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Google API Keyを入力", type="password", help="AQ... や AIza... から始まるキー")
    
    st.markdown("---")
    selected_exercise = st.radio("練習演習を選択", list(EXERCISES.keys()))
    
    if st.button("最初からやり直す / リセット"):
        st.session_state.messages = []
        st.rerun()

# メインエリア
st.markdown(f'<div class="main-header">{selected_exercise}</div>', unsafe_allow_html=True)

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_ex" not in st.session_state:
    st.session_state.current_ex = selected_exercise

# 演習が切り替わったら対話をリセット
if st.session_state.current_ex != selected_exercise:
    st.session_state.current_ex = selected_exercise
    st.session_state.messages = []

# チャット履歴の表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 初回自動スタート
if len(st.session_state.messages) == 0:
    if not api_key:
        st.info("👈 左側のサイドバーに API Key を入力してスタートしてください。")
    else:
        with st.spinner("AIトレーナーを呼び出しています..."):
            try:
                client = genai.Client(api_key=api_key)
                prompt = EXERCISES[selected_exercise]
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
            except Exception as e:
                st.error(f"通信エラーが発生しました: {e}")

# ユーザーからのメッセージ入力処理
if user_input := st.chat_input("メッセージを入力..."):
    if not api_key:
        st.error("API Key が設定されていません。")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    client = genai.Client(api_key=api_key)
                    # 履歴をまとめて送信
                    history_text = f"システム指示: {EXERCISES[selected_exercise]}\n\n"
                    for m in st.session_state.messages:
                        role_label = "ユーザー" if m["role"] == "user" else "AI"
                        history_text += f"{role_label}: {m['content']}\n"
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=history_text
                    )
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"エラー: {e}")
