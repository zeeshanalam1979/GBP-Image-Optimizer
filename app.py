import streamlit as st
import pandas as pd
import piexif
import json
import zipfile
import io
import os
import re
from PIL import Image
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GBP Image Optimizer",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:      #1c2333;
    --surface: #232d42;
    --card:    #2a3550;
    --border:  #3d5080;
    --accent:  #00e5ff;
    --accent2: #7c3aed;
    --success: #10b981;
    --warn:    #f59e0b;
    --text:    #ffffff;
    --muted:   #a0b0cc;
    --danger:  #ef4444;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 2px solid var(--border) !important;
}

h1,h2,h3,h4 { font-family:'Syne',sans-serif !important; font-weight:800 !important; color:#fff !important; }

/* ── Labels ── */
label, .stRadio label, [data-testid="stWidgetLabel"] p,
div[data-testid="stMarkdownContainer"] p {
    color: var(--text) !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background:   var(--card) !important;
    border:       2px solid var(--border) !important;
    color:        #ffffff !important;
    border-radius:8px !important;
    font-family:  'Space Mono', monospace !important;
    font-size:    0.9rem !important;
    font-weight:  700 !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea  > div > div > textarea::placeholder {
    color: #7a90b0 !important;
    font-weight: 400 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,0.2) !important;
}

/* ── Section labels ── */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
    font-weight: 700;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg,var(--accent2),#4f46e5) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono',monospace !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    padding: 0.55rem 1.3rem !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(124,58,237,0.5) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 2px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Space Mono',monospace !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 3px solid transparent !important;
    padding: 0.8rem 1.6rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 3px solid var(--accent) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'Space Mono',monospace !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    font-size: 0.8rem !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }
[data-testid="stFileUploader"] label {
    color: var(--text) !important;
    font-weight: 700 !important;
}

/* ── Dataframe ── */
.stDataFrame { background: var(--card) !important; border-radius:10px !important; }

