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
SPREADSHEET_KEY = "1GFS4FjxcHvamWlJaFbXFTmJuL3UyTtaiT4eVxxF15vU"

try:
sheet = client.open_by_key(SPREADSHEET_KEY).sheet1
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
"""PDFをメモリ上で生成してBytesIOオブジェクトを返す"""
lp = calculate_life_path_number(y, m, d)
data = get_fortune_data(lp)
monthly_data = get_monthly_fortunes(lp)

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
c.drawCentredString(width/2, current_y, f"生年月日: {y}年{m}月{d}日  (LP: {lp})")
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

# アップセル（占いミザリーへの誘導）セクション
current_y -= 30
c.setFillColor(title_color)
c.setFont(font_name, 16)
c.drawCentredString(width/2, current_y, "より深い悩みは占いミザリーへ")
current_y -= 25

c.setFillColor(text_color)
c.setFont(font_name, 11)
upsell_text = "恋愛・仕事・人間関係など、もっと詳しく知りたい方は\n電話占いでプロの占い師に直接ご相談ください。\nLINE予約なら1,000円割引20分2,980円～"
current_y = draw_wrapped_text(c, upsell_text, margin, current_y, content_width, font_name, 11, 20, text_color)
current_y -= 20

# 電話占いのURL（クリック可能なリンクとして追加）
c.setFillColor(HexColor("#D81B60"))
c.setFont(font_name, 10)
phone_fortune_url = "https://mizary.com/"
url_text_y = current_y
c.drawCentredString(width/2, url_text_y, phone_fortune_url)

# リンクを追加（ReportLabのlinkURLを使用）
link_left = width/2 - 120
link_right = width/2 + 120
link_bottom = url_text_y - 5
link_top = url_text_y + 10
c.linkURL(phone_fortune_url, (link_left, link_bottom, link_right, link_top), relative=0)

# フッター
current_y = 50
c.setFillColor(HexColor("#999999"))
c.setFont(font_name, 9)
c.drawCentredString(width/2, current_y, "Mizary Fortune Telling - 2026 Special Report")

c.save()
buffer.seek(0)
return buffer

# ==========================================
# 7. アプリUI
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
   
   /* ボタンデザイン（#e10080） */
   div.stButton > button {
       background-color: #e10080 !important;
       color: white !important;
       font-weight: bold !important;
       border: none !important;
       padding: 10px 20px !important;
       border-radius: 10px !important;
   }
   
   /* カスタムボタン（#e10080） */
   a[href*="stripe"] button,
   div[style*="text-align: center"] button {
       background-color: #e10080 !important;
       color: white !important;
       border: none !important;
       padding: 15px 40px !important;
       font-size: 18px !important;
       font-weight: 500 !important;
       border-radius: 25px !important;
       cursor: pointer !important;
       box-shadow: 0 4px 12px rgba(225, 0, 128, 0.3) !important;
       transition: all 0.3s ease !important;
   }
   
   a[href*="stripe"] button:hover,
   div[style*="text-align: center"] button:hover {
       background-color: #c1006e !important;
       transform: translateY(-2px) !important;
       box-shadow: 0 6px 16px rgba(225, 0, 128, 0.4) !important;
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

query_params = st.query_params
is_paid = query_params.get("paid") == "true" or query_params.get("checkout") == "success"

# セッション管理
if 'user_name' not in st.session_state: st.session_state.update({k: v for k, v in zip(['user_name','birth_year','birth_month','birth_day'], ['', 2000, 1, 1])})
if 'pdf_data' not in st.session_state: st.session_state.pdf_data = None

if not is_paid:
st.info("👋 ようこそ！まずは無料プレビューをご覧ください。")

preview_name = ""
preview_year = 2000
preview_month = 1
preview_day = 1

with st.form("preview"):
preview_name = st.text_input("お名前", placeholder="山田 花子")
cols = st.columns(3)
preview_year = cols[0].number_input("年", 1900, 2025, 2000)
preview_month = cols[1].number_input("月", 1, 12, 1)
preview_day = cols[2].number_input("日", 1, 31, 1)
preview_submitted = st.form_submit_button("鑑定結果の一部を見る")

if preview_submitted and preview_name:
# ライフパスナンバーを計算
preview_lp = calculate_life_path_number(preview_year, preview_month, preview_day)
preview_data = get_fortune_data(preview_lp)

# 名前と見出し（興味を引く内容）を表示
st.markdown("---")
st.markdown(f"### {preview_name} 様の2026年運勢")
st.markdown(f"**ライフパスナンバー: {preview_lp}**")

# 興味を引く見出しを表示
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
           <a href="#完全版鑑定書" style="color: #e10080; text-decoration: none; font-weight: bold; font-size: 1.1rem;">
               ↓ 続きは「完全版鑑定書 (PDF)」をご覧ください ↓
           </a>
       </div>
       """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div id="完全版鑑定書"></div>', unsafe_allow_html=True)
st.header("💎 完全版鑑定書 (PDF)")
st.write("2026年を最高の一年にするための、あなただけのガイドブックです。")

with st.form("pay"):
name = st.text_input("お名前", key="p_name", placeholder="山田 花子")
c1, c2, c3 = st.columns(3)
y = c1.number_input("年", 1900, 2025, 2000, key="p_y")
m = c2.number_input("月", 1, 12, 1, key="p_m")
d = c3.number_input("日", 1, 31, 1, key="p_d")
if st.form_submit_button("情報を保存"):
st.session_state.update({'user_name': name, 'birth_year': y, 'birth_month': m, 'birth_day': d})
st.success("保存しました")

st.markdown("<br>", unsafe_allow_html=True)
    # ▼▼▼ Stripeリンク（ボタン色#e10080） ▼▼▼
    stripe_url = "https://buy.stripe.com/8x2fZhfsm01Q813847cfT1v"
    # ▼▼▼【重要】ここにStripeの本番URLを貼り付けてください！▼▼▼
    
    # Stripeリンク
stripe_url = "https://buy.stripe.com/8x2fZhfsm01Q813847cfT1v"

    # 料金表記（50%オフ）
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <div style="color: #e10080; font-size: 1.2rem; font-weight: bold; margin-bottom: 5px;">
            <span style="text-decoration: line-through; color: #999; font-size: 0.9rem; margin-right: 10px;">通常1,000円</span>
            <span style="background-color: #fff3cd; color: #e10080; padding: 3px 10px; border-radius: 5px; font-size: 0.9rem;">50%OFF</span>
        </div>
        <div style="color: #666; font-size: 0.85rem; margin-bottom: 15px;">
            ※1月31日まで
        </div>
    </div>
    """, unsafe_allow_html=True)
    
