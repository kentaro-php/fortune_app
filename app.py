import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os
import urllib.request
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="2026年運勢鑑定書",
    layout="centered"
)

# フォントファイルのパス
FONT_DIR = "fonts"
FONT_PATH = os.path.join(FONT_DIR, "ipaexm.ttf")

def download_font():
    """IPAex明朝フォントをダウンロードする"""
    if not os.path.exists(FONT_DIR):
        os.makedirs(FONT_DIR)
    
    if not os.path.exists(FONT_PATH):
        font_url = "https://raw.githubusercontent.com/making/demo-jasper-report-ja/master/src/main/resources/fonts/ipaexm/ipaexm.ttf"
        try:
            urllib.request.urlretrieve(font_url, FONT_PATH)
            st.success("フォントをダウンロードしました")
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
# 【重要】日本語対応の折り返し関数
# ==========================================
def draw_wrapped_text(c, text, x, y, max_width, font_name, font_size, line_height, color=HexColor("#333333")):
    """長い日本語テキストを指定幅で折り返して描画し、書き終わったY座標を返す"""
    c.setFillColor(color)
    c.setFont(font_name, font_size)
    
    lines = []
    current_line = ""
    
    # 1文字ずつ幅をチェックしていく
    for char in text:
        # 今の行にこの文字を足しても幅に収まるか？
        if c.stringWidth(current_line + char, font_name, font_size) <= max_width:
            current_line += char
        else:
            # 収まらないなら今の行を保存して、新しい行にする
            lines.append(current_line)
            current_line = char
    
    # 最後の行を追加
    if current_line:
        lines.append(current_line)
    
    # 描画処理
    for line in lines:
        if y < 50: break # ページ下端チェック
        c.drawString(x, y, line)
        y -= line_height
    
    return y

# -------------------------------------------------
# 運勢ロジック（変更なし）
# -------------------------------------------------
def calculate_life_path_number(year, month, day):
    def sum_digits(n):
        while n >= 10:
            n = sum(int(d) for d in str(n))
        return n
    total = sum_digits(year) + sum_digits(month) + sum_digits(day)
    life_path = sum_digits(total)
    if total in [11, 22, 33]: return total
    return life_path

def get_personality(life_path):
    personalities = {
        1: "あなたには、自然と人を導く力が備わっている傾向があります。独立心が強く、新しいことに挑戦する勇気をお持ちのようです。自分らしさを大切にしながら、周囲の人々にも良い影響を与えられる存在として輝いていらっしゃることでしょう。",
        2: "感受性が豊かで、人の気持ちを深く理解できる優しさをお持ちのようです。協調性があり、周囲との調和を大切にされる傾向があります。その繊細な心は、あなたの大きな魅力となっています。",
        3: "創造性と表現力に恵まれ、芸術的な才能やコミュニケーション能力が高い傾向があります。あなたのアイデアや言葉は、周囲の人々に喜びと感動を与える力を持っているようです。",
        4: "誠実で責任感が強く、実務的な能力に優れている傾向があります。安定を好み、着実に物事を進める力をお持ちのようです。その真面目さと信頼性は、周囲から高く評価されていることでしょう。",
        5: "自由を愛し、好奇心旺盛なあなたは、変化を楽しみながら多様な経験を求められる傾向があります。その柔軟性と冒険心は、人生を豊かに彩る力となっているようです。",
        6: "愛情深く、奉仕の精神が強いあなたは、家族や友人を大切にし、調和を重んじる傾向があります。その優しさと献身的な姿勢は、周囲の人々に安心感を与えていることでしょう。",
        7: "分析的で内省的、スピリチュアルな探求や深い思考を好まれる傾向があります。その洞察力と直感は、人生の本質を見抜く力となっているようです。",
        8: "実力があり、成功への意欲が強い傾向があります。ビジネスセンスに優れ、権威を築く力をお持ちのようです。その努力と才能は、着実に実を結んでいくことでしょう。",
        9: "博愛主義で理想が高く、人々のために貢献することを喜びとされる傾向があります。その慈愛に満ちた心は、多くの人々に希望と勇気を与える力となっているようです。",
        11: "直感力が鋭く、インスピレーションに富まれている傾向があります。スピリチュアルな導き手としての資質をお持ちのようです。その直感を信じて行動されることで、素晴らしい道が開けていくことでしょう。",
        22: "実践的な理想主義者として、大きなビジョンを現実化する力をお持ちの傾向があります。その理想と実践力のバランスは、多くの人々に希望を与える存在となっているようです。",
        33: "慈愛に満ちた教師として、多くの人々を導き、癒す力を持たれている傾向があります。その優しさと知恵は、周囲の人々に深い影響を与える特別な存在となっているようです。"
    }
    return personalities.get(life_path, "独特な個性を持ち、独自の道を歩んでいらっしゃるようです。")

