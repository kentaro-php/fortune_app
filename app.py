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

# ▼▼▼【追加】スプレッドシート連携用ライブラリ ▼▼▼
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================================
# 1. ページ設定（必ず最初に記述）
# ==========================================
st.set_page_config(
    page_title="2026年運勢鑑定書 | 占いミザリー",
    page_icon="🔮",
    layout="centered"
)

# --- UI完全削除（埋め込みモードのフッター対策強化版） ---
hide_st_style = """
    <style>
    /* 1. ヘッダー・フッターの徹底削除 */
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important; height: 0px !important;}
    
    /* 2. Streamlitの特定要素IDに対する非表示 */
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    
    /* 3. embed=true 時の下部バー対策 */
    /* 通常のfooterタグだけでなく、アプリ直下のfooter要素もターゲットにする */
    .stApp > footer {display: none !important;}
    
    /* 4. ツールバー・ビューワーバッジの削除 */
    div[class*="viewerBadge"] {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    
    /* 5. ハンバーガーメニューとデコレーションラインの削除 */
    #MainMenu {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    
    /* 6. 余白調整 */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* 7. 右下の固定要素を包括的に非表示（念のための強力な指定） */
    [style*="position: fixed"][style*="bottom"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* 8. リンク（Built with Streamlit）を含む可能性のある要素を消す */
    a[href*="streamlit.io"] {display: none !important;}
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
    if os.path.exists(FONT_PATH_ROOT):
        return FONT_PATH_ROOT
    elif os.path.exists(FONT_PATH_FALLBACK):
        return FONT_PATH_FALLBACK
    return None

def download_font():
    if not os.path.exists(FONT_DIR):
        os.makedirs(FONT_DIR)
    if not os.path.exists(FONT_PATH_FALLBACK):
        font_url = "https://raw.githubusercontent.com/making/demo-jasper-report-ja/master/src/main/resources/fonts/ipaexm/ipaexm.ttf"
        try:
            urllib.request.urlretrieve(font_url, FONT_PATH_FALLBACK)
        except Exception as e:
            st.error(f"フォントのダウンロードに失敗しました: {e}")
            return False
    return True

def register_font():
    font_path = get_font_path()
    if font_path and os.path.exists(font_path):
        try:
            if "ipaexg" in font_path.lower():
                font_name = 'IPAexGothic'
            else:
                font_name = 'IPAexMincho'
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            return font_name
        except Exception as e:
            st.error(f"フォントの登録に失敗しました: {e}")
            return None
    if download_font():
        font_path = get_font_path()
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont('IPAexMincho', font_path))
                return 'IPAexMincho'
            except Exception as e:
                st.error(f"フォントの登録に失敗しました: {e}")
    return None

# ==========================================
# 3. PDF描画用ヘルパー関数
# ==========================================
def draw_wrapped_text(c, text, x, y, max_width, font_name, font_size, line_height, color=HexColor("#333333")):
    c.setFillColor(color)
    c.setFont(font_name, font_size)
    lines = []
    current_line = ""
    for char in text:
        if c.stringWidth(current_line + char, font_name, font_size) <= max_width:
            current_line += char
        else:
            lines.append(current_line)
            current_line = char
    if current_line:
        lines.append(current_line)
    for line in lines:
        if y < 30: break
        c.drawString(x, y, line)
        y -= line_height
    return y

# ==========================================
# 4. 運勢データ・ロジック
# ==========================================
def calculate_life_path_number(year, month, day):
    def sum_digits(n):
        while n >= 10:
            n = sum(int(d) for d in str(n))
        return n
    total = sum_digits(year) + sum_digits(month) + sum_digits(day)
    life_path = sum_digits(total)
    if total in [11, 22, 33]: return total
    return life_path

def get_fortune_data(life_path):
    data = {
        "personality": "独自の感性と才能を持ち、周囲に新しい風を吹き込む力を持っています。",
        "overall": ("大吉", "2026年は飛躍の年。これまでの努力が実を結び、新しいステージへと進む準備が整います。"),
        "love": (5, "素晴らしい出会いが期待できる年。パートナーとの絆も深まり、穏やかな愛に包まれるでしょう。"),
        "work": (4, "リーダーシップを発揮する場面が増えそうです。自信を持って決断することで信頼を得られます。"),
        "money": (4, "安定した金運です。自己投資にお金を使うことで、将来的なリターンが大きくなるでしょう。"),
        "health": (3, "忙しさから疲れが溜まりやすい時期。適度な休息とバランスの取れた食事を心がけてください。"),
        "interpersonal": (5, "人脈が広がる年です。新しいコミュニティに参加することで、人生を豊かにする出会いがあります。"),
        "color": "ゴールド",
        "item": "手帳"
    }
    if life_path % 2 == 0:
        data["color"] = "シルバー"
        data["overall"] = ("中吉", "2026年は基盤を固める年。焦らず着実に進むことで、揺るぎない成果を手に入れます。")
    return data

def get_monthly_fortunes(life_path):
    return [
        "1月: 新しいことを始めるのに最適な時期です。",
        "2月: 周囲との協力を大切にしましょう。",
        "3月: アイデアが湧き出るクリエイティブな月。",
        "4月: 足元を固める慎重さが必要です。",
        "5月: 変化を楽しむことで運気が上がります。",
        "6月: 愛情運が最高潮。家族との時間を大切に。",
        "7月: 自分の内面と向き合う静かな時間を持って。",
        "8月: パワフルに行動できる月。目標達成のチャンス。",
        "9月: 一つの区切りがつき、次の準備を始めるとき。",
        "10月: 新たなスタート。直感を信じて。",
        "11月: 人との繋がりが幸運を運びます。",
        "12月: 一年の総仕上げ。感謝の気持ちを伝えて。"
    ]

# ==========================================
# 5. スプレッドシート保存関数
# ==========================================
def save_to_gsheet(name, year, month, day, life_path):
    """スプレッドシートに行を追加する関数"""
    try:
        if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
            st.warning("⚠️ Secretsの設定が見つかりません。ログへの記録のみ行います。")
            print(f"【保存失敗】Secrets未設定: {name}, LP:{life_path}")
            return False

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        SPREADSHEET_NAME = "顧客リスト_2026運勢" 
        
        try:
            sheet = client.open(SPREADSHEET_NAME).sheet1
        except gspread.exceptions.SpreadsheetNotFound:
            st.error(f"❌ スプレッドシート「{SPREADSHEET_NAME}」が見つかりません。名前を確認するか、共有設定を見直してください。")
            return False

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = [timestamp, name, f"{year}/{month}/{day}", life_path]
        sheet.append_row(row)
        return True
        
    except Exception as e:
        print(f"スプレッドシート保存エラー: {e}")
        return False

# ==========================================
# 6. PDF生成関数
# ==========================================
def create_pdf(name, birth_year, birth_month, birth_day):
    life_path = calculate_life_path_number(birth_year, birth_month, birth_day)
    data = get_fortune_data(life_path)
    monthly_data = get_monthly_fortunes(life_path)
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4 
    
    bg_color = HexColor("#FFFBF0")
    text_color = HexColor("#333333")
    accent_color = HexColor("#C0A060")
    title_color = HexColor("#C71585")
    
    font_name = register_font()
    if not font_name:
        font_name = 'Helvetica'

    # --- 1ページ目 ---
    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, fill=1)
    
    margin = 50          
    content_width = width - (margin * 2) 
    current_y = height - 60 

    c.setFillColor(title_color)
    c.setFont(font_name, 26)
    c.drawCentredString(width/2, current_y, "2026年 運勢鑑定書")
    current_y -= 40
    
    c.setFillColor(accent_color)
    c.setFont(font_name, 22)
    c.drawCentredString(width/2, current_y, f"{name} 様")
    current_y -= 30
    
    c.setFillColor(text_color)
    c.setFont(font_name, 12)
    c.drawCentredString(width/2, current_y, f"生年月日: {birth_year}年{birth_month}月{birth_day}日  (LP: {life_path})")
    current_y -= 40

    c.setFillColor(title_color)
    c.setFont(font_name, 14)
    c.drawString(margin, current_y, "【あなたの本質】")
    current_y -= 20
    current_y = draw_wrapped_text(c, data["personality"], margin, current_y, content_width, font_name, 11, 18, text_color)
    current_y -= 25

    c.setFillColor(title_color)
    c.setFont(font_name, 14)
    c.drawString(margin, current_y, "【2026年の総合運】")
    c.setFillColor(accent_color)
    c.drawString(margin + 150, current_y, data["overall"][0])
    current_y -= 20
    current_y = draw_wrapped_text(c, data["overall"][1], margin, current_y, content_width, font_name, 11, 18, text_color)
    current_y -= 25

    topics = [("恋愛運", data["love"]), ("仕事運", data["work"]), ("金運", data["money"]), ("健康運", data["health"]), ("対人運", data["interpersonal"])]
    for title, (stars, text) in topics:
        c.setFillColor(title_color)
        c.setFont(font_name, 14)
        c.drawString(margin, current_y, f"【{title}】")
        c.setFillColor(accent_color)
        star_str = "★" * stars + "☆" * (5 - stars)
        c.drawString(margin + 100, current_y, star_str)
        current_y -= 20
        current_y = draw_wrapped_text(c, text, margin, current_y, content_width, font_name, 11, 18, text_color)
        current_y -= 20

    current_y -= 10
    c.setFillColor(title_color)
    c.setFont(font_name, 14)
    c.drawString(margin, current_y, f"ラッキーカラー： {data['color']}   /   ラッキーアイテム： {data['item']}")
    
    # --- 2ページ目 ---
    c.showPage()
    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, fill=1)
    
    current_y = height - 60
    c.setFillColor(title_color)
    c.setFont(font_name, 20)
    c.drawCentredString(width/2, current_y, "2026年 月別運勢カレンダー")
    current_y -= 50
    
    c.setFillColor(text_color)
    c.setFont(font_name, 12)
    
    for month_text in monthly_data:
        current_y = draw_wrapped_text(c, month_text, margin, current_y, content_width, font_name, 12, 25, text_color)
        current_y -= 15

    c.setFillColor(HexColor("#999999"))
    c.setFont(font_name, 9)
    c.drawCentredString(width/2, 30, "Mizary Fortune Telling - 2026 Special Report")

    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 7. アプリUI
# ==========================================

st.markdown("""
    <style>
    .title-container {text-align: center; padding-bottom: 20px; border-bottom: 2px solid #C0A060; margin-bottom: 30px;}
    .main-title {font-family: "Helvetica", sans-serif; font-weight: bold; font-size: 2.5rem; background: linear-gradient(45deg, #FFB6C1, #C71585); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;}
    .sub-title {font-size: 1.2rem; color: #C0A060; font-weight: bold;}
    div.stButton > button {background-color: #C71585; color: white; font-weight: bold; border: none; padding: 10px 20px; border-radius: 10px;}
    .custom-footer {text-align: center; padding: 30px 20px; margin-top: 50px; border-top: 1px solid #E8E8E8; color: #666666; font-size: 0.9rem;}
    .custom-footer a {color: #D81B60; text-decoration: none; margin: 0 10px;}
    </style>
    
    <div class="title-container">
        <div class="sub-title">✨ 数秘術で紐解くあなたの未来 ✨</div>
        <div class="main-title">2026年 運勢鑑定書</div>
        <div style="color: #cccccc;">Designed for your special year</div>
    </div>
    """, unsafe_allow_html=True)

font_path = get_font_path()
if not font_path:
    download_font()

# 決済チェック（URLパラメータ または 強制テスト用）
query_params = st.query_params
is_paid = query_params.get("paid") == "true" or query_params.get("checkout") == "success"

# ★テスト用：Stripeをスキップしたい場合はここを True に書き換えてください
# is_paid = True 

# セッション初期化
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'birth_year' not in st.session_state: st.session_state.birth_year = 2000
if 'birth_month' not in st.session_state: st.session_state.birth_month = 1
if 'birth_day' not in st.session_state: st.session_state.birth_day = 1
if 'pdf_data' not in st.session_state: st.session_state.pdf_data = None
if 'pdf_filename' not in st.session_state: st.session_state.pdf_filename = None

# --- パターンA: 未払い ---
if not is_paid:
    st.info("👋 ようこそ！まずは無料プレビューをご覧ください。")
    with st.form("preview_form"):
        st.write("### 🔮 無料プレビュー")
        name = st.text_input("お名前", placeholder="山田 花子")
        col1, col2, col3 = st.columns(3)
        with col1: st.number_input("年", 1900, 2024, 2000)
        with col2: st.number_input("月", 1, 12, 1)
        with col3: st.number_input("日", 1, 31, 1)
        submitted = st.form_submit_button("鑑定結果の一部を見る")
    
    if submitted:
        st.warning("🔒 詳しい結果を見るには「完全版」の購入が必要です。")

    st.markdown("---")
    st.header("💎 完全版鑑定書 (PDF)")
    with st.form("payment_form"):
        st.write("### 📝 お客様情報")
        payment_name = st.text_input("お名前", value=st.session_state.user_name, placeholder="山田 花子", key="payment_name")
        col1, col2, col3 = st.columns(3)
        with col1: payment_year = st.number_input("年", 1900, 2024, st.session_state.birth_year, key="payment_year")
        with col2: payment_month = st.number_input("月", 1, 12, st.session_state.birth_month, key="payment_month")
        with col3: payment_day = st.number_input("日", 1, 31, st.session_state.birth_day, key="payment_day")
        
        if st.form_submit_button("情報を保存して決済へ進む"):
            st.session_state.user_name = payment_name
            st.session_state.birth_year = payment_year
            st.session_state.birth_month = payment_month
            st.session_state.birth_day = payment_day
            st.success("✅ 情報を保存しました。決済ボタンをクリックしてください。")
    
    stripe_url = "https://buy.stripe.com/28E4gzcga8yma9b1FJcfT1k"
    st.link_button(label="👉 500円で鑑定書を発行する", url=stripe_url, type="primary", use_container_width=True)

# --- パターンB: 支払い完了（発行 & シート保存） ---
else:
    st.success("✅ ご購入ありがとうございます！鑑定書を発行できます。")
    
    with st.form("fortune_form"):
        st.write("### 📄 鑑定書発行フォーム")
        default_name = st.session_state.user_name if st.session_state.user_name else ""
        default_year = st.session_state.birth_year if st.session_state.birth_year else 2000
        default_month = st.session_state.birth_month if st.session_state.birth_month else 1
        default_day = st.session_state.birth_day if st.session_state.birth_day else 1
        
        name = st.text_input("お名前", value=default_name, placeholder="山田 花子", key="form_name")
        col1, col2, col3 = st.columns(3)
        with col1: birth_year = st.number_input("年", 1900, 2024, default_year, key="form_year")
        with col2: birth_month = st.number_input("月", 1, 12, default_month, key="form_month")
        with col3: birth_day = st.number_input("日", 1, 31, default_day, key="form_day")
        
        submitted = st.form_submit_button("✨ 鑑定書PDFをダウンロードする", use_container_width=True)

    if submitted and name:
        st.session_state.user_name = name
        st.session_state.birth_year = birth_year
        st.session_state.birth_month = birth_month
        st.session_state.birth_day = birth_day
        
        with st.spinner("鑑定書を生成中..."):
            try:
                # 1. PDF生成
                pdf_buffer = create_pdf(name, birth_year, birth_month, birth_day)
                pdf_data = pdf_buffer.getvalue()
                
                # 2. スプレッドシート保存（ここが追加機能）
                life_path = calculate_life_path_number(birth_year, birth_month, birth_day)
                save_to_gsheet(name, birth_year, birth_month, birth_day, life_path)

                # 3. セッションに保存
                st.session_state.pdf_data = pdf_data
                filename = f"運勢鑑定書_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                st.session_state.pdf_filename = filename
                
                st.success("✅ PDFの生成が完了しました！")
                st.balloons()
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.exception(e)
    
    if st.session_state.pdf_data:
        st.download_button(
            label="📥 PDFをダウンロード", 
            data=st.session_state.pdf_data, 
            file_name=st.session_state.pdf_filename, 
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

st.markdown("""
    <div class="custom-footer">
        <div>
            <a href="https://mizary.com/tokusyouhou/" target="_blank">特定商取引法に基づく表記</a> | 
            <a href="https://mizary.com/privacy/" target="_blank">プライバシーポリシー</a>
        </div>
        <div class="copyright">© 2026 占いミザリー</div>
    </div>
    """, unsafe_allow_html=True)