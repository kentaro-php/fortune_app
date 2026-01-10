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
    page_title="恋愛運勢鑑定書 | 占いミザリー",
    page_icon="💕",
    layout="centered"
)

# ==========================================
# UI装飾（CSS）
# ==========================================
hide_st_style = """
    <style>
    header {visibility: hidden !important; height: 0px !important;}
    footer {visibility: hidden !important; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    .block-container {padding-top: 1rem !important; padding-bottom: 3rem !important;}
    
    .intro-box {
        background-color: #fff0f5;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        border: 2px solid #ffb6c1;
    }
    
    /* ボタン装飾 */
    div[data-testid="stLinkButton"] > a,
    div[data-testid="stLinkButton"] > a button,
    div[data-testid="stButton"] > button {
        border-radius: 12px !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stLinkButton"] > a,
    div[data-testid="stLinkButton"] > a button {
        background-color: #e10080 !important;
        color: white !important;
        padding: 15px 30px !important;
        font-size: 1.2rem !important;
    }
    div[data-testid="stForm"] div[data-testid="stButton"] > button {
        background-color: #ff69b4 !important;
        color: white !important;
    }
    .download-btn div[data-testid="stButton"] > button {
        background-color: #38b2ac !important;
    }

    /* フッター装飾（修正版） */
    .custom-footer {
        text-align: center;
        margin-top: 50px;
        padding: 30px 15px;
        border-top: 1px solid #e0e0e0;
        background-color: #f9f9f9;
        color: #666;
        font-size: 0.9rem;
    }
    .footer-links {
        margin-bottom: 15px;
        font-weight: bold;
    }
    .footer-links a {
        color: #e10080;
        text-decoration: none;
        margin: 0 10px;
    }
    .footer-links a:hover {
        text-decoration: underline;
    }
    .footer-support {
        background: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #eeeeee;
        display: inline-block;
        width: 100%;
        max-width: 400px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    .support-title {
        font-weight: bold;
        color: #333;
        margin-bottom: 8px;
        display: block;
    }
    .support-item {
        margin-bottom: 5px;
        font-size: 0.85rem;
    }
    .support-item a {
        color: #333;
        text-decoration: underline;
    }

    .mode-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .badge-normal { background-color: #e2e8f0; color: #4a5568; }
    .badge-detailed { background-color: #fefcbf; color: #744210; border: 1px solid #d69e2e; }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

from pdf_generator import create_pdf, calculate_life_path_number, get_fortune_data

def save_data_via_gas(action_type, name, year, month, day, lp):
    gas_url = "https://script.google.com/macros/s/AKfycbx7er_1XN-G1KmGFvmAo8zHKNfA0_nKYPr5m6SL4pexfoz8M7JgovdtQ6VYxopjSj5C/exec"
    data = {"action": action_type, "name": name, "dob": f"{year}/{month}/{day}", "lp": lp}
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(gas_url, data=json_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as res: pass
    except: pass

# ==========================================
# 4. アプリUI本編
# ==========================================
st.markdown("""
    <div style="text-align: center; padding-bottom: 15px; border-bottom: 2px solid #C0A060; margin-bottom: 20px;">
        <div style="font-size: 1.0rem; color: #C0A060; font-weight: bold;">💕 数秘術で紐解く恋の未来 💕</div>
        <div style="font-family: Helvetica, sans-serif; font-weight: bold; font-size: 2.2rem; background: linear-gradient(45deg, #FFB6C1, #C71585); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">恋愛運勢鑑定書</div>
    </div>