def get_fortune(life_path):
    fortunes = {
        1: ("大吉", "2026年は、あなたにとって新しいスタートの年となる傾向があります。積極的に行動されることで、大きな成果が期待できるでしょう。"),
        2: ("中吉", "2026年は、協力関係が特に重要となる年となりそうです。パートナーシップを大切にされることで、運気が上昇していく傾向があります。"),
        3: ("大吉", "2026年は、あなたの創造性が開花する年となる傾向があります。表現活動やコミュニケーションを通じて、成功のチャンスが訪れる可能性が高いでしょう。"),
        4: ("中吉", "2026年は、着実な成長の年となりそうです。努力を積み重ねることで、安定した成果を得られる傾向があります。焦らず、一歩ずつ進まれることで、確かな実りが待っていることでしょう。"),
        5: ("小吉", "2026年は、変化と自由の年となる傾向があります。新しい環境や経験が、あなたの運気を高める可能性が高いでしょう。"),
        6: ("中吉", "2026年は、愛情と調和の年となりそうです。人間関係が深まり、心の豊かさが増していく傾向があります。"),
        7: ("小吉", "2026年は、内面の探求の年となる傾向があります。スピリチュアルな成長と深い洞察が得られる可能性が高いでしょう。"),
        8: ("大吉", "2026年は、成功と達成の年となる傾向があります。ビジネスやキャリアにおいて、大きな飛躍が期待できるでしょう。"),
        9: ("中吉", "2026年は、完成と新たな始まりの年となる傾向があります。これまでの努力が実を結び、次のステップへと進む準備が整う可能性が高いでしょう。"),
        11: ("大吉", "2026年は、直感とインスピレーションが強く働く年となる傾向があります。スピリチュアルな導きが、あなたの人生をより良い方向へと導いてくれる可能性が高いでしょう。"),
        22: ("大吉", "2026年は、大きなビジョン実現の年となる傾向があります。理想を現実化する力が最大限に発揮される可能性が高いでしょう。"),
        33: ("大吉", "2026年は、慈愛と癒しの年となる傾向があります。多くの人々に影響を与える特別な年となりそうです。")
    }
    return fortunes.get(life_path, ("中吉", "2026年は、バランスの取れた一年となる傾向があります。"))

def get_love_fortune(life_path):
    love_fortunes = {
        1: (4, "2026年は、積極的なアプローチが成功の鍵となる傾向があります。新しい出会いを求めて行動されることで、素晴らしい出会いが訪れる可能性が高いでしょう。"),
        2: (5, "2026年は、パートナーシップが深まる年となる傾向があります。相手の気持ちに寄り添うことで、関係がより深く発展していく可能性が高いでしょう。"),
        3: (5, "2026年は、コミュニケーションが特に重要となる年となりそうです。楽しい会話を通じて、関係が深まっていく傾向があります。"),
        4: (3, "2026年は、安定した関係を築く年となる傾向があります。誠実さと信頼が、あなたの恋愛運を高めていく可能性が高いでしょう。"),
        5: (4, "2026年は、新しい出会いのチャンスが訪れる年となりそうです。自由な心で恋愛を楽しまれることで、素晴らしい出会いが待っている可能性が高いでしょう。"),
        6: (5, "2026年は、愛情が深まる年となる傾向があります。家族やパートナーとの絆が、より強く深くなっていく可能性が高いでしょう。"),
        7: (3, "2026年は、内面の成長が恋愛運を高める年となりそうです。深いつながりを求められることで、真のパートナーシップが築かれる可能性が高いでしょう。"),
        8: (4, "2026年は、魅力的なあなたに注目が集まる年となる傾向があります。自信を持って行動されることで、素晴らしい出会いが訪れる可能性が高いでしょう。"),
        9: (4, "2026年は、理想のパートナーとの出会いの可能性が高い年となりそうです。広い視野で探されることで、心から理解し合える相手と出会える可能性があります。"),
        11: (5, "2026年は、直感に従うことで素晴らしい出会いが訪れる年となる傾向があります。内なる声を信じて行動されることで、運命的な出会いが待っている可能性が高いでしょう。"),
        22: (5, "2026年は、理想的なパートナーシップが実現する可能性が高い年となりそうです。これまでに描いてきた理想の関係が、現実のものとなる可能性があります。"),
        33: (5, "2026年は、深い愛情と理解に満ちた関係が築かれる年となる傾向があります。あなたの優しさと慈愛が、パートナーとの絆をより深くしていく可能性が高いでしょう。")
    }
    return love_fortunes.get(life_path, (3, "2026年は、バランスの取れた恋愛運となる傾向があります。"))

