# 📍 GBP Image Optimizer

A professional Streamlit tool for injecting GPS coordinates, keywords, descriptions, and business metadata into images — built for Google Business Profile SEO workflows.

---

## Features

- ✅ **Single image mode** — quick inject & download
- ✅ **Batch mode** — CSV + bulk images → ZIP download
- ✅ **Profile saving** — save GBP profiles (business, coords, keywords) for reuse
- ✅ **Full metadata strip** — clean slate before injection
- ✅ **SEO filename rename** — `business-service-location-date-01.jpg`
- ✅ **Metadata viewer** — verify injected EXIF on any image
- ✅ **CSV template** — pre-filled downloadable template
- ✅ **All formats** — JPG, PNG, WEBP, TIFF, BMP

## Metadata Injected

| Field | EXIF Location |
|-------|--------------|
| GPS Coordinates | GPSLatitude / GPSLongitude |
| Description | ImageDescription |
| Business Name | Artist |
| Copyright | Copyright |
| Keywords | XPKeywords + UserComment |
| Date Taken | DateTime + DateTimeOriginal |

---

## Local Setup

```bash
# 1. Clone or copy files to a folder
cd gbp_image_tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run locally
streamlit run app.py
```

App will open at `http://localhost:8501`

---

## Streamlit Cloud Deployment

1. Push this folder to a **GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repo, branch, and set `app.py` as the main file
5. Click **Deploy**

> ⚠️ Note: GBP profiles are saved to `gbp_profiles.json` locally.  
> On Streamlit Cloud, profiles reset on each deployment.  
> For persistent profiles on cloud, replace JSON storage with `st.session_state` only or use a small database like SQLite or Supabase.

---

## CSV Format

| Column | Description |
|--------|-------------|
| filename | Must match uploaded image filename exactly |
| business_name | Business name for EXIF Artist field |
| service | Used in output filename |
| location | Used in output filename |
| lat | Decimal latitude (e.g. 24.8607) |
| lng | Decimal longitude (e.g. 67.0011) |
| keywords | Comma-separated keywords |
| description | Image description / alt text |
| copyright | Copyright string |
| date_taken | Format: YYYY-MM-DD |

---

## Output Filename Pattern

```
{business-name}-{service}-{location}-{YYYY-MM-DD}-{index}.{ext}

Example:
abc-plumbing-drain-repair-karachi-2025-01-15-01.jpg
```

---

## Roadmap / Future Features

- [ ] Google Maps embed for coordinate picking
- [ ] HEIC format support (requires pillow-heif)
- [ ] XMP metadata support
- [ ] Multi-profile batch (different profile per image)
- [ ] Cloud profile storage (Supabase)
- [ ] Metadata comparison (before vs after side-by-side)