""", unsafe_allow_html=True)

query_params = st.query_params

def get_param(key):
    val = query_params.get(key, "")
    if isinstance(val, list):
        return val[0] if val else ""
    return val

is_paid = get_param("paid") == "true" or get_param("checkout") == "success"
is_upsell_paid = get_param("upsell") == "success"

if 'user_name' not in st.session_state: st.session_state.update({'user_name': '', 'birth_year': 2000, 'birth_month': 1, 'birth_day': 1})
if 'pdf_data' not in st.session_state: st.session_state.pdf_data = None
if 'pdf_filename' not in st.session_state: st.session_state.pdf_filename = None

# パターン1: 未払い（トップページ）
if not is_paid:
    st.markdown("""
    <div class="intro-box">
        <div style="font-weight:bold; color:#e10080; margin-bottom:10px;">💕 あなたの恋愛運勢を鑑定します</div>
        <div style="font-size:0.9rem;">
            あなたの恋愛運勢バイオリズムを<br>
            A4サイズの鑑定書（宝地図風PDF）として発行します。
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("##### ❶ まずは無料でお試し")
    with st.form("preview"):
        name_pre = st.text_input("お名前")
        c1, c2, c3 = st.columns(3)
        y_pre = c1.number_input("年", 1900, 2025, 2000)
        m_pre = c2.number_input("月", 1, 12, 1)
        d_pre = c3.number_input("日", 1, 31, 1)
        
        if st.form_submit_button("恋愛運勢をチラ見せ"):
            if name_pre:
                lp = calculate_life_path_number(y_pre, m_pre, d_pre)
                preview_data = get_fortune_data(lp)
                st.info(f"✨ {name_pre}さんのライフパスナンバーは【 {lp} 】です！")
                st.markdown(f"**恋愛運勢のテーマ:** {preview_data['overall'][0]}")
                st.caption(f"{preview_data['overall'][1][:30]}...")
                st.warning("🔒 詳しい続きや月別カレンダーは、鑑定書を発行してご覧ください。")
                st.session_state.update({'user_name': name_pre, 'birth_year': y_pre, 'birth_month': m_pre, 'birth_day': d_pre})
            else:
                st.error("お名前を入力してください")
    
    st.write("##### ❷ 鑑定書を発行")
    with st.form("pay_save"):
        st.caption("鑑定書に記載するお名前を確認して保存してください")
        name_pay = st.text_input("お名前", value=st.session_state.user_name, key="p_name")
        c1, c2, c3 = st.columns(3)
        y_p = c1.number_input("年", 1900, 2025, st.session_state.birth_year, key="p_y")
        m_p = c2.number_input("月", 1, 12, st.session_state.birth_month, key="p_m")
        d_p = c3.number_input("日", 1, 31, st.session_state.birth_day, key="p_d")
        
        if st.form_submit_button("情報を保存して決済へ"):
             st.session_state.update({'user_name': name_pay, 'birth_year': y_p, 'birth_month': m_p, 'birth_day': d_p})
             st.success("保存しました。下のボタンを押してください。")

    st.link_button("👉 500円で恋愛運勢鑑定書を発行する", "https://buy.stripe.com/8x2fZhfsm01Q813847cfT1v", type="primary", use_container_width=True)