def get_work_fortune(life_path):
    work_fortunes = {
        1: (5, "2026年は、リーダーシップを発揮する年となる傾向があります。新しいプロジェクトで成功を収められる可能性が高いでしょう。"),
        2: (4, "2026年は、チームワークが特に重要となる年となりそうです。協力関係を大切にされることで、成果が上がっていく傾向があります。"),
        3: (5, "2026年は、創造的な仕事で評価される年となる傾向があります。アイデアが次々と実現していく可能性が高いでしょう。"),
        4: (4, "2026年は、着実な努力が認められる年となりそうです。責任ある立場での活躍が期待できる傾向があります。"),
        5: (3, "2026年は、変化とチャレンジの年となる傾向があります。新しい分野への挑戦が、あなたの運気を高めていく可能性が高いでしょう。"),
        6: (4, "2026年は、サービス精神が評価される年となる傾向があります。人のために働くことで、成果が得られていく可能性が高いでしょう。"),
        7: (4, "2026年は、分析力と研究が光る年となりそうです。専門性を高めることで、評価が上がっていく傾向があります。"),
        8: (5, "2026年は、ビジネスで大きな成功を収める年となる傾向があります。権威や地位が向上していく可能性が高いでしょう。"),
        9: (4, "2026年は、理想を実現する年となる傾向があります。社会貢献につながる仕事で、成果を上げられる可能性が高いでしょう。"),
        11: (5, "2026年は、インスピレーションが仕事を導く年となる傾向があります。直感を信じて行動されることで、素晴らしい成果が得られる可能性が高いでしょう。"),
        22: (5, "2026年は、大きなプロジェクトの成功が期待できる年となりそうです。理想を現実化する力が、最大限に発揮される傾向があります。"),
        33: (5, "2026年は、多くの人々に影響を与える仕事で成功する年となる傾向があります。あなたの慈愛と知恵が、仕事を通じて多くの人々に希望と勇気を与えていくことでしょう。")
    }
    return work_fortunes.get(life_path, (3, "2026年は、バランスの取れた仕事運となる傾向があります。"))

def get_lucky_color(life_path):
    colors = {1:"ゴールド", 2:"ピンク", 3:"イエロー", 4:"エメラルドグリーン", 5:"ターコイズブルー", 6:"ローズピンク", 7:"パープル", 8:"シルバー", 9:"ロイヤルブルー", 11:"クリスタル", 22:"プラチナ", 33:"レインボー"}
    return colors.get(life_path, "ピンク")

def get_lucky_item(life_path):
    items = {1:"ペンダント", 2:"ハート型のアクセサリー", 3:"アート作品", 4:"実用的なバッグ", 5:"旅行グッズ", 6:"家族の写真", 7:"クリスタル", 8:"高級時計", 9:"記念品", 11:"スピリチュアルなアイテム", 22:"ビジョンボード", 33:"癒しのアイテム"}
    return items.get(life_path, "お守り")

