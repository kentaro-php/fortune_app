import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os
import urllib.request
from datetime import datetime
import io
import json  # jsonモジュールを追加

# ▼▼▼ スプレッドシート連携用 ▼▼▼
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================================
# 1. ページ設定
# ==========================================
st.set_page_config(
    page_title="2026年運勢鑑定書 | 占いミザリー",
    page_icon="🔮",
    layout="centered"
)

# ==========================================
# UI完全削除（CSS）
# ==========================================
hide_st_style = """
    <style>
    header {visibility: hidden !important; height: 0px !important;}
    footer {visibility: hidden !important; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    div[class*="viewerBadge"] {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    .block-container {padding-top: 0rem !important; padding-bottom: 0rem !important;}
    .stApp > header {display: none !important;}
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
    return [f"{i}月: 運勢メッセージ..." for i in range(1, 13)] # 簡略化（実際は元のテキストを使用）

# ==========================================
# 5. スプレッドシート保存関数（Heroku対応版）
# ==========================================
def save_to_gsheet(name, year, month, day, life_path):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = None
        
        # 1. Herokuの環境変数(Config Vars)を確認
        if "GCP_CREDENTIALS" in os.environ:
            creds_dict = json.loads(os.environ["GCP_CREDENTIALS"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        # 2. Streamlit CloudのSecretsを確認
        elif "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            creds_dict = dict(st.secrets["connections"]["gsheets"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            print("【保存失敗】鍵の設定が見つかりません (GCP_CREDENTIALS or Secrets)")
            return False

        client = gspread.authorize(creds)
        SPREADSHEET_NAME = "顧客リスト_2026運勢"
        
        try:
            sheet = client.open(SPREADSHEET_NAME).sheet1
        except:
            print(f"❌ シート「{SPREADSHEET_NAME}」が見つかりません。共有設定を確認してください。")
            return False

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.append_row([timestamp, name, f"{year}/{month}/{day}", life_path])
        return True
    except Exception as e:
        print(f"スプレッドシート保存エラー: {e}")
        return False

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
    
    # ページ1
    c.setFillColor(HexColor("#FFFBF0")); c.rect(0, 0, width, height, fill=1)
    c.setFillColor(HexColor("#C71585")); c.setFont(font_name, 26); c.drawCentredString(width/2, height-60, "2026年 運勢鑑定書")
    c.setFillColor(HexColor("#C0A060")); c.setFont(font_name, 22); c.drawCentredString(width/2, height-100, f"{name} 様")
    c.setFillColor(HexColor("#333333")); c.setFont(font_name, 12); c.drawCentredString(width/2, height-130, f"生年月日: {y}年{m}月{d}日 (LP: {lp})")
    
    # 本文（簡略化して描画）
    c.setFillColor(HexColor("#C71585")); c.setFont(font_name, 14); c.drawString(50, height-180, "【あなたの本質】")
    draw_wrapped_text(c, data["personality"], 50, height-200, width-100, font_name, 11, 18)
    
    # ページ2
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

# セッション管理
if 'user_name' not in st.session_state: st.session_state.update({k: v for k, v in zip(['user_name','birth_year','birth_month','birth_day'], ['', 2000, 1, 1])})
if 'pdf_data' not in st.session_state: st.session_state.pdf_data = None

if not is_paid:
    st.info("👋 ようこそ！まずは無料プレビューをご覧ください。")
    with st.form("preview"):
        st.text_input("お名前")
        st.columns(3)[0].number_input("年", 1900, 2025, 2000)
        if st.form_submit_button("鑑定結果の一部を見る"): st.warning("🔒 完全版は購入が必要です。")

    st.markdown("---")
    st.header("💎 完全版鑑定書 (PDF)")
    with st.form("pay"):
        name = st.text_input("お名前", key="p_name")
        c1, c2, c3 = st.columns(3)
        y = c1.number_input("年", 1900, 2025, 2000, key="p_y")
        m = c2.number_input("月", 1, 12, 1, key="p_m")
        d = c3.number_input("日", 1, 31, 1, key="p_d")
        if st.form_submit_button("情報を保存して決済へ"):
            st.session_state.update({'user_name': name, 'birth_year': y, 'birth_month': m, 'birth_day': d})
            st.success("✅ 保存しました。下のボタンから決済してください。")
            
    # ▼▼▼ Stripeリンク（HerokuのURLに合わせてください） ▼▼▼
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
        submitted = st.form_submit_button("✨ PDFをダウンロード", use_container_width=True)

    if submitted and name:
        with st.spinner("生成中..."):
            try:
                pdf = create_pdf(name, y, m, d)
                st.session_state.pdf_data = pdf.getvalue()
                st.session_state.pdf_filename = f"運勢鑑定書_{name}.pdf"
                
                # スプレッドシート保存
                save_to_gsheet(name, y, m, d, calculate_life_path_number(y, m, d))
                st.success("完了しました！")
            except Exception as e:
                st.error(f"エラー: {e}")

    if st.session_state.pdf_data:
        st.download_button("📥 ダウンロード", st.session_state.pdf_data, file_name=st.session_state.pdf_filename, mime="application/pdf", type="primary", use_container_width=True)