# パターン2: 支払い完了（ダウンロード画面）
else:
    st.markdown("""
    <div class="success-area">
        <h3 style="margin:0; color:#2c7a7b;">✅ 決済が完了しました！</h3>
        <p style="margin:5px 0 0 0;">あとワンクリックで恋愛運勢鑑定書を受け取れます。</p>
    </div>
    """, unsafe_allow_html=True)
    
    if is_upsell_paid:
        st.markdown('<div style="text-align:center;"><span class="mode-badge badge-detailed">💎 完全版モード（全3ページ）</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;"><span class="mode-badge badge-normal">📄 通常版モード（全2ページ）</span></div>', unsafe_allow_html=True)

    if not is_upsell_paid:
        with st.expander("✨【追加オプション】さらに詳しく知りたい方へ", expanded=True):
            st.markdown("""
            <div style="text-align: center;">
                <p style="font-weight:bold; color:#e10080;">あなたの「恋愛の裏の才能」や「運命の出会いの日付」を知りたくないですか？</p>
                <p style="font-size:0.9rem;">+1,000円で、シークレットページ（第3ページ）を追加した<br>【完全版】にアップグレードできます。</p>
            </div>
            """, unsafe_allow_html=True)
            # ★本番用Stripeリンク★
            upsell_stripe_link = "https://buy.stripe.com/fZufZheoicOCchj2JNcfT1J" 
            st.link_button("👉 完全版にアップグレード (+1,000円)", upsell_stripe_link, type="primary", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.get('pdf_data'):
        st.info("👇 恋愛運勢鑑定書の準備ができています")
        st.download_button(
            label="📥 恋愛運勢鑑定書(PDF)をダウンロードする",
            data=st.session_state.pdf_data,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
        with st.expander("名前や日付を修正して再発行する"):
             with st.form("fix_form"):
                name = st.text_input("お名前", value=st.session_state.user_name)
                c1, c2, c3 = st.columns(3)
                y = c1.number_input("年", 1900, 2025, st.session_state.birth_year)
                m = c2.number_input("月", 1, 12, st.session_state.birth_month)
                d = c3.number_input("日", 1, 31, st.session_state.birth_day)
                if st.form_submit_button("再発行"):
                    with st.spinner("生成中..."):
                        current_mode = "detailed" if is_upsell_paid else "normal"
                        pdf = create_pdf(name, y, m, d, mode=current_mode)
                        st.session_state.pdf_data = pdf.getvalue()
                        st.session_state.pdf_filename = f"恋愛運勢鑑定書_{name}.pdf"
                        st.rerun()

    else:
        st.warning("👇 下のボタンを押して、恋愛運勢鑑定書を発行してください")
        if is_upsell_paid:
            st.caption("※基本恋愛運勢 + 12ヶ月カレンダー + 【極秘】恋愛の運命の指針 が全て含まれます")
        else:
            st.caption("※基本恋愛運勢 + 12ヶ月カレンダー が含まれます")

        with st.form("final_auto"):
            st.caption("以下の内容で発行します（修正可能）")
            name = st.text_input("お名前", value=st.session_state.user_name)
            c1, c2, c3 = st.columns(3)
            y = c1.number_input("年", 1900, 2025, st.session_state.birth_year)
            m = c2.number_input("月", 1, 12, st.session_state.birth_month)
            d = c3.number_input("日", 1, 31, st.session_state.birth_day)
            submitted = st.form_submit_button("✨ 恋愛運勢鑑定書(PDF)を受け取る", use_container_width=True)

        if submitted:
            if not name:
                st.error("お名前が空欄です。入力してください。")
            else:
                with st.spinner("恋愛運勢鑑定書を作成しています..."):
                    try:
                        current_mode = "detailed" if is_upsell_paid else "normal"
                        pdf = create_pdf(name, y, m, d, mode=current_mode)
                        pdf_bytes = pdf.getvalue()
                        st.session_state.pdf_data = pdf_bytes
                        st.session_state.pdf_filename = f"恋愛運勢鑑定書_{name}.pdf"
                        st.session_state.update({'user_name': name, 'birth_year': y, 'birth_month': m, 'birth_day': d})
                        try:
                            save_data_via_gas(f"発行({current_mode})", name, y, m, d, calculate_life_path_number(y, m, d))
                        except: pass
                        st.rerun()
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")

# ==========================================
# 5. フッター（修正版）
# ==========================================
# 修正ポイント：HTMLインデントを削除して1行ずつ記述、見やすいボックスデザイン
st.markdown("""
<div class="custom-footer">
<div class="footer-links">
<a href="https://mizary.com/tokusyouhou/" target="_blank">特定商取引法に基づく表記</a>
<span style="color:#ccc;">｜</span>
<a href="https://mizary.com/" target="_blank">トップへ戻る</a>
</div>
<div class="footer-support">
<span class="support-title">【サポート窓口】</span>
<div class="support-item">Mail: <a href="mailto:info@dspartners.jp">info@dspartners.jp</a></div>
<div class="support-item">LINE: <a href="https://lin.ee/qRReG8T" target="_blank">公式LINEはこちら</a></div>
</div>
<div style="margin-top:15px;">© 2026 占いミザリー</div>
</div>
""", unsafe_allow_html=True)
