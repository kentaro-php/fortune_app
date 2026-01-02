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

def calculate_life_path_number(year, month, day):
    """生年月日からライフパスナンバーを計算する"""
    def sum_digits(n):
        while n >= 10:
            n = sum(int(d) for d in str(n))
        return n
    
    total = sum_digits(year) + sum_digits(month) + sum_digits(day)
    life_path = sum_digits(total)
    
    # マスターナンバー（11, 22, 33）の処理
    if total == 11 or total == 22 or total == 33:
        return total
    
    return life_path

def get_personality(life_path):
    """ライフパスナンバーから性格を取得"""
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
    return personalities.get(life_path, "あなたは独特な個性を持ち、独自の道を歩んでいらっしゃるようです。その個性を大切にしながら、自分らしい人生を切り拓いていかれることでしょう。")

def get_fortune(life_path):
    """ライフパスナンバーから運勢を取得"""
    fortunes = {
        1: ("大吉", "2026年は、あなたにとって新しいスタートの年となる傾向があります。積極的に行動されることで、大きな成果が期待できるでしょう。これまでに培ってきた経験と勇気を糧に、一歩ずつ前に進まれることをお勧めいたします。"),
        2: ("中吉", "2026年は、協力関係が特に重要となる年となりそうです。パートナーシップを大切にされることで、運気が上昇していく傾向があります。周囲の人々との信頼関係を深めながら、共に成長していかれると良いでしょう。"),
        3: ("大吉", "2026年は、あなたの創造性が開花する年となる傾向があります。表現活動やコミュニケーションを通じて、成功のチャンスが訪れる可能性が高いでしょう。自分らしさを大切にしながら、その才能を存分に発揮されると良いでしょう。"),
        4: ("中吉", "2026年は、着実な成長の年となりそうです。努力を積み重ねることで、安定した成果を得られる傾向があります。焦らず、一歩ずつ進まれることで、確かな実りが待っていることでしょう。"),
        5: ("小吉", "2026年は、変化と自由の年となる傾向があります。新しい環境や経験が、あなたの運気を高める可能性が高いでしょう。柔軟な心で、これまでとは違う世界に目を向けてみられると良いかもしれません。"),
        6: ("中吉", "2026年は、愛情と調和の年となりそうです。人間関係が深まり、心の豊かさが増していく傾向があります。大切な人との時間を大切にしながら、温かい絆を育んでいかれると良いでしょう。"),
        7: ("小吉", "2026年は、内面の探求の年となる傾向があります。スピリチュアルな成長と深い洞察が得られる可能性が高いでしょう。静かな時間を大切にしながら、自分自身と向き合うことで、新たな気づきが訪れることでしょう。"),
        8: ("大吉", "2026年は、成功と達成の年となる傾向があります。ビジネスやキャリアにおいて、大きな飛躍が期待できるでしょう。これまでの努力が実を結び、新たなステージへと進まれる可能性が高い年となりそうです。"),
        9: ("中吉", "2026年は、完成と新たな始まりの年となる傾向があります。これまでの努力が実を結び、次のステップへと進む準備が整う可能性が高いでしょう。過去を振り返りながら、未来への希望を胸に歩まれると良いでしょう。"),
        11: ("大吉", "2026年は、直感とインスピレーションが強く働く年となる傾向があります。スピリチュアルな導きが、あなたの人生をより良い方向へと導いてくれる可能性が高いでしょう。内なる声に耳を傾けながら、その導きに従って行動されると良いでしょう。"),
        22: ("大吉", "2026年は、大きなビジョン実現の年となる傾向があります。理想を現実化する力が最大限に発揮される可能性が高いでしょう。これまでに描いてきた夢を、着実に形にしていかれると良いでしょう。"),
        33: ("大吉", "2026年は、慈愛と癒しの年となる傾向があります。多くの人々に影響を与える特別な年となりそうです。あなたの優しさと知恵が、周囲の人々に希望と勇気を与える力となっていくことでしょう。")
    }
    return fortunes.get(life_path, ("中吉", "2026年は、バランスの取れた一年となる傾向があります。日々の努力が運気を高め、着実に前進していかれることでしょう。焦らず、自分らしいペースで歩まれると良いでしょう。"))

