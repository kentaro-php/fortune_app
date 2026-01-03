import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os
import urllib.request
from datetime import datetime

# ==========================================
# 1. ページ設定
# ==========================================
st.set_page_config(
    page_title="2026年運勢鑑定書",
    layout="centered",
    page_icon="🔮"
)

# フォントファイルのパス設定
FONT_DIR = "fonts"
FONT_PATH = os.path.join(FONT_DIR, "ipaexm.ttf")

# ==========================================
# 2. フォント準備・登録関数
# ==========================================
def download_font():
    """IPAex明朝フォントをダウンロードする"""
    if not os.path.exists(FONT_DIR):
        os.makedirs(FONT_DIR)
    
    if not os.path.exists(FONT_PATH):
        font_url = "https://raw.githubusercontent.com/making/demo-jasper-report-ja/master/src/main/resources/fonts/ipaexm/ipaexm.ttf"
        try:
            urllib.request.urlretrieve(font_url, FONT_PATH)
        except Exception as e:
            st.error(f"フォントのダウンロードに失敗しました: {e}")
            return False
    return True

def register_font():
    """フォントをReportLabに登録する"""
    if os.path.exists(FONT_PATH):
        try:
            pdfmetrics.registerFont(TTFont('IPAexMincho', FONT_PATH))
            return True
        except Exception as e:
            st.error(f"フォントの登録に失敗しました: {e}")
            return False
    return False

# ==========================================
# 3. PDF描画用ヘルパー関数（日本語折り返し対応）
# ==========================================
def draw_wrapped_text(c, text, x, y, max_width, font_name, font_size, line_height, color=HexColor("#333333")):
    """長い日本語テキストを指定幅で折り返して描画し、書き終わったY座標を返す"""
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
        if y < 30: # ページ下端に来たら中断
            break
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
    """ライフパスナンバーに基づく運勢データを一括取得"""
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
    """1月〜12月の運勢リストを返す"""
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
# 5. PDF生成関数（2ページ構成）
# ==========================================
def create_pdf(name, birth_year, birth_month, birth_day):
    life_path = calculate_life_path_number(birth_year, birth_month, birth_day)
    data = get_fortune_data(life_path)
    monthly_data = get_monthly_fortunes(life_path)
    
    filename = f"運勢鑑定書_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4 
    
    # 色定義
    bg_color = HexColor("#FFFBF0")
    text_color = HexColor("#333333")
    accent_color = HexColor("#C0A060")
    title_color = HexColor("#C71585")
    
    if register_font():
        font_name = 'IPAexMincho'
    else:
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

    topics = [
        ("恋愛運", data["love"]),
        ("仕事運", data["work"]),
        ("金運", data["money"]),
        ("健康運", data["health"]),
        ("対人運", data["interpersonal"]),
    ]
    
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
    
    # --- 2ページ目（月別運勢） ---
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
    return filename

# ==========================================
# 6. アプリUI (Stripe & 強制非表示CSS対応)
# ==========================================

st.markdown("""
    <style>
    /* タイトルデザイン */
    .title-container {
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #C0A060;
        margin-bottom: 30px;
    }
    .main-title {
        font-family: "Helvetica", "Arial", sans-serif;
        font-weight: bold;
        font-size: 2.5rem;
        background: linear-gradient(45deg, #FFB6C1, #C71585);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #C0A060;
        font-weight: bold;
    }
    
    /* ボタンデザイン */
    div.stButton > button {
        background-color: #C71585;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
    }
    
    /* --- 管理用ボタン・メニューの非表示設定 --- */
    
    /* 右上のハンバーガーメニューを非表示 */
    #MainMenu { visibility: hidden; }
    .stDeployButton { display: none; }
    
    /* フッター（Made with Streamlit）を完全に非表示 */
    footer { visibility: hidden; }
    footer[data-testid="stFooter"] { display: none !important; }
    .stApp footer { display: none !important; }
    
    /* ヘッダーを非表示 */
    header { visibility: hidden; }
    
    /* 右下のツールバー（王冠アイコン等）を強制的に消す */
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    /* 右下のユーザープロフィール画像とツールバーボタンを完全に非表示 */
    div[data-testid="stToolbar"] > * {
        display: none !important;
    }
    button[title="Manage app"] {
        display: none !important;
    }
    button[kind="header"] {
        display: none !important;
    }
    /* Streamlit Cloudのユーザーアバター */
    div[data-testid="stHeader"] {
        display: none !important;
    }
    /* 右下に固定されるすべての要素 */
    div[style*="position: fixed"][style*="bottom"] {
        display: none !important;
    }
    /* より具体的なセレクタで右下の要素を非表示 */
    .stApp > div:last-child > div:last-child {
        display: none !important;
    }
    /* ツールバー関連のすべての要素 */
    [class*="stToolbar"],
    [class*="toolbar"],
    [data-testid*="toolbar"],
    [data-testid*="Toolbar"] {
        display: none !important;
    }
    /* Streamlit Cloudのユーザーアバターとボタン */
    div[data-testid="stHeader"] button,
    div[data-testid="stHeader"] img,
    div[data-testid="stHeader"] a {
        display: none !important;
    }
    /* 右下に固定されるすべてのボタンと画像 */
    button[style*="position: fixed"],
    img[style*="position: fixed"],
    a[style*="position: fixed"] {
        display: none !important;
    }
    /* より包括的な非表示設定 */
    iframe[title*="streamlit"],
    iframe[src*="streamlit"] {
        display: none !important;
    }
    
    /* カスタムフッターのスタイル */
    .custom-footer {
        text-align: center;
        padding: 30px 20px;
        margin-top: 50px;
        border-top: 1px solid #E8E8E8;
        color: #666666;
        font-size: 0.9rem;
    }
    .custom-footer a {
        color: #D81B60;
        text-decoration: none;
        margin: 0 10px;
    }
    .custom-footer a:hover {
        text-decoration: underline;
    }
    .custom-footer .copyright {
        margin-top: 10px;
        color: #999999;
        font-size: 0.85rem;
    }
    </style>
    
    <div class="title-container">
        <div class="sub-title">✨ 数秘術で紐解くあなたの未来 ✨</div>
        <div class="main-title">2026年 運勢鑑定書</div>
        <div style="color: #cccccc;">Designed for your special year</div>
    </div>
    """, unsafe_allow_html=True)

