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
# 0. URLパラメータから設定ファイルを決定
# ==========================================
# Streamlitのquery_paramsを最初に取得
query_params = st.query_params

# configパラメータの値を取得（デフォルトは空文字列）
config_param = query_params.get("config", "")

# 設定ファイル名のマッピング（短縮名でも指定可能）
config_map = {
    "love": "config_love.json",
    "february": "config_love_february.json",
    "default": "config.json"
}

# 設定ファイル名を決定
if config_param in config_map:
    # 短縮名が指定された場合
    config_file = config_map[config_param]
elif config_param.endswith(".json"):
    # 直接ファイル名が指定された場合
    config_file = config_param
else:
    # パラメータがない、または不明な値の場合
    config_file = "config.json"

# ==========================================
# 1. 設定ファイル読み込み
# ==========================================
def load_config(config_path="config.json"):
    """設定ファイルを読み込む関数"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 見つからない場合はデフォルトを試す
        if config_path != "config.json":
             try:
                with open("config.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
             except:
                pass
        st.error(f"設定ファイル '{config_path}' が見つかりません。")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"設定ファイルのJSON形式が正しくありません: {e}")
        st.stop()

# 設定を読み込む
CONFIG = load_config(config_file)

# ==========================================
# 2. ページ設定（設定ファイル読み込み後に実行）
# ==========================================
st.set_page_config(
    page_title=CONFIG.get("app_title", "運勢鑑定書"),
    page_icon=CONFIG.get("app_icon", "🔮"),
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
# 3. PDFヘルパー関数（※バックグラウンド生成用に維持）
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

def get_love_diagnosis_result(name, year, month, day, course="basic"):
    """恋愛攻略モード用：ユーザー名と日付をシードにして診断結果を選択"""
    import hashlib
    
    # ユーザー名と日付を組み合わせてシードを作成
    seed_string = f"{name}_{year}_{month}_{day}_{datetime.now().strftime('%Y-%m-%d')}"
    seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)
    
    # 設定ファイルから結果リストを取得
    results = CONFIG.get("results", {})
    course_results = results.get(course, [])
    
    if not course_results:
        return "診断結果のデータが見つかりませんでした。"
    
    # シードに基づいて結果を選択（同じ入力なら同じ結果）
    index = seed_hash % len(course_results)
    return course_results[index]

# ==========================================
# 5. GAS経由でのデータ保存
# ==========================================
def save_data_via_gas(action_type, name, year, month, day, lp):
    """設定ファイルからGAS URLを取得してデータを保存"""
    gas_url = CONFIG.get("gas_url", "")
    
    # URLが設定されていない場合は何もしない
    if not gas_url:
        return

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
# 7. アプリUI
# ==========================================
# タイトルとサブタイトルを設定ファイルから取得
app_subtitle = CONFIG.get("app_subtitle", "")
app_main_title = CONFIG.get("app_main_title", "運勢鑑定書")

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

# query_paramsは既に上で定義済み
is_paid = query_params.get("paid") == "true" or query_params.get("checkout") == "success" or query_params.get("payment_status") == "success"

if 'user_name' not in st.session_state: st.session_state.update({k: v for k, v in zip(['user_name','birth_year','birth_month','birth_day'], ['', 2000, 1, 1])})

if not is_paid:
    # ▼▼▼ 興味を引くコンテンツセクション（設定ファイルから取得）▼▼▼
    app_description = CONFIG.get("app_description", "")
    app_intro_questions = CONFIG.get("app_intro_questions", [])
    app_intro_text = CONFIG.get("app_intro_text", "")
    
    questions_html = ""
    for question in app_intro_questions:
        questions_html += f'<span class="question">{question}</span>\n            '
    
    # HTMLタグが正しく処理されるように、文字列連結を使用
    intro_box_start = f"""
    <div class="intro-box">
        <div class="intro-head">{app_description}</div>
        <div class="intro-text">
            {questions_html}
    """
    
    intro_box_end = """
        </div>
    </div>
    """
    
    # intro-boxの開始部分を表示
    st.markdown(intro_box_start, unsafe_allow_html=True)
    
    # app_intro_textを直接表示（HTMLタグが正しく処理される）
    if app_intro_text:
        st.markdown(f"<br>{app_intro_text}", unsafe_allow_html=True)
    
    # intro-boxの終了部分を表示
    st.markdown(intro_box_end, unsafe_allow_html=True)
    # ▲▲▲ ここまで ▲▲▲

    ui_config = CONFIG.get("ui", {})
    form_labels = ui_config.get("form_labels", {})
    
    st.info(ui_config.get("preview_info_message", "👋 まずは無料プレビューで、あなたの「数字」を知ってください。"))
    
    with st.form("preview"):
        name_label = form_labels.get("name") if form_labels.get("name") else "お名前"
        name_pre = st.text_input(name_label, key="preview_name")
        col1, col2, col3 = st.columns(3)
        with col1:
            y_pre = st.number_input(form_labels.get("year", "年"), 1900, 2025, 2000, key="preview_year")
        with col2:
            m_pre = st.number_input(form_labels.get("month", "月"), 1, 12, 1, key="preview_month")
        with col3:
            d_pre = st.number_input(form_labels.get("day", "日"), 1, 31, 1, key="preview_day")
        
        if st.form_submit_button(ui_config.get("preview_button", "鑑定結果の一部を見る")):
            if name_pre:
                # モード判定
                app_mode = CONFIG.get("mode", "normal")
                
                if app_mode == "love":
                    # 恋愛攻略モード：resultsからランダム選択
                    diagnosis_result = get_love_diagnosis_result(name_pre, y_pre, m_pre, d_pre, "basic")
                    
                    # ▼ GAS経由でデータを保存
                    save_data_via_gas("無料プレビュー", name_pre, y_pre, m_pre, d_pre, "love_mode")
                    
                    # 興味を引く見出しを表示
                    st.markdown("---")
                    fortune_year = CONFIG.get("fortune_year", "")
                    preview_title_template = ui_config.get("preview_success_title_template", "{name} 様の{year}運勢")
                    
                    st.markdown(f"### {preview_title_template.format(name=name_pre, year=fortune_year)}")
                    
                    st.markdown(f"#### {ui_config.get('preview_section_title', '💘 気になる診断結果')}")
                    st.markdown(f"**{diagnosis_result}**")
                    
                    st.markdown("---")
                    st.warning(ui_config.get("preview_warning", "🔒 詳しい戦略アドバイス（Xデー・具体的な作戦・タイミング分析など）をご覧になるには、完全版の購入が必要です。"))
                    
                    # 完全版へのアンカーリンク
                    preview_link_text = ui_config.get("preview_link_text", "↓ 完全版鑑定書を見る ↓")
                    st.markdown(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="#完全版鑑定書" style="color: #e10080; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-block; padding: 10px 20px; background-color: #fff0f5; border-radius: 25px; border: 2px solid #e10080;">
                            {preview_link_text}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 通常モード：数秘術ロジック
                    lp = calculate_life_path_number(y_pre, m_pre, d_pre)
                    preview_data = get_fortune_data(lp)
                    
                    # ▼ GAS経由でデータを保存
                    save_data_via_gas("無料プレビュー", name_pre, y_pre, m_pre, d_pre, lp)
                    
                    # 興味を引く見出しを表示
                    st.markdown("---")
                    fortune_year = CONFIG.get("fortune_year", "")
                    preview_title_template = ui_config.get("preview_success_title_template", "{name} 様の{year}運勢")
                    preview_subtitle_template = ui_config.get("preview_success_subtitle_template", "✨ あなたの{year}はこんな年に！")
                    
                    st.markdown(f"### {preview_title_template.format(name=name_pre, year=fortune_year)}")
                    st.markdown(f"**{CONFIG.get('pdf', {}).get('labels', {}).get('life_path_number', 'ライフパスナンバー:')} {lp}**")
                    
                    st.markdown(f"#### {preview_subtitle_template.format(year=fortune_year)}")
                    st.markdown(f"**{CONFIG.get('pdf', {}).get('sections', {}).get('overall', '【総合運】').replace('【', '').replace('】', '')}: {preview_data['overall'][0]}**")
                    st.markdown(f"{preview_data['overall'][1]}")
                    
                    st.markdown(f"#### {ui_config.get('preview_section_title', '💫 気になる運勢の一部')}")
                    st.markdown(f"**{CONFIG.get('pdf', {}).get('sections', {}).get('love', '【恋愛運】').replace('【', '').replace('】', '')}**: {'★' * preview_data['love'][0] + '☆' * (5 - preview_data['love'][0])}")
                    st.markdown(f"{preview_data['love'][1]}")
                    
                    st.markdown("---")
                    st.warning(ui_config.get("preview_warning", "🔒 詳しい結果（全運勢・月別カレンダー・ラッキーアイテムなど）をご覧になるには、完全版の購入が必要です。"))
                    
                    # 完全版へのアンカーリンク
                    preview_link_text = ui_config.get("preview_link_text", "↓ 完全版鑑定書を見る ↓")
                    st.markdown(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="#完全版鑑定書" style="color: #e10080; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-block; padding: 10px 20px; background-color: #fff0f5; border-radius: 25px; border: 2px solid #e10080;">
                            {preview_link_text}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error(ui_config.get("name_required_error", "お名前を入力してください"))

    st.markdown("---")
    # アンカー用のIDを追加
    st.markdown('<div id="完全版鑑定書"></div>', unsafe_allow_html=True)
    full_version_title = ui_config.get("full_version_title", "💎 完全版鑑定書")
    
    st.markdown(f'<h2 style="white-space: nowrap;">{full_version_title}</h2>', unsafe_allow_html=True)
    with st.form("pay"):
        name = st.text_input(form_labels.get("name", "お名前"), key="p_name")
        col1, col2, col3 = st.columns(3)
        with col1:
            y = st.number_input(form_labels.get("year", "年"), 1900, 2025, 2000, key="p_y")
        with col2:
            m = st.number_input(form_labels.get("month", "月"), 1, 12, 1, key="p_m")
        with col3:
            d = st.number_input(form_labels.get("day", "日"), 1, 31, 1, key="p_d")
        if st.form_submit_button(ui_config.get("save_button", "情報を保存して決済へ")):
            st.session_state.update({'user_name': name, 'birth_year': y, 'birth_month': m, 'birth_day': d})
            st.success(ui_config.get("save_success", "✅ 保存しました。下のボタンから決済してください。"))
            
    # ▼▼▼ Stripeリンク（設定ファイルから取得）▼▼▼
    stripe_checkout_url = CONFIG.get("stripe_checkout_url", "")
    price_display = CONFIG.get("price_display", "500円")
    if stripe_checkout_url:
        st.link_button(f"👉 {price_display}で発行する", stripe_checkout_url, type="primary", use_container_width=True)

else:
    # ==========================================
    # ▼ 決済成功時の表示処理（スマホ最適化版）
    # ==========================================
    ui_config = CONFIG.get("ui", {})
    form_labels = ui_config.get("form_labels", {})
    
    st.success(ui_config.get("purchase_success", "✅ ご購入ありがとうございます！"))
    
    # フォームを表示して鑑定を実行
    with st.form("final"):
        st.write(f"### {ui_config.get('pdf_form_title', '📄 発行フォーム')}")
        name = st.text_input(form_labels.get("name", "お名前"), value=st.session_state.user_name, key="final_name")
        col1, col2, col3 = st.columns(3)
        with col1:
            y = st.number_input(form_labels.get("year", "年"), 1900, 2025, st.session_state.birth_year, key="final_year")
        with col2:
            m = st.number_input(form_labels.get("month", "月"), 1, 12, st.session_state.birth_month, key="final_month")
        with col3:
            d = st.number_input(form_labels.get("day", "日"), 1, 31, st.session_state.birth_day, key="final_day")
        submitted = st.form_submit_button(ui_config.get("pdf_create_button", "✨ 鑑定結果を表示する"), use_container_width=True)

    if submitted and name:
        with st.spinner("鑑定中..."):
            try:
                # モード判定
                app_mode = CONFIG.get("mode", "normal")
                
                # ログ保存：購入完了
                # ▼ GAS経由でデータを保存
                try:
                    lp = calculate_life_path_number(y, m, d) if app_mode != "love" else "love_mode"
                    save_data_via_gas("購入・発行", name, y, m, d, lp)
                except:
                    pass  # 保存エラーは無視
                
                # 鑑定結果のテキストを生成
                if app_mode == "love":
                    # 恋愛攻略モード
                    diagnosis_result = get_love_diagnosis_result(name, y, m, d, "basic")
                    fortune_year = CONFIG.get("fortune_year", "2月")
                    
                    # パーソナライズされたヘッダーを追加
                    full_response = f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    full_response += f"💘 {name} 様 専用鑑定書 💘\n"
                    full_response += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    full_response += f"📅 生年月日: {y}年{m}月{d}日\n"
                    full_response += f"📆 鑑定対象期間: {fortune_year}\n"
                    full_response += f"🔮 鑑定日: {datetime.now().strftime('%Y年%m月%d日')}\n\n"
                    full_response += diagnosis_result
                else:
                    # 通常モード：数秘術ロジック
                    lp = calculate_life_path_number(y, m, d)
                    data = get_fortune_data(lp)
                    monthly = get_monthly_fortunes(lp)
                    
                    # テキストを整形
                    pdf_labels = CONFIG.get("pdf", {}).get("labels", {})
                    pdf_sections = CONFIG.get("pdf", {}).get("sections", {})
                    fortune_year = CONFIG.get("fortune_year", "")
                    
                    full_response = f"{name} 様の{fortune_year}運勢\n\n"
                    full_response += f"{pdf_labels.get('life_path_number', 'ライフパスナンバー:')} {lp}\n"
                    full_response += f"{data.get('lp_description', '')}\n\n"
                    
                    full_response += f"{pdf_sections.get('overall', '【総合運】')}\n"
                    full_response += f"{data['overall'][0]}\n"
                    full_response += f"{data['overall'][1]}\n\n"
                    
                    full_response += f"{pdf_sections.get('love', '【恋愛運】')}\n"
                    full_response += f"{'★' * data['love'][0] + '☆' * (5 - data['love'][0])}\n"
                    full_response += f"{data['love'][1]}\n\n"
                    
                    full_response += f"{pdf_sections.get('work', '【仕事運】')}\n"
                    full_response += f"{'★' * data['work'][0] + '☆' * (5 - data['work'][0])}\n"
                    full_response += f"{data['work'][1]}\n\n"
                    
                    full_response += f"{pdf_sections.get('money', '【金運】')}\n"
                    full_response += f"{'★' * data['money'][0] + '☆' * (5 - data['money'][0])}\n"
                    full_response += f"{data['money'][1]}\n\n"
                    
                    full_response += f"{pdf_sections.get('health', '【健康運】')}\n"
                    full_response += f"{'★' * data['health'][0] + '☆' * (5 - data['health'][0])}\n"
                    full_response += f"{data['health'][1]}\n\n"
                    
                    if data.get('color'):
                        full_response += f"ラッキーカラー: {data['color']}\n"
                    if data.get('item'):
                        full_response += f"ラッキーアイテム: {data['item']}\n\n"
                    
                    if monthly:
                        monthly_title = CONFIG.get("pdf_monthly_title", "月別運勢カレンダー")
                        full_response += f"{monthly_title}\n"
                        for txt in monthly:
                            if txt and txt.strip():
                                full_response += f"{txt}\n"
                
                # セッションステートに保存
                st.session_state.fortune_result = full_response
                st.rerun()  # ページを再読み込みして結果を表示
            except Exception as e:
                st.error(f"鑑定結果生成エラー: {e}")
                import traceback
                st.error(f"詳細: {traceback.format_exc()}")
    
    # 鑑定結果を表示（スマホ最適化カード）
    if st.session_state.get('fortune_result'):
        full_response = st.session_state.fortune_result
        
        # 1. お祝いの演出
        st.balloons()
        
        # 2. デザイン定義（CSS）- スマホ最適化
        st.markdown("""
        <style>
            /* 全体のカード枠 */
            .fortune-card {
                background-color: #fff0f5;
                border: 2px solid #ff69b4;
                border-radius: 15px;
                padding: 24px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "メイリオ", sans-serif;
            }
            /* タイトル部分 */
            .fortune-header {
                color: #c71585;
                font-size: 26px;
                font-weight: bold;
                text-align: center;
                border-bottom: 2px dashed #ff69b4;
                padding-bottom: 12px;
                margin-bottom: 18px;
            }
            /* 本文部分 */
            .fortune-content {
                color: #333333;
                font-size: 18px;
                line-height: 2.0;
                white-space: pre-wrap;
                word-break: break-word;
            }
            /* フッター */
            .fortune-footer {
                margin-top: 20px;
                text-align: center;
                font-size: 14px;
                color: #888;
            }
            /* LINE登録カード */
            .line-card {
                background: linear-gradient(135deg, #06C755 0%, #00B04F 100%);
                border: 2px solid #06C755;
                border-radius: 15px;
                padding: 24px;
                box-shadow: 0 4px 12px rgba(6, 199, 85, 0.3);
                margin: 30px 0 20px 0;
                text-align: center;
                color: white;
            }
            .line-card-title {
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 12px;
                color: white;
            }
            .line-card-text {
                font-size: 16px;
                line-height: 1.8;
                margin-bottom: 16px;
                color: white;
            }
            .line-card-price {
                font-size: 20px;
                font-weight: bold;
                margin: 12px 0;
                color: #FFD700;
            }
            .line-button {
                display: inline-block;
                background-color: white;
                color: #06C755;
                padding: 14px 32px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                font-size: 18px;
                margin-top: 12px;
                transition: transform 0.2s;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .line-button:hover {
                transform: scale(1.05);
            }
            /* スマホ対応 */
            @media (max-width: 600px) {
                .fortune-card {
                    padding: 18px;
                    border-radius: 12px;
                }
                .fortune-header {
                    font-size: 24px;
                }
                .fortune-content {
                    font-size: 17px;
                    line-height: 1.9;
                }
                .line-card {
                    padding: 20px;
                }
                .line-card-title {
                    font-size: 20px;
                }
                .line-card-text {
                    font-size: 15px;
                }
                .line-card-price {
                    font-size: 18px;
                }
                .line-button {
                    padding: 12px 24px;
                    font-size: 16px;
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # 3. 画面描画
        st.markdown(f"""
        <div class="fortune-card">
            <div class="fortune-header">🔮 鑑定結果 🔮</div>
            <div class="fortune-content">
                {full_response} 
            </div>
            <div class="fortune-footer">
                screen shot this page to save<br>
                Presented by {CONFIG.get('app_title', '運勢鑑定書')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("鑑定完了です！この画面をスクリーンショットして保存してください。")
        
        # テキスト保存ボタン（バックアップ用）
        st.download_button(
            label="📝 バックアップ用テキスト保存",
            data=full_response,
            file_name="uranai_result.txt",
            mime="text/plain"
        )
        
        # LINE登録への導線
        st.markdown("""
        <div class="line-card">
            <div class="line-card-title">💬 もっと詳しく知りたい方はLINE登録</div>
            <div class="line-card-text">
                より詳しい鑑定や、個別の相談をご希望の方は<br>
                公式LINEからお気軽にお問い合わせください
            </div>
            <div class="line-card-price">✨ LINE予約で20分2,980円から ✨</div>
            <a href="https://lin.ee/2aPNobM" target="_blank" rel="noopener noreferrer" class="line-button">
                📱 公式LINEを友だち追加
            </a>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 8. トップへ戻るリンク + フッター（著作権表示）
# ==========================================
# フッター情報を設定ファイルから取得
fortune_site_url = CONFIG.get("fortune_site_url", "")
contact_email_url = CONFIG.get("contact_email_url", "")
contact_email = CONFIG.get("contact_email", contact_email_url.replace('mailto:', '').replace('https://', '').replace('http://', ''))
contact_line_url = CONFIG.get("contact_line_url", "")
legal_url = CONFIG.get("legal_url", "")
copyright_text = CONFIG.get("copyright_text", "")

st.markdown(f"""
    <div class="custom-footer">
        <div style="margin-bottom: 20px;">
            <a href="{legal_url}" target="_blank" rel="noopener noreferrer">特定商取引法に基づく表記</a>
            <span style="margin: 0 8px; color: #ccc;">|</span>
            <a href="{fortune_site_url}" target="_blank" rel="noopener noreferrer">トップへ戻る</a>
        </div>
        <div style="margin-bottom: 15px;">
            <strong>【サポート窓口】</strong>
        </div>
        <div style="margin-bottom: 10px;">
            <span>メール: </span>
            <a href="mailto:{contact_email}" style="color: #0066cc;">{contact_email}</a>
        </div>
        <div style="margin-bottom: 20px;">
            <span>LINE: </span>
            <a href="{contact_line_url}" target="_blank" rel="noopener noreferrer" style="color: #0066cc;">公式LINEはこちら</a>
        </div>
        <div class="copyright">{copyright_text}</div>
    </div>
""", unsafe_allow_html=True)