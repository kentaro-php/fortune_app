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
# 4. 運勢ロジック（ここを修正しました）
# ==========================================
def calculate_life_path_number(year, month, day):
    def sum_digits(n):
        while n >= 10: n = sum(int(d) for d in str(n))
        return n
    total = sum_digits(year) + sum_digits(month) + sum_digits(day)
    lp = sum_digits(total)
    return total if total in [11, 22, 33] else lp

def get_fortune_data(lp):
    # LP4の場合の詳細な説明（画像に基づく）
    if lp == 4:
        data = {
            "personality": "独自の感性と才能を持ち、周囲に新しい風を吹き込む力を持っています。",
            "lp_description": "誠実で責任感が強く、実務的な能力に優れている傾向があります。安定を好み、着実に物事を進める力をお持ちのようです。その真面目さと信頼性は、周囲から高く評価されていることでしょう。着実な努力を積み重ねることで、長期的な成功と安定を手に入れられる可能性が高いでしょう。",
            "overall": ("中吉", "2026年は、着実な成長の年となりそうです。努力を積み重ねることで、安定した成果を得られる傾向があります。焦らず、一歩ずつ進まれることで、確かな実りが待っていることでしょう。責任ある立場での活躍が期待でき、周囲からの信頼も深まっていくことでしょう。"),
            "love": (3, "2026年は、安定した関係を築く年となる傾向があります。誠実さと信頼が、あなたの恋愛運を高めていく可能性が高いでしょう。焦らず、着実に信頼関係を深めていかれると良いでしょう。真面目で誠実なあなたの姿勢が、パートナーからの信頼を深めていくことでしょう。"),
            "work": (4, "2026年は、着実な努力が認められる年となりそうです。責任ある立場での活躍が期待できる傾向があります。これまでに積み重ねてきた努力が、実を結んでいくことでしょう。誠実さと責任感が、周囲からの信頼を深めていくことでしょう。安定した成果を手に入れられる可能性が高いでしょう。"),
            "money": (4, "2026年は、着実な貯蓄と計画的な投資が金運を高める年となる傾向があります。安定した収入を基盤に、計画的に資産を増やしていかれると良いでしょう。真面目で誠実な姿勢が、経済的な安定をもたらしていくことでしょう。長期的な視点で資産を築いていくことで、将来の金運が高まっていくことでしょう。"),
            "health": (3, "2026年は、規則正しい生活習慣が健康運を高める年となる傾向があります。適度な運動とバランスの取れた食事を心がけることで、体調を良好に保てるでしょう。無理をせず、着実に健康管理を続けていくことが大切です。"),
            "color": "シルバー",
            "item": "手帳"
        }
    else:
        # その他のLPの場合（デフォルト）
        data = {
            "personality": "独自の感性と才能を持ち、周囲に新しい風を吹き込む力を持っています。",
            "lp_description": "あなたは独自の才能と魅力を持っています。2026年は、その才能を活かして新しいステージへと進む準備が整います。",
            "overall": ("大吉", "2026年は飛躍の年。これまでの努力が実を結び、新しいステージへと進む準備が整います。"),
            "love": (5, "素晴らしい出会いが期待できる年。パートナーとの絆も深まり、穏やかな愛に包まれるでしょう。"),
            "work": (4, "リーダーシップを発揮する場面が増えそうです。自信を持って決断することで信頼を得られます。"),
            "money": (4, "安定した金運です。自己投資にお金を使うことで、将来的なリターンが大きくなるでしょう。"),
            "health": (3, "忙しさから疲れが溜まりやすい時期。適度な休息とバランスの取れた食事を心がけてください。"),
            "color": "ゴールド",
            "item": "手帳"
        }
    return data

def get_monthly_fortunes(lp):
    # ▼▼▼ 【修正】月の重複を削除しました ▼▼▼
    messages = [
        "1月: 着実な成長の月です。努力を積み重ねることで、安定した成果を得られます。",
        "2月: 安定した関係を築く月です。誠実さと信頼が、運気を高めます。",
        "3月: 計画的な行動が重要となる月です。着実に物事を進めましょう。",
        "4月: 責任ある立場での活躍が期待できる月です。真面目さと信頼性が評価されます。",
        "5月: 変化に対応する月です。柔軟な姿勢が運気を高めます。",
        "6月: 安定した関係が深まる月です。誠実さと信頼が、絆を強めます。",
        "7月: 内面の安定が重要となる月です。着実な成長が運気を高めます。",
        "8月: 着実な努力が認められる月です。責任ある立場での活躍が期待できます。",
        "9月: 完成と新たな始まりの月です。これまでの努力が実を結びます。",
        "10月: 計画的な行動が成果を生む月です。着実に目標を達成しましょう。",
        "11月: 大きなプロジェクトの基盤を築く月です。理想を現実化する準備が整います。",
        "12月: 安定した成果を手に入れる月です。誠実さと責任感が、成功をもたらします。"
    ]
    return messages

