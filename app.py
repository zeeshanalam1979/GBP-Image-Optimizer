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
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GBP Image Optimizer",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:       #0a0e1a;
    --surface:  #111827;
    --card:     #1a2235;
    --border:   #2a3548;
    --accent:   #00e5ff;
    --accent2:  #7c3aed;
    --success:  #10b981;
    --warn:     #f59e0b;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --danger:   #ef4444;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }

.stButton > button {
    background: linear-gradient(135deg, var(--accent2), #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.5) !important;
}

.accent-btn > button {
    background: linear-gradient(135deg, var(--accent), #0891b2) !important;
    color: #0a0e1a !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,229,255,0.15) !important;
}

[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.75rem 1.5rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}

.stDataFrame { background: var(--card) !important; border-radius: 10px !important; }

.stAlert { border-radius: 10px !important; }

[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'Space Mono', monospace !important; }

div[data-testid="column"] { padding: 0.25rem !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent2); }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #111827 0%, #1a1040 50%, #0a1628 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(0,229,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #fff;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
}
.hero-title span { color: var(--accent); }
.hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0;
}

/* Image card grid */
.img-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.75rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.img-card:hover { border-color: var(--accent2); }
.img-card-name {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    word-break: break-all;
    margin-top: 0.4rem;
    text-align: center;
}
.img-card-status {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    text-align: center;
    margin-top: 0.2rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
}
.status-ready { background: rgba(16,185,129,0.15); color: var(--success); }
.status-missing { background: rgba(239,68,68,0.15); color: var(--danger); }
.status-done { background: rgba(0,229,255,0.15); color: var(--accent); }

/* Profile card */
.profile-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent2);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
}
.profile-card:hover { border-left-color: var(--accent); background: #1e2d44; }
.profile-card-name { font-weight: 700; font-size: 0.9rem; color: var(--text); }
.profile-card-meta { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: var(--muted); margin-top: 0.2rem; }

/* Divider */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1rem 0;
}

/* Tag pill */
.tag-pill {
    display: inline-block;
    background: rgba(124,58,237,0.2);
    color: #a78bfa;
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 20px;
    padding: 0.15rem 0.6rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    margin: 0.15rem;
}

/* Section label */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.4rem;
}

.stSuccess { background: rgba(16,185,129,0.1) !important; border-color: var(--success) !important; }
.stError   { background: rgba(239,68,68,0.1) !important; border-color: var(--danger) !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border-color: var(--warn) !important; }
.stInfo    { background: rgba(0,229,255,0.08) !important; border-color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
PROFILES_FILE = "gbp_profiles.json"

def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE) as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)

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
    return [(d, 1), (m, 1), (s, 10000)]