if not os.path.exists(FONT_PATH):
    download_font()

# -------------------------------------------
# 決済状態のチェック
# -------------------------------------------
query_params = st.query_params
is_paid = query_params.get("paid") == "true"

# -------------------------------------------
# パターンA：未払い（LPページ）
# -------------------------------------------
if not is_paid:
    st.info("👋 ようこそ！まずは無料プレビューをご覧ください。")
    
    with st.form("preview_form"):
        st.write("### 🔮 無料プレビュー")
        st.caption("お名前と生年月日を入力してください")
        name = st.text_input("お名前", placeholder="山田 花子")
        col1, col2, col3 = st.columns(3)
        with col1: st.number_input("年", 1900, 2024, 2000)
        with col2: st.number_input("月", 1, 12, 1)
        with col3: st.number_input("日", 1, 31, 1)
        
        submitted = st.form_submit_button("鑑定結果の一部を見る")
    
    if submitted:
        st.warning("🔒 詳しい結果を見るには「完全版」の購入が必要です。")
        st.markdown(f"""
        **{name}** 様の運勢の鍵となる「ライフパスナンバー」や、
        **2026年の月別詳細運勢**、**金運・健康運**などを網羅した
        全2ページの鑑定書を発行します。
        """)

    st.markdown("---")
    st.header("💎 完全版鑑定書 (PDF)")
    st.write("2026年を最高の一年にするための、あなただけのガイドブックです。")
    
    # ▼▼▼【重要】ここにStripeの本番URLを貼り付けてください！▼▼▼
    stripe_url = "https://buy.stripe.com/28E4gzcga8yma9b1FJcfT1k" 
    
    st.link_button(
        label="👉 500円で鑑定書を発行する", 
        url=stripe_url, 
        type="primary", 
        use_container_width=True
    )

# -------------------------------------------
# パターンB：支払い完了（発行ページ）
# -------------------------------------------
else:
    st.success("✅ ご購入ありがとうございます！鑑定書を発行できます。")
    
    with st.form("fortune_form"):
        st.write("### 📄 鑑定書発行フォーム")
        st.write("正確な情報を入力して、PDFを生成してください。")
        name = st.text_input("お名前", placeholder="山田 花子")
        col1, col2, col3 = st.columns(3)
        with col1: birth_year = st.number_input("年", 1900, 2024, 2000)
        with col2: birth_month = st.number_input("月", 1, 12, 1)
        with col3: birth_day = st.number_input("日", 1, 31, 1)
        
        submitted = st.form_submit_button("✨ 鑑定書PDFをダウンロードする", use_container_width=True)

    if submitted and name:
        with st.spinner("鑑定書を生成中..."):
            try:
                pdf_file = create_pdf(name, birth_year, birth_month, birth_day)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥 PDFをダウンロード", 
                        data=f, 
                        file_name=pdf_file, 
                        mime="application/pdf",
                        type="primary"
                    )
                st.balloons()
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# -------------------------------------------
# フッター（著作権表示）
# -------------------------------------------
st.markdown("""
    <div class="custom-footer">
        <div>
            <a href="https://mizary.com/tokusyouhou/" target="_blank" rel="noopener noreferrer">特定商取引法に基づく表記</a> | 
            <a href="https://mizary.com/privacy/" target="_blank" rel="noopener noreferrer">プライバシーポリシー</a>
        </div>
        <div class="copyright">© 2026 占いミザリー</div>
    </div>
    """, unsafe_allow_html=True)