# ==========================================
# 5. GAS経由でのデータ保存（修正版）
# ==========================================
def save_data_via_gas(action_type, name, year, month, day, lp):
    # ▼▼▼ URLを設定済み（xのもの） ▼▼▼
    gas_url = "https://script.google.com/macros/s/AKfycbx7er_1XN-G1KmGFvmAo8zHKNfA0_nKYPr5m6SL4pexfoz8M7JgovdtQ6VYxopjSj5C/exec"

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
    
    # 2ページ目: 月別運勢カレンダー
    c.showPage()
    c.setFillColor(HexColor("#FFFBF0"))
    c.rect(0, 0, width, height, fill=1)
    
    # タイトル「2026年 月別運勢カレンダー」
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 20)
    c.drawCentredString(width/2, height-60, "2026年 月別運勢カレンダー")
    
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
    
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 10)
    text_width = c.stringWidth("鑑定した占い師 MIZARY", font_name, 10)
    text_x = (width - text_width) / 2
    c.drawString(text_x, y_pos, "鑑定した占い師 MIZARY")
    # リンクを追加
    c.linkURL("https://mizary.com/staff/mizary/", (text_x, y_pos - 2, text_x + text_width, y_pos + 12), relative=0)
    
    # 占いミザリーへの案内
    y_pos -= 35
    if y_pos < 200:  # スペースが足りない場合は改ページ
        c.showPage()
        c.setFillColor(HexColor("#FFFBF0"))
        c.rect(0, 0, width, height, fill=1)
        y_pos = height - 100
    
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 12)
    c.drawCentredString(width/2, y_pos, "さらにもっと深く知るには占いミザリーへ")
    
    y_pos -= 25
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 11)
    c.drawCentredString(width/2, y_pos, "https://mizary.com/")
    
    y_pos -= 30
    c.setFillColor(HexColor("#C71585"))
    c.setFont(font_name, 11)
    c.drawCentredString(width/2, y_pos, "LINE予約で20分2,980円~")
    
    # フッター
    y_pos -= 50
    if y_pos < 80:  # フッターのスペースが足りない場合は調整
        y_pos = 50
    c.setFillColor(HexColor("#666666"))
    c.setFont(font_name, 9)
    c.drawCentredString(width/2, y_pos, "この鑑定書は数秘術に基づいて作成されました。")
        
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
                <div style="text-align: center; margin: 20px 0;">
                    <a href="javascript:void(0);" onclick="document.querySelector('#完全版鑑定書').scrollIntoView({behavior: 'smooth'});" style="color: #e10080; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-block; padding: 10px 20px; background-color: #fff0f5; border-radius: 25px; border: 2px solid #e10080;">
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
            
    # ▼▼▼ Stripeリンク ▼▼▼
    st.link_button("👉 500円で発行する", "https://buy.stripe.com/8x2fZhfsm01Q813847cfT1v", type="primary", use_container_width=True)

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
st.markdown("""
    <div class="top-link">
        <a href="https://mizary.com/" target="_blank" rel="noopener noreferrer">トップへ戻る</a>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="custom-footer">
        <div>
            <strong>お問い合わせ</strong>
            <div>
                <a href="https://mizary.com/contact/" target="_blank" rel="noopener noreferrer">メール</a>
                <span style="margin: 0 8px;">|</span>
                <a href="https://lin.ee/OKV7A8H" target="_blank" rel="noopener noreferrer">LINE</a>
            </div>
        </div>
        <div>
            <a href="https://mizary.com/tokusyouhou/" target="_blank" rel="noopener noreferrer">特定商取引法に基づく表記</a>
        </div>
        <div class="copyright">© 2026 占いミザリー</div>
    </div>
""", unsafe_allow_html=True)