def inject_metadata(img_bytes, row, ext, output_format=None):
    """Strip all metadata then inject from CSV row. Returns (processed bytes, actual_ext)."""
    ext = ext.lower().lstrip('.')

    img = Image.open(io.BytesIO(img_bytes))

    # Determine output format
    if output_format and output_format != "Keep Original":
        out_fmt  = output_format.upper()   # "JPEG" or "PNG"
        out_ext  = "jpg" if out_fmt == "JPEG" else "png"
    else:
        out_fmt  = "JPEG" if ext in ("jpg", "jpeg", "webp", "heic", "bmp", "tiff") else "PNG"
        out_ext  = "jpg"  if out_fmt == "JPEG" else "png"

    # Convert RGBA → RGB for JPEG (JPEG cannot store alpha channel)
    img_clean = Image.new(img.mode, img.size)
    img_clean.putdata(list(img.getdata()))
    if out_fmt == "JPEG" and img_clean.mode in ("RGBA", "P", "LA"):
        bg = Image.new("RGB", img_clean.size, (255, 255, 255))
        if img_clean.mode == "P":
            img_clean = img_clean.convert("RGBA")
        bg.paste(img_clean, mask=img_clean.split()[-1] if img_clean.mode in ("RGBA","LA") else None)
        img_clean = bg
    elif out_fmt == "JPEG" and img_clean.mode != "RGB":
        img_clean = img_clean.convert("RGB")

    # Build EXIF — JPEG only (PNG doesn't support EXIF natively via piexif)
    exif_bytes = None
    if out_fmt == "JPEG":
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

        desc = str(row.get("description", "")).encode("utf-8")
        if desc:
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = desc

        biz = str(row.get("business_name", "")).encode("utf-8")
        if biz:
            exif_dict["0th"][piexif.ImageIFD.Artist] = biz

        copy_val = str(row.get("copyright", "")).encode("utf-8")
        if copy_val:
            exif_dict["0th"][piexif.ImageIFD.Copyright] = copy_val

        keywords = str(row.get("keywords", ""))
        if keywords:
            exif_dict["0th"][piexif.ImageIFD.XPKeywords] = keywords.encode("utf-16-le")
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = (
                b"UNICODE\x00" + keywords.encode("utf-16-le")
            )

        date_val = str(row.get("date_taken", "")).strip()
        if date_val:
            try:
                d = datetime.strptime(date_val, "%Y-%m-%d")
                dt_str = d.strftime("%Y:%m:%d %H:%M:%S").encode()
                exif_dict["0th"][piexif.ImageIFD.DateTime] = dt_str
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dt_str
            except Exception:
                pass

        lat = row.get("lat", "")
        lng = row.get("lng", "")
        if lat and lng:
            try:
                lat_f = float(lat)
                lng_f = float(lng)
                exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef]  = b"N" if lat_f >= 0 else b"S"
                exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]     = deg_to_dms_rational(lat_f)
                exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = b"E" if lng_f >= 0 else b"W"
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
    """Read and return metadata dict from image bytes."""
    result = {}
    try:
        img = Image.open(io.BytesIO(img_bytes))
        exif_data = img.info.get("exif", b"")
        if exif_data:
            exif_dict = piexif.load(exif_data)
            gps = exif_dict.get("GPS", {})
            if piexif.GPSIFD.GPSLatitude in gps:
                def dms(d):
                    deg = d[0][0]/d[0][1] + d[1][0]/d[1][1]/60 + d[2][0]/d[2][1]/3600
                    return round(deg, 6)
                lat = dms(gps[piexif.GPSIFD.GPSLatitude])
                lng = dms(gps[piexif.GPSIFD.GPSLongitude])
                if gps.get(piexif.GPSIFD.GPSLatitudeRef) == b"S": lat = -lat
                if gps.get(piexif.GPSIFD.GPSLongitudeRef) == b"W": lng = -lng
                result["GPS"] = f"{lat}, {lng}"
            ifd0 = exif_dict.get("0th", {})
            if piexif.ImageIFD.ImageDescription in ifd0:
                result["Description"] = ifd0[piexif.ImageIFD.ImageDescription].decode("utf-8", errors="replace")
            if piexif.ImageIFD.Artist in ifd0:
                result["Artist/Business"] = ifd0[piexif.ImageIFD.Artist].decode("utf-8", errors="replace")
            if piexif.ImageIFD.Copyright in ifd0:
                result["Copyright"] = ifd0[piexif.ImageIFD.Copyright].decode("utf-8", errors="replace")
            if piexif.ImageIFD.DateTime in ifd0:
                result["DateTime"] = ifd0[piexif.ImageIFD.DateTime].decode("utf-8", errors="replace")
            if piexif.ImageIFD.XPKeywords in ifd0:
                kw_raw = ifd0[piexif.ImageIFD.XPKeywords]
                result["Keywords"] = kw_raw.decode("utf-16-le", errors="replace").rstrip("\x00")
    except Exception as e:
        result["error"] = str(e)
    return result

# ── Session state ─────────────────────────────────────────────────────────────
if "profiles" not in st.session_state:
    st.session_state.profiles = load_profiles()
