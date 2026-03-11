import streamlit as st
from google import genai
from config import API_KEY
import io
from datetime import datetime

st.set_page_config(
    page_title="Kariyerini Planla | ResumeIQ",
    page_icon="⚡",
    layout="centered"
)

# --- Oturum değişkenleri ---
defaults = {
    "cv_metni":         "",
    "cv_adi":           "",
    "cv2_metni":        "",
    "cv2_adi":          "",
    "mesajlar":         [],
    "sohbet_gecmisi":   [],
    "analiz_sayisi":    0,
    "aktif_gecmis_idx": None,
    "dil":              "🇹🇷 Türkçe",
    "tema_renk":        "#4f8ef7",
    "soru_counter":     0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- Tema renk hesaplamaları ---
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

tr = st.session_state.tema_renk
r, g, b = hex_to_rgb(tr)
AL = f"rgba({r},{g},{b},0.15)"   # low opacity
AM = f"rgba({r},{g},{b},0.35)"   # mid opacity
AH = f"rgba({r},{g},{b},0.55)"   # high opacity

# --- CSS ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {{
    --accent:      {tr};
    --accent2:     #38c4e8;
    --bg:          #0d1b3e;
    --card:        #162040;
    --card2:       #1c2a52;
    --border:      #2a3f6e;
    --muted:       #b0c4e8;
}}

html, body, [data-theme="light"], [data-theme="dark"], [class*="css"] {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: #fff !important;
    background-color: #0d1b3e !important;
}}

.stApp, .main, .block-container,
[data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background:
        radial-gradient(ellipse at 15% 0%, {AL} 0%, transparent 50%),
        radial-gradient(ellipse at 85% 100%, rgba(56,196,232,0.08) 0%, transparent 50%),
        #0d1b3e !important;
    min-height: 100vh;
}}

