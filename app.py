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
    page_icon="�",
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
        1: "リーダーシップがあり、独立心が強い。新しいことに挑戦する勇気があります。",
        2: "協調性があり、感受性が豊か。人の気持ちを理解する能力に優れています。",
        3: "創造性が高く、表現力豊か。芸術的な才能やコミュニケーション能力があります。",
        4: "実務的で、安定を好む。誠実で責任感が強く、組織を支える力があります。",
        5: "自由を愛し、好奇心旺盛。変化を楽しみ、多様な経験を求めます。",
        6: "愛情深く、奉仕の精神が強い。家族や友人を大切にし、調和を重んじます。",
        7: "分析的で、内省的。スピリチュアルな探求や深い思考を好みます。",
        8: "実力があり、成功への意欲が強い。ビジネスセンスに優れ、権威を築きます。",
        9: "博愛主義で、理想が高い。人々のために貢献することを喜びとします。",
        11: "直感力が鋭く、インスピレーションに富む。スピリチュアルな導き手です。",
        22: "実践的な理想主義者。大きなビジョンを現実化する力があります。",
        33: "慈愛に満ちた教師。多くの人々を導き、癒す力を持っています。"
    }
    return personalities.get(life_path, "独特な個性を持ち、独自の道を歩んでいます。")

def get_fortune(life_path):
    """ライフパスナンバーから運勢を取得"""
    fortunes = {
        1: ("大吉", "新しいスタートの年。積極的に行動することで大きな成果が期待できます。"),
        2: ("中吉", "協力関係が重要。パートナーシップを大切にすることで運気が上昇します。"),
        3: ("大吉", "創造性が開花する年。表現活動やコミュニケーションで成功のチャンスがあります。"),
        4: ("中吉", "着実な成長の年。努力を積み重ねることで安定した成果を得られます。"),
        5: ("小吉", "変化と自由の年。新しい環境や経験が運気を高めます。"),
        6: ("中吉", "愛情と調和の年。人間関係が深まり、心の豊かさが増します。"),
        7: ("小吉", "内面の探求の年。スピリチュアルな成長と深い洞察が得られます。"),
        8: ("大吉", "成功と達成の年。ビジネスやキャリアで大きな飛躍が期待できます。"),
        9: ("中吉", "完成と新たな始まりの年。これまでの努力が実を結びます。"),
        11: ("大吉", "直感とインスピレーションの年。スピリチュアルな導きが強く働きます。"),
        22: ("大吉", "大きなビジョン実現の年。理想を現実化する力が最大限に発揮されます。"),
        33: ("大吉", "慈愛と癒しの年。多くの人々に影響を与える特別な年です。")
    }
    return fortunes.get(life_path, ("中吉", "バランスの取れた一年。日々の努力が運気を高めます。"))

def get_love_fortune(life_path):
    """恋愛運を取得"""
    love_fortunes = {
        1: (4, "積極的なアプローチが成功の鍵。新しい出会いを求めて行動しましょう。"),
        2: (5, "パートナーシップが深まる年。相手の気持ちに寄り添うことで関係が発展します。"),
        3: (5, "コミュニケーションが重要。楽しい会話で関係が深まります。"),
        4: (3, "安定した関係を築く年。誠実さと信頼が恋愛運を高めます。"),
        5: (4, "新しい出会いのチャンス。自由な心で恋愛を楽しみましょう。"),
        6: (5, "愛情が深まる年。家族やパートナーとの絆が強くなります。"),
        7: (3, "内面の成長が恋愛運を高めます。深いつながりを求めましょう。"),
        8: (4, "魅力的なあなたに注目が集まります。自信を持って行動しましょう。"),
        9: (4, "理想のパートナーとの出会いの可能性。広い視野で探してみましょう。"),
        11: (5, "直感に従うことで素晴らしい出会いがあります。"),
        22: (5, "理想的なパートナーシップが実現する可能性が高い年です。"),
        33: (5, "深い愛情と理解に満ちた関係が築かれます。")
    }
    return love_fortunes.get(life_path, (3, "バランスの取れた恋愛運。自然な流れに任せましょう。"))

def get_work_fortune(life_path):
    """仕事運を取得"""
    work_fortunes = {
        1: (5, "リーダーシップを発揮する年。新しいプロジェクトで成功を収められます。"),
        2: (4, "チームワークが重要。協力関係を大切にすることで成果が上がります。"),
        3: (5, "創造的な仕事で評価される年。アイデアが次々と実現します。"),
        4: (4, "着実な努力が認められる年。責任ある立場での活躍が期待できます。"),
        5: (3, "変化とチャレンジの年。新しい分野への挑戦が運気を高めます。"),
        6: (4, "サービス精神が評価される年。人のために働くことで成果が得られます。"),
        7: (4, "分析力と研究が光る年。専門性を高めることで評価が上がります。"),
        8: (5, "ビジネスで大きな成功を収める年。権威や地位が向上します。"),
        9: (4, "理想を実現する年。社会貢献につながる仕事で成果を上げられます。"),
        11: (5, "インスピレーションが仕事を導きます。直感を信じて行動しましょう。"),
        22: (5, "大きなプロジェクトの成功が期待できます。理想を現実化する力が発揮されます。"),
        33: (5, "多くの人々に影響を与える仕事で成功します。")
    }
    return work_fortunes.get(life_path, (3, "バランスの取れた仕事運。日々の努力が実を結びます。"))

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
    gold = HexColor("#FFD700")
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
st.title("� 2026年運勢鑑定書発行アプリ")
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
    
    submitted = st.form_submit_button("� 鑑定書を発行する", use_container_width=True)

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