st.markdown(f"""
   <div style="text-align: center; margin: 30px 0;">
       <a href="{stripe_url}" style="text-decoration: none;">
           <button style="background-color: #e10080 !important; color: white !important; border: none !important; padding: 15px 40px !important; font-size: 18px !important; font-weight: 500 !important; border-radius: 25px !important; cursor: pointer !important; box-shadow: 0 4px 12px rgba(225, 0, 128, 0.3) !important; transition: all 0.3s ease !important;">
               👉 500円で鑑定書を発行する
           </button>
       </a>
   </div>
   """, unsafe_allow_html=True)

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
    
    # セッションから情報を取得
    name = st.session_state.user_name if st.session_state.user_name else ""
    y = st.session_state.birth_year if st.session_state.birth_year else 2000
    m = st.session_state.birth_month if st.session_state.birth_month else 1
    d = st.session_state.birth_day if st.session_state.birth_day else 1
    
    # セッションに情報があれば自動的にPDFを生成
    if name and not st.session_state.pdf_data:
        with st.spinner("鑑定書を生成中..."):
try:
pdf = create_pdf(name, y, m, d)
st.session_state.pdf_data = pdf.getvalue()
                st.session_state.pdf_filename = f"運勢鑑定書_{name}.pdf"
                st.session_state.pdf_filename = f"運勢鑑定書_{name}_{datetime.now().strftime('%Y%m%d')}.pdf"

# スプレッドシート保存
save_to_gsheet(name, y, m, d, calculate_life_path_number(y, m, d))
                st.success("完了しました！")
                st.success("✅ 鑑定書の準備が完了しました！")
except Exception as e:
                st.error(f"エラー: {e}")

                st.error(f"エラーが発生しました: {e}")
    
    # 情報が不足している場合はフォームを表示
    if not name:
        st.info("お名前を入力してください。")
        with st.form("final"):
            st.write("### 📄 発行フォーム")
            name = st.text_input("お名前", placeholder="山田 花子")
            c1, c2, c3 = st.columns(3)
            y = c1.number_input("年", 1900, 2025, y)
            m = c2.number_input("月", 1, 12, m)
            d = c3.number_input("日", 1, 31, d)
            submitted = st.form_submit_button("✨ PDFをダウンロード", use_container_width=True)
        
        if submitted and name:
            # セッションに保存
            st.session_state.user_name = name
            st.session_state.birth_year = y
            st.session_state.birth_month = m
            st.session_state.birth_day = d
            
            with st.spinner("生成中..."):
                try:
                    pdf = create_pdf(name, y, m, d)
                    st.session_state.pdf_data = pdf.getvalue()
                    st.session_state.pdf_filename = f"運勢鑑定書_{name}_{datetime.now().strftime('%Y%m%d')}.pdf"
                    
                    # スプレッドシート保存
                    save_to_gsheet(name, y, m, d, calculate_life_path_number(y, m, d))
                    st.success("完了しました！")
                    st.rerun()
                except Exception as e:
                    st.error(f"エラー: {e}")
    
    # PDFが生成済みの場合はダウンロードボタンを表示
if st.session_state.pdf_data:
        st.download_button("📥 ダウンロード", st.session_state.pdf_data, file_name=st.session_state.pdf_filename, mime="application/pdf", type="primary", use_container_width=True)
        st.markdown("---")
        st.markdown(f"### {name} 様の鑑定書")
        st.download_button(
            "📥 PDFをダウンロード", 
            st.session_state.pdf_data, 
            file_name=st.session_state.pdf_filename, 
            mime="application/pdf", 
            type="primary", 
            use_container_width=True
        )
        
        # もう一度最初からボタン
        if st.button("トップに戻る"):
            st.session_state.pdf_data = None
            st.session_state.pdf_filename = None
            st.query_params.clear()
            st.rerun()

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
