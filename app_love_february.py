import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os
import urllib.request
import urllib.parse
from datetime import datetime
import io
import json
import base64

# ==========================================
# 0. 設定ファイル読み込み
# ==========================================
def load_config(config_path="config_love_february.json"):
    """設定ファイルを読み込む関数"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"設定ファイル '{config_path}' が見つかりません。")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"設定ファイルのJSON形式が正しくありません: {e}")
        st.stop()

# 設定を読み込む（2月限定恋愛占い用）
CONFIG = load_config("config_love_february.json")

# ==========================================
# 1. ページ設定
# ==========================================
st.set_page_config(
    page_title=CONFIG.get("app_title", "2月限定 恋愛運勢鑑定書"),
    page_icon=CONFIG.get("app_icon", "💕"),
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
        margin: 40px 0 20px 0;
        padding: 30px 20px;
        border-top: 1px solid #e0e0e0;
        color: #666;
        font-size: 0.9rem;
        line-height: 1.8;
    }
    .custom-footer > div {
        margin-bottom: 15px;
    }
    .custom-footer > div:last-child {
        margin-bottom: 0;
    }
    .custom-footer strong {
        display: block;
        margin-bottom: 8px;
        color: #333;
        font-size: 0.95rem;
    }
    .custom-footer a {
        color: #666;
        text-decoration: none;
        margin: 0 8px;
        transition: color 0.3s ease;
    }
    .custom-footer a:hover {
        color: #e10080;
        text-decoration: underline;
    }
    .custom-footer .copyright {
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px solid #e0e0e0;
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
# 4. 運勢ロジック（設定ファイルから読み込み）
# ==========================================
def calculate_life_path_number(year, month, day):
    def sum_digits(n):
        while n >= 10: n = sum(int(d) for d in str(n))
        return n
    total = sum_digits(year) + sum_digits(month) + sum_digits(day)
    lp = sum_digits(total)
    return total if total in [11, 22, 33] else lp

def get_fortune_data(lp):
    """設定ファイルから運勢データを取得"""
    lp_str = str(lp)
    life_path_config = CONFIG.get("life_path_descriptions", {})
    
    # 特定のLPの設定がある場合はそれを使用、なければデフォルトを使用
    if lp_str in life_path_config:
        lp_data = life_path_config[lp_str]
    else:
        lp_data = life_path_config.get("default", {})
    
    # データ構造を変換（後方互換性のため）
    data = {
        "personality": lp_data.get("personality", ""),
        "lp_description": lp_data.get("lp_description", ""),
        "overall": (
            lp_data.get("overall", {}).get("rank", "中吉"),
            lp_data.get("overall", {}).get("description", "")
        ),
        "love": (
            lp_data.get("love", {}).get("stars", 3),
            lp_data.get("love", {}).get("description", "")
        ),
        "work": (
            lp_data.get("work", {}).get("stars", 3),
            lp_data.get("work", {}).get("description", "")
        ),
        "money": (
            lp_data.get("money", {}).get("stars", 3),
            lp_data.get("money", {}).get("description", "")
        ),
        "health": (
            lp_data.get("health", {}).get("stars", 3),
            lp_data.get("health", {}).get("description", "")
        ),
        "color": lp_data.get("color", ""),
        "item": lp_data.get("item", "")
    }
    return data

def get_monthly_fortunes(lp):
    """設定ファイルから月別運勢を取得"""
    return CONFIG.get("monthly_fortunes", [])

# ==========================================
# 5. GAS経由でのデータ保存（修正版）
# ==========================================
def save_data_via_gas(action_type, name, year, month, day, lp):
    """設定ファイルからGAS URLを取得してデータを保存"""
    gas_url = CONFIG.get("gas_url", "")

    data = {
        "action": action_type,
        "name": name,
        "dob": f"{year}/{month}/{day}",
        "lp": lp
    }
    
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(gas_url, data=json_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as res:
            pass # 送信成功
    except Exception as e:
        # 保存エラーは静かに失敗（バックグラウンド処理のため、ユーザーには表示しない）
        pass

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
    pdf_title = CONFIG.get("pdf_title", "2月限定 恋愛運勢鑑定書")
    c.setFillColor(HexColor("#C71585")); c.setFont(font_name, 26); c.drawCentredString(width/2, height-60, pdf_title)
    c.setFillColor(HexColor("#C0A060")); c.setFont(font_name, 22); c.drawCentredString(width/2, height-100, f"{name} 様")
    c.setFillColor(HexColor("#333333")); c.setFont(font_name, 12); c.drawCentredString(width/2, height-130, f"生年月日: {y}年{m}月{d}日")
    c.setFillColor(HexColor("#333333")); c.setFont(font_name, 12); c.drawCentredString(width/2, height-150, f"ライフパスナンバー: {lp}")
    
    # ライフパスナンバーの説明
    y_pos = height-180
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 11)
    y_pos = draw_wrapped_text(c, data.get("lp_description", ""), 50, y_pos, width-100, font_name, 11, 18)
    
    # 【総合運】
    y_pos -= 20
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 14)
    c.drawString(50, y_pos, "【総合運】")
    y_pos -= 20
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    c.drawString(50, y_pos, data["overall"][0])
    y_pos -= 20
    c.setFont(font_name, 11)
    y_pos = draw_wrapped_text(c, data["overall"][1], 50, y_pos, width-100, font_name, 11, 18)
    
    # 【恋愛運】
    y_pos -= 20
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 14)
    c.drawString(50, y_pos, "【恋愛運】")
    y_pos -= 20
    stars = "★" * data["love"][0] + "☆" * (5 - data["love"][0])
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    c.drawString(50, y_pos, stars)
    y_pos -= 20
    c.setFont(font_name, 11)
    y_pos = draw_wrapped_text(c, data["love"][1], 50, y_pos, width-100, font_name, 11, 18)
    
    # 【仕事運】
    y_pos -= 20
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 14)
    c.drawString(50, y_pos, "【仕事運】")
    y_pos -= 20
    stars = "★" * data["work"][0] + "☆" * (5 - data["work"][0])
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    c.drawString(50, y_pos, stars)
    y_pos -= 20
    c.setFont(font_name, 11)
    y_pos = draw_wrapped_text(c, data["work"][1], 50, y_pos, width-100, font_name, 11, 18)
    
    # 【金運】
    y_pos -= 20
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 14)
    c.drawString(50, y_pos, "【金運】")
    y_pos -= 20
    stars = "★" * data["money"][0] + "☆" * (5 - data["money"][0])
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    c.drawString(50, y_pos, stars)
    y_pos -= 20
    c.setFont(font_name, 11)
    y_pos = draw_wrapped_text(c, data["money"][1], 50, y_pos, width-100, font_name, 11, 18)
    
    # 【健康運】
    y_pos -= 20
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 14)
    c.drawString(50, y_pos, "【健康運】")
    y_pos -= 20
    stars = "★" * data["health"][0] + "☆" * (5 - data["health"][0])
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    c.drawString(50, y_pos, stars)
    y_pos -= 20
    c.setFont(font_name, 11)
    y_pos = draw_wrapped_text(c, data["health"][1], 50, y_pos, width-100, font_name, 11, 18)
    
    # ラッキーカラーとラッキーアイテム
    y_pos -= 20
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 14)
    c.drawString(50, y_pos, "【ラッキーカラー・アイテム】")
    y_pos -= 20
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 11)
    lucky_info = f"ラッキーカラー: {data.get('color', '')} / ラッキーアイテム: {data.get('item', '')}"
    y_pos = draw_wrapped_text(c, lucky_info, 50, y_pos, width-100, font_name, 11, 18)
    
    # 2ページ目: 月別運勢カレンダー
    c.showPage()
    c.setFillColor(HexColor("#FFFBF0"))
    c.rect(0, 0, width, height, fill=1)
    
    # タイトル（設定ファイルから取得）
    monthly_title = CONFIG.get("pdf_monthly_title", "2月 恋愛運勢カレンダー")
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 20)
    c.drawCentredString(width/2, height-60, monthly_title)
    
    # 月別運勢リストを描画
    y_pos = height-100
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    
    for txt in monthly:
        if txt and txt.strip():  # テキストが空でないことを確認
            if y_pos < 200:  # スペースが足りない場合は改ページ
                c.showPage()
                c.setFillColor(HexColor("#FFFBF0"))
                c.rect(0, 0, width, height, fill=1)
                y_pos = height - 100
            y_pos = draw_wrapped_text(c, txt, 50, y_pos, width-100, font_name, 12, 20, HexColor("#333333"))
            y_pos -= 15  # 月間の間隔を追加
    
    # 鑑定した占い師（12月の運勢の下）
    y_pos -= 40
    if y_pos < 250:  # スペースが足りない場合は改ページ
        c.showPage()
        c.setFillColor(HexColor("#FFFBF0"))
        c.rect(0, 0, width, height, fill=1)
        y_pos = height - 100
    
    fortune_teller_name = CONFIG.get("fortune_teller_name", "占い師")
    fortune_teller_url = CONFIG.get("fortune_teller_url", "")
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 10)
    fortune_teller_text = f"鑑定した占い師 {fortune_teller_name}"
    text_width = c.stringWidth(fortune_teller_text, font_name, 10)
    text_x = (width - text_width) / 2
    c.drawString(text_x, y_pos, fortune_teller_text)
    # リンクを追加
    if fortune_teller_url:
        c.linkURL(fortune_teller_url, (text_x, y_pos - 2, text_x + text_width, y_pos + 12), relative=0)
    
    # フッター（鑑定した占い師の下）
    y_pos -= 25
    c.setFillColor(HexColor("#666666"))
    c.setFont(font_name, 9)
    c.drawCentredString(width/2, y_pos, "この鑑定書は数秘術に基づいて作成されました。")
    
    # 占いミザリーへの案内
    y_pos -= 35
    if y_pos < 200:  # スペースが足りない場合は改ページ
        c.showPage()
        c.setFillColor(HexColor("#FFFBF0"))
        c.rect(0, 0, width, height, fill=1)
        y_pos = height - 100
    
    # 「さらにもっと深く知るには」のテキストを描画（設定ファイルから取得）
    fortune_site_url = CONFIG.get("fortune_site_url", "")
    fortune_site_name = CONFIG.get("fortune_site_name", "")
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 12)
    text1 = "さらにもっと深く知るには"
    text2 = fortune_site_name
    text3 = "へ"
    text1_width = c.stringWidth(text1, font_name, 12)
    text2_width = c.stringWidth(text2, font_name, 12)
    text3_width = c.stringWidth(text3, font_name, 12)
    total_width = text1_width + text2_width + text3_width
    start_x = (width - total_width) / 2
    
    c.drawString(start_x, y_pos, text1)
    link_x = start_x + text1_width
    c.drawString(link_x, y_pos, text2)
    if fortune_site_url:
        c.linkURL(fortune_site_url, (link_x, y_pos - 2, link_x + text2_width, y_pos + 14), relative=0)
    c.drawString(link_x + text2_width, y_pos, text3)
    
    y_pos -= 35
    line_reservation_text = CONFIG.get("line_reservation_text", "")
    if line_reservation_text:
        c.setFillColor(HexColor("#C71585"))
        c.setFont(font_name, 11)
        c.drawCentredString(width/2, y_pos, line_reservation_text)
        
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 7. アプリUI
# ==========================================
# タイトルとサブタイトルを設定ファイルから取得
app_subtitle = CONFIG.get("app_subtitle", "")
app_main_title = CONFIG.get("app_main_title", "2月限定 恋愛運勢鑑定書")

st.markdown(f"""
    <style>
    .title-container {{text-align: center; padding-bottom: 20px; border-bottom: 2px solid #C0A060; margin-bottom: 30px;}}
    .main-title {{font-family: "Helvetica", sans-serif; font-weight: bold; font-size: 2.5rem; background: linear-gradient(45deg, #FFB6C1, #C71585); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}}
    .sub-title {{font-size: 1.2rem; color: #C0A060; font-weight: bold;}}
    div.stButton > button {{background-color: #C71585; color: white; border-radius: 10px; padding: 10px 20px; border:none;}}
    </style>
    <div class="title-container">
        <div class="sub-title">{app_subtitle}</div>
        <div class="main-title">{app_main_title}</div>
    </div>
""", unsafe_allow_html=True)

query_params = st.query_params
is_paid = query_params.get("paid") == "true" or query_params.get("checkout") == "success"

if 'user_name' not in st.session_state: st.session_state.update({k: v for k, v in zip(['user_name','birth_year','birth_month','birth_day'], ['', 2000, 1, 1])})
if 'pdf_data' not in st.session_state: st.session_state.pdf_data = None
if 'pdf_filename' not in st.session_state: st.session_state.pdf_filename = None

if not is_paid:
    # ▼▼▼ 興味を引くコンテンツセクション（設定ファイルから取得）▼▼▼
    app_description = CONFIG.get("app_description", "")
    app_intro_questions = CONFIG.get("app_intro_questions", [])
    app_intro_text = CONFIG.get("app_intro_text", "")
    
    questions_html = ""
    for question in app_intro_questions:
        questions_html += f'<span class="question">{question}</span>\n            '
    
    st.markdown(f"""
    <div class="intro-box">
        <div class="intro-head">{app_description}</div>
        <div class="intro-text">
            {questions_html}
            <br>
            {app_intro_text}
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ▲▲▲ ここまで ▲▲▲

    st.info("👋 まずは無料プレビューで、あなたの「2月の恋愛運の数字」を知ってください。")
    
    with st.form("preview"):
        name_pre = st.text_input("お名前")
        c1, c2, c3 = st.columns(3)
        y_pre = c1.number_input("年", 1900, 2025, 2000)
        m_pre = c2.number_input("月", 1, 12, 1)
        d_pre = c3.number_input("日", 1, 31, 1)
        
        if st.form_submit_button("鑑定結果の一部を見る"):
            if name_pre:
                lp = calculate_life_path_number(y_pre, m_pre, d_pre)
                preview_data = get_fortune_data(lp)
                
                # ▼ GAS経由でデータを保存（URL修正版）
                save_data_via_gas("無料プレビュー", name_pre, y_pre, m_pre, d_pre, lp)
                
                # 興味を引く見出しを表示
                st.markdown("---")
                fortune_year = CONFIG.get("fortune_year", "")
                st.markdown(f"### {name_pre} 様の{fortune_year}恋愛運勢")
                st.markdown(f"**ライフパスナンバー: {lp}**")
                
                st.markdown(f"#### ✨ あなたの{fortune_year}恋愛運はこんな月に！")
                st.markdown(f"**総合運: {preview_data['overall'][0]}**")
                st.markdown(f"{preview_data['overall'][1]}")
                
                st.markdown("#### 💕 気になる恋愛運")
                st.markdown(f"**恋愛運**: {'★' * preview_data['love'][0] + '☆' * (5 - preview_data['love'][0])}")
                st.markdown(f"{preview_data['love'][1]}")
                
                st.markdown("---")
                st.warning("🔒 詳しい結果（全運勢・月別カレンダー・ラッキーアイテムなど）をご覧になるには、完全版の購入が必要です。")
                
                # 完全版へのアンカーリンク
                st.markdown("""
                <div style="text-align: center; margin: 20px 0;">
                    <a href="#完全版鑑定書" style="color: #e10080; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-block; padding: 10px 20px; background-color: #fff0f5; border-radius: 25px; border: 2px solid #e10080;">
                        ↓ 完全版鑑定書を見る ↓
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
        name = st.text_input("お名前", key="p_name")
        c1, c2, c3 = st.columns(3)
        y = c1.number_input("年", 1900, 2025, 2000, key="p_y")
        m = c2.number_input("月", 1, 12, 1, key="p_m")
        d = c3.number_input("日", 1, 31, 1, key="p_d")
        if st.form_submit_button("情報を保存して決済へ"):
            st.session_state.update({'user_name': name, 'birth_year': y, 'birth_month': m, 'birth_day': d})
            st.success("✅ 保存しました。下のボタンから決済してください。")
            
    # ▼▼▼ Stripeリンク（設定ファイルから取得）▼▼▼
    stripe_checkout_url = CONFIG.get("stripe_checkout_url", "")
    price_display = CONFIG.get("price_display", "500円")
    if stripe_checkout_url:
        st.link_button(f"👉 {price_display}で発行する", stripe_checkout_url, type="primary", use_container_width=True)

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
                st.session_state.pdf_filename = f"2月限定恋愛運勢鑑定書_{name}.pdf"
                
                # ログ保存：購入完了
                # ▼ GAS経由でデータを保存（エラーが発生しても続行）
                try:
                    save_data_via_gas("購入・発行", name, y, m, d, calculate_life_path_number(y, m, d))
                except:
                    pass  # 保存エラーは無視
                
                st.success("完了しました！下のボタンからダウンロードできます。")
                st.rerun()  # ページを再読み込みしてダウンロードボタンを表示
            except Exception as e:
                st.error(f"PDF生成エラー: {e}")
                import traceback
                st.error(f"詳細: {traceback.format_exc()}")
    
    # PDFダウンロードボタンを表示
    if st.session_state.get('pdf_data') and st.session_state.get('pdf_filename'):
        st.markdown("---")
        st.download_button(
            label="📥 PDFをダウンロード",
            data=st.session_state.pdf_data,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

# ==========================================
# 8. トップへ戻るリンク + フッター（著作権表示）
# ==========================================
# フッター情報を設定ファイルから取得
fortune_site_url = CONFIG.get("fortune_site_url", "")
contact_email_url = CONFIG.get("contact_email_url", "")
contact_line_url = CONFIG.get("contact_line_url", "")
legal_url = CONFIG.get("legal_url", "")
copyright_text = CONFIG.get("copyright_text", "")

st.markdown(f"""
    <div class="top-link">
        <a href="{fortune_site_url}" target="_blank" rel="noopener noreferrer">トップへ戻る</a>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="custom-footer">
        <div>
            <strong>お問い合わせ</strong>
            <div>
                <a href="{contact_email_url}" target="_blank" rel="noopener noreferrer">メール</a>
                <span style="margin: 0 8px;">|</span>
                <a href="{contact_line_url}" target="_blank" rel="noopener noreferrer">LINE</a>
            </div>
        </div>
        <div>
            <a href="{legal_url}" target="_blank" rel="noopener noreferrer">特定商取引法に基づく表記</a>
        </div>
        <div class="copyright">{copyright_text}</div>
    </div>
""", unsafe_allow_html=True)