p, h1, h2, h3, h4, h5, h6, span, div, label, li, a,
.stMarkdown p, [data-testid="stMarkdownContainer"] p {{ color: #fff !important; }}

@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes pulseGlow {{
    0%, 100% {{ box-shadow: 0 0 14px {AM}; }}
    50%       {{ box-shadow: 0 0 28px {AH}; }}
}}

.hero-wrap {{
    text-align: center;
    padding: 2.5rem 0 1.2rem;
    animation: fadeUp 0.8s ease-out;
}}
.brand-badge {{
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: {AL}; border: 1px solid {AM};
    border-radius: 999px; padding: 0.3rem 1rem;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
    color: {tr}; text-transform: uppercase; margin-bottom: 1rem;
}}
.main-title {{
    font-size: 3.6rem; font-weight: 800;
    letter-spacing: -2px; line-height: 1; margin-bottom: 0.5rem;
}}
.main-title span {{
    background: linear-gradient(90deg, {tr}, #38c4e8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.sub-title {{ color: #b0c4e8; font-size: 1rem; }}

.stats-row {{
    display: flex; justify-content: center;
    gap: 1rem; padding: 1rem 0; flex-wrap: wrap;
    animation: fadeUp 1s ease-out;
}}
.stat-card {{
    background: #162040; border: 1px solid #2a3f6e;
    border-radius: 14px; padding: 0.8rem 1.4rem;
    text-align: center; min-width: 110px;
    transition: transform 0.25s, border-color 0.25s;
}}
.stat-card:hover {{ transform: translateY(-4px); border-color: {tr}; }}
.stat-num   {{ font-size: 1.5rem; font-weight: 800; color: {tr}; }}
.stat-label {{ font-size: 0.65rem; color: #b0c4e8; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.25rem; }}

.feature-row {{
    display: flex; justify-content: center;
    gap: 0.5rem; flex-wrap: wrap; margin: 0.5rem 0 1.5rem;
}}
.chip {{
    background: {AL}; border: 1px solid {AM};
    border-radius: 999px; padding: 0.28rem 0.8rem;
    font-size: 0.72rem; color: {tr}; font-weight: 500;
}}

section[data-testid="stFileUploadDropzone"],
section[data-testid="stFileUploadDropzone"] > div,
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] section {{
    background: #162040 !important;
    border: 2px dashed {AM} !important;
    border-radius: 18px !important;
    transition: all 0.25s !important;
}}
section[data-testid="stFileUploadDropzone"]:hover,
[data-testid="stFileUploader"]:hover section {{
    border-color: {tr} !important; background: #1c2a52 !important;
}}
section[data-testid="stFileUploadDropzone"] *,
[data-testid="stFileUploader"] * {{ color: #b0c4e8 !important; background-color: transparent !important; }}
[data-testid="stFileUploader"] button,
section[data-testid="stFileUploadDropzone"] button {{
    background: linear-gradient(135deg, #1e40af, {tr}) !important;
    color: #fff !important; border: none !important; border-radius: 8px !important;
}}

.cv-loaded-box {{
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(56,196,232,0.06));
    border: 1px solid rgba(16,185,129,0.3); border-radius: 14px;
    padding: 0.9rem 1.3rem; display: flex; align-items: center;
    gap: 0.8rem; margin: 0.8rem 0; animation: fadeUp 0.4s ease-out;
}}
.cv-loaded-icon {{ font-size: 1.4rem; }}
.cv-loaded-text {{ font-size: 0.88rem; color: #6ee7b7; font-weight: 600; }}
.cv-loaded-sub  {{ font-size: 0.73rem; color: #b0c4e8; }}

.stButton > button {{
    border-radius: 12px;
    background: linear-gradient(135deg, #1e40af, {tr}) !important;
    color: #fff !important; font-weight: 700 !important;
    border: none !important; height: 3.1rem; width: 100%;
    box-shadow: 0 4px 14px {AM} !important;
    transition: all 0.3s cubic-bezier(0.175,0.885,0.32,1.275) !important;
    font-size: 0.88rem !important; letter-spacing: 0.02em !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 8px 24px {AH} !important;
    background: linear-gradient(135deg, {tr}, #38c4e8) !important;
}}

div[data-baseweb="select"] > div {{
    background: #162040 !important; border-color: #2a3f6e !important;
    color: #fff !important; border-radius: 12px !important;
}}
div[data-baseweb="select"] svg {{ color: {tr} !important; }}
[data-baseweb="menu"], [data-baseweb="popover"] {{
    background: #162040 !important; border: 1px solid #2a3f6e !important;
}}
[data-baseweb="option"] {{ background: #162040 !important; color: #fff !important; }}
[data-baseweb="option"]:hover {{ background: #1c2a52 !important; }}

[data-testid="stMetric"] {{ background: transparent !important; }}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ color: #fff !important; }}

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {{
    background: #162040 !important;
    border-right: 1px solid #2a3f6e !important;
}}
section[data-testid="stSidebar"] * {{ color: #fff !important; }}

div[data-testid="stChatMessage"] {{
    border-radius: 14px; padding: 1.1rem 1.3rem; margin-bottom: 0.9rem;
    border: 1px solid #2a3f6e !important;
    background: #162040 !important;
    animation: fadeUp 0.35s ease-out;
}}
div[data-testid="stChatMessage"] * {{ color: #fff !important; }}

div[data-testid="stTextInput"] input {{
    background: #162040 !important; border: 1px solid #2a3f6e !important;
    border-radius: 12px !important; color: #fff !important;
    font-size: 0.94rem !important; padding: 0.7rem 1rem !important; height: 3.1rem !important;
}}
div[data-testid="stTextInput"] input:focus {{
    border-color: {tr} !important; box-shadow: 0 0 0 2px {AL} !important;
}}
div[data-testid="stTextInput"] input::placeholder {{ color: #5a7ab5 !important; }}

hr {{ border-color: #2a3f6e !important; opacity: 0.4; }}

.section-label {{
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #b0c4e8;
    padding: 0.5rem 0; border-bottom: 1px solid #2a3f6e; margin-bottom: 0.5rem;
}}

.dev-card {{
    background: linear-gradient(135deg, {AL}, rgba(56,196,232,0.07));
    border: 1px solid {AM}; border-radius: 13px;
    padding: 1rem; margin: 0.4rem 0 0.7rem; text-align: center;
    animation: pulseGlow 3s infinite;
}}
.dev-name {{ font-size: 1rem; font-weight: 800; }}
.dev-role {{ font-size: 0.7rem; color: #b0c4e8 !important; font-family: 'DM Mono', monospace; margin-top: 0.15rem; }}

.compare-box {{
    background: linear-gradient(135deg, {AL}, rgba(56,196,232,0.04));
    border: 1px solid {AM}; border-radius: 14px;
    padding: 1.2rem 1.4rem; margin: 0.7rem 0;
}}

::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: #0d1b3e; }}
::-webkit-scrollbar-thumb {{ background: #2a3f6e; border-radius: 2px; }}
::-webkit-scrollbar-thumb:hover {{ background: {tr}; }}

@media (max-width: 768px) {{
    .block-container {{ padding: 0.5rem 0.8rem !important; max-width: 100% !important; }}
    .main-title {{ font-size: 2.3rem !important; letter-spacing: -1px !important; }}
    .sub-title  {{ font-size: 0.88rem !important; }}
    .brand-badge {{ font-size: 0.62rem !important; padding: 0.22rem 0.65rem !important; }}
    .stat-card  {{ min-width: 78px !important; padding: 0.55rem 0.75rem !important; }}
    .stat-num   {{ font-size: 1.25rem !important; }}
    .chip       {{ font-size: 0.66rem !important; padding: 0.22rem 0.6rem !important; }}
    .stButton > button {{ height: 2.7rem !important; font-size: 0.8rem !important; }}
    [data-testid="stTabs"] button {{ font-size: 0.73rem !important; padding: 0.35rem 0.45rem !important; }}
    div[data-testid="stChatMessage"] {{ padding: 0.85rem 0.95rem !important; font-size: 0.88rem !important; }}
    [data-testid="stHorizontalBlock"] {{ flex-direction: column !important; gap: 0.45rem !important; }}
    [data-testid="stHorizontalBlock"] > div {{ width: 100% !important; flex: 1 1 100% !important; }}
    [data-testid="stHorizontalBlock"]:has(input) {{ flex-direction: row !important; }}
    [data-testid="stHorizontalBlock"]:has(input) > div:first-child {{ flex: 1 1 75% !important; min-width: 0 !important; }}
    [data-testid="stHorizontalBlock"]:has(input) > div:last-child  {{ flex: 0 0 auto !important; min-width: 68px !important; }}
    footer, [data-testid="stDecoration"] {{ display: none !important; }}
}}

@media (max-width: 390px) {{
    .main-title {{ font-size: 1.9rem !important; }}
    .stat-card  {{ min-width: 68px !important; padding: 0.45rem !important; }}
}}
</style>
""", unsafe_allow_html=True)

# --- Gemini istemcisi ---
istemci  = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash"


# --- Yardımcı fonksiyonlar ---

def cv_metin_oku(dosya):
    """PDF, DOCX veya TXT dosyasını okuyup düz metin döndürür."""
    tip     = dosya.type
    icerik  = dosya.read()
    try:
        if tip == "text/plain":
            return icerik.decode("utf-8", errors="ignore")
        if tip == "application/pdf":
            import pdfplumber
            with pdfplumber.open(io.BytesIO(icerik)) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        if "word" in tip or "docx" in tip:
            import docx
            return "\n".join(p.text for p in docx.Document(io.BytesIO(icerik)).paragraphs)
    except Exception as e:
        st.error(f"Dosya okunamadı: {e}")
    return None


def sorgula(istem):
    """Gemini'ye istem gönderir, metin yanıt döndürür."""
    try:
        from google.genai import types
        yanit = istemci.models.generate_content(
            model=MODEL_ID,
            contents=[istem],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        return yanit.text if yanit and yanit.text else "Yanıt alınamadı, lütfen tekrar deneyin."
    except Exception as e:
        return f"Bağlantı hatası: {e}"


def dil_talimat(dil):
    """Modele hangi dilde yanıt vereceğini söyler."""
    return "Yanıtlarını Türkçe ver." if "Türkçe" in dil else "Please respond in English."


def gecmise_kaydet(mesajlar, baslik):
    """Mevcut sohbeti geçmiş listesine ekler."""
    st.session_state.sohbet_gecmisi.append({
        "baslik":   baslik,
        "zaman":    datetime.now().strftime("%H:%M"),
        "mesajlar": mesajlar.copy(),
    })


# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div class="dev-card">
        <div style="font-size:2rem;margin-bottom:0.3rem;">👨‍💻</div>
        <div class="dev-name">Yusuf Aksu</div>
        <div class="dev-role">Software Engineering Student</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.62rem;color:#5a7ab5;text-align:center;"
        "margin:-4px 0 10px;font-family:DM Mono,monospace;'>"
        "ResumeIQ v4.0 — Powered by Gemini 2.5</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("<div class='section-label'>🌐 Dil / Language</div>", unsafe_allow_html=True)
    dil_sec = st.selectbox(
        "Dil", ["🇹🇷 Türkçe", "🇬🇧 English"],
        index=0 if st.session_state.dil == "🇹🇷 Türkçe" else 1,
        label_visibility="collapsed",
    )
    if dil_sec != st.session_state.dil:
        st.session_state.dil = dil_sec
        st.rerun()

    st.divider()

    st.markdown("<div class='section-label'>🎨 Tema Rengi</div>", unsafe_allow_html=True)
    yeni_renk = st.color_picker("Renk", value=st.session_state.tema_renk, label_visibility="collapsed")
    if yeni_renk != st.session_state.tema_renk:
        st.session_state.tema_renk = yeni_renk
        st.rerun()

    st.divider()

    st.markdown("<div class='section-label'>📊 Oturum</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Analiz", st.session_state.analiz_sayisi)
    c2.metric("Mesaj",  len(st.session_state.mesajlar))

    st.divider()

    st.markdown("<div class='section-label'>💬 Geçmiş</div>", unsafe_allow_html=True)
    if st.session_state.sohbet_gecmisi:
        for i, g in enumerate(reversed(st.session_state.sohbet_gecmisi[-6:])):
            idx = len(st.session_state.sohbet_gecmisi) - 1 - i
            if st.button(f"📄 {g['baslik']}  •  {g['zaman']}", key=f"g_{idx}", use_container_width=True):
                st.session_state.aktif_gecmis_idx = idx
                st.rerun()
    else:
        st.markdown(
            "<div style='font-size:0.76rem;color:#5a7ab5;padding:0.3rem 0;'>Kayıt yok.</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        if st.session_state.mesajlar:
            gecmise_kaydet(
                st.session_state.mesajlar,
                f"{len(st.session_state.mesajlar)} mesajlık oturum",
            )
        for k in ("mesajlar", "cv_metni", "cv_adi", "cv2_metni", "cv2_adi"):
            st.session_state[k] = [] if k == "mesajlar" else ""
        st.session_state.aktif_gecmis_idx = None
        st.rerun()


# --- Geçmiş oturum görüntüsü ---
if st.session_state.aktif_gecmis_idx is not None:
    idx = st.session_state.aktif_gecmis_idx
    g   = st.session_state.sohbet_gecmisi[idx]
    st.markdown(
        f"<div style='background:{AL};border:1px solid {AM};border-radius:12px;"
        f"padding:0.9rem 1.3rem;margin-bottom:1rem;font-size:0.83rem;font-weight:700;color:{tr};'>"
        f"📂 {g['baslik']} — {g['zaman']}</div>",
        unsafe_allow_html=True,
    )
    for m in g.get("mesajlar", []):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    if st.button("← Aktif Sohbete Dön"):
        st.session_state.aktif_gecmis_idx = None
        st.rerun()
    st.stop()


# --- Ana sayfa ---
is_en = "English" in st.session_state.dil

st.markdown(f"""
<div class="hero-wrap">
    <div class="brand-badge">⚡ AI-POWERED CAREER INTELLIGENCE</div>
    <h1 class="main-title">{"Career" if is_en else "Kariyerini"}<span> {"Planner" if is_en else "Planla"}</span></h1>
    <p class="sub-title">{"Analyze your CV instantly — get professional career insights." if is_en else "CV'nizi saniyeler içinde analiz edin — profesyonel kariyer içgörüleri elde edin."}</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="feature-row">
    <span class="chip">🎯 ATS {"Score"  if is_en else "Skoru"}</span>
    <span class="chip">📋 {"Cover Letter" if is_en else "Niyet Mektubu"}</span>
    <span class="chip">🔍 {"Deep Analysis" if is_en else "Derin Analiz"}</span>
    <span class="chip">💡 {"Project Ideas" if is_en else "Proje Önerileri"}</span>
    <span class="chip">🗺️ {"Career Path"  if is_en else "Kariyer Yolu"}</span>
    <span class="chip">⚖️ {"CV Compare"   if is_en else "CV Karşılaştır"}</span>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="stats-row">
    <div class="stat-card"><div class="stat-num">2.5</div><div class="stat-label">Gemini Flash</div></div>
    <div class="stat-card"><div class="stat-num">{st.session_state.analiz_sayisi}</div><div class="stat-label">{"Total Analysis" if is_en else "Toplam Analiz"}</div></div>
    <div class="stat-card"><div class="stat-num">6</div><div class="stat-label">{"Fields" if is_en else "Alan"}</div></div>
    <div class="stat-card"><div class="stat-num">∞</div><div class="stat-label">{"Questions" if is_en else "Soru"}</div></div>
</div>
""", unsafe_allow_html=True)

st.divider()

tab_labels = (
    ["📄 CV Analysis", "⚖️ CV Compare", "☁️ Word Cloud"]
    if is_en else
    ["📄 CV Analizi",  "⚖️ CV Karşılaştırma", "☁️ Kelime Bulutu"]
)
sekme1, sekme2, sekme3 = st.tabs(tab_labels)


# ── Sekme 1: CV Analizi ──────────────────────────────────────────
with sekme1:
    yuklenen = st.file_uploader(
        "CV", type=["pdf", "docx", "txt"],
        label_visibility="collapsed", key="cv1_uploader",
    )

    if yuklenen and yuklenen.name != st.session_state.cv_adi:
        metin = cv_metin_oku(yuklenen)
        if metin:
            st.session_state.cv_metni = metin
            st.session_state.cv_adi   = yuklenen.name
            st.toast("CV yüklendi!" if not is_en else "CV uploaded!", icon="✅")

    if st.session_state.cv_metni:
        kelime = len(st.session_state.cv_metni.split())
        st.markdown(f"""
        <div class="cv-loaded-box">
            <div class="cv-loaded-icon">📄</div>
            <div>
                <div class="cv-loaded-text">✅ {st.session_state.cv_adi}</div>
                <div class="cv-loaded-sub">~{kelime} {"words" if is_en else "kelime"} · {"Ready" if is_en else "Hazır"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        alan = st.selectbox(
            "🎯 Target Field" if is_en else "🎯 Hedef Alan",
            ["⚡ AI / ML", "🖥️ Backend Development", "🎨 Frontend Development",
             "📊 Data Science", "📱 Mobile Development", "🔧 General Software"],
        )

        c1, c2, c3 = st.columns(3)

        if c1.button("🔍 " + ("Deep Analysis" if is_en else "Derin Analiz")):
            p = (
                f"{dil_talimat(st.session_state.dil)}\n"
                f"Deneyimli bir kariyer koçu olarak CV'yi {alan} alanına göre analiz et:\n"
                f"1. 💪 Güçlü Yanlar\n2. ⚠️ Eksikler\n3. 🛠️ Teknik Öneriler\n"
                f"4. 💡 Proje Önerileri (3 adet)\n5. 📈 ATS Skoru (1-10)\n6. 🎯 Sonraki Adımlar\n\n"
                f"CV:\n{st.session_state.cv_metni}"
            )
            with st.spinner("Analiz yapılıyor..." if not is_en else "Analyzing..."):
                sonuc = sorgula(p)
            yeni = {"role": "assistant", "content": f"### 🔍 Derin Analiz — {alan}\n\n{sonuc}"}
            st.session_state.mesajlar.append(yeni)
            st.session_state.analiz_sayisi += 1
            gecmise_kaydet([yeni], f"Derin Analiz · {alan.split()[-1]}")
            st.rerun()

        if c2.button("📝 " + ("Cover Letter" if is_en else "Niyet Mektubu")):
            p = (
                f"{dil_talimat(st.session_state.dil)}\n"
                f"{alan} pozisyonuna yönelik etkileyici, kurumsal bir niyet mektubu yaz.\n\n"
                f"CV:\n{st.session_state.cv_metni}"
            )
            with st.spinner("Mektup oluşturuluyor..."):
                sonuc = sorgula(p)
            yeni = {"role": "assistant", "content": f"### 📝 Niyet Mektubu — {alan}\n\n{sonuc}"}
            st.session_state.mesajlar.append(yeni)
            st.session_state.analiz_sayisi += 1
            gecmise_kaydet([yeni], f"Niyet Mektubu · {alan.split()[-1]}")
            st.rerun()

        if c3.button("🗺️ " + ("Career Path" if is_en else "Kariyer Yolu")):
            p = (
                f"{dil_talimat(st.session_state.dil)}\n"
                f"{alan} alanında 12 aylık, somut kariyer yol haritası oluştur. "
                f"Her ay için beceri, proje ve hedef belirt.\n\nCV:\n{st.session_state.cv_metni}"
            )
            with st.spinner("Yol haritası hazırlanıyor..."):
                sonuc = sorgula(p)
            yeni = {"role": "assistant", "content": f"### 🗺️ 12 Aylık Kariyer Yol Haritası — {alan}\n\n{sonuc}"}
            st.session_state.mesajlar.append(yeni)
            st.session_state.analiz_sayisi += 1
            gecmise_kaydet([yeni], f"Kariyer Yolu · {alan.split()[-1]}")
            st.rerun()

        if st.session_state.mesajlar:
            st.divider()
            st.markdown("<div class='section-label'>💬 Sohbet</div>", unsafe_allow_html=True)

        for m in st.session_state.mesajlar:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)
        gi, gb = st.columns([5, 1])
        soru = gi.text_input(
            "soru",
            placeholder="✨ " + ("Ask anything..." if is_en else "Hayalindeki kariyere giden yolu birlikte çizelim..."),
            label_visibility="collapsed",
            key=f"soru_input_{st.session_state.soru_counter}",
        )
        gonder = gb.button("➤ " + ("Gönder" if not is_en else "Submit"), use_container_width=True)

        if gonder and soru.strip():
            temiz_soru = soru.strip()
            st.session_state.mesajlar.append({"role": "user", "content": temiz_soru})
            tesekkur = {"tesekkur","sagol","eyvallah","thanks","thank you","ok","super","harika"}
            if any(k in temiz_soru.lower() for k in tesekkur) and len(temiz_soru) < 30:
                yanit = "Rica ederim! 🚀 Başka soruların olursa buradayım."
            else:
                with st.spinner("🤖 " + ("Thinking..." if is_en else "Yanıt hazırlanıyor...")):
                    yanit = sorgula(
                        f"{dil_talimat(st.session_state.dil)}\n"
                        f"Kariyer koçu olarak CV'ye dayanarak soruyu yanıtla. "
                        f"Net ve somut tavsiyeler ver.\n\n"
                        f"CV:\n{st.session_state.cv_metni[:3000]}\n\nSoru: {temiz_soru}"
                    )
            st.session_state.mesajlar.append({"role": "assistant", "content": yanit})
            st.session_state.soru_counter += 1
            st.rerun()

    else:
        st.markdown(
            f"<div style='text-align:center;padding:2.5rem;color:#5a7ab5;font-size:0.9rem;'>"
            f"⬆️ {'Upload your CV to get started.' if is_en else 'Başlamak için CV yükleyin (PDF, DOCX, TXT).'}"
            f"</div>",
            unsafe_allow_html=True,
        )


# ── Sekme 2: CV Karşılaştırma ────────────────────────────────────
with sekme2:
    st.markdown(
        f"<div style='color:#b0c4e8;font-size:0.88rem;margin-bottom:0.8rem;'>"
        f"{'Upload two CVs to compare.' if is_en else 'İki CV yükleyin, hangisinin daha güçlü olduğunu öğrenin.'}"
        f"</div>",
        unsafe_allow_html=True,
    )

    k1, k2 = st.columns(2)

    with k1:
        st.markdown("<div style='font-size:0.82rem;color:#7aaeff;font-weight:600;margin-bottom:0.4rem;'>📄 CV 1</div>", unsafe_allow_html=True)
        f1 = st.file_uploader("CV 1", type=["pdf","docx","txt"], label_visibility="collapsed", key="cmp1")
        if f1 and f1.name != st.session_state.cv_adi:
            m = cv_metin_oku(f1)
            if m:
                st.session_state.cv_metni = m
                st.session_state.cv_adi   = f1.name
        if f1:
            st.markdown(f"<div style='font-size:0.76rem;color:#6ee7b7;'>✅ {f1.name}</div>", unsafe_allow_html=True)

    with k2:
        st.markdown("<div style='font-size:0.82rem;color:#7aaeff;font-weight:600;margin-bottom:0.4rem;'>📄 CV 2</div>", unsafe_allow_html=True)
        f2 = st.file_uploader("CV 2", type=["pdf","docx","txt"], label_visibility="collapsed", key="cmp2")
        if f2 and f2.name != st.session_state.cv2_adi:
            m2 = cv_metin_oku(f2)
            if m2:
                st.session_state.cv2_metni = m2
                st.session_state.cv2_adi   = f2.name
        if f2:
            st.markdown(f"<div style='font-size:0.76rem;color:#6ee7b7;'>✅ {f2.name}</div>", unsafe_allow_html=True)

    if st.session_state.cv_metni and st.session_state.cv2_metni:
        if st.button("⚖️ " + ("Compare" if is_en else "Karşılaştır"), use_container_width=True):
            p = (
                f"{dil_talimat(st.session_state.dil)}\n"
                f"İki CV'yi karşılaştır:\n"
                f"1. 🏆 Genel Değerlendirme\n2. 💪 CV 1 Güçlü Yanları\n3. 💪 CV 2 Güçlü Yanları\n"
                f"4. ⚠️ CV 1 Eksikleri\n5. ⚠️ CV 2 Eksikleri\n6. 📈 ATS Skoru (1-10)\n7. 🎯 Tavsiyeler\n\n"
                f"--- CV 1: {st.session_state.cv_adi} ---\n{st.session_state.cv_metni[:2000]}\n\n"
                f"--- CV 2: {st.session_state.cv2_adi} ---\n{st.session_state.cv2_metni[:2000]}"
            )
            with st.spinner("Karşılaştırılıyor..."):
                sonuc = sorgula(p)
            st.session_state.analiz_sayisi += 1
            st.markdown("<div class='compare-box'>", unsafe_allow_html=True)
            st.markdown(f"### ⚖️ Karşılaştırma Sonucu\n\n{sonuc}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button(
                "⬇️ " + ("Download" if is_en else "İndir (.txt)"),
                data=sonuc.encode("utf-8"),
                file_name="karsilastirma.txt",
                mime="text/plain",
            )
    else:
        st.markdown(
            f"<div style='text-align:center;padding:1.2rem;color:#5a7ab5;font-size:0.86rem;'>"
            f"{'Please upload both CVs.' if is_en else 'Her iki CV yi de yükleyin.'}"
            f"</div>",
            unsafe_allow_html=True,
        )


# ── Sekme 3: Kelime Bulutu ───────────────────────────────────────
with sekme3:
    st.markdown(
        f"<div style='color:#b0c4e8;font-size:0.88rem;margin-bottom:0.8rem;'>"
        f"{'Most frequent words in your CV.' if is_en else 'CV deki en sık geçen kelimeler.'}"
        f"</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.cv_metni:
        if st.button("☁️ " + ("Generate" if is_en else "Oluştur"), use_container_width=True):
            try:
                from wordcloud import WordCloud
                import matplotlib
                import matplotlib.pyplot as plt
                matplotlib.use("Agg")

                stop_words = {
                    "ve","ile","bir","bu","da","de","ki","mi","mı","mu","mü",
                    "için","ama","veya","gibi","daha","en","çok","her","ne",
                    "olan","olarak","şu","o","ben","sen","biz","siz",
                    "the","and","to","of","in","a","is","for","on","with","as","at",
                }

                wc = WordCloud(
                    width=800, height=380, background_color="#0d1b3e",
                    colormap="Blues", max_words=80, stopwords=stop_words,
                    prefer_horizontal=0.8, min_font_size=10,
                    max_font_size=80, collocations=False,
                ).generate(st.session_state.cv_metni)

                fig, ax = plt.subplots(figsize=(10, 4.5), facecolor="#0d1b3e")
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                plt.tight_layout(pad=0)
                st.pyplot(fig)
                plt.close()

                buf = io.BytesIO()
                wc.to_image().save(buf, format="PNG")
                st.download_button(
                    "⬇️ " + ("Download PNG" if is_en else "PNG İndir"),
                    data=buf.getvalue(),
                    file_name="kelime_bulutu.png",
                    mime="image/png",
                )
            except ImportError:
                st.error("wordcloud ve matplotlib gerekli: pip install wordcloud matplotlib")
    else:
        st.markdown(
            f"<div style='text-align:center;padding:1.2rem;color:#5a7ab5;font-size:0.86rem;'>"
            f"{'Upload a CV first.' if is_en else 'Önce CV Analizi sekmesinde CV yükleyin.'}"
            f"</div>",
            unsafe_allow_html=True,
        )


# --- Footer ---
st.markdown("""
<div style="text-align:center;padding:1.8rem 0 0.8rem;margin-top:2.5rem;
    border-top:1px solid #2a3f6e;color:#5a7ab5;
    font-size:0.76rem;font-family:'DM Mono',monospace;letter-spacing:0.04em;">
    © 2026 <span style="color:#7aaeff;font-weight:600;">Yusuf Aksu</span> — Tüm hakları saklıdır.
</div>
""", unsafe_allow_html=True)