def create_pdf(name, birth_year, birth_month, birth_day):
    """PDFを生成する（レイアウト修正版）"""
    life_path = calculate_life_path_number(birth_year, birth_month, birth_day)
    personality = get_personality(life_path)
    overall_fortune, fortune_desc = get_fortune(life_path)
    love_stars, love_advice = get_love_fortune(life_path)
    work_stars, work_advice = get_work_fortune(life_path)
    lucky_color = get_lucky_color(life_path)
    lucky_item = get_lucky_item(life_path)
    
    filename = f"運勢鑑定書_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4 
    
    bg_color = HexColor("#FFFBF0")
    text_color = HexColor("#333333")
    accent_color = HexColor("#C0A060")
    title_color = HexColor("#C71585")

    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, fill=1)
    
    if register_font():
        font_name = 'IPAexMincho'
    else:
        font_name = 'Helvetica'
    
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
    c.drawCentredString(width/2, current_y, f"生年月日: {birth_year}年{birth_month}月{birth_day}日")
    current_y -= 40

    c.setFillColor(title_color)
    c.setFont(font_name, 18)
    c.drawCentredString(width/2, current_y, f"ライフパスナンバー：{life_path}")
    current_y -= 40

    # 性格（自動折り返し）
    current_y = draw_wrapped_text(c, personality, margin, current_y, content_width, font_name, 11, 18, text_color)
    current_y -= 30 

    # 総合運
    c.setFillColor(title_color)
    c.setFont(font_name, 16)
    c.drawString(margin, current_y, "【総合運】")
    current_y -= 25
    
    c.setFillColor(accent_color)
    c.setFont(font_name, 20)
    c.drawString(margin, current_y, overall_fortune)
    current_y -= 25
    
    current_y = draw_wrapped_text(c, fortune_desc, margin, current_y, content_width, font_name, 11, 18, text_color)
    current_y -= 30

    # 恋愛運
    c.setFillColor(title_color)
    c.setFont(font_name, 16)
    c.drawString(margin, current_y, "【恋愛運】")
    current_y -= 25
    
    c.setFillColor(accent_color)
    c.setFont(font_name, 16)
    stars = "★" * love_stars + "☆" * (5 - love_stars)
    c.drawString(margin, current_y, stars)
    current_y -= 25
    
    current_y = draw_wrapped_text(c, love_advice, margin, current_y, content_width, font_name, 11, 18, text_color)
    current_y -= 30

    # 仕事運
    c.setFillColor(title_color)
    c.setFont(font_name, 16)
    c.drawString(margin, current_y, "【仕事運】")
    current_y -= 25
    
    c.setFillColor(accent_color)
    c.setFont(font_name, 16)
    stars = "★" * work_stars + "☆" * (5 - work_stars)
    c.drawString(margin, current_y, stars)
    current_y -= 25
    
    current_y = draw_wrapped_text(c, work_advice, margin, current_y, content_width, font_name, 11, 18, text_color)
    current_y -= 30

    # ラッキーアイテムなど
    c.setFillColor(title_color)
    c.setFont(font_name, 14)
    c.drawString(margin, current_y, f"ラッキーカラー： {lucky_color}")
    current_y -= 25
    c.drawString(margin, current_y, f"ラッキーアイテム： {lucky_item}")

    c.setFillColor(HexColor("#999999"))
    c.setFont(font_name, 9)
    c.drawCentredString(width/2, 30, "この鑑定書は数秘術に基づいて作成されました。")
    
    c.save()
    return filename

# UI部分
st.title("2026年 運勢鑑定書発行アプリ")
st.markdown("---")
if not os.path.exists(FONT_PATH):
    download_font()

with st.form("fortune_form"):
    name = st.text_input("お名前", placeholder="山田 花子")
    col1, col2, col3 = st.columns(3)
    with col1: birth_year = st.number_input("年", 1900, 2024, 2000)
    with col2: birth_month = st.number_input("月", 1, 12, 1)
    with col3: birth_day = st.number_input("日", 1, 31, 1)
    submitted = st.form_submit_button("鑑定書を発行する", use_container_width=True)

if submitted and name:
    with st.spinner("鑑定書を生成中..."):
        try:
            pdf_file = create_pdf(name, birth_year, birth_month, birth_day)
            with open(pdf_file, "rb") as f:
                st.download_button("📥 PDFをダウンロード", f, file_name=pdf_file, mime="application/pdf")
        except Exception as e:
            st.error(f"エラー: {e}")