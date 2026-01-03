import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os
import urllib.request
import urllib.parse  # ▼ 追加：GASへの送信に必要
from datetime import datetime
import io
import json
import base64

# （不要なスプレッドシート用ライブラリは削除しました）

# ==========================================
# 1. ページ設定
# ==========================================
st.set_page_config(
    page_title="2026年運勢鑑定書 | 占いミザリー",
    page_icon="🔮",
    layout="centered"
)

# ==========================================
# UI完全削除（CSS） + 導入エリア装飾 + トップへ戻るボタン
# ==========================================
hide_st_style = """
    <style>
    /* 既存の非表示設定 */
    header {visibility: hidden !important; height: 0px !important;}
    footer {visibility: hidden !important; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    div[class*="viewerBadge"] {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    .block-container {padding-top: 0rem !important; padding-bottom: 2rem !important;}
    .stApp > header {display: none !important;}
    
    /* ▼▼▼ 興味付けセクションのスタイル ▼▼▼ */
    .intro-box {
        background-color: #fff0f5;
        padding: 25px 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
        border: 2px solid #ffb6c1;
        box-shadow: 0 2px 8px rgba(225, 0, 128, 0.1);
    }
    .intro-head {
        color: #e10080;
        font-weight: bold;
        font-size: 1.3rem;
        margin-bottom: 15px;
        line-height: 1.4;
    }
    .intro-text {
        color: #333;
        font-size: 0.95rem;
        line-height: 1.8;
        max-width: 600px;
        margin: 0 auto;
    }
    .intro-text .question {
        color: #555;
        font-size: 1rem;
        margin: 8px 0;
        display: block;
    }
    .intro-text strong {
        color: #e10080;
        font-weight: bold;
    }
    
    /* ▼▼▼ トップへ戻るリンク ▼▼▼ */
    .top-link {
        text-align: center;
        margin: 30px 0;
        padding: 20px 0;
    }
    .top-link a {
        color: #e10080;
        text-decoration: underline;
        font-size: 0.95rem;
    }
    .top-link a:hover {
        color: #c1006e;
    }
    
    /* ▼▼▼ フッター（著作権表示） ▼▼▼ */
    .custom-footer {
        text-align: center;
        margin: 40px 0 0 0;
        padding: 20px 0 10px 0;
        border-top: 1px solid #e0e0e0;
        color: #666;
        font-size: 0.85rem;
    }
    .custom-footer a {
        color: #666;
        text-decoration: none;
        margin: 0 5px;
    }
    .custom-footer a:hover {
        color: #e10080;
        text-decoration: underline;
    }
    .custom-footer .copyright {
        margin-top: 10px;
        margin-bottom: 0;
        color: #999;
        font-size: 0.8rem;
    }
    
    /* ▼▼▼ 発行ボタンのスタイル ▼▼▼ */
    div[data-testid="stLinkButton"] > a,
    div[data-testid="stLinkButton"] > a button {
        background-color: #e10080 !important;
        color: white !important;
        padding: 18px 30px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stLinkButton"] > a:hover,
    div[data-testid="stLinkButton"] > a button:hover {
        background-color: #c1006e !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(225, 0, 128, 0.3) !important;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# フォント設定
FONT_PATH_ROOT = "ipaexg.ttf"
FONT_DIR = "fonts"
FONT_PATH_FALLBACK = os.path.join(FONT_DIR, "ipaexm.ttf")

# ==========================================
# 2. フォント準備・登録関数
# ==========================================
def get_font_path():
    if os.path.exists(FONT_PATH_ROOT): return FONT_PATH_ROOT
    elif os.path.exists(FONT_PATH_FALLBACK): return FONT_PATH_FALLBACK
    return None

def download_font():
    if not os.path.exists(FONT_DIR): os.makedirs(FONT_DIR)
    if not os.path.exists(FONT_PATH_FALLBACK):
        try:
            urllib.request.urlretrieve("https://raw.githubusercontent.com/making/demo-jasper-report-ja/master/src/main/resources/fonts/ipaexm/ipaexm.ttf", FONT_PATH_FALLBACK)
        except: return False
    return True

def register_font():
    font_path = get_font_path() or (download_font() and get_font_path())
    if font_path:
        try:
            font_name = 'IPAexGothic' if "ipaexg" in font_path.lower() else 'IPAexMincho'
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            return font_name
        except: pass
    return None

# ==========================================
# 3. PDFヘルパー関数
# ==========================================
def draw_wrapped_text(c, text, x, y, max_width, font_name, font_size, line_height, color=HexColor("#333333")):
    c.setFillColor(color)
    c.setFont(font_name, font_size)
    lines, current_line = [], ""
    for char in text:
        if c.stringWidth(current_line + char, font_name, font_size) <= max_width: current_line += char
        else: lines.append(current_line); current_line = char
    if current_line: lines.append(current_line)
    for line in lines:
        if y < 30: break
        c.drawString(x, y, line); y -= line_height
    return y

# ==========================================
# 4. 運勢ロジック
# ==========================================
def calculate_life_path_number(year, month, day):
    def sum_digits(n):
        while n >= 10: n = sum(int(d) for d in str(n))
        return n
    total = sum_digits(year) + sum_digits(month) + sum_digits(day)
    lp = sum_digits(total)
    return total if total in [11, 22, 33] else lp

def get_fortune_data(lp):
    data = {
        "personality": "独自の感性と才能を持ち、周囲に新しい風を吹き込む力を持っています。",
        "overall": ("大吉", "2026年は飛躍の年。これまでの努力が実を結び、新しいステージへと進む準備が整います。"),
        "love": (5, "素晴らしい出会いが期待できる年。パートナーとの絆も深まり、穏やかな愛に包まれるでしょう。"),
        "work": (4, "リーダーシップを発揮する場面が増えそうです。自信を持って決断することで信頼を得られます。"),
        "money": (4, "安定した金運です。自己投資にお金を使うことで、将来的なリターンが大きくなるでしょう。"),
        "health": (3, "忙しさから疲れが溜まりやすい時期。適度な休息とバランスの取れた食事を心がけてください。"),
        "interpersonal": (5, "人脈が広がる年です。新しいコミュニティに参加することで、人生を豊かにする出会いがあります。"),
        "color": "ゴールド", "item": "手帳"
    }
    if lp % 2 == 0:
        data["color"], data["overall"] = "シルバー", ("中吉", "2026年は基盤を固める年。焦らず着実に進むことで、揺るぎない成果を手に入れます。")
    return data

def get_monthly_fortunes(lp):
    return [f"{i}月: 運勢メッセージ..." for i in range(1, 13)]

# ==========================================
# 5. GAS経由でのデータ保存（一番簡単な保存方法）
# ==========================================
def save_data_via_gas(action_type, name, year, month, day, lp):
    # ▼▼▼ 手順1でコピーしたURLをここに貼り付け ▼▼▼
    gas_url = "https://script.google.com/macros/s/AKfycby7er_1XN-G1KmGFvmAo8zHKNfA0_nKYPr5m6SL4pexfoz8M7JgovdtQ6VYxopjSj5C/exec"
    # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
    
    if gas_url == "https://script.google.com/macros/s/AKfycby7er_1XN-G1KmGFvmAo8zHKNfA0_nKYPr5m6SL4pexfoz8M7JgovdtQ6VYxopjSj5C/exec":
        return # URL未設定時は何もしない

    data = {
        "action": action_type,
        "name": name,
        "dob": f"{year}/{month}/{day}",
        "lp": lp
    }
    
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(gas_url, data=json_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as res:
            pass # 送信成功
    except Exception as e:
        st.error(f"⚠️ 保存エラー: {e}")

# ==========================================
# 6. PDF生成
# ==========================================
def create_pdf(name, y, m, d):
    lp = calculate_life_path_number(y, m, d)
    data = get_fortune_data(lp)
    monthly = get_monthly_fortunes(lp)
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    font_name = register_font() or 'Helvetica'
    
    c.setFillColor(HexColor("#FFFBF0")); c.rect(0, 0, width, height, fill=1)
    c.setFillColor(HexColor("#C71585")); c.setFont(font_name, 26); c.drawCentredString(width/2, height-60, "2026年 運勢鑑定書")
    c.setFillColor(HexColor("#C0A060")); c.setFont(font_name, 22); c.drawCentredString(width/2, height-100, f"{name} 様")
    c.setFillColor(HexColor("#333333")); c.setFont(font_name, 12); c.drawCentredString(width/2, height-130, f"生年月日: {y}年{m}月{d}日 (LP: {lp})")
    
    c.setFillColor(HexColor("#C71585")); c.setFont(font_name, 14); c.drawString(50, height-180, "【あなたの本質】")
    draw_wrapped_text(c, data["personality"], 50, height-200, width-100, font_name, 11, 18)
    
    c.showPage()
    c.setFillColor(HexColor("#FFFBF0")); c.rect(0, 0, width, height, fill=1)
    c.setFillColor(HexColor("#C71585")); c.setFont(font_name, 20); c.drawCentredString(width/2, height-60, "月別運勢カレンダー")
    
    y_pos = height-100
    for txt in monthly:
        y_pos = draw_wrapped_text(c, txt, 50, y_pos, width-100, font_name, 12, 25) - 15
        
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 7. アプリUI
# ==========================================
st.markdown("""
    <style>
    .title-container {text-align: center; padding-bottom: 20px; border-bottom: 2px solid #C0A060; margin-bottom: 30px;}
    .main-title {font-family: "Helvetica", sans-serif; font-weight: bold; font-size: 2.5rem; background: linear-gradient(45deg, #FFB6C1, #C71585); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .sub-title {font-size: 1.2rem; color: #C0A060; font-weight: bold;}
    div.stButton > button {background-color: #C71585; color: white; border-radius: 10px; padding: 10px 20px; border:none;}
    </style>
    <div class="title-container">
        <div class="sub-title">✨ 数秘術で紐解くあなたの未来 ✨</div>
        <div class="main-title">2026年 運勢鑑定書</div>
    </div>
""", unsafe_allow_html=True)

query_params = st.query_params
is_paid = query_params.get("paid") == "true" or query_params.get("checkout") == "success"

if 'user_name' not in st.session_state: st.session_state.update({k: v for k, v in zip(['user_name','birth_year','birth_month','birth_day'], ['', 2000, 1, 1])})
if 'pdf_data' not in st.session_state: st.session_state.pdf_data = None
if 'pdf_filename' not in st.session_state: st.session_state.pdf_filename = None

if not is_paid:
    # ▼▼▼ 興味を引くコンテンツセクション ▼▼▼
    st.markdown("""
    <div class="intro-box">
        <div class="intro-head">🔮 2026年、あなたを待つ運命とは？</div>
        <div class="intro-text">
            <span class="question">「来年はどんな年になる？」</span>
            <span class="question">「恋愛や仕事の転機はいつ？」</span>
            <br>
            あなたの生年月日から導き出される特別な数字で、<strong>2026年の運勢バイオリズム</strong>を読み解きましょう。
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ▲▲▲ ここまで ▲▲▲

    st.info("👋 まずは無料プレビューで、あなたの「数字」を知ってください。")
    
    with st.form("preview"):
        # セッションステートから値を取得（既に入力済みの場合は自動反映）
        name_pre = st.text_input("お名前", value=st.session_state.user_name if st.session_state.user_name else "")
        c1, c2, c3 = st.columns(3)
        y_pre = c1.number_input("年", 1900, 2025, st.session_state.birth_year if st.session_state.birth_year else 2000)
        m_pre = c2.number_input("月", 1, 12, st.session_state.birth_month if st.session_state.birth_month else 1)
        d_pre = c3.number_input("日", 1, 31, st.session_state.birth_day if st.session_state.birth_day else 1)
        
        if st.form_submit_button("鑑定結果の一部を見る"):
            if name_pre:
                # セッションステートに保存（完全版鑑定書フォームに自動反映される）
                st.session_state.update({
                    'user_name': name_pre,
                    'birth_year': y_pre,
                    'birth_month': m_pre,
                    'birth_day': d_pre
                })
                
                lp = calculate_life_path_number(y_pre, m_pre, d_pre)
                preview_data = get_fortune_data(lp)
                
                # ▼ GAS経由でデータを保存
                save_data_via_gas("無料プレビュー", name_pre, y_pre, m_pre, d_pre, lp)
                
                # 興味を引く見出しを表示
                st.markdown("---")
                st.markdown(f"### {name_pre} 様の2026年運勢")
                st.markdown(f"**ライフパスナンバー: {lp}**")
                
                st.markdown("#### ✨ あなたの2026年はこんな年に！")
                st.markdown(f"**総合運: {preview_data['overall'][0]}**")
                st.markdown(f"{preview_data['overall'][1]}")
                
                st.markdown("#### 💫 気になる運勢の一部")
                st.markdown(f"**恋愛運**: {'★' * preview_data['love'][0] + '☆' * (5 - preview_data['love'][0])}")
                st.markdown(f"{preview_data['love'][1]}")
                
                st.markdown("---")
                st.warning("🔒 詳しい結果（全運勢・月別カレンダー・ラッキーアイテムなど）をご覧になるには、完全版の購入が必要です。")
                
                # 完全版へのアンカーリンク
                st.markdown("""
                <div style="text-align: center; margin: 25px 0;">
                    <a href="javascript:void(0);" onclick="document.querySelector('#完全版鑑定書').scrollIntoView({behavior: 'smooth'});" style="color: #e10080; text-decoration: underline; font-weight: bold; font-size: 1rem;">
                        完全版鑑定書を見る
                    </a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("お名前を入力してください")

    st.markdown("---")
    # アンカー用のIDを追加
    st.markdown('<div id="完全版鑑定書"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="white-space: nowrap;">💎 完全版鑑定書 <small style="font-size: 0.7em;">(PDF)</small></h2>', unsafe_allow_html=True)
    with st.form("pay"):
        # 無料プレビューで入力した情報を自動的に反映
        name = st.text_input("お名前", value=st.session_state.user_name if st.session_state.user_name else "", key="p_name")
        c1, c2, c3 = st.columns(3)
        y = c1.number_input("年", 1900, 2025, st.session_state.birth_year if st.session_state.birth_year else 2000, key="p_y")
        m = c2.number_input("月", 1, 12, st.session_state.birth_month if st.session_state.birth_month else 1, key="p_m")
        d = c3.number_input("日", 1, 31, st.session_state.birth_day if st.session_state.birth_day else 1, key="p_d")
        if st.form_submit_button("情報を保存して決済へ"):
            st.session_state.update({'user_name': name, 'birth_year': y, 'birth_month': m, 'birth_day': d})
            st.success("✅ 保存しました。下のボタンから決済してください。")
            
    # ▼▼▼ Stripeリンク ▼▼▼
    st.link_button("👉 500円で発行する", "https://buy.stripe.com/28E4gzcga8yma9b1FJcfT1k", type="primary", use_container_width=True)

else:
    st.success("✅ ご購入ありがとうございます！")
    with st.form("final"):
        st.write("### 📄 発行フォーム")
        name = st.text_input("お名前", value=st.session_state.user_name)
        c1, c2, c3 = st.columns(3)
        y = c1.number_input("年", 1900, 2025, st.session_state.birth_year)
        m = c2.number_input("月", 1, 12, st.session_state.birth_month)
        d = c3.number_input("日", 1, 31, st.session_state.birth_day)
        submitted = st.form_submit_button("✨ PDFを作成する", use_container_width=True)

    if submitted and name:
        with st.spinner("生成中..."):
            try:
                pdf = create_pdf(name, y, m, d)
                pdf_bytes = pdf.getvalue()
                st.session_state.pdf_data = pdf_bytes
                st.session_state.pdf_filename = f"運勢鑑定書_{name}.pdf"
                
                # ログ保存：購入完了
                # ▼ GAS経由でデータを保存
                save_data_via_gas("購入・発行", name, y, m, d, calculate_life_path_number(y, m, d))
                
                st.success("完了しました！下のバーからダウンロードできます。")
            except Exception as e:
                st.error(f"エラー: {e}")

# ==========================================
# 8. トップへ戻るリンク + フッター（著作権表示）
# ==========================================
st.markdown("""
    <div class="top-link">
        <a href="https://mizary.com/" target="_blank" rel="noopener noreferrer">トップへ戻る</a>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="custom-footer">
        <div>
            <a href="https://mizary.com/tokusyouhou/" target="_blank" rel="noopener noreferrer">特定商取引法に基づく表記</a> | 
            <a href="https://mizary.com/privacy/" target="_blank" rel="noopener noreferrer">プライバシーポリシー</a>
        </div>
        <div class="copyright">© 2026 占いミザリー</div>
    </div>
""", unsafe_allow_html=True)