def get_love_fortune(life_path):
    """恋愛運を取得"""
    love_fortunes = {
        1: (4, "2026年は、積極的なアプローチが成功の鍵となる傾向があります。新しい出会いを求めて行動されることで、素晴らしい出会いが訪れる可能性が高いでしょう。自分らしさを大切にしながら、勇気を持って一歩を踏み出されると良いでしょう。"),
        2: (5, "2026年は、パートナーシップが深まる年となる傾向があります。相手の気持ちに寄り添うことで、関係がより深く発展していく可能性が高いでしょう。お互いを尊重し合いながら、温かい愛情を育んでいかれると良いでしょう。"),
        3: (5, "2026年は、コミュニケーションが特に重要となる年となりそうです。楽しい会話を通じて、関係が深まっていく傾向があります。あなたの表現力と明るさが、パートナーとの絆をより強くしていくことでしょう。"),
        4: (3, "2026年は、安定した関係を築く年となる傾向があります。誠実さと信頼が、あなたの恋愛運を高めていく可能性が高いでしょう。焦らず、着実に信頼関係を深めていかれると良いでしょう。"),
        5: (4, "2026年は、新しい出会いのチャンスが訪れる年となりそうです。自由な心で恋愛を楽しまれることで、素晴らしい出会いが待っている可能性が高いでしょう。固定観念にとらわれず、新しい可能性に目を向けてみられると良いでしょう。"),
        6: (5, "2026年は、愛情が深まる年となる傾向があります。家族やパートナーとの絆が、より強く深くなっていく可能性が高いでしょう。お互いを大切にしながら、温かい時間を共有されると良いでしょう。"),
        7: (3, "2026年は、内面の成長が恋愛運を高める年となりそうです。深いつながりを求められることで、真のパートナーシップが築かれる可能性が高いでしょう。表面的な関係ではなく、心の奥底でつながる関係を大切にされると良いでしょう。"),
        8: (4, "2026年は、魅力的なあなたに注目が集まる年となる傾向があります。自信を持って行動されることで、素晴らしい出会いが訪れる可能性が高いでしょう。あなたの実力と魅力が、自然と良い出会いを引き寄せていくことでしょう。"),
        9: (4, "2026年は、理想のパートナーとの出会いの可能性が高い年となりそうです。広い視野で探されることで、心から理解し合える相手と出会える可能性があります。理想を大切にしながら、柔軟な心で出会いを待たれると良いでしょう。"),
        11: (5, "2026年は、直感に従うことで素晴らしい出会いが訪れる年となる傾向があります。内なる声を信じて行動されることで、運命的な出会いが待っている可能性が高いでしょう。スピリチュアルな導きに従いながら、自然な流れに任せられると良いでしょう。"),
        22: (5, "2026年は、理想的なパートナーシップが実現する可能性が高い年となりそうです。これまでに描いてきた理想の関係が、現実のものとなる可能性があります。お互いを尊重し合いながら、共に成長していかれると良いでしょう。"),
        33: (5, "2026年は、深い愛情と理解に満ちた関係が築かれる年となる傾向があります。あなたの優しさと慈愛が、パートナーとの絆をより深くしていく可能性が高いでしょう。お互いを癒し合いながら、温かい愛情を育んでいかれると良いでしょう。")
    }
    return love_fortunes.get(life_path, (3, "2026年は、バランスの取れた恋愛運となる傾向があります。自然な流れに任せながら、自分らしさを大切にされると良いでしょう。焦らず、心を開いて出会いを待たれると良いでしょう。"))

def get_work_fortune(life_path):
    """仕事運を取得"""
    work_fortunes = {
        1: (5, "2026年は、リーダーシップを発揮する年となる傾向があります。新しいプロジェクトで成功を収められる可能性が高いでしょう。あなたの決断力と行動力が、周囲から高く評価されていくことでしょう。自信を持って、リーダーとしての役割を担われると良いでしょう。"),
        2: (4, "2026年は、チームワークが特に重要となる年となりそうです。協力関係を大切にされることで、成果が上がっていく傾向があります。あなたの協調性と感受性が、チーム全体の力を引き出す鍵となることでしょう。"),
        3: (5, "2026年は、創造的な仕事で評価される年となる傾向があります。アイデアが次々と実現していく可能性が高いでしょう。あなたの表現力と創造性が、仕事の成果を大きく左右していくことでしょう。"),
        4: (4, "2026年は、着実な努力が認められる年となりそうです。責任ある立場での活躍が期待できる傾向があります。これまでに積み重ねてきた努力が、実を結んでいくことでしょう。誠実さと責任感が、周囲からの信頼を深めていくことでしょう。"),
        5: (3, "2026年は、変化とチャレンジの年となる傾向があります。新しい分野への挑戦が、あなたの運気を高めていく可能性が高いでしょう。柔軟な心で、これまでとは違う世界に飛び込まれると良いでしょう。"),
        6: (4, "2026年は、サービス精神が評価される年となる傾向があります。人のために働くことで、成果が得られていく可能性が高いでしょう。あなたの優しさと献身的な姿勢が、周囲から感謝され、評価されていくことでしょう。"),
        7: (4, "2026年は、分析力と研究が光る年となりそうです。専門性を高めることで、評価が上がっていく傾向があります。深い洞察力と探究心が、あなたの仕事に新たな価値を生み出していくことでしょう。"),
        8: (5, "2026年は、ビジネスで大きな成功を収める年となる傾向があります。権威や地位が向上していく可能性が高いでしょう。これまでの努力と実力が、目に見える形で実を結んでいくことでしょう。"),
        9: (4, "2026年は、理想を実現する年となる傾向があります。社会貢献につながる仕事で、成果を上げられる可能性が高いでしょう。あなたの理想と情熱が、多くの人々に希望を与える仕事となっていくことでしょう。"),
        11: (5, "2026年は、インスピレーションが仕事を導く年となる傾向があります。直感を信じて行動されることで、素晴らしい成果が得られる可能性が高いでしょう。スピリチュアルな導きに従いながら、創造的な仕事を進められると良いでしょう。"),
        22: (5, "2026年は、大きなプロジェクトの成功が期待できる年となりそうです。理想を現実化する力が、最大限に発揮される傾向があります。これまでに描いてきた大きなビジョンが、着実に形になっていくことでしょう。"),
        33: (5, "2026年は、多くの人々に影響を与える仕事で成功する年となる傾向があります。あなたの慈愛と知恵が、仕事を通じて多くの人々に希望と勇気を与えていくことでしょう。")
    }
    return work_fortunes.get(life_path, (3, "2026年は、バランスの取れた仕事運となる傾向があります。日々の努力が実を結び、着実に前進していかれることでしょう。焦らず、自分らしいペースで仕事を進められると良いでしょう。"))