/* ── Hero ── */
.hero-banner {
    background: linear-gradient(135deg,#1a2540 0%,#1e1545 50%,#0f1e38 100%);
    border: 2px solid var(--border);
    border-radius: 18px;
    padding: 1.6rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content:'';
    position:absolute; top:-60%; right:-5%;
    width:420px; height:420px;
    background: radial-gradient(circle,rgba(0,229,255,0.1) 0%,transparent 70%);
    pointer-events:none;
}
.hero-logo {
    width: 64px; height: 64px;
    border-radius: 14px;
    object-fit: contain;
    background: rgba(0,229,255,0.08);
    border: 2px solid rgba(0,229,255,0.2);
    padding: 6px;
    flex-shrink: 0;
}
.hero-logo-placeholder {
    width:64px; height:64px;
    border-radius:14px;
    background: linear-gradient(135deg,#7c3aed,#00e5ff);
    display:flex; align-items:center; justify-content:center;
    font-size:2rem; flex-shrink:0;
    border: 2px solid rgba(0,229,255,0.3);
}
.hero-text-block { flex:1; }
.hero-title {
    font-family:'Syne',sans-serif;
    font-size:1.9rem; font-weight:800;
    color:#fff; margin:0 0 0.2rem 0;
    letter-spacing:-0.02em;
}
.hero-title span { color:var(--accent); }
.hero-sub {
    font-family:'Space Mono',monospace;
    font-size:0.72rem; color:var(--muted);
    letter-spacing:0.1em; text-transform:uppercase; margin:0;
}

/* ── Win11 field group ── */
.field-group {
    background: var(--card);
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.field-group-title {
    font-family:'Space Mono',monospace;
    font-size:0.68rem; font-weight:700;
    letter-spacing:0.18em; text-transform:uppercase;
    color:var(--accent); margin-bottom:0.8rem;
    border-bottom:1px solid var(--border);
    padding-bottom:0.5rem;
}

/* ── Image cards ── */
.img-card-name {
    font-family:'Space Mono',monospace;
    font-size:0.72rem; color:var(--muted);
    word-break:break-all; margin-top:0.4rem; text-align:center;
    font-weight:700;
}
.img-card-status {
    font-family:'Space Mono',monospace;
    font-size:0.68rem; text-align:center;
    margin-top:0.2rem; padding:0.25rem 0.5rem;
    border-radius:4px; font-weight:700;
}
.status-ready   { background:rgba(16,185,129,0.2);  color:#34d399; }
.status-missing { background:rgba(239,68,68,0.2);   color:#f87171; }

/* ── Profile card ── */
.profile-card {
    background:var(--card);
    border:2px solid var(--border);
    border-left:4px solid var(--accent2);
    border-radius:10px;
    padding:0.7rem 1rem;
    margin-bottom:0.4rem;
}
.profile-card-name { font-weight:700; font-size:0.9rem; color:#fff; }
.profile-card-meta { font-family:'Space Mono',monospace; font-size:0.65rem; color:var(--muted); margin-top:0.2rem; }

/* ── Tag pill ── */
.tag-pill {
    display:inline-block;
    background:rgba(124,58,237,0.25); color:#c4b5fd;
    border:1px solid rgba(124,58,237,0.4);
    border-radius:20px; padding:0.15rem 0.6rem;
    font-family:'Space Mono',monospace; font-size:0.65rem; margin:0.15rem;
    font-weight:700;
}

/* ── Warn banner ── */
.warn-banner {
    background: rgba(245,158,11,0.12);
    border: 2px solid rgba(245,158,11,0.4);
    border-radius:10px; padding:0.6rem 1rem;
    font-family:'Space Mono',monospace;
    font-size:0.72rem; color:#fbbf24;
    font-weight:700; margin-bottom:0.8rem;
}

.divider { border:none; border-top:2px solid var(--border); margin:1rem 0; }

/* Scrollbar */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:var(--accent2); }

/* Radio */
.stRadio > div { gap:0.8rem !important; }
.stRadio > div > label {
    background:var(--card) !important;
    border:2px solid var(--border) !important;
    border-radius:8px !important;
    padding:0.4rem 1rem !important;
    color:#fff !important;
    font-size:0.82rem !important;
    font-weight:700 !important;
}

/* Date input */
.stDateInput > div > div > input {
    background:var(--card) !important;
    border:2px solid var(--border) !important;
    color:#fff !important;
    font-family:'Space Mono',monospace !important;
    font-size:0.9rem !important;
    font-weight:700 !important;
    border-radius:8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
PROFILES_FILE = "gbp_profiles.json"
LOGO_FILE     = "logo.png"

def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE) as f:
            return json.load(f)
    return {}

def save_profiles(p):
    with open(PROFILES_FILE, "w") as f:
        json.dump(p, f, indent=2)

def slugify(text):
    text = str(text).lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text

def build_filename(business_name, service, location, date_str, index, ext):
    parts = [slugify(business_name), slugify(service), slugify(location)]
    if date_str:
        try:
            d = datetime.strptime(str(date_str), "%Y-%m-%d")
            parts.append(d.strftime("%Y-%m-%d"))
        except Exception:
            parts.append(slugify(str(date_str)))
    parts.append(str(index).zfill(2))
    return "-".join([p for p in parts if p]) + f".{ext.lower().lstrip('.')}"

def deg_to_dms_rational(deg):
    deg = float(deg)
    d = int(abs(deg))
    m = int((abs(deg) - d) * 60)
    s = round(((abs(deg) - d) * 60 - m) * 60 * 10000)
    return [(d,1),(m,1),(s,10000)]

def inject_metadata(img_bytes, row, ext, output_format=None):
    """Strip all metadata then inject from row dict. Returns (bytes, ext)."""
    ext = ext.lower().lstrip('.')
    img = Image.open(io.BytesIO(img_bytes))

    if output_format and output_format != "Keep Original":
        out_fmt = output_format.upper()
        out_ext = "jpg" if out_fmt == "JPEG" else "png"
    else:
        out_fmt = "JPEG" if ext in ("jpg","jpeg","webp","heic","bmp","tiff") else "PNG"
        out_ext = "jpg"  if out_fmt == "JPEG" else "png"

    img_clean = Image.new(img.mode, img.size)
    img_clean.putdata(list(img.getdata()))

    if out_fmt == "JPEG":
        if img_clean.mode in ("RGBA","P","LA"):
            bg = Image.new("RGB", img_clean.size, (255,255,255))
            if img_clean.mode == "P":
                img_clean = img_clean.convert("RGBA")
            bg.paste(img_clean, mask=img_clean.split()[-1] if img_clean.mode in ("RGBA","LA") else None)
            img_clean = bg
        elif img_clean.mode != "RGB":
            img_clean = img_clean.convert("RGB")

    exif_bytes = None
    if out_fmt == "JPEG":
        exif_dict = {"0th":{},"Exif":{},"GPS":{},"1st":{}}

        # Title → ImageDescription
        title = str(row.get("title","")).encode("utf-8")
        if title:
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = title

        # Subject → XPSubject
        subject = str(row.get("subject",""))
        if subject:
            exif_dict["0th"][piexif.ImageIFD.XPSubject] = subject.encode("utf-16-le")

        # Tags → XPKeywords
        tags = str(row.get("tags",""))
        if tags:
            exif_dict["0th"][piexif.ImageIFD.XPKeywords] = tags.encode("utf-16-le")

        # Comments → UserComment
        comments = str(row.get("comments",""))
        if comments:
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = (
                b"UNICODE\x00" + comments.encode("utf-16-le")
            )

        # Authors → Artist
        authors = str(row.get("authors","")).encode("utf-8")
        if authors:
            exif_dict["0th"][piexif.ImageIFD.Artist] = authors

        # Copyright
        copy_val = str(row.get("copyright","")).encode("utf-8")
        if copy_val:
            exif_dict["0th"][piexif.ImageIFD.Copyright] = copy_val

        # Date Taken
        date_val = str(row.get("date_taken","")).strip()
        if date_val:
            try:
                d = datetime.strptime(date_val, "%Y-%m-%d")
                dt_str = d.strftime("%Y:%m:%d %H:%M:%S").encode()
                exif_dict["0th"][piexif.ImageIFD.DateTime]          = dt_str
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]  = dt_str
            except Exception:
                pass

        # GPS
        lat = row.get("latitude","") or row.get("lat","")
        lng = row.get("longitude","") or row.get("lng","")
        if lat and lng:
            try:
                lat_f = float(lat); lng_f = float(lng)
                exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef]  = b"N" if lat_f>=0 else b"S"
                exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]     = deg_to_dms_rational(lat_f)
                exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = b"E" if lng_f>=0 else b"W"
                exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]    = deg_to_dms_rational(lng_f)
            except Exception:
                pass

        exif_bytes = piexif.dump(exif_dict)

    out_buf = io.BytesIO()
    if out_fmt == "JPEG":
        img_clean.save(out_buf, format="JPEG", exif=exif_bytes, quality=95)
    else:
        img_clean.save(out_buf, format="PNG")

    return out_buf.getvalue(), out_ext

def read_metadata(img_bytes):
    result = {}
    try:
        img = Image.open(io.BytesIO(img_bytes))
        exif_data = img.info.get("exif", b"")
        if exif_data:
            exif_dict = piexif.load(exif_data)
            gps = exif_dict.get("GPS",{})
            if piexif.GPSIFD.GPSLatitude in gps:
                def dms(d):
                    return round(d[0][0]/d[0][1]+d[1][0]/d[1][1]/60+d[2][0]/d[2][1]/3600,6)
                lat = dms(gps[piexif.GPSIFD.GPSLatitude])
                lng = dms(gps[piexif.GPSIFD.GPSLongitude])
                if gps.get(piexif.GPSIFD.GPSLatitudeRef)==b"S":  lat=-lat
                if gps.get(piexif.GPSIFD.GPSLongitudeRef)==b"W": lng=-lng
                result["GPS Coordinates"] = f"{lat}, {lng}"
            ifd0 = exif_dict.get("0th",{})
            exif = exif_dict.get("Exif",{})
            if piexif.ImageIFD.ImageDescription in ifd0:
                result["Title"] = ifd0[piexif.ImageIFD.ImageDescription].decode("utf-8","replace")
            if piexif.ImageIFD.XPSubject in ifd0:
                result["Subject"] = ifd0[piexif.ImageIFD.XPSubject].decode("utf-16-le","replace").rstrip("\x00")
            if piexif.ImageIFD.XPKeywords in ifd0:
                result["Tags"] = ifd0[piexif.ImageIFD.XPKeywords].decode("utf-16-le","replace").rstrip("\x00")
            if piexif.ExifIFD.UserComment in exif:
                raw = exif[piexif.ExifIFD.UserComment]
                result["Comments"] = raw[8:].decode("utf-16-le","replace").rstrip("\x00") if raw[:8]==b"UNICODE\x00" else raw.decode("utf-8","replace")
            if piexif.ImageIFD.Artist in ifd0:
                result["Authors"] = ifd0[piexif.ImageIFD.Artist].decode("utf-8","replace")
            if piexif.ImageIFD.Copyright in ifd0:
                result["Copyright"] = ifd0[piexif.ImageIFD.Copyright].decode("utf-8","replace")
            if piexif.ImageIFD.DateTime in ifd0:
                result["Date Taken"] = ifd0[piexif.ImageIFD.DateTime].decode("utf-8","replace")
    except Exception as e:
        result["error"] = str(e)
    return result

# ── Session state ─────────────────────────────────────────────────────────────
if "profiles" not in st.session_state:
    st.session_state.profiles = load_profiles()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo upload
    st.markdown('<div class="section-label">🎨 Tool Logo</div>', unsafe_allow_html=True)
    logo_up = st.file_uploader("Upload your logo (PNG/JPG)", type=["png","jpg","jpeg"], key="logo_up", label_visibility="collapsed")
    if logo_up:
        with open(LOGO_FILE,"wb") as f:
            f.write(logo_up.read())
        st.success("Logo saved!")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📁 GBP Profiles</div>', unsafe_allow_html=True)

    profiles = st.session_state.profiles

    with st.expander("＋ New Profile", expanded=False):
        pname = st.text_input("Profile Name", placeholder="ABC Plumbing Karachi", key="pname")
        pbiz  = st.text_input("Business / Authors", placeholder="ABC Plumbing", key="pbiz")
        plat  = st.text_input("Latitude",  placeholder="24.8607", key="plat")
        plng  = st.text_input("Longitude", placeholder="67.0011", key="plng")
        pcity = st.text_input("City / Area", placeholder="Karachi", key="pcity")
        ptags = st.text_input("Default Tags", placeholder="plumber karachi; drain repair", key="ptags")
        pcopy = st.text_input("Copyright", placeholder="ABC Plumbing 2025", key="pcopy")
        if st.button("💾 Save Profile"):
            if pname:
                profiles[pname] = {"authors":pbiz,"lat":plat,"lng":plng,"city":pcity,"tags":ptags,"copyright":pcopy}
                st.session_state.profiles = profiles
                save_profiles(profiles)
                st.success(f"Saved: {pname}")
            else:
                st.error("Profile name required")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    selected_profile = None
    if profiles:
        st.markdown('<div class="section-label">Saved Profiles</div>', unsafe_allow_html=True)
        for pn, pd_ in list(profiles.items()):
            c1, c2 = st.columns([4,1])
            with c1:
                st.markdown(f"""
                <div class="profile-card">
                    <div class="profile-card-name">{pn}</div>
                    <div class="profile-card-meta">📍 {pd_.get('lat','?')}, {pd_.get('lng','?')} · {pd_.get('city','')}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                if st.button("✗", key=f"del_{pn}"):
                    del profiles[pn]; save_profiles(profiles); st.rerun()

        sel = st.selectbox("Load profile →", ["— none —"]+list(profiles.keys()), key="load_profile_select")
        if sel != "— none —":
            selected_profile = profiles[sel]
    else:
        st.info("No profiles yet.")

# ── Hero ──────────────────────────────────────────────────────────────────────
logo_html = ""
if os.path.exists(LOGO_FILE):
    import base64
    with open(LOGO_FILE,"rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{b64}" class="hero-logo"/>'
else:
    logo_html = '<div class="hero-logo-placeholder">📍</div>'

st.markdown(f"""
<div class="hero-banner">
    {logo_html}
    <div class="hero-text-block">
        <div class="hero-title">GBP Image <span>Optimizer</span></div>
        <div class="hero-sub">Strip · Inject · Rename · Download — Built for Google Business Profile SEO</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ Single Image",
    "📦 Batch (CSV + Images)",
    "🔍 Metadata Viewer",
    "📋 CSV Template",
])

