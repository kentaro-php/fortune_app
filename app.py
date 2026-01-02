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
        if y < 30: # ページ下端に来たら中断（改ページ処理は簡易的に省略）
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
    # 簡易データ（本来はもっと長文を入れると価値が上がります）
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
    # ナンバーごとのカスタマイズ（例として一部変化させています）
    if life_path % 2 == 0:
        data["color"] = "シルバー"
        data["overall"] = ("中吉", "2026年は基盤を固める年。焦らず着実に進むことで、揺るぎない成果を手に入れます。")
    return data

def get_monthly_fortunes(life_path):
    """1月〜12月の運勢リストを返す"""
    # サンプルデータ（実際はLPごとに変えるロジックを入れる）
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

    # タイトル
    c.setFillColor(title_color)
    c.setFont(font_name, 26)
    c.drawCentredString(width/2, current_y, "2026年 運勢鑑定書")
    current_y -= 40
    
    # 名前・基本情報
    c.setFillColor(accent_color)
    c.setFont(font_name, 22)
    c.drawCentredString(width/2, current_y, f"{name} 様")
    current_y -= 30
    
    c.setFillColor(text_color)
    c.setFont(font_name, 12)
    c.drawCentredString(width/2, current_y, f"生年月日: {birth_year}年{birth_month}月{birth_day}日  (LP: {life_path})")
    current_y -= 40

    # 性格
    c.setFillColor(title_color)
    c.setFont(font_name, 14)
    c.drawString(margin, current_y, "【あなたの本質】")
    current_y -= 20
    current_y = draw_wrapped_text(c, data["personality"], margin, current_y, content_width, font_name, 11, 18, text_color)
    current_y -= 25

    # 総合運
    c.setFillColor(title_color)
    c.setFont(font_name, 14)
    c.drawString(margin, current_y, "【2026年の総合運】")
    c.setFillColor(accent_color)
    c.drawString(margin + 150, current_y, data["overall"][0]) # 大吉など
    current_y -= 20
    current_y = draw_wrapped_text(c, data["overall"][1], margin, current_y, content_width, font_name, 11, 18, text_color)
    current_y -= 25

    # 各種運勢（グリッドっぽく配置）
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
        
        # ★表示
        c.setFillColor(accent_color)
        star_str = "★" * stars + "☆" * (5 - stars)
        c.drawString(margin + 100, current_y, star_str)
        current_y -= 20
        
        current_y = draw_wrapped_text(c, text, margin, current_y, content_width, font_name, 11, 18, text_color)
        current_y -= 20 # 行間

    # ラッキーアイテム
    current_y -= 10
    c.setFillColor(title_color)
    c.setFont(font_name, 14)
    c.drawString(margin, current_y, f"ラッキーカラー： {data['color']}   /   ラッキーアイテム： {data['item']}")
    
    # --- 2ページ目（月別運勢） ---
    c.showPage()
    
    # 背景
    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, fill=1)
    
    current_y = height - 60
    c.setFillColor(title_color)
    c.setFont(font_name, 20)
    c.drawCentredString(width/2, current_y, "2026年 月別運勢カレンダー")
    current_y -= 50
    
    # リスト表示
    c.setFillColor(text_color)
    c.setFont(font_name, 12)
    
    for month_text in monthly_data:
        # 月の部分だけ色を変えたり太字にしたいが、シンプルに描画
        current_y = draw_wrapped_text(c, month_text, margin, current_y, content_width, font_name, 12, 25, text_color)
        current_y -= 15 # 各月の間隔

    # フッター
    c.setFillColor(HexColor("#999999"))
    c.setFont(font_name, 9)
    c.drawCentredString(width/2, 30, "Mizary Fortune Telling - 2026 Special Report")

    c.save()
    return filename

# ==========================================
# 6. アプリUI (Stripe対応版)
# ==========================================

# CSSで見栄えを良くする（不要なボタン非表示設定を追加）
st.markdown("""
    <style>
    /* タイトル周りのデザイン */
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
    /* ボタンのカスタマイズ */
    div.stButton > button {
        background-color: #C71585;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
    }
    
    /* ▼▼▼ ここが追加：Streamlitの標準パーツを消す設定 ▼▼▼ */
    
    /* 右下の「Manage app」ボタンなどを消す */
    .stDeployButton {
        display: none;
    }
    
    /* 右上の「ハンバーガーメニュー（三本線）」を消す */
    #MainMenu {
        visibility: hidden;
    }
    
    /* 下部の「Made with Streamlit」フッターを消す */
    footer {
        visibility: hidden;
    }
    
    /* 上部のヘッダーバーを消す */
    header {
        visibility: hidden;
    }
    </style>
    
    <div class="title-container">
        <div class="sub-title">✨ 数秘術で紐解くあなたの未来 ✨</div>
        <div class="main-title">2026年 運勢鑑定書</div>
        <div style="color: #cccccc;">Designed for your special year</div>
    </div>
    """, unsafe_allow_html=True)
    
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