def get_lucky_color(life_path):
    """ラッキーカラーを取得"""
    colors = {
        1: "ゴールド",
        2: "ピンク",
        3: "イエロー",
        4: "エメラルドグリーン",
        5: "ターコイズブルー",
        6: "ローズピンク",
        7: "パープル",
        8: "シルバー",
        9: "ロイヤルブルー",
        11: "クリスタル",
        22: "プラチナ",
        33: "レインボー"
    }
    return colors.get(life_path, "ピンク")

def get_lucky_item(life_path):
    """ラッキーアイテムを取得"""
    items = {
        1: "ペンダント",
        2: "ハート型のアクセサリー",
        3: "アート作品",
        4: "実用的なバッグ",
        5: "旅行グッズ",
        6: "家族の写真",
        7: "クリスタル",
        8: "高級時計",
        9: "慈善活動の記念品",
        11: "スピリチュアルなアイテム",
        22: "ビジョンボード",
        33: "癒しのアイテム"
    }
    return items.get(life_path, "お守り")

def create_pdf(name, birth_year, birth_month, birth_day):
    """PDFを生成する"""
    # ライフパスナンバーを計算
    life_path = calculate_life_path_number(birth_year, birth_month, birth_day)
    
    # 運勢情報を取得
    personality = get_personality(life_path)
    overall_fortune, fortune_desc = get_fortune(life_path)
    love_stars, love_advice = get_love_fortune(life_path)
    work_stars, work_advice = get_work_fortune(life_path)
    lucky_color = get_lucky_color(life_path)
    lucky_item = get_lucky_item(life_path)
    
    # PDFファイル名
    filename = f"運勢鑑定書_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # PDFを作成
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # 色の定義
    pink = HexColor("#FFB6C1")
    gold = HexColor("#C0A060")  # 落ち着いたゴールドに変更
    dark_pink = HexColor("#C71585")
    light_gold = HexColor("#FFF8DC")
    
    # 背景の装飾（薄いピンク）
    c.setFillColor(light_gold)
    c.rect(0, 0, width, height, fill=1)
    
    # フォント設定
    if register_font():
        font_name = 'IPAexMincho'
    else:
        font_name = 'Helvetica'
    
    # タイトル
    c.setFillColor(dark_pink)
    c.setFont(font_name, 28)
    title = f"2026年 運勢鑑定書"
    title_width = c.stringWidth(title, font_name, 28)
    c.drawString((width - title_width) / 2, height - 50, title)
    
    # 名前
    c.setFillColor(gold)
    c.setFont(font_name, 24)
    name_text = f"{name} 様"
    name_width = c.stringWidth(name_text, font_name, 24)
    c.drawString((width - name_width) / 2, height - 90, name_text)
    
    # 生年月日
    c.setFillColor(HexColor("#666666"))
    c.setFont(font_name, 14)
    birth_text = f"生年月日: {birth_year}年{birth_month}月{birth_day}日"
    birth_width = c.stringWidth(birth_text, font_name, 14)
    c.drawString((width - birth_width) / 2, height - 120, birth_text)
    
    # ライフパスナンバー
    c.setFillColor(dark_pink)
    c.setFont(font_name, 18)
    path_text = f"ライフパスナンバー: {life_path}"
    path_width = c.stringWidth(path_text, font_name, 18)
    c.drawString((width - path_width) / 2, height - 160, path_text)
    
    # 性格
    y_pos = height - 200
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    
    # テキストを折り返して表示
    words = personality.split('。')
    for word in words:
        if word:
            c.drawString(50, y_pos, word + '。')
            y_pos -= 25
    
    # 総合運
    y_pos -= 20
    c.setFillColor(dark_pink)
    c.setFont(font_name, 18)
    c.drawString(50, y_pos, "【総合運】")
    
    y_pos -= 30
    c.setFillColor(gold)
    c.setFont(font_name, 24)
    c.drawString(50, y_pos, overall_fortune)
    
    y_pos -= 30
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    c.drawString(50, y_pos, fortune_desc)
    
    # 恋愛運
    y_pos -= 50
    c.setFillColor(dark_pink)
    c.setFont(font_name, 18)
    c.drawString(50, y_pos, "【恋愛運】")
    
    y_pos -= 30
    c.setFillColor(gold)
    c.setFont(font_name, 16)
    stars = "★" * love_stars + "☆" * (5 - love_stars)
    c.drawString(50, y_pos, stars)
    
    y_pos -= 25
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    c.drawString(50, y_pos, love_advice)
    
    # 仕事運
    y_pos -= 50
    c.setFillColor(dark_pink)
    c.setFont(font_name, 18)
    c.drawString(50, y_pos, "【仕事運】")
    
    y_pos -= 30
    c.setFillColor(gold)
    c.setFont(font_name, 16)
    stars = "★" * work_stars + "☆" * (5 - work_stars)
    c.drawString(50, y_pos, stars)
    
    y_pos -= 25
    c.setFillColor(HexColor("#333333"))
    c.setFont(font_name, 12)
    c.drawString(50, y_pos, work_advice)
    
    # ラッキーカラー
    y_pos -= 50
    c.setFillColor(dark_pink)
    c.setFont(font_name, 18)
    c.drawString(50, y_pos, "【ラッキーカラー】")
    
    y_pos -= 30
    c.setFillColor(gold)
    c.setFont(font_name, 16)
    c.drawString(50, y_pos, lucky_color)
    
    # ラッキーアイテム
    y_pos -= 50
    c.setFillColor(dark_pink)
    c.setFont(font_name, 18)
    c.drawString(50, y_pos, "【ラッキーアイテム】")
    
    y_pos -= 30
    c.setFillColor(gold)
    c.setFont(font_name, 16)
    c.drawString(50, y_pos, lucky_item)
    
    # フッター
    c.setFillColor(HexColor("#999999"))
    c.setFont(font_name, 10)
    footer = "この鑑定書は数秘術に基づいて作成されました。"
    footer_width = c.stringWidth(footer, font_name, 10)
    c.drawString((width - footer_width) / 2, 30, footer)
    
    c.save()
    return filename