if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1rem'>
        <div style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#fff'>
            📍 GBP<span style='color:#00e5ff'>Optimizer</span>
        </div>
        <div style='font-family:Space Mono,monospace;font-size:0.62rem;color:#64748b;letter-spacing:0.12em;text-transform:uppercase'>
            Image Metadata Tool v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">📁 GBP Profiles</div>', unsafe_allow_html=True)

    profiles = st.session_state.profiles

    # Save new profile
    with st.expander("＋ New Profile", expanded=False):
        pname  = st.text_input("Profile Name", placeholder="ABC Plumbing Karachi", key="pname")
        pbiz   = st.text_input("Business Name", placeholder="ABC Plumbing", key="pbiz")
        plat   = st.text_input("Latitude",  placeholder="24.8607", key="plat")
        plng   = st.text_input("Longitude", placeholder="67.0011", key="plng")
        pcity  = st.text_input("City / Area", placeholder="Karachi", key="pcity")
        pkw    = st.text_input("Default Keywords", placeholder="plumber karachi, drain repair", key="pkw")
        pcopy  = st.text_input("Copyright",  placeholder="ABC Plumbing 2025", key="pcopy")
        if st.button("💾 Save Profile"):
            if pname:
                profiles[pname] = {
                    "business_name": pbiz, "lat": plat, "lng": plng,
                    "city": pcity, "keywords": pkw, "copyright": pcopy
                }
                st.session_state.profiles = profiles
                save_profiles(profiles)
                st.success(f"Saved: {pname}")
            else:
                st.error("Profile name required")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # List profiles
    selected_profile = None
    if profiles:
        st.markdown('<div class="section-label">Saved Profiles</div>', unsafe_allow_html=True)
        for pn, pd_ in profiles.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class="profile-card">
                    <div class="profile-card-name">{pn}</div>
                    <div class="profile-card-meta">📍 {pd_.get('lat','?')}, {pd_.get('lng','?')} · {pd_.get('city','')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✗", key=f"del_{pn}", help=f"Delete {pn}"):
                    del profiles[pn]
                    save_profiles(profiles)
                    st.rerun()

        selected_profile_name = st.selectbox(
            "Load profile into form →",
            ["— none —"] + list(profiles.keys()),
            key="load_profile_select"
        )
        if selected_profile_name != "— none —":
            selected_profile = profiles[selected_profile_name]
    else:
        st.info("No profiles yet. Create one above.")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label" style="font-size:0.6rem">💡 Tip: Load a profile to auto-fill batch defaults</div>', unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">GBP Image <span>Optimizer</span></div>
    <div class="hero-sub">Strip · Inject · Rename · Download — Built for Google Business Profile SEO</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ Single Image",
    "📦 Batch (CSV + Images)",
    "🔍 Metadata Viewer",
    "📋 CSV Template",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single Image
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Single Image Mode")
    st.markdown('<div class="section-label">Quick inject for one image — great for testing</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="section-label">📤 Upload Image</div>', unsafe_allow_html=True)
        single_img = st.file_uploader(
            "Drop image here", type=["jpg","jpeg","png","webp","heic","tiff","bmp"],
            key="single_upload", label_visibility="collapsed"
        )

        if single_img:
            st.image(single_img, use_container_width=True)
            st.markdown(f'<div class="img-card-name">{single_img.name} · {round(single_img.size/1024,1)} KB</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-label">🏷️ Metadata Fields</div>', unsafe_allow_html=True)

        pfx = selected_profile or {}
        s_biz   = st.text_input("Business Name",  value=pfx.get("business_name",""), key="s_biz")
        s_svc   = st.text_input("Service / Topic", placeholder="drain repair", key="s_svc")
        s_loc   = st.text_input("Location",        value=pfx.get("city",""), key="s_loc")
        c1, c2  = st.columns(2)
        s_lat   = c1.text_input("Latitude",  value=pfx.get("lat",""), key="s_lat")
        s_lng   = c2.text_input("Longitude", value=pfx.get("lng",""), key="s_lng")
        s_kw    = st.text_input("Keywords (comma-separated)", value=pfx.get("keywords",""), key="s_kw")
        s_desc  = st.text_area("Description / Alt Text", height=80, key="s_desc")
        s_copy  = st.text_input("Copyright", value=pfx.get("copyright",""), key="s_copy")
        s_date  = st.date_input("Date Taken", value=datetime.today(), key="s_date")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🔄 Output Format</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.65rem;color:#f59e0b;margin-bottom:0.5rem">⚠️ Google Business Profile only accepts JPG and PNG — WEBP will be rejected</div>', unsafe_allow_html=True)
        s_fmt = st.radio(
            "Output format", ["JPG (Recommended for GBP)", "PNG", "Keep Original"],
            index=0, key="s_fmt", horizontal=True, label_visibility="collapsed"
        )
        fmt_map = {"JPG (Recommended for GBP)": "JPEG", "PNG": "PNG", "Keep Original": "Keep Original"}

        st.markdown("")
        if st.button("🚀 Inject Metadata & Download", key="single_go"):
            if not single_img:
                st.error("Please upload an image first.")
            else:
                with st.spinner("Processing…"):
                    row = {
                        "business_name": s_biz, "service": s_svc, "location": s_loc,
                        "lat": s_lat, "lng": s_lng, "keywords": s_kw,
                        "description": s_desc, "copyright": s_copy,
                        "date_taken": s_date.strftime("%Y-%m-%d"),
                    }
                    orig_ext = single_img.name.rsplit(".", 1)[-1]
                    out_bytes, out_ext = inject_metadata(
                        single_img.read(), row, orig_ext,
                        output_format=fmt_map[s_fmt]
                    )
                    fname = build_filename(s_biz, s_svc, s_loc, s_date.strftime("%Y-%m-%d"), 1, out_ext)

                converted = orig_ext.lower().lstrip(".") != out_ext.lower().lstrip(".")
                msg = f"✅ Done! Output: `{fname}`"
                if converted:
                    msg += f"  ·  Converted **{orig_ext.upper()} → {out_ext.upper()}**"
                st.success(msg)
                st.download_button(
                    "⬇️ Download Optimized Image", data=out_bytes,
                    file_name=fname,
                    mime=f"image/{'jpeg' if out_ext=='jpg' else out_ext}",
                    key="single_dl"
                )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Batch
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Batch Processing")
    st.markdown('<div class="section-label">Upload CSV + images → auto-match → inject → download ZIP</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1], gap="large")

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

    # Preview cards
    if batch_imgs and df is not None:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("#### 🔎 Image Preview & CSV Match")

        img_map = {f.name: f for f in batch_imgs}
        csv_fnames = set(df["filename"].astype(str).tolist()) if "filename" in df.columns else set()

        cols_per_row = 5
        rows_of_imgs = [batch_imgs[i:i+cols_per_row] for i in range(0, len(batch_imgs), cols_per_row)]

        for row_imgs in rows_of_imgs:
            cols = st.columns(cols_per_row)
            for col, img_file in zip(cols, row_imgs):
                matched = img_file.name in csv_fnames
                status_cls  = "status-ready" if matched else "status-missing"
                status_text = "✓ Matched" if matched else "✗ No CSV row"
                with col:
                    img_file.seek(0)
                    st.image(img_file, use_container_width=True)
                    st.markdown(f"""
                    <div class="img-card-name">{img_file.name}</div>
                    <div class="img-card-status {status_cls}">{status_text}</div>
                    """, unsafe_allow_html=True)

        matched_count = sum(1 for f in batch_imgs if f.name in csv_fnames)
        m1, m2, m3 = st.columns(3)
        m1.metric("Images Uploaded", len(batch_imgs))
        m2.metric("Matched to CSV", matched_count)
        m3.metric("Missing CSV Rows", len(batch_imgs) - matched_count)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        st.markdown('<div class="section-label">🔄 Output Format for All Images</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.65rem;color:#f59e0b;margin-bottom:0.5rem">⚠️ Google Business Profile only accepts JPG and PNG — WEBP will be rejected by GBP</div>', unsafe_allow_html=True)
        b_fmt = st.radio(
            "Batch output format", ["JPG (Recommended for GBP)", "PNG", "Keep Original"],
            index=0, key="b_fmt", horizontal=True, label_visibility="collapsed"
        )
        b_fmt_map = {"JPG (Recommended for GBP)": "JPEG", "PNG": "PNG", "Keep Original": "Keep Original"}

        if st.button("🚀 Process All Matched Images → ZIP", key="batch_go"):
            if matched_count == 0:
                st.error("No images matched CSV rows. Check that 'filename' column in CSV matches uploaded filenames.")
            else:
                zip_buf = io.BytesIO()
                processed = 0
                errors = []
                conversions = 0

                progress = st.progress(0, text="Processing images…")

                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for idx, img_file in enumerate(batch_imgs):
                        fname = img_file.name
                        progress.progress((idx+1)/len(batch_imgs), text=f"Processing {fname}…")

                        if fname not in csv_fnames:
                            continue

                        csv_row = df[df["filename"] == fname].iloc[0].to_dict()
                        orig_ext = fname.rsplit(".", 1)[-1]

                        try:
                            img_file.seek(0)
                            out_bytes, out_ext = inject_metadata(
                                img_file.read(), csv_row, orig_ext,
                                output_format=b_fmt_map[b_fmt]
                            )
                            if orig_ext.lower() != out_ext.lower():
                                conversions += 1
                            new_name = build_filename(
                                csv_row.get("business_name","biz"),
                                csv_row.get("service","service"),
                                csv_row.get("location","location"),
                                csv_row.get("date_taken",""),
                                idx + 1,
                                out_ext
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
                        mime="application/zip",
                        key="batch_dl"
                    )
                if errors:
                    st.warning(f"⚠️ {len(errors)} errors:")
                    for e in errors:
                        st.code(e)

    elif batch_imgs and df is None:
        st.warning("⬆️ Please also upload a CSV file to match images.")
    elif df is not None and not batch_imgs:
        st.info("⬆️ CSV loaded. Now upload your images.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Metadata Viewer
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Metadata Viewer")
    st.markdown('<div class="section-label">Verify injected metadata on any image before uploading to GBP</div>', unsafe_allow_html=True)

    view_img = st.file_uploader(
        "Drop image to inspect", type=["jpg","jpeg","png","webp","tiff","bmp"],
        key="view_upload"
    )

    if view_img:
        col_v1, col_v2 = st.columns([1, 2], gap="large")
        with col_v1:
            st.image(view_img, use_container_width=True)
            st.markdown(f'<div class="img-card-name">{view_img.name}</div>', unsafe_allow_html=True)

        with col_v2:
            view_img.seek(0)
            meta = read_metadata(view_img.read())

            if meta:
                st.markdown('<div class="section-label">📋 Detected Metadata</div>', unsafe_allow_html=True)
                for k, v in meta.items():
                    if k == "error":
                        st.error(f"Parse error: {v}")
                    else:
                        c1, c2 = st.columns([1, 3])
                        c1.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.75rem;color:#64748b;padding-top:0.3rem">{k}</div>', unsafe_allow_html=True)
                        c2.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.8rem;color:#e2e8f0;background:#1a2235;padding:0.3rem 0.6rem;border-radius:6px;border:1px solid #2a3548">{v}</div>', unsafe_allow_html=True)
                        st.markdown("")

                # GPS map link
                if "GPS" in meta:
                    lat_v, lng_v = meta["GPS"].split(",")
                    maps_url = f"https://www.google.com/maps?q={lat_v.strip()},{lng_v.strip()}"
                    st.markdown(f'<a href="{maps_url}" target="_blank" style="font-family:Space Mono,monospace;font-size:0.75rem;color:#00e5ff;text-decoration:none">🗺️ View on Google Maps →</a>', unsafe_allow_html=True)
            else:
                st.warning("No readable EXIF metadata found in this image.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CSV Template
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### CSV Template")
    st.markdown('<div class="section-label">Download and fill in the template — one row per image</div>', unsafe_allow_html=True)

    # Build sample template
    pfx2 = selected_profile or {}
    sample_data = {
        "filename":      ["photo1.jpg", "photo2.jpg", "photo3.jpg"],
        "business_name": [pfx2.get("business_name","ABC Plumbing")] * 3,
        "service":       ["drain repair", "pipe installation", "emergency plumber"],
        "location":      [pfx2.get("city","Karachi")] * 3,
        "lat":           [pfx2.get("lat","24.8607")] * 3,
        "lng":           [pfx2.get("lng","67.0011")] * 3,
        "keywords":      [
            pfx2.get("keywords","plumber karachi, drain repair, emergency plumber"),
            pfx2.get("keywords","pipe installation karachi, plumbing services"),
            pfx2.get("keywords","emergency plumber karachi, 24hr plumbing"),
        ],
        "description":   [
            "Professional drain repair service in Karachi by ABC Plumbing",
            "Expert pipe installation services across Karachi",
            "24-hour emergency plumber available in Karachi",
        ],
        "copyright":     [pfx2.get("copyright","ABC Plumbing 2025")] * 3,
        "date_taken":    [datetime.today().strftime("%Y-%m-%d")] * 3,
    }
    template_df = pd.DataFrame(sample_data)

    st.dataframe(template_df, use_container_width=True)

    csv_bytes = template_df.to_csv(index=False).encode()
    st.download_button(
        "⬇️ Download CSV Template",
        data=csv_bytes,
        file_name="gbp_image_template.csv",
        mime="text/csv",
        key="csv_dl"
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("#### 📖 Column Reference")

    col_ref = {
        "filename":      "Must match uploaded image filename exactly (case-sensitive)",
        "business_name": "Injected into Artist EXIF field",
        "service":       "Used in filename generation only",
        "location":      "Used in filename generation only",
        "lat":           "Decimal degrees, e.g. 24.8607 (use negative for S)",
        "lng":           "Decimal degrees, e.g. 67.0011 (use negative for W)",
        "keywords":      "Comma-separated, injected into XPKeywords + UserComment",
        "description":   "Injected into ImageDescription EXIF field",
        "copyright":     "Injected into Copyright EXIF field",
        "date_taken":    "Format: YYYY-MM-DD",
    }
    for col_n, col_d in col_ref.items():
        c1, c2 = st.columns([1, 3])
        c1.markdown(f'<span class="tag-pill">{col_n}</span>', unsafe_allow_html=True)
        c2.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.72rem;color:#94a3b8;padding-top:0.4rem">{col_d}</div>', unsafe_allow_html=True)
