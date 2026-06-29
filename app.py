import streamlit as st
import pickle
import pandas as pd
import random
from src.remove_ import remove
from src.recommender import RecommenderEngine

st.set_page_config(page_title="PhoneForge | AI Mobile Finder", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

if "page" not in st.session_state:
    st.session_state.page = "landing"

@st.cache_resource(show_spinner="Initializing PhoneForge AI Engine...")
def load_data():
    df = pickle.load(file=open(file=r"src/model/dataframe.pkl", mode="rb"))
    similarity = pickle.load(file=open(file=r"src/model/similarity.pkl", mode="rb"))
    engine = RecommenderEngine(df, similarity)
    return df, similarity, engine

df, similarity, engine = load_data()

# ─── LIGHT THEME CSS ─────────────────────────────────────────────────────────
CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap");

:root {
    --purple:      #7c3aed;
    --orange:      #f97316;
    --pink:        #ec4899;
    --teal:        #0d9488;
    --blue:        #3b82f6;
    --green:       #10b981;
    --bg:          #f5f3ff;
    --bg-card:     #ffffff;
    --bg-sidebar:  #faf5ff;
    --text:        #1e1b4b;
    --text-muted:  #6b7280;
    --border:      #e9d5ff;
    --grad-main:   linear-gradient(135deg, #7c3aed 0%, #ec4899 100%);
    --grad-warm:   linear-gradient(135deg, #f97316 0%, #ec4899 100%);
    --grad-cool:   linear-gradient(135deg, #3b82f6 0%, #0d9488 100%);
    --shadow-card: 0 4px 24px rgba(124,58,237,0.08), 0 1px 4px rgba(0,0,0,0.06);
    --shadow-hover: 0 20px 60px rgba(124,58,237,0.18), 0 4px 16px rgba(249,115,22,0.1);
}

/* ── BASE ── */
.stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: "Space Grotesk", sans-serif !important;
    overflow-x: hidden;
}
[data-testid="stAppViewContainer"],[data-testid="stHeader"],
[data-testid="stToolbar"],[data-testid="stMainViewContainer"] {
    background: transparent !important;
}

/* ═══════════════════════════════════
   ANIMATION 1 — Soft Pastel Aurora Blobs
   ═══════════════════════════════════ */
.aurora-bg {
    position: fixed; top:0; left:0;
    width:100vw; height:100vh;
    z-index:0; pointer-events:none; overflow:hidden;
}
.aurora-blob {
    position:absolute; border-radius:50%;
    filter:blur(90px); mix-blend-mode:multiply;
    animation: auroraMorph 14s ease-in-out infinite alternate;
}
.aurora-blob:nth-child(1){width:700px;height:700px;top:-150px;left:-150px;
    background:radial-gradient(circle,rgba(167,139,250,0.35),transparent 70%);animation-duration:13s;}
.aurora-blob:nth-child(2){width:550px;height:550px;top:20%;right:-100px;
    background:radial-gradient(circle,rgba(249,115,22,0.2),transparent 70%);animation-duration:10s;animation-delay:-4s;}
.aurora-blob:nth-child(3){width:450px;height:450px;bottom:-80px;left:35%;
    background:radial-gradient(circle,rgba(59,130,246,0.18),transparent 70%);animation-duration:17s;animation-delay:-8s;}
.aurora-blob:nth-child(4){width:380px;height:380px;top:30%;left:20%;
    background:radial-gradient(circle,rgba(236,72,153,0.15),transparent 70%);animation-duration:21s;animation-delay:-2s;}
@keyframes auroraMorph {
    0%   {transform:translate(0,0) scale(1);     opacity:0.7;}
    33%  {transform:translate(55px,-40px) scale(1.12); opacity:1;}
    66%  {transform:translate(-35px,55px) scale(0.9);  opacity:0.75;}
    100% {transform:translate(22px,22px) scale(1.04);  opacity:0.85;}
}

/* ═══════════════════════════════════
   ANIMATION 2 — Light Dot Grid Drift
   ═══════════════════════════════════ */
.dot-grid {
    position:fixed; inset:0; z-index:0; pointer-events:none;
    background-image:radial-gradient(circle, rgba(124,58,237,0.12) 1px, transparent 1px);
    background-size:36px 36px;
    animation: dotDrift 32s linear infinite;
}
@keyframes dotDrift {
    from {background-position:0 0;}
    to   {background-position:36px 36px;}
}

/* ═══════════════════════════════════
   ANIMATION 3 — Pastel Orb Particles
   ═══════════════════════════════════ */
.orb-field {position:fixed;inset:0;z-index:0;pointer-events:none;}
.orb {
    position:absolute; border-radius:50%;
    animation:orbRise linear infinite;
}
@keyframes orbRise {
    0%   {transform:translateY(0) translateX(0) scale(1);  opacity:0;}
    8%   {opacity:0.8;}
    50%  {transform:translateY(-50vh) translateX(15px) scale(1.2); opacity:0.6;}
    92%  {opacity:0.3;}
    100% {transform:translateY(-108vh) translateX(-10px) scale(0.7); opacity:0;}
}

/* ═══════════════════════════════════
   ANIMATION 4 — Shimmer Gradient Brand
   ═══════════════════════════════════ */
.brand-title {
    font-family:"Syne",sans-serif; font-weight:800;
    font-size:5.5rem; line-height:1; letter-spacing:-3px;
    background:linear-gradient(270deg,#7c3aed,#f97316,#ec4899,#3b82f6,#0d9488,#7c3aed);
    background-size:500% 500%;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:shimmerGrad 5s ease-in-out infinite;
}
@keyframes shimmerGrad {
    0%  {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100%{background-position:0% 50%;}
}

/* ═══════════════════════════════════
   ANIMATION 5 — Fade-up Tagline
   ═══════════════════════════════════ */
.brand-tagline {
    font-family:"JetBrains Mono",monospace; font-size:0.88rem;
    color:var(--purple); letter-spacing:4px; text-transform:uppercase;
    margin-bottom:1.5rem; opacity:0;
    animation:tagFadeUp 0.9s ease-out 0.2s forwards;
}
@keyframes tagFadeUp {
    from{opacity:0;transform:translateY(14px);}
    to  {opacity:0.9;transform:translateY(0);}
}

/* ═══════════════════════════════════
   ANIMATION 6 — Stagger-in Stat Chips
   ═══════════════════════════════════ */
.hero-stats {display:flex;gap:1.5rem;justify-content:center;flex-wrap:wrap;margin:2rem auto;}
.stat-chip {
    background:#ffffff; border:1.5px solid #e9d5ff;
    border-radius:50px; padding:10px 24px;
    display:inline-flex; align-items:center; gap:10px;
    font-size:0.9rem; color:var(--text);
    box-shadow:0 2px 12px rgba(124,58,237,0.1);
    transition:all 0.35s cubic-bezier(0.23,1,0.32,1);
    animation:chipRise 0.7s ease-out both;
}
@keyframes chipRise {
    from{opacity:0;transform:translateY(22px) scale(0.9);}
    to  {opacity:1;transform:translateY(0) scale(1);}
}
.stat-chip:hover {
    border-color:var(--purple); background:#faf5ff;
    box-shadow:0 8px 28px rgba(124,58,237,0.2);
    transform:translateY(-5px) scale(1.02);
}
.stat-value {font-family:"Syne",sans-serif;font-weight:700;font-size:1.1rem;color:var(--purple);}

/* ═══════════════════════════════════
   ANIMATION 7 — 3D Flip-in Feature Cards
   ═══════════════════════════════════ */
.feature-grid {display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem;margin:2.5rem auto;max-width:1100px;}
.feature-card {
    background:#ffffff; border:1.5px solid #f3e8ff;
    border-radius:22px; padding:2rem 1.5rem; text-align:center;
    position:relative; overflow:hidden;
    box-shadow:0 4px 20px rgba(124,58,237,0.07);
    transition:all 0.5s cubic-bezier(0.23,1,0.32,1);
    animation:flipIn3D 0.8s ease-out both;
}
@keyframes flipIn3D {
    from{opacity:0;transform:perspective(900px) rotateX(35deg) translateY(35px);}
    to  {opacity:1;transform:perspective(900px) rotateX(0deg) translateY(0);}
}
.feature-card::before {
    content:""; position:absolute; top:0; left:-110%; right:0; height:3px;
    background:var(--grad-main); transition:left 0.55s ease;
}
.feature-card:hover::before {left:0;}
.feature-card::after {
    content:""; position:absolute; inset:0; border-radius:22px;
    background:linear-gradient(135deg,rgba(124,58,237,0.04),rgba(249,115,22,0.04));
    opacity:0; transition:opacity 0.4s;
}
.feature-card:hover::after {opacity:1;}
.feature-card:hover {
    transform:translateY(-10px) scale(1.02);
    border-color:#d8b4fe;
    box-shadow:0 24px 60px rgba(124,58,237,0.14),0 0 0 1px rgba(124,58,237,0.08);
}

/* ═══════════════════════════════════
   ANIMATION 8 — Floating Icon Bounce
   ═══════════════════════════════════ */
.feature-icon {
    font-size:2.5rem; margin-bottom:1rem; display:block;
    filter:drop-shadow(0 4px 8px rgba(124,58,237,0.25));
    animation:iconFloat 2.5s ease-in-out infinite;
}
@keyframes iconFloat {
    0%,100%{transform:translateY(0) rotate(0deg);}
    50%    {transform:translateY(-8px) rotate(3deg);}
}
.feature-title{font-family:"Syne",sans-serif;font-weight:700;font-size:1rem;color:var(--text);margin-bottom:0.5rem;}
.feature-desc{font-size:0.8rem;color:var(--text-muted);line-height:1.5;}

/* ═══════════════════════════════════
   ANIMATION 9 — Button Ripple + Lift
   ═══════════════════════════════════ */
.stButton > button {
    background:linear-gradient(135deg,#7c3aed 0%,#ec4899 100%) !important;
    color:#fff !important; border:none !important; border-radius:12px !important;
    padding:0.9rem 2.5rem !important; font-family:"Syne",sans-serif !important;
    font-weight:700 !important; font-size:0.95rem !important;
    letter-spacing:1.5px !important; text-transform:uppercase !important;
    transition:all 0.3s cubic-bezier(0.23,1,0.32,1) !important;
    box-shadow:0 8px 28px rgba(124,58,237,0.35) !important;
    position:relative !important; overflow:hidden !important;
}
.stButton > button::before {
    content:""; position:absolute; top:50%; left:50%;
    width:0; height:0;
    background:rgba(255,255,255,0.25); border-radius:50%;
    transform:translate(-50%,-50%);
    transition:width 0.5s ease, height 0.5s ease, opacity 0.5s ease;
    opacity:0;
}
.stButton > button:hover::before {width:300px;height:300px;opacity:1;}
.stButton > button:hover {
    transform:translateY(-4px) scale(1.04) !important;
    box-shadow:0 20px 50px rgba(124,58,237,0.45) !important;
}
.stButton > button:active {
    transform:translateY(0) scale(0.97) !important;
    box-shadow:0 4px 12px rgba(124,58,237,0.3) !important;
}

/* ═══════════════════════════════════
   ANIMATION 10 — Phone Card Slide-up + Shadow Lift
   ═══════════════════════════════════ */
.phone-card {
    background:#ffffff; border:1.5px solid #f3e8ff;
    border-radius:20px; padding:20px; position:relative; overflow:hidden;
    box-shadow:var(--shadow-card);
    transition:all 0.45s cubic-bezier(0.23,1,0.32,1); margin-bottom:1rem;
    animation:cardSlideUp 0.55s ease-out both;
}
@keyframes cardSlideUp {
    from{opacity:0;transform:translateY(32px) scale(0.97);}
    to  {opacity:1;transform:translateY(0) scale(1);}
}
.phone-card::before {
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background:var(--grad-main); opacity:0; transition:opacity 0.4s;
}
.phone-card:hover::before {opacity:1;}
.phone-card:hover {
    transform:translateY(-10px) scale(1.02);
    border-color:#d8b4fe;
    box-shadow:var(--shadow-hover);
}

/* ═══════════════════════════════════
   ANIMATION 11 — Badge Pop-in
   ═══════════════════════════════════ */
.phone-card-badge {
    position:absolute; top:14px; right:14px; z-index:2;
    color:#fff; font-family:"JetBrains Mono",monospace;
    font-weight:700; font-size:0.6rem; padding:3px 10px;
    border-radius:20px; text-transform:uppercase; letter-spacing:1.2px;
    animation:badgePop 0.5s cubic-bezier(0.175,0.885,0.32,1.275) both;
}
@keyframes badgePop {
    from{transform:scale(0) rotate(-15deg);opacity:0;}
    to  {transform:scale(1) rotate(0deg);opacity:1;}
}

.phone-name {
    font-family:"Syne",sans-serif; font-weight:700;
    font-size:0.9rem; color:var(--text); margin:10px 0 6px; line-height:1.3;
}

/* ═══════════════════════════════════
   ANIMATION 12 — Price Gradient Pulse
   ═══════════════════════════════════ */
.phone-price {
    font-family:"Syne",sans-serif; font-weight:800; font-size:1.25rem;
    background:var(--grad-warm); -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:pricePulse 2.5s ease-in-out infinite alternate;
}
@keyframes pricePulse {
    from{filter:drop-shadow(0 1px 4px rgba(249,115,22,0.3));}
    to  {filter:drop-shadow(0 2px 12px rgba(236,72,153,0.5));}
}
.phone-rating{font-size:0.77rem;color:#f59e0b;margin-top:4px;font-weight:600;}

/* ═══════════════════════════════════
   ANIMATION 13 — Spec Tag Micro-hover
   ═══════════════════════════════════ */
.spec-row{display:flex;flex-wrap:wrap;gap:5px;margin:10px 0;}
.spec-tag {
    background:#f5f3ff; border:1.5px solid #ddd6fe;
    color:var(--purple); font-family:"JetBrains Mono",monospace;
    font-size:0.63rem; padding:3px 8px; border-radius:6px; white-space:nowrap;
    transition:all 0.22s ease; cursor:default;
}
.spec-tag:hover {
    background:#ede9fe; border-color:var(--purple);
    transform:translateY(-2px) scale(1.06);
    box-shadow:0 4px 12px rgba(124,58,237,0.18);
}

/* ═══════════════════════════════════
   ANIMATION 14 — Section Title Wipe Underline
   ═══════════════════════════════════ */
.section-title {
    font-family:"Syne",sans-serif; font-weight:800; font-size:1.8rem;
    background:var(--grad-main);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    position:relative; display:inline-block; margin-bottom:1.5rem;
}
.section-title::after {
    content:""; position:absolute; bottom:-4px; left:0;
    width:100%; height:3px;
    background:var(--grad-main); border-radius:2px;
    animation:wipeIn 0.9s cubic-bezier(0.23,1,0.32,1) forwards;
    transform-origin:left;
}
@keyframes wipeIn{from{transform:scaleX(0);}to{transform:scaleX(1);}}

/* ═══════════════════════════════════
   ANIMATION 15 — Sidebar Rainbow Border
   ═══════════════════════════════════ */
[data-testid="stSidebar"] {
    background:var(--bg-sidebar) !important;
    border-right:1.5px solid #e9d5ff !important;
    box-shadow:4px 0 24px rgba(124,58,237,0.06) !important;
}
[data-testid="stSidebar"]::before {
    content:""; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,#7c3aed,#ec4899,#f97316,#0d9488,#3b82f6,#7c3aed);
    background-size:400% 100%;
    animation:rainbowSlide 5s linear infinite;
}
@keyframes rainbowSlide {
    from{background-position:0% 0%;}
    to  {background-position:400% 0%;}
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color:var(--purple) !important; font-family:"Syne",sans-serif !important;
    font-size:0.82rem !important; font-weight:700 !important;
    text-transform:uppercase; letter-spacing:2px;
    -webkit-text-fill-color:var(--purple) !important;
}

/* ═══════════════════════════════════
   ANIMATION 16 — Page Header Slide-down + Glow
   ═══════════════════════════════════ */
.page-header {
    display:flex; align-items:center; gap:1rem; margin-bottom:2rem;
    padding-bottom:1.5rem; border-bottom:2px solid #f3e8ff;
    animation:headerDown 0.5s ease-out both;
}
@keyframes headerDown{from{opacity:0;transform:translateY(-22px);}to{opacity:1;transform:translateY(0);}}
.page-header-icon {
    width:50px; height:50px; background:var(--grad-main);
    border-radius:14px; display:flex; align-items:center; justify-content:center;
    font-size:1.5rem; flex-shrink:0;
    animation:iconGlow 3s ease-in-out infinite;
    box-shadow:0 8px 24px rgba(124,58,237,0.35);
}
@keyframes iconGlow {
    0%,100%{box-shadow:0 8px 24px rgba(124,58,237,0.35);}
    50%    {box-shadow:0 8px 32px rgba(236,72,153,0.5),0 0 40px rgba(124,58,237,0.15);}
}
.page-title-main {
    font-family:"Syne",sans-serif; font-weight:800; font-size:2rem;
    background:linear-gradient(90deg,#7c3aed,#f97316,#0d9488);
    background-size:300% 100%; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:shimmerGrad 3.5s ease-in-out infinite; line-height:1.1;
}
.page-subtitle{font-size:0.82rem;color:var(--text-muted);font-family:"JetBrains Mono",monospace;}

/* ═══════════════════════════════════
   ANIMATION 17 — Animated Score Bars
   ═══════════════════════════════════ */
.score-bar-track {
    background:#f3e8ff; border-radius:4px;
    height:6px; margin-bottom:6px; overflow:hidden;
}
.score-bar-fill {
    height:6px; border-radius:4px;
    animation:barGrow 1.1s cubic-bezier(0.23,1,0.32,1) both;
    transform-origin:left;
}
@keyframes barGrow {
    from{transform:scaleX(0);opacity:0;}
    to  {transform:scaleX(1);opacity:1;}
}

/* ═══════════════════════════════════
   ANIMATION 18 — Weight Cards Pop
   ═══════════════════════════════════ */
.weight-card {
    background:#ffffff; border-radius:14px; padding:16px 12px; text-align:center; margin-bottom:1rem;
    box-shadow:0 2px 12px rgba(124,58,237,0.08);
    transition:transform 0.3s,box-shadow 0.3s;
    animation:wPop 0.55s cubic-bezier(0.175,0.885,0.32,1.275) both;
}
@keyframes wPop{from{transform:scale(0.65);opacity:0;}to{transform:scale(1);opacity:1;}}
.weight-card:hover{transform:scale(1.06);box-shadow:0 8px 28px rgba(124,58,237,0.16);}

/* ═══════════════════════════════════
   ANIMATION 19 — Filter Badges Slide-in
   ═══════════════════════════════════ */
.filter-badge {
    display:inline-block; background:#faf5ff;
    border:1.5px solid #d8b4fe; color:var(--purple);
    font-family:"JetBrains Mono",monospace; font-size:0.72rem;
    padding:3px 12px; border-radius:20px; margin:3px;
    animation:badgeSlide 0.35s ease-out both;
}
@keyframes badgeSlide{from{opacity:0;transform:translateX(-12px);}to{opacity:1;transform:translateX(0);}}

/* ═══════════════════════════════════
   ANIMATION 20 — Mode Badge Pulse
   ═══════════════════════════════════ */
.mode-badge {
    background:linear-gradient(135deg,rgba(124,58,237,0.1),rgba(236,72,153,0.1));
    border:1.5px solid #ddd6fe; border-radius:12px;
    padding:12px 16px; margin-bottom:1rem; font-size:0.75rem;
    color:var(--purple); font-family:"JetBrains Mono",monospace; text-align:center;
    animation:modePulse 2.5s ease-in-out infinite;
}
@keyframes modePulse{0%,100%{box-shadow:none;}50%{box-shadow:0 0 18px rgba(124,58,237,0.2);}}

/* ═══════════════════════════════════
   ANIMATION 21 — Notification Slide-in
   ═══════════════════════════════════ */
[data-testid="stNotification"] {
    background:#faf5ff !important;
    border:1.5px solid #d8b4fe !important;
    border-radius:12px !important;
    animation:notifySlide 0.4s ease-out both !important;
}
@keyframes notifySlide{from{opacity:0;transform:translateX(-16px);}to{opacity:1;transform:translateX(0);}}
[data-testid="stNotification"] p{color:var(--text) !important;}

/* ─── FORM CONTROLS ─── */
.stSelectbox > div > div > div,
div[data-testid="stSelectboxSelectControl"] {
    background:#ffffff !important; border:1.5px solid #e9d5ff !important;
    color:var(--text) !important; border-radius:10px !important;
    transition:all 0.25s ease !important;
    box-shadow:0 1px 4px rgba(124,58,237,0.06) !important;
}
.stSelectbox > div > div > div:hover,
div[data-testid="stSelectboxSelectControl"]:hover {
    border-color:#a78bfa !important; box-shadow:0 0 12px rgba(124,58,237,0.12) !important;
}
div[data-baseweb="select"] span{color:var(--text) !important;}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"] {
    background:#ffffff !important; border:1.5px solid #e9d5ff !important;
    border-radius:12px !important; box-shadow:0 8px 32px rgba(124,58,237,0.12) !important;
}
[data-baseweb="menu"] li,[role="option"]{color:var(--text) !important;}
[data-baseweb="menu"] li:hover,[role="option"]:hover {
    background:#faf5ff !important; color:var(--purple) !important;
}
[role="option"][aria-selected="true"],[data-baseweb="menu"] li[aria-selected="true"] {
    background:#ede9fe !important; color:var(--purple) !important; font-weight:700 !important;
}
.stTextInput > div > div > input {
    background:#ffffff !important; border:1.5px solid #e9d5ff !important;
    color:var(--text) !important; border-radius:10px !important;
    transition:all 0.3s ease !important;
    box-shadow:0 1px 4px rgba(124,58,237,0.06) !important;
}
.stTextInput > div > div > input:focus {
    border-color:var(--purple) !important;
    box-shadow:0 0 0 3px rgba(124,58,237,0.15) !important;
}
.stSelectbox label,.stSlider label,.stTextInput label,.stRadio label,.stMultiSelect label {
    color:var(--purple) !important; font-weight:700 !important;
    font-size:0.78rem !important; text-transform:uppercase !important; letter-spacing:1px !important;
}
[data-testid="stSlider"] [role="slider"] {
    background:var(--purple) !important; border:2px solid var(--purple) !important;
    box-shadow:0 0 10px rgba(124,58,237,0.4) !important; transition:box-shadow 0.3s !important;
}
[data-testid="stSlider"] [role="slider"]:hover{box-shadow:0 0 20px rgba(124,58,237,0.7) !important;}
[data-testid="stRadio"] label{color:var(--text) !important;text-transform:none !important;letter-spacing:0 !important;font-size:0.9rem !important;}
[data-testid="stCheckbox"] label{color:var(--text) !important;text-transform:none !important;letter-spacing:0 !important;}
[data-testid="stMetricValue"]{color:var(--purple) !important;font-family:"Syne",sans-serif !important;font-weight:800 !important;}
[data-testid="stMetricLabel"] p{color:var(--text-muted) !important;font-size:0.75rem !important;text-transform:uppercase !important;letter-spacing:1px !important;}
[data-testid="stMetricValue"] ~ div {color:var(--text-muted) !important;}
[data-baseweb="tag"]{background:#ede9fe !important;border:1.5px solid #c4b5fd !important;color:var(--purple) !important;border-radius:6px !important;}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:#f5f3ff;}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,#7c3aed,#ec4899);border-radius:10px;}
.stApp p,.stApp span {color:var(--text);}
.stApp small{color:var(--text-muted) !important;}
.neon-divider{height:1px;background:linear-gradient(90deg,transparent,#c4b5fd,#f9a8d4,transparent);margin:1.5rem 0;border:none;}
[data-testid="stDeployButton"],.stAppDeployButton,
[data-testid="stToolbar"],[data-testid="stToolbarActions"],
footer,[data-testid="stFooter"]{display:none !important;visibility:hidden !important;}
h1 a,h2 a,h3 a,[data-testid="stHeadingWithActionElements"] a,
.stHeadingWithActionElements a{display:none !important;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ─── ANIMATED LIGHT BACKGROUND ────────────────────────────────────────────────
def render_background():
    random.seed(42)
    colors = ["#7c3aed","#ec4899","#f97316","#3b82f6","#0d9488","#a78bfa"]
    orbs = ""
    for i in range(25):
        c = random.choice(colors)
        left  = random.uniform(0, 100)
        sz    = random.uniform(5, 12)
        dur   = random.uniform(18, 55)
        delay = random.uniform(-55, 0)
        opa   = round(random.uniform(0.15, 0.4), 2)
        orbs += (
            f'<div class="orb" style="left:{left:.1f}%;bottom:-80px;'
            f'width:{sz:.1f}px;height:{sz:.1f}px;'
            f'background:{c};opacity:{opa};'
            f'animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s;"></div>'
        )
    html = (
        '<div class="aurora-bg">'
        + '<div class="aurora-blob"></div>' * 4
        + '</div>'
        + '<div class="dot-grid"></div>'
        + f'<div class="orb-field">{orbs}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

render_background()


# ─── DISPLAY PHONES ──────────────────────────────────────────────────────────
def display_mobiles(recommended_df, title="Recommended Phones", persona_idx=None, active_specs=None):
    import math, urllib.parse
    if recommended_df.empty:
        st.warning("No phones found. Try widening your filters.")
        return
    st.markdown(f'<div><div class="section-title">{title}</div></div>', unsafe_allow_html=True)

    def safe_num(val, mn=0, mx=99999):
        try:
            v = float(val)
            return v if not (math.isnan(v) or math.isinf(v)) and mn <= v <= mx else 0
        except: return 0

    def fmt(v): return str(int(v)) if v == int(v) else str(round(v, 1))

    def gstr(row, col):
        val = row.get(col, "")
        s = str(val).strip()
        return s if s not in ("nan", "None", "") else ""

    PSMAP = {
        1:["processor","ram","battery","refresh_rate","fast_charge","screen"],
        2:["ram","battery","storage","processor","screen","price"],
        3:["camera","f_camera","ois","battery","storage","ram","display"],
        4:["ram","battery","storage","processor","screen","price"],
        5:["display","stereo","screen","battery","fast_charge","ram"],
        6:["battery","fast_charge","processor","storage","screen","ram"],
        7:["f_camera","camera","storage","ram","battery","fast_charge"],
        8:["price","ram","battery","storage","camera","screen"],
        9:["battery","storage","screen","price","ram","camera"],
        10:["battery","build","screen","5g","processor","storage"],
        11:["processor","ram","refresh_rate","fast_charge","screen","camera","battery"],
        12:["build","screen","storage","ram","display","battery"],
    }
    spec_keys = active_specs if active_specs else PSMAP.get(persona_idx, ["ram","storage","battery","camera"])

    def build_tags(row):
        tags = []
        for k in spec_keys:
            if k == "ram":
                v = safe_num(row.get("ram_gb"),1,24) or safe_num(row.get("ram"),1,24)
                if v: tags.append(f"🧠 {fmt(v)}GB")
            elif k == "storage":
                v = safe_num(row.get("storage_gb"),1,1024) or safe_num(row.get("storage"),1,1024)
                if v: tags.append(f"💾 {fmt(v)}GB")
            elif k == "battery":
                v = safe_num(row.get("battery_mah"),1000,10000) or safe_num(row.get("battery"),1000,10000)
                if v: tags.append(f"🔋 {fmt(v)}mAh")
            elif k == "camera":
                v = safe_num(row.get("rear_camera_mp"),1,200) or safe_num(row.get("camera"),1,200)
                if v: tags.append(f"📷 {fmt(v)}MP")
            elif k == "f_camera":
                v = safe_num(row.get("front_camera_mp"),1,100)
                if v: tags.append(f"🤳 {fmt(v)}MP")
            elif k == "ois" and gstr(row,"ois").lower() == "yes":
                tags.append("✅ OIS")
            elif k == "processor":
                v = gstr(row,"processor")
                if v: tags.append(f"⚡ {v[:18]}")
            elif k == "refresh_rate":
                v = safe_num(row.get("refresh_rate"),60,240)
                if v: tags.append(f"🖥️ {fmt(v)}Hz")
            elif k == "display":
                v = gstr(row,"display_type")
                if v: tags.append(f"🖥️ {v}")
                elif "amoled" in str(row.get("corpus","")).lower(): tags.append("🖥️ AMOLED")
            elif k == "stereo":
                if gstr(row,"stereo_speakers").lower()=="yes" or "stereo" in str(row.get("corpus","")).lower():
                    tags.append("🔊 Stereo")
            elif k == "screen":
                v = safe_num(row.get("screen_size"),4,8) or safe_num(row.get("screen"),4,8)
                if v: tags.append(f'📐 {fmt(v)}"')
            elif k == "fast_charge":
                v = safe_num(row.get("fast_charging_watt"),5,240)
                if v: tags.append(f"⚡ {fmt(v)}W")
                elif "fast charg" in str(row.get("corpus","")).lower(): tags.append("⚡ Fast")
            elif k == "build":
                if "gorilla" in str(row.get("corpus","")).lower(): tags.append("🛡️ Gorilla")
            elif k == "5g":
                v = gstr(row,"5g")
                if v in ("Yes","True","1","yes") or "5g" in str(row.get("corpus","")).lower():
                    tags.append("📶 5G")
            elif k == "price":
                v = safe_num(row.get("price_numeric"),1000,500000)
                if v: tags.append(f"💰 ₹{fmt(v)}")
        return tags[:5]

    BADGES = [
        ("TOP PICK",     "linear-gradient(135deg,#7c3aed,#ec4899)"),
        ("TRENDING",     "linear-gradient(135deg,#f97316,#ec4899)"),
        ("BEST VALUE",   "linear-gradient(135deg,#0d9488,#3b82f6)"),
        ("EDITORS PICK", "linear-gradient(135deg,#ec4899,#f97316)"),
        ("HOT",          "linear-gradient(135deg,#3b82f6,#7c3aed)"),
    ]

    for i in range(0, len(recommended_df), 4):
        cols = st.columns(4)
        chunk = recommended_df.iloc[i:i+4]
        for idx, (index, row) in enumerate(chunk.iterrows()):
            with cols[idx]:
                tags = build_tags(row)
                pnum = safe_num(row.get("price_numeric"), 1)
                pdis = f"₹{int(pnum):,}" if pnum > 0 else str(row.get("price","N/A"))
                if "₹" not in pdis: pdis = f"₹{pdis}"
                try: rdis = f"⭐ {float(row.get('ratings',0)):.1f} / 5"
                except: rdis = f"⭐ {row.get('ratings',0)}"
                img_url = f"https://tse2.mm.bing.net/th?q={urllib.parse.quote_plus(row['name']+' smartphone')}"
                bl, bbg = BADGES[(i + idx) % len(BADGES)]
                tags_html = "".join(f'<span class="spec-tag">{t}</span>' for t in tags) or '<span class="spec-tag">📱 Phone</span>'
                delay_s = f"{idx * 0.1:.1f}s"
                st.markdown(f"""
<div class="phone-card" style="animation-delay:{delay_s}">
  <div class="phone-card-badge" style="background:{bbg};animation-delay:{delay_s}">{bl}</div>
  <img src="{img_url}" style="width:100%;height:175px;object-fit:contain;border-radius:10px;filter:drop-shadow(0 4px 16px rgba(0,0,0,0.12));">
  <div class="phone-name">{row["name"]}</div>
  <div class="spec-row">{tags_html}</div>
  <div class="phone-price">{pdis}</div>
  <div class="phone-rating">{rdis}</div>
</div>
""", unsafe_allow_html=True)


# ─── LANDING PAGE ─────────────────────────────────────────────────────────────
def render_landing_page():
    st.markdown("""
<div style="position:relative;z-index:10;text-align:center;padding:4rem 2rem 2rem;">
  <div class="brand-tagline">⚡ AI-Powered &nbsp;·&nbsp; Real-Time &nbsp;·&nbsp; Personalized</div>
  <div class="brand-title">PhoneForge</div>
  <div style="font-size:1.35rem;color:#6b7280;margin-top:1.2rem;max-width:640px;
              margin-left:auto;margin-right:auto;line-height:1.65;animation:tagFadeUp 1s ease-out 0.5s both;">
    Stop scrolling. Start finding. Let AI forge the perfect smartphone for your unique lifestyle.
  </div>
</div>
<div class="hero-stats">
  <div class="stat-chip" style="animation-delay:0.15s">
    <span style="font-size:1.2rem">📱</span><span><span class="stat-value">1000+</span> Phones</span>
  </div>
  <div class="stat-chip" style="animation-delay:0.28s">
    <span style="font-size:1.2rem">🧠</span><span><span class="stat-value">4</span> AI Modes</span>
  </div>
  <div class="stat-chip" style="animation-delay:0.41s">
    <span style="font-size:1.2rem">⚡</span><span><span class="stat-value">Real-Time</span> Results</span>
  </div>
  <div class="stat-chip" style="animation-delay:0.54s">
    <span style="font-size:1.2rem">🎯</span><span><span class="stat-value">12</span> Personas</span>
  </div>
</div>
<div class="feature-grid">
  <div class="feature-card" style="animation-delay:0.1s">
    <span class="feature-icon">🎯</span>
    <div class="feature-title">Rule-Based Filter</div>
    <div class="feature-desc">Fine-tune by specs, budget, brand &amp; network for precision results</div>
  </div>
  <div class="feature-card" style="animation-delay:0.25s">
    <span class="feature-icon">🧠</span>
    <div class="feature-title">Content-Based AI</div>
    <div class="feature-desc">Describe your lifestyle — our AI matches you perfectly</div>
  </div>
  <div class="feature-card" style="animation-delay:0.4s">
    <span class="feature-icon">⚖️</span>
    <div class="feature-title">Weighted Scoring</div>
    <div class="feature-desc">Dial in camera, battery, RAM priorities your way</div>
  </div>
  <div class="feature-card" style="animation-delay:0.55s">
    <span class="feature-icon">🔍</span>
    <div class="feature-title">KNN Similarity</div>
    <div class="feature-desc">Pick a phone you love and find its closest AI siblings</div>
  </div>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2:
        if st.button("⚡  Launch PhoneForge", use_container_width=True):
            st.session_state.page = "app"
            st.rerun()


# ─── RECOMMENDER PAGE ─────────────────────────────────────────────────────────
def render_recommender_page():
    st.sidebar.markdown("""
<div style="text-align:center;padding:1.5rem 0 1rem;">
  <div style="font-family:Syne,sans-serif;font-weight:800;font-size:1.4rem;
              background:linear-gradient(135deg,#7c3aed,#ec4899);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
    ⚡ PhoneForge
  </div>
  <div style="font-size:0.68rem;color:#9ca3af;font-family:JetBrains Mono,monospace;letter-spacing:2px;margin-top:4px;">
    AI ENGINE v2.0
  </div>
</div>
<hr class="neon-divider" style="margin:0 0 1.2rem;">
""", unsafe_allow_html=True)

    mode = st.sidebar.selectbox("🔧 Recommendation Mode",
        ["Rule-Based", "Content-Based", "Weighted Scoring", "KNN"])
    st.sidebar.markdown(f'<div class="mode-badge">MODE: {mode.upper()}</div>', unsafe_allow_html=True)

    ct, ch = st.columns([5, 1])
    with ct:
        st.markdown("""
<div class="page-header">
  <div class="page-header-icon">⚡</div>
  <div>
    <div class="page-title-main">PhoneForge AI</div>
    <div class="page-subtitle">// Intelligent Mobile Recommendations</div>
  </div>
</div>""", unsafe_allow_html=True)
    with ch:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "landing"; st.rerun()

    # ── RULE-BASED ─────────────────────────────────────────────────────────
    if mode == "Rule-Based":
        st.sidebar.markdown("### ⚙️ Filters")
        ftype = st.sidebar.radio("Filter Type", ["Use Case / Persona", "Custom Filters"])
        if ftype == "Use Case / Persona":
            personas = {
                1:"🎮 Gaming Beast", 2:"📱 Daily Driver", 3:"📸 Photography Pro",
                4:"💼 Business Power", 5:"🎬 Entertainment Hub", 6:"🔋 Battery Champion",
                7:"📶 Content Creator", 8:"🎓 Student Budget", 9:"👴 Senior Friendly",
                10:"📡 Travel Ready", 11:"🧑‍💻 Tech Enthusiast", 12:"🎨 Design Lover"
            }
            opts = list(personas.values())
            sel = st.sidebar.selectbox("Select Your Persona", opts)
            pidx = list(personas.keys())[opts.index(sel)]
            st.sidebar.markdown("### 📊 Sort By")
            psort = st.sidebar.selectbox("Sort By", ["Relevance","Price: Low to High","Price: High to Low","Rating: High to Low","Popularity (Rating Count)"])
            if st.button("🔍 Find Best Phones"):
                with st.spinner("Forging your recommendations..."):
                    res = engine.persona_based(pidx, sort_option=psort)
                display_mobiles(res, f"Top Picks · {sel}", persona_idx=pidx)
        else:
            st.sidebar.markdown("### 💰 Price Range")
            bmin, bmax = st.sidebar.slider("Budget (₹)", 5000, 200000, (10000, 50000), 5000)
            st.sidebar.markdown("### 🔩 Core Specs")
            ram = st.sidebar.selectbox("Min RAM (GB)", [0,2,4,6,8,12,16])
            storage = st.sidebar.selectbox("Min Storage (GB)", [0,32,64,128,256,512])
            st.sidebar.markdown("### 📷 Camera")
            camera = st.sidebar.selectbox("Min Rear Cam (MP)", [0,12,32,48,64,108,200])
            fcam = st.sidebar.selectbox("Min Front Cam (MP)", [0,8,16,32,50])
            st.sidebar.markdown("### ⚡ Performance")
            battery = st.sidebar.selectbox("Min Battery (mAh)", [0,3000,4000,4500,5000,6000,7000])
            fast = st.sidebar.checkbox("Fast Charging Required")
            rr = st.sidebar.selectbox("Min Refresh Rate (Hz)", [0,60,90,120,144,165])
            st.sidebar.markdown("### 📡 Connectivity")
            net = st.sidebar.radio("Network", ["Any","5G Only","4G Only"])
            st.sidebar.markdown("### 📱 Brand")
            brands_all = ["Samsung","Apple","OnePlus","Xiaomi","Redmi","POCO","Realme","OPPO","Vivo","iQOO","Motorola","Infinix","Tecno","Nokia","Google","Nothing"]
            sel_brands = st.sidebar.multiselect("Brands (any if empty)", brands_all, default=[])
            st.sidebar.markdown("### ⭐ Rating")
            minr = st.sidebar.selectbox("Min Rating", ["Any","3.0+ Stars","3.5+ Stars","4.0+ Stars","4.5+ Stars"], index=0)
            st.sidebar.markdown("### 🖥️ Display")
            disp_types = st.sidebar.multiselect("Display Types (any if empty)", ["AMOLED","Super AMOLED","OLED","LCD","IPS"], default=[])
            st.sidebar.markdown("### 📋 Sort")
            sort = st.sidebar.selectbox("Sort By", ["Relevance","Price: Low to High","Price: High to Low","Rating: High to Low","Popularity (Rating Count)"])
            c1, c2 = st.sidebar.columns(2)
            with c1: find = st.button("🔍 Find", use_container_width=True)
            with c2: rst  = st.button("🔄 Reset", use_container_width=True)
            if rst: st.session_state.clear(); st.rerun()
            if find:
                rv = 0.0
                if "4.5" in minr: rv=4.5
                elif "4.0" in minr: rv=4.0
                elif "3.5" in minr: rv=3.5
                elif "3.0" in minr: rv=3.0
                afl = [f"₹{bmin:,}–₹{bmax:,}"]
                if sel_brands: afl.append(", ".join(sel_brands[:2]))
                if ram>0: afl.append(f"RAM≥{ram}GB")
                if storage>0: afl.append(f"Stor≥{storage}GB")
                if battery>0: afl.append(f"Bat≥{battery}mAh")
                if camera>0: afl.append(f"Cam≥{camera}MP")
                if fast: afl.append("FastCharge")
                if net!="Any": afl.append(net)
                bh = "".join(f'<span class="filter-badge">{f}</span>' for f in afl)
                st.markdown(f'<div style="margin-bottom:1.5rem;"><div style="font-size:0.72rem;color:#9ca3af;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">Active Filters</div>{bh}</div><hr class="neon-divider">', unsafe_allow_html=True)
                fc = st.columns(4)
                with fc[0]: st.metric("Price", f"₹{bmin//1000}K–{bmax//1000}K")
                with fc[1]: st.metric("Brands", f"{len(sel_brands)} sel." if sel_brands else "Any")
                with fc[2]: st.metric("Rating", minr)
                with fc[3]: st.metric("Sort", sort.split(":")[0])
                with st.spinner("⚡ Forging recommendations..."):
                    res = engine.rule_based_enhanced(
                        min_budget=bmin, max_budget=bmax, min_ram=ram, min_storage=storage,
                        min_battery=battery, min_camera=camera, min_front_camera=fcam,
                        brands=sel_brands, network=net, display_types=disp_types,
                        fast_charging=fast, min_refresh_rate=rr, min_rating=rv, sort_option=sort)
                asp = []
                if ram>0: asp.append("ram")
                if storage>0: asp.append("storage")
                if camera>0: asp.append("camera")
                if fcam>0: asp.append("f_camera")
                if battery>0: asp.append("battery")
                if fast: asp.append("fast_charge")
                if rr>0: asp.append("refresh_rate")
                if disp_types: asp += ["display","screen"]
                if net=="5G Only": asp.append("5g")
                if not asp: asp = ["ram","storage","battery","camera"]
                if not res.empty:
                    st.info(f"✨ Found **{len(res)}** phones matching your criteria")
                    display_mobiles(res, f"Results · ₹{bmin//1000}K–₹{bmax//1000}K", active_specs=asp)
                else:
                    st.warning("No phones found. Try widening your filters.")

    # ── CONTENT-BASED ───────────────────────────────────────────────────────
    elif mode == "Content-Based":
        st.sidebar.markdown("### 💰 Budget")
        cbmin, cbmax = st.sidebar.slider("Price Range (₹)", 5000, 200000, (10000,50000), 5000)
        st.sidebar.markdown("### 🎯 Usage Type")
        umap = {"🎮 Gaming":"gaming","📸 Photography":"photography","🔋 Battery Life":"battery","🎬 Entertainment":"entertainment","📱 Normal Use":"normal"}
        ulabel = st.sidebar.selectbox("Primary Usage", list(umap.keys()))
        utype = umap[ulabel]
        st.sidebar.markdown("### 🎚️ Feature Priority")
        pp = st.sidebar.select_slider("⚡ Performance", ["low","medium","high"], value="medium")
        cp = st.sidebar.select_slider("📷 Camera",      ["low","medium","high"], value="medium")
        bp = st.sidebar.select_slider("🔋 Battery",     ["low","medium","high"], value="medium")
        dp = st.sidebar.select_slider("🖥️ Display",     ["low","medium","high"], value="medium")
        st.sidebar.markdown("### 📋 Sort")
        cbsort = st.sidebar.selectbox("Sort By", ["Relevance","Price: Low to High","Price: High to Low","Rating: High to Low","Popularity (Rating Count)"])
        if st.button("✨ Find My Perfect Phone"):
            with st.spinner("Running AI analysis..."):
                results, reasons = engine.preference_based(
                    min_budget=cbmin, max_budget=cbmax, usage_type=utype,
                    perf_pref=pp, camera_pref=cp, battery_pref=bp,
                    display_pref=dp, sort_option=cbsort)
            st.session_state.cb_results = (results, reasons)
        if "cb_results" in st.session_state:
            import math, urllib.parse
            results, reasons = st.session_state.cb_results
            if results.empty:
                st.warning("No phones found in that price range.")
            else:
                def ss(v):
                    try: f=float(v); return f if not math.isnan(f) else 0
                    except: return 0
                def sbar(sc, col, delay="0s"):
                    pct = int(sc * 10)
                    return f'<div class="score-bar-track"><div class="score-bar-fill" style="width:{pct}%;background:{col};animation-delay:{delay};"></div></div>'
                st.info(f"✨ Found **{len(results)}** matches")
                st.markdown('<div class="section-title">Your Perfect Matches</div>', unsafe_allow_html=True)
                for i in range(0, len(results), 4):
                    cols = st.columns(4)
                    chunk = results.iloc[i:i+4]
                    rchunk = reasons.iloc[i:i+4]
                    for idx, ((_, row), reason) in enumerate(zip(chunk.iterrows(), rchunk)):
                        with cols[idx]:
                            ps=ss(row.get("performance_score",0)); cs=ss(row.get("camera_score",0))
                            bs=ss(row.get("battery_score",0));     ds=ss(row.get("display_score",0))
                            pv=ss(row.get("price_numeric",0))
                            price_s = f"₹{int(pv):,}" if pv else row.get("price","N/A")
                            try: rd=f"⭐ {float(row.get('ratings',0)):.1f}"
                            except: rd=f"⭐ {row.get('ratings',0)}"
                            img = f"https://tse2.mm.bing.net/th?q={urllib.parse.quote_plus(row['name']+' smartphone')}"
                            d = f"{idx*0.1:.1f}s"
                            st.markdown(f"""
<div class="phone-card" style="animation-delay:{d}">
  <img src="{img}" style="width:100%;height:168px;object-fit:contain;border-radius:10px;filter:drop-shadow(0 4px 16px rgba(0,0,0,0.1));">
  <div class="phone-name">{row["name"]}</div>
  <div style="margin:10px 0 4px;">
    <div style="font-size:0.63rem;color:#9ca3af;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">AI Scores</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 10px;">
      <div><div style="font-size:0.6rem;color:#7c3aed;font-family:JetBrains Mono,monospace;">⚡ PERF</div>{sbar(ps,"#7c3aed",d)}</div>
      <div><div style="font-size:0.6rem;color:#0d9488;font-family:JetBrains Mono,monospace;">📷 CAM</div>{sbar(cs,"#0d9488",d)}</div>
      <div><div style="font-size:0.6rem;color:#f97316;font-family:JetBrains Mono,monospace;">🔋 BAT</div>{sbar(bs,"#f97316",d)}</div>
      <div><div style="font-size:0.6rem;color:#ec4899;font-family:JetBrains Mono,monospace;">🖥️ DISP</div>{sbar(ds,"#ec4899",d)}</div>
    </div>
  </div>
  <div class="phone-price" style="margin-top:10px;">{price_s}</div>
  <div class="phone-rating">{rd}</div>
</div>
""", unsafe_allow_html=True)

    # ── WEIGHTED SCORING ────────────────────────────────────────────────────
    elif mode == "Weighted Scoring":
        st.sidebar.markdown("### ⚖️ Feature Weights")
        st.sidebar.caption("Slide to **1.0** for top priority, **0.0** to ignore.")
        wb  = st.sidebar.slider("💰 Max Budget (₹)", 5000, 200000, 200000, 5000)
        wp  = st.sidebar.slider("⚡ Performance", 0.0, 1.0, 0.5)
        wr  = st.sidebar.slider("🧠 RAM",         0.0, 1.0, 0.5)
        ws  = st.sidebar.slider("💾 Storage",     0.0, 1.0, 0.5)
        wra = st.sidebar.slider("⭐ Rating",      0.0, 1.0, 0.5)
        wba = st.sidebar.slider("🔋 Battery",     0.0, 1.0, 0.5)
        wc  = st.sidebar.slider("📷 Camera",      0.0, 1.0, 0.5)
        weights = {"performance":wp,"ram":wr,"storage":ws,"rating":wra,"battery":wba,"camera":wc}
        st.sidebar.markdown("### 📋 Sort")
        wssort = st.sidebar.selectbox("Sort By", ["Relevance","Price: Low to High","Price: High to Low","Rating: High to Low","Popularity (Rating Count)"])
        st.markdown('<div class="section-title">Weight Configuration</div>', unsafe_allow_html=True)
        wdata = [("⚡","Performance",wp,"#7c3aed"),("🧠","RAM",wr,"#0d9488"),
                 ("💾","Storage",ws,"#f97316"),("⭐","Rating",wra,"#ec4899"),
                 ("🔋","Battery",wba,"#3b82f6"),("📷","Camera",wc,"#10b981")]
        wcols = st.columns(6)
        for i, (wc2, (icon, label, val, col)) in enumerate(zip(wcols, wdata)):
            with wc2:
                pct = int(val * 100)
                d = f"{i * 0.12:.2f}s"
                st.markdown(f"""
<div class="weight-card" style="border:2px solid {col}22;animation-delay:{d}">
  <div style="font-size:1.5rem;margin-bottom:6px;">{icon}</div>
  <div style="font-size:0.7rem;color:#9ca3af;font-family:JetBrains Mono,monospace;text-transform:uppercase;margin-bottom:8px;">{label}</div>
  <div style="font-family:Syne,sans-serif;font-weight:800;font-size:1.3rem;color:{col};">{pct}%</div>
  <div class="score-bar-track" style="margin-top:8px;">
    <div class="score-bar-fill" style="width:{pct}%;background:{col};animation-delay:{d};"></div>
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button("⚖️ Calculate Best Value Phones"):
            with st.spinner("Calculating optimal scores..."):
                res = engine.weighted_scoring(weights, max_budget=wb, sort_option=wssort)
            display_mobiles(res, f"Best Value · Under ₹{wb:,}")

    # ── KNN ────────────────────────────────────────────────────────────────
    elif mode == "KNN":
        st.markdown("""
<div style="margin-bottom:1.5rem;">
  <div class="section-title">Find Similar Phones</div>
  <p style="color:#6b7280;font-size:0.9rem;font-family:JetBrains Mono,monospace;">
    Select a reference phone — KNN finds the closest AI-matched alternatives
  </p>
</div>""", unsafe_allow_html=True)
        phones = df["name"].values
        sel = st.selectbox("📱 Reference Phone", phones, help="Choose a phone you like")
        c1, _ = st.columns([1, 3])
        with c1:
            if st.button("🔍 Find Similar", use_container_width=True):
                with st.spinner(f"Searching similar to {sel}..."):
                    res = engine.knn_recommend(sel)
                display_mobiles(res, f"Similar to · {sel}")


# ─── NAVIGATION ──────────────────────────────────────────────────────────────
if st.session_state.page == "landing":
    render_landing_page()
else:
    render_recommender_page()