# Streamlit UI
st.title("2026年 運勢鑑定書発行アプリ")
st.markdown("---")

# フォントのダウンロード
if not os.path.exists(FONT_PATH):
    st.info("初回起動時、フォントをダウンロードします...")
    download_font()

# 入力フォーム
with st.form("fortune_form"):
    name = st.text_input("お名前", placeholder="山田 花子")
    col1, col2, col3 = st.columns(3)
    with col1:
        birth_year = st.number_input("生まれた年", min_value=1900, max_value=2024, value=2000)
    with col2:
        birth_month = st.number_input("生まれた月", min_value=1, max_value=12, value=1)
    with col3:
        birth_day = st.number_input("生まれた日", min_value=1, max_value=31, value=1)
    
    submitted = st.form_submit_button("鑑定書を発行する", use_container_width=True)

if submitted:
    if not name:
        st.error("お名前を入力してください。")
    else:
        try:
            # 日付の妥当性チェック
            datetime(birth_year, birth_month, birth_day)
            
            with st.spinner("鑑定書を生成しています..."):
                pdf_filename = create_pdf(name, birth_year, birth_month, birth_day)
                
                # PDFファイルを読み込んでダウンロードボタンを表示
                with open(pdf_filename, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    st.success("鑑定書が生成されました！")
                    st.download_button(
                        label="📥 PDFをダウンロード",
                        data=pdf_bytes,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
        except ValueError:
            st.error("正しい日付を入力してください。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# サイドバーに説明
with st.sidebar:
    st.header("📖 使い方")
    st.markdown("""
    1. お名前を入力してください
    2. 生年月日を入力してください
    3. 「鑑定書を発行する」ボタンをクリック
    4. 生成されたPDFをダウンロードしてください
    """)
    
    st.header("✨ このアプリについて")
    st.markdown("""
    このアプリは数秘術（ライフパスナンバー）に基づいて
    2026年の運勢を鑑定します。
    
    生年月日から計算されたライフパスナンバーをもとに、
    あなたの性格、総合運、恋愛運、仕事運などを
    美しいPDFでお届けします。
    """)