FMT_OPTIONS = ["JPG (Recommended for GBP)", "PNG", "Keep Original"]
FMT_MAP     = {"JPG (Recommended for GBP)":"JPEG","PNG":"PNG","Keep Original":"Keep Original"}

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single Image
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Single Image Mode")
    st.markdown('<div class="section-label">Quick inject for one image</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1,1], gap="large")

    with col_left:
        st.markdown('<div class="section-label">📤 Upload Image</div>', unsafe_allow_html=True)
        single_img = st.file_uploader(
            "Drop image", type=["jpg","jpeg","png","webp","heic","tiff","bmp"],
            key="single_upload", label_visibility="collapsed"
        )
        if single_img:
            st.image(single_img, use_container_width=True)
            st.markdown(f'<div class="img-card-name">{single_img.name} · {round(single_img.size/1024,1)} KB</div>', unsafe_allow_html=True)

    with col_right:
        pfx = selected_profile or {}

        # ── Description group ──────────────────────────────────────────────
        st.markdown('<div class="field-group-title">📝 Description</div>', unsafe_allow_html=True)
        s_title   = st.text_input("Title",   placeholder="Smoke Heaven Heights Ho...", key="s_title")
        s_subject = st.text_input("Subject", placeholder="Best smoke shop in Karachi", key="s_subject")
        s_tags    = st.text_input("Tags (semicolon-separated)", value=pfx.get("tags",""), placeholder="smoke shop; smoke shop near me", key="s_tags")
        s_comments= st.text_area("Comments", placeholder="smoke shop, smoke shop near me...", height=80, key="s_comments")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ── Origin group ───────────────────────────────────────────────────
        st.markdown('<div class="field-group-title">🏢 Origin</div>', unsafe_allow_html=True)
        s_authors = st.text_input("Authors (Business Name)", value=pfx.get("authors",""), placeholder="Smoke Heaven", key="s_authors")
        s_copy    = st.text_input("Copyright", value=pfx.get("copyright",""), placeholder="Smoke Heaven 2026", key="s_copy")
        s_date    = st.date_input("Date Taken", value=datetime.today(), key="s_date")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ── GPS group ──────────────────────────────────────────────────────
        st.markdown('<div class="field-group-title">📍 GPS Coordinates</div>', unsafe_allow_html=True)
        gc1, gc2 = st.columns(2)
        s_lat = gc1.text_input("Latitude",  value=pfx.get("lat",""), placeholder="24.8607", key="s_lat")
        s_lng = gc2.text_input("Longitude", value=pfx.get("lng",""), placeholder="67.0011", key="s_lng")

        # ── Service / Location for filename ───────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="field-group-title">📁 Filename Pattern</div>', unsafe_allow_html=True)
        fn1, fn2 = st.columns(2)
        s_svc = fn1.text_input("Service / Topic", placeholder="drain-repair", key="s_svc")
        s_loc = fn2.text_input("Location",        value=pfx.get("city",""), placeholder="karachi", key="s_loc")

        # ── Format ────────────────────────────────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="warn-banner">⚠️ Google Business Profile only accepts JPG and PNG — WEBP will be rejected</div>', unsafe_allow_html=True)
        s_fmt = st.radio("Output Format", FMT_OPTIONS, index=0, key="s_fmt", horizontal=True)

        st.markdown("")
        if st.button("🚀 Inject Metadata & Download", key="single_go"):
            if not single_img:
                st.error("Please upload an image first.")
            else:
                with st.spinner("Processing…"):
                    row = {
                        "title":s_title,"subject":s_subject,"tags":s_tags,
                        "comments":s_comments,"authors":s_authors,"copyright":s_copy,
                        "date_taken":s_date.strftime("%Y-%m-%d"),
                        "latitude":s_lat,"longitude":s_lng,
                    }
                    orig_ext = single_img.name.rsplit(".",1)[-1]
                    out_bytes, out_ext = inject_metadata(single_img.read(), row, orig_ext, FMT_MAP[s_fmt])
                    fname = build_filename(s_authors, s_svc, s_loc, s_date.strftime("%Y-%m-%d"), 1, out_ext)

                converted = orig_ext.lower() != out_ext.lower()
                msg = f"✅ Done! Output: `{fname}`"
                if converted:
                    msg += f"  ·  Converted **{orig_ext.upper()} → {out_ext.upper()}**"
                st.success(msg)
                st.download_button(
                    "⬇️ Download Optimized Image", data=out_bytes,
                    file_name=fname, mime=f"image/{'jpeg' if out_ext=='jpg' else out_ext}",
                    key="single_dl"
                )

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — Batch
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Batch Processing")
    st.markdown('<div class="section-label">Upload CSV + images → auto-match → inject → download ZIP</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1,1], gap="large")
    with col_a:
        st.markdown('<div class="section-label">📄 Upload CSV</div>', unsafe_allow_html=True)
        csv_file = st.file_uploader("CSV file", type=["csv"], key="batch_csv", label_visibility="collapsed")
        df = None
        if csv_file:
            df = pd.read_csv(csv_file)
            st.dataframe(df, use_container_width=True, height=220)
            st.markdown(f'<div class="section-label">✅ {len(df)} rows loaded</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-label">🖼️ Upload Images</div>', unsafe_allow_html=True)
        batch_imgs = st.file_uploader(
            "Images", type=["jpg","jpeg","png","webp","heic","tiff","bmp"],
            accept_multiple_files=True, key="batch_imgs", label_visibility="collapsed"
        )
        if batch_imgs:
            st.markdown(f'<div class="section-label">✅ {len(batch_imgs)} images uploaded</div>', unsafe_allow_html=True)

    if batch_imgs and df is not None:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("#### 🔎 Image Preview & CSV Match")

        csv_fnames = set(df["filename"].astype(str).tolist()) if "filename" in df.columns else set()
        cols_per_row = 5

        for row_imgs in [batch_imgs[i:i+cols_per_row] for i in range(0,len(batch_imgs),cols_per_row)]:
            cols = st.columns(cols_per_row)
            for col, img_file in zip(cols, row_imgs):
                matched = img_file.name in csv_fnames
                with col:
                    img_file.seek(0)
                    st.image(img_file, use_container_width=True)
                    st.markdown(f"""
                    <div class="img-card-name">{img_file.name}</div>
                    <div class="img-card-status {'status-ready' if matched else 'status-missing'}">
                        {'✓ Matched' if matched else '✗ No CSV row'}
                    </div>""", unsafe_allow_html=True)

        matched_count = sum(1 for f in batch_imgs if f.name in csv_fnames)
        m1,m2,m3 = st.columns(3)
        m1.metric("Images Uploaded", len(batch_imgs))
        m2.metric("Matched to CSV",  matched_count)
        m3.metric("Missing CSV Rows",len(batch_imgs)-matched_count)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="warn-banner">⚠️ Google Business Profile only accepts JPG and PNG — WEBP will be rejected</div>', unsafe_allow_html=True)

        b_fmt = st.radio("Batch Output Format", FMT_OPTIONS, index=0, key="b_fmt", horizontal=True)

        if st.button("🚀 Process All Matched Images → ZIP", key="batch_go"):
            if matched_count == 0:
                st.error("No images matched. Check 'filename' column matches uploaded filenames exactly.")
            else:
                zip_buf = io.BytesIO()
                processed = conversions = 0
                errors = []
                progress = st.progress(0, text="Processing images…")

                with zipfile.ZipFile(zip_buf,"w",zipfile.ZIP_DEFLATED) as zf:
                    for idx, img_file in enumerate(batch_imgs):
                        fname = img_file.name
                        progress.progress((idx+1)/len(batch_imgs), text=f"Processing {fname}…")
                        if fname not in csv_fnames:
                            continue
                        csv_row  = df[df["filename"]==fname].iloc[0].to_dict()
                        orig_ext = fname.rsplit(".",1)[-1]
                        try:
                            img_file.seek(0)
                            out_bytes, out_ext = inject_metadata(img_file.read(), csv_row, orig_ext, FMT_MAP[b_fmt])
                            if orig_ext.lower() != out_ext.lower():
                                conversions += 1
                            new_name = build_filename(
                                csv_row.get("authors", csv_row.get("business_name","biz")),
                                csv_row.get("service","service"),
                                csv_row.get("location","location"),
                                csv_row.get("date_taken",""),
                                idx+1, out_ext
                            )
                            zf.writestr(new_name, out_bytes)
                            processed += 1
                        except Exception as e:
                            errors.append(f"{fname}: {e}")

                progress.empty()
                if processed > 0:
                    msg = f"✅ {processed} images processed!"
                    if conversions:
                        msg += f"  ·  {conversions} files converted to {b_fmt.split()[0]}"
                    st.success(msg)
                    st.download_button(
                        f"⬇️ Download ZIP ({processed} images)",
                        data=zip_buf.getvalue(),
                        file_name=f"gbp_optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip", key="batch_dl"
                    )
                if errors:
                    st.warning(f"⚠️ {len(errors)} errors:")
                    for e in errors: st.code(e)

    elif batch_imgs and df is None:
        st.warning("⬆️ Please also upload a CSV file.")
    elif df is not None and not batch_imgs:
        st.info("⬆️ CSV loaded. Now upload your images.")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — Metadata Viewer
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Metadata Viewer")
    st.markdown('<div class="section-label">Verify injected metadata — matches Windows 11 File Properties panel</div>', unsafe_allow_html=True)

    view_img = st.file_uploader(
        "Drop image to inspect", type=["jpg","jpeg","png","webp","tiff","bmp"], key="view_upload"
    )
    if view_img:
        col_v1, col_v2 = st.columns([1,2], gap="large")
        with col_v1:
            st.image(view_img, use_container_width=True)
            st.markdown(f'<div class="img-card-name">{view_img.name}</div>', unsafe_allow_html=True)
        with col_v2:
            view_img.seek(0)
            meta = read_metadata(view_img.read())

            # Group display like Windows 11
            desc_fields   = ["Title","Subject","Tags","Comments"]
            origin_fields = ["Authors","Copyright","Date Taken"]
            gps_fields    = ["GPS Coordinates"]

            def render_meta_group(title, fields):
                st.markdown(f'<div class="field-group-title">{title}</div>', unsafe_allow_html=True)
                found = False
                for k in fields:
                    v = meta.get(k)
                    c1,c2 = st.columns([1,3])
                    c1.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.78rem;color:#a0b0cc;font-weight:700;padding-top:0.3rem">{k}</div>', unsafe_allow_html=True)
                    if v:
                        c2.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.82rem;color:#ffffff;font-weight:700;background:#2a3550;padding:0.35rem 0.7rem;border-radius:7px;border:2px solid #3d5080">{v}</div>', unsafe_allow_html=True)
                        found = True
                    else:
                        c2.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.78rem;color:#3d5080;font-style:italic;padding-top:0.3rem">—</div>', unsafe_allow_html=True)
                    st.markdown("")
                return found

            if meta and "error" not in meta:
                render_meta_group("📝 Description", desc_fields)
                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                render_meta_group("🏢 Origin", origin_fields)
                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                render_meta_group("📍 GPS", gps_fields)

                if "GPS Coordinates" in meta:
                    lat_v,lng_v = meta["GPS Coordinates"].split(",")
                    maps_url = f"https://www.google.com/maps?q={lat_v.strip()},{lng_v.strip()}"
                    st.markdown(f'<a href="{maps_url}" target="_blank" style="font-family:Space Mono,monospace;font-size:0.78rem;color:#00e5ff;text-decoration:none;font-weight:700">🗺️ View on Google Maps →</a>', unsafe_allow_html=True)
            elif "error" in meta:
                st.error(f"Parse error: {meta['error']}")
            else:
                st.warning("No readable EXIF metadata found.")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — CSV Template
# ═════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### CSV Template")
    st.markdown('<div class="section-label">Download and fill in — one row per image. Columns match Windows 11 File Properties.</div>', unsafe_allow_html=True)

    pfx2 = selected_profile or {}
    sample = {
        "filename":  ["photo1.jpg","photo2.jpg","photo3.jpg"],
        "title":     ["Smoke Shop Karachi Interior","Smoke Shop Products Display","Smoke Shop Exterior"],
        "subject":   ["Best smoke shop in Karachi"]*3,
        "tags":      [pfx2.get("tags","smoke shop; smoke shop near me; hookah karachi")]*3,
        "comments":  ["smoke shop, smoke shop near me, hookah karachi"]*3,
        "authors":   [pfx2.get("authors","Smoke Heaven")]*3,
        "copyright": [pfx2.get("copyright","Smoke Heaven 2026")]*3,
        "date_taken":[datetime.today().strftime("%Y-%m-%d")]*3,
        "latitude":  [pfx2.get("lat","24.8607")]*3,
        "longitude": [pfx2.get("lng","67.0011")]*3,
        "service":   ["smoke-shop","products","exterior"],
        "location":  [pfx2.get("city","karachi")]*3,
    }
    template_df = pd.DataFrame(sample)
    st.dataframe(template_df, use_container_width=True)

    st.download_button(
        "⬇️ Download CSV Template",
        data=template_df.to_csv(index=False).encode(),
        file_name="gbp_image_template.csv",
        mime="text/csv", key="csv_dl"
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("#### 📖 Column Reference")

    col_ref = {
        "filename":  "Must match uploaded image filename exactly (case-sensitive)",
        "title":     "Windows: Title — injected into ImageDescription EXIF",
        "subject":   "Windows: Subject — injected into XPSubject EXIF",
        "tags":      "Windows: Tags — semicolon-separated, injected into XPKeywords",
        "comments":  "Windows: Comments — injected into UserComment EXIF",
        "authors":   "Windows: Authors — injected into Artist EXIF (business name)",
        "copyright": "Windows: Copyright — injected into Copyright EXIF",
        "date_taken":"Windows: Date Taken — format YYYY-MM-DD",
        "latitude":  "GPS Latitude in decimal degrees (e.g. 24.8607)",
        "longitude": "GPS Longitude in decimal degrees (e.g. 67.0011)",
        "service":   "Used in output filename only (e.g. drain-repair)",
        "location":  "Used in output filename only (e.g. karachi)",
    }
    for cn,cd in col_ref.items():
        c1,c2 = st.columns([1,3])
        c1.markdown(f'<span class="tag-pill">{cn}</span>', unsafe_allow_html=True)
        c2.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.75rem;color:#a0b0cc;padding-top:0.4rem;font-weight:700">{cd}</div>', unsafe_allow_html=True)
