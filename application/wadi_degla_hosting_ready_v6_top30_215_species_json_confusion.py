import base64
import datetime
import io
import glob
import os
import traceback
import logging
from typing import Any, Dict, List, Tuple

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from PIL import Image
import joblib
import json


import torch
from torchvision import transforms
import torch.nn.functional as F

# ============================================================
# Wadi Degla Plant Identifier - Redesigned Dash Application
# Keeps your original model inference workflow, but upgrades UI.
# ============================================================

MODEL_PATH = "model_top_30_215.pkl"
INDEX_TO_CLASS_PATH = "idx_to_class_data.pkl"
PLANTS_INFO_DIR = "assets"  
PLACEHOLDER = "_"
CONFIDENCE_THRESHOLD = 5.0  # %
MAX_UPLOAD_SIZE_MB = 20
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
LOW_CONFIDENCE_THRESHOLD = 50.0
HIGH_CONFIDENCE_THRESHOLD = 80.0

IMAGE_TARGET_SIZE = (224, 224)
if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")

model = None
index_to_class = None
index_to_class_info = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
logger.info(f"Using device: {DEVICE}")

SPECIES_NAME_OVERRIDES = {
    "Salsola imbricata Forssk.": "Caroxylon imbricatum (Forssk.) Moq.",
}

# -------------------- Load model and metadata --------------------

try:
    model = joblib.load(MODEL_PATH)
    model.eval()
    model.to(DEVICE)
    print(f"PyTorch model '{MODEL_PATH}' loaded successfully on {DEVICE}.")

    index_to_class = joblib.load(INDEX_TO_CLASS_PATH)
    print(f"Class mapping '{INDEX_TO_CLASS_PATH}' loaded successfully. Classes: {len(index_to_class)}")

    try:
        dummy_input = torch.randn(1, 3, IMAGE_TARGET_SIZE[0], IMAGE_TARGET_SIZE[1]).to(DEVICE)
        with torch.no_grad():
            dummy_output = model(dummy_input)
        if dummy_output.shape[1] != len(index_to_class):
            print(
                f"WARNING: model output classes ({dummy_output.shape[1]}) do not match "
                f"index_to_class length ({len(index_to_class)})."
            )
    except Exception as e:
        print(f"Warning: could not verify output shape: {e}")

except Exception as e:
    print(f"Error loading model or class mapping: {e}")


SPECIES_POWO_PATH = os.path.join("assets", "species_powo_links.json")

try:
    with open(SPECIES_POWO_PATH, "r", encoding="utf-8") as f:
        species_powo_links = json.load(f)
except Exception as e:
    print(f"Failed to load species POWO links: {e}")
    species_powo_links = {}

# -------------------- Image transforms --------------------
test_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(IMAGE_TARGET_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# -------------------- Dash app --------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Wadi Degla Plant Identifier",
)
server = app.server

# Custom CSS injected directly. For production, you can move this to assets/style.css.
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root{
                --green-950:#063b2b;
                --green-900:#0b4b35;
                --green-800:#155d3e;
                --green-700:#2f6b2f;
                --green-600:#4f8a3a;
                --green-100:#edf6e9;
                --green-050:#f6fbf3;
                --sand-050:#fbf8f1;
                --sand-100:#f3ead7;
                --stone:#6d746d;
                --ink:#173126;
                --line:#e6e0d2;
                --shadow:0 16px 40px rgba(11, 75, 53, 0.10);
                --shadow-sm:0 8px 24px rgba(11, 75, 53, 0.08);
            }
            * { box-sizing: border-box; }
            html{ scroll-behavior:smooth; }
            #home, #identify, #species-guide, #covered-species-list, #about-project, #contact, #acknowledgement{ scroll-margin-top:96px; }
            body{
                margin:0;
                background:linear-gradient(180deg, #fbf8f1 0%, #f8faf5 45%, #ffffff 100%);
                color:var(--ink);
                font-family: Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
            }
            .app-shell{ padding:0; max-width:100%; }
            .top-nav{
                background:linear-gradient(90deg, var(--green-950), var(--green-900));
                color:white;
                min-height:72px;
                display:flex;
                align-items:center;
                justify-content:space-between;
                padding:0 7vw;
                position:sticky;
                top:0;
                z-index:10;
                box-shadow:0 4px 20px rgba(0,0,0,.12);
            }
            .brand{display:flex;align-items:center;gap:14px;flex-shrink:0;}
            .brand-mark{
                width:48px;height:48px;border-radius:16px;border:1px solid rgba(255,255,255,.35);
                display:grid;place-items:center;background:rgba(255,255,255,.10);font-size:25px;
            }
            .brand-title{font-family:Georgia, 'Times New Roman', serif;font-size:24px;font-weight:700;line-height:1;white-space:nowrap;}
            .brand-subtitle{font-size:12px;opacity:.82;margin-top:4px;}
            .nav-links{display:flex;align-items:center;gap:28px;font-size:14px;font-weight:650;}
            .nav-links a{opacity:.94;white-space:nowrap;color:white;text-decoration:none;}
            .nav-links a:hover{opacity:1;color:#fff8ec;}
            .nav-active{border-bottom:3px solid var(--sand-100);padding-bottom:8px;}
            .hero{
                position:relative;
                min-height:320px;
                padding:48px 7vw 28px 7vw;
                overflow:hidden;
                background:
                  radial-gradient(circle at 85% 20%, rgba(112,145,61,.20), transparent 28%),
                  linear-gradient(110deg, #fffaf0 0%, #fffdf8 42%, rgba(246,251,243,.55) 100%);
                border-bottom:1px solid rgba(230,224,210,.75);
            }
            .hero:before{
                content:"";
                position:absolute;inset:0;
                background-image:
                    linear-gradient(120deg, rgba(11,75,53,.045) 1px, transparent 1px),
                    linear-gradient(30deg, rgba(11,75,53,.035) 1px, transparent 1px);
                background-size:90px 90px, 120px 120px;
                mask-image:linear-gradient(90deg, #000 0%, transparent 65%);
            }
            .hero-content{position:relative;z-index:1;display:grid;grid-template-columns:minmax(610px,1.15fr) 1fr;align-items:center;gap:40px;}
            .hero h1{font-family:Georgia, 'Times New Roman', serif;color:var(--green-900);font-size:clamp(40px,3.45vw,52px);line-height:1.05;margin:0 0 16px;font-weight:800;letter-spacing:-1px;}
            .hero-title-line{display:block;white-space:nowrap;}
            .hero p{font-size:18px;line-height:1.55;max-width:610px;color:#35473d;margin:0 0 22px;}
            .hero-actions{display:flex;gap:14px;align-items:center;flex-wrap:wrap;}
            .primary-btn, .secondary-btn{
                border-radius:10px;padding:14px 22px;font-weight:800;border:1px solid transparent;display:inline-flex;gap:10px;align-items:center;
                text-decoration:none;cursor:pointer;
            }
            .primary-btn{background:var(--green-700);color:white;box-shadow:0 10px 22px rgba(47,107,47,.24);}
            .secondary-btn{background:rgba(255,255,255,.72);color:var(--green-800);border-color:#9caf8d;}
            .hero-help{font-size:13px!important;color:#6a7069!important;margin-top:12px!important;}
            .plant-visual{
                position:relative;height:300px;border-radius:0 0 0 90px;overflow:hidden;
                background:
                    linear-gradient(90deg, rgba(255,250,240,.15), rgba(255,250,240,.82)),
                    radial-gradient(circle at 70% 25%, rgba(255,255,255,.42), transparent 24%),
                    linear-gradient(135deg, #e8d9bd, #cda56f 54%, #8e785e 100%);
                box-shadow:var(--shadow-sm);
            }
            .plant-visual:before{
                display: none;
                content:"";position:absolute;right:-70px;bottom:-65px;width:460px;height:230px;border-radius:55% 45% 0 0;background:linear-gradient(135deg,#9b7b57,#e8d3ad);opacity:.75;
                transform:rotate(-8deg);
            }
            .plant-visual:after{
                content:"✦";position:absolute;left:15%;top:14%;font-size:190px;color:rgba(22,91,60,.18);text-shadow:90px 50px 0 rgba(22,91,60,.16), 210px 10px 0 rgba(22,91,60,.13);
            }
            .branch-line{position:absolute;inset:30px 20px 30px 40px;color:rgba(22,91,60,.55);font-size:130px;letter-spacing:24px;transform:rotate(-8deg);}
            .workspace{padding:0 7vw 28px 7vw;margin-top:-22px;position:relative;z-index:2;}
            .glass-card{
                background:rgba(255,255,255,.92);border:1px solid rgba(217,224,211,.9);border-radius:16px;box-shadow:var(--shadow);overflow:hidden;
            }
            .card-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 20px;border-bottom:1px solid var(--line);background:rgba(255,255,255,.72);}
            .title-wrap{display:flex;align-items:center;gap:12px;font-weight:850;font-size:20px;color:var(--green-900);}
            .step-badge{width:31px;height:31px;border-radius:50%;display:grid;place-items:center;background:var(--green-900);color:white;font-weight:900;box-shadow:0 4px 12px rgba(11,75,53,.2);}
            .card-body-custom{padding:16px 18px 18px;background:#fffefa;}
            .drop-zone{
                width:100%;padding:32px 20px;border:2px dashed #c8b99f;border-radius:13px;background:linear-gradient(180deg,#fffdfa,#fffaf0);text-align:center;cursor:pointer;transition:.2s ease;color:#304237;
            }
            .drop-zone:hover{border-color:var(--green-600);background:#fbfff8;}
            .upload-icon{font-size:32px;color:#587a56;margin-bottom:8px;}
            .preview-box{display:grid;grid-template-columns:230px 1fr;gap:16px;margin-top:14px;align-items:center;border:1px solid #ece7dc;border-radius:14px;padding:12px;background:white;}
            .preview-img{width:100%;height:142px;object-fit:cover;border-radius:11px;border:1px solid #e8e4d8;}
            .ready-pill{display:inline-flex;gap:6px;align-items:center;margin-top:10px;background:#e9f6df;color:#326b32;border:1px solid #c9e6bd;border-radius:999px;padding:5px 10px;font-size:12px;font-weight:800;}
            .empty-state{min-height:225px;display:grid;place-items:center;text-align:center;color:#7a8179;background:white;border-radius:12px;border:1px solid #eee9df;}
            .result-hero{display:grid;grid-template-columns:72px 1fr 126px;gap:18px;align-items:center;background:linear-gradient(90deg,#f5fbef,#eef7e8);border:1px solid #dfe9d8;border-radius:13px;padding:18px;}
            .species-icon{width:66px;height:66px;border-radius:50%;background:white;border:1px solid #d8e4d1;display:grid;place-items:center;color:var(--green-600);font-size:28px;}
            .small-label{text-transform:uppercase;letter-spacing:.07em;font-size:11px;font-weight:900;color:#5e7563;margin-bottom:5px;}
            .species-name{font-family:Georgia, 'Times New Roman', serif;color:var(--green-800);font-size:30px;font-weight:850;line-height:1.08;}
            .confidence-wrap{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;}
            .confidence-ring{width:104px;height:104px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--green-600) var(--score), #dbe7d4 0);}
            .confidence-inner{width:78px;height:78px;border-radius:50%;background:#fffefa;display:grid;place-items:center;text-align:center;font-weight:950;color:var(--green-900);font-size:22px;line-height:1;}
            .confidence-label{font-size:11px;color:#607163;font-weight:900;text-transform:uppercase;letter-spacing:.06em;}
            .info-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:13px;}
            .info-chip{border:1px solid #eee7db;border-radius:12px;background:#fff;padding:12px;display:flex;gap:10px;align-items:center;min-height:60px;}
            .info-chip i{color:var(--green-600);font-size:18px;}
            .info-chip strong{display:block;font-size:12px;color:#576858;}
            .info-chip span{font-size:12px;color:#2f3b32;}
            .description-box{margin-top:14px;background:white;border:1px solid #eee9df;border-radius:13px;padding:15px;line-height:1.65;color:#36443b;text-align:justify;}
            .support-section{margin-top:16px;}
            .mini-grid{display:grid;grid-template-columns:1.25fr 1.25fr 1fr;gap:16px;margin-top:16px;}
            .mini-card{background:white;border:1px solid rgba(217,224,211,.9);box-shadow:var(--shadow-sm);border-radius:14px;padding:16px;min-height:170px;}
            .mini-card h5{font-weight:900;color:var(--green-900);font-size:16px;margin:0 0 12px;}
            .side-stack{display:grid;grid-template-rows:auto auto;gap:16px;align-content:start;}
            .how-card{min-height:150px;}
            .model-limitations-card{min-height:unset;}
            .model-limitations-card .disclaimer-box{margin-top:0;margin-bottom:12px;}
            .similar-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;}
            .species-thumb{height:72px;border-radius:10px;background:linear-gradient(135deg,#7d9f63,#d8caa2);display:grid;place-items:center;color:white;font-size:24px;}
            .thumb-caption{font-size:11px;text-align:center;line-height:1.2;margin-top:6px;color:#334238;}
            .feature-list{list-style:none;margin:0;padding:0;display:grid;gap:8px;font-size:13px;color:#455349;}
            .feature-list li:before{content:"♧";color:var(--green-600);font-weight:900;margin-right:8px;}
            .map-box{height:118px;border-radius:12px;background:linear-gradient(120deg,#e7eee1 0%,#f8f5ec 42%,#dcebd9 100%);position:relative;overflow:hidden;border:1px solid #ece5d8;}
            .map-box:before{content:"";position:absolute;left:42%;top:-20%;width:50px;height:170%;background:#8cc6d8;transform:rotate(20deg);opacity:.75;border-radius:40px;}
            .pin{position:absolute;left:48%;top:42%;color:#d66f3b;font-size:26px;}
            .map-label{position:absolute;right:18px;top:34px;font-weight:900;color:var(--green-900);font-size:14px;}
            .steps{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;text-align:center;align-items:stretch;}
            .step-icon{width:58px;height:58px;border-radius:18px;background:#edf6e9;margin:0 auto 12px;display:grid;place-items:center;color:var(--green-600);font-size:26px;}
            .steps strong{font-size:16px;display:block;color:#273b2f;}
            .steps p{font-size:13px;color:#667067;margin:6px 0 0;line-height:1.35;}
            .metrics-band{display:grid;grid-template-columns:1.25fr repeat(5,1fr);gap:0;margin-top:16px;background:white;border:1px solid rgba(217,224,211,.9);box-shadow:var(--shadow-sm);border-radius:14px;overflow:hidden;}
            .metric-block{padding:18px 20px;border-left:1px solid #eee9df;display:flex;align-items:center;gap:12px;min-height:95px;}
            .metric-block:first-child{border-left:0;}
            .metric-icon{width:46px;height:46px;border-radius:50%;background:#f3f0e8;border:1px solid #e0d7c6;display:grid;place-items:center;color:var(--green-600);font-size:19px;}
            .metric-value{font-size:25px;font-weight:950;color:var(--green-900);line-height:1;}
            .metric-label{font-size:12px;color:#687169;margin-top:4px;line-height:1.25;}
            .footer{margin-top:34px;background:linear-gradient(90deg,var(--green-950),#0a4a34);color:white;padding:18px 7vw;text-align:center;display:block;}
            .footer-single{font-size:14px;font-weight:800;color:rgba(255,255,255,.90);white-space:nowrap;}
            .download-btn{border:1px solid #d5cbb9;background:#fffaf0;border-radius:8px;padding:7px 12px;font-size:12px;font-weight:800;color:var(--green-800);}

            .confusion-panel{display:grid;gap:12px;}
            .confusion-card{border:1px solid #eee7db;border-radius:12px;background:#fffdfa;padding:12px;}
            .confusion-title{font-size:12px;text-transform:uppercase;letter-spacing:.06em;font-weight:900;color:#687169;margin-bottom:6px;}
            .confusion-species{font-family:Georgia, 'Times New Roman', serif;color:var(--green-800);font-weight:850;font-size:18px;line-height:1.15;}
            .score-pill{display:inline-flex;align-items:center;gap:6px;background:#e9f6df;color:#326b32;border:1px solid #c9e6bd;border-radius:999px;padding:4px 9px;font-size:11px;font-weight:900;margin-top:8px;}
            .placeholder{color:#7a8179;font-weight:700;}
            .about-section,.contact-section{margin-top:16px;background:white;border:1px solid rgba(217,224,211,.9);box-shadow:var(--shadow-sm);border-radius:14px;padding:22px;scroll-margin-top:96px;}
            .section-heading{display:flex;align-items:center;gap:12px;margin-bottom:16px;color:var(--green-900);}
            .section-heading h3{font-family:Georgia, 'Times New Roman', serif;font-weight:900;margin:0;}
            .summary-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:16px 0;}
            .summary-card{border:1px solid #eee7db;background:#fffdfa;border-radius:13px;padding:14px;min-height:84px;}
            .summary-value{font-size:24px;font-weight:950;color:var(--green-900);line-height:1;}
            .summary-label{font-size:12px;color:#667067;margin-top:8px;line-height:1.3;}
            .contact-grid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.9fr) minmax(0,1.45fr) minmax(0,1fr);gap:14px;align-items:stretch;}
            .contact-card{border:1px solid #eee7db;background:#fffdfa;border-radius:13px;padding:16px;min-height:100%;overflow:hidden;font-size:15px;line-height:1.5;min-width:0;}
            .contact-card h6{font-size:15px;font-weight:900;margin-bottom:10px;white-space:nowrap;}
            .contact-card p{font-size:15px;line-height:1.5;margin-bottom:0;}
            .contact-card a{color:var(--green-800);font-weight:700;text-decoration:none;display:block;margin:5px 0;font-size:15px;line-height:1.45;}
            .contact-card a[href^="https://wa.me"]{white-space:nowrap;word-break:keep-all;overflow-wrap:normal;}
            .contact-card a[href^="mailto:"]{font-size:14px;word-break:normal;overflow-wrap:anywhere;}
            .powo-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
            }
            
            .powo-item {
                display: block;
                padding: 10px 12px;
                border: 1px solid #eee7db;
                border-radius: 10px;
                background: #fffdfa;
                text-decoration: none;
                color: var(--green-900);
                font-size: 14px;
                transition: 0.2s ease;
            }
            
            .powo-item:hover {
                background: #f6fbf3;
                border-color: var(--green-600);
            }
            
            .powo-item i {
                font-style: italic;   /* species italic */
                color: var(--green-800);
            }
            
            .powo-item span {
                font-style: normal;   /* author normal */
                margin-left: 4px;
                opacity: 0.8;
            }

            .footer-grid {
                display: grid;
                grid-template-columns: 1.5fr 1fr;
                gap: 40px;
                align-items: start;
            }
            
            .footer-ack h6 {
                font-weight: 900;
                margin-bottom: 10px;
            }
            
            .footer-ack p {
                font-size: 13px;
                color: rgba(255,255,255,0.80);
                margin: 4px 0;
            }

            .upload-guidance{margin-top:12px;border:1px solid #eee7db;border-radius:12px;background:#fffdfa;padding:12px 14px;color:#526157;font-size:13px;line-height:1.45;}
            .analysis-message{margin-top:10px;color:#667067;font-size:12px;text-align:center;}
            .confidence-status{display:inline-flex;align-items:center;gap:8px;margin-top:10px;border-radius:999px;padding:7px 11px;font-size:12px;font-weight:900;border:1px solid #ddd;}
            .confidence-high{background:#e9f6df;color:#326b32;border-color:#c9e6bd;}
            .confidence-moderate{background:#fff4d6;color:#8a6400;border-color:#ead28a;}
            .confidence-low{background:#fff0ed;color:#9a3d28;border-color:#efc2b5;}
            .warning-card{margin-top:12px;border:1px solid #efc2b5;background:#fff7f5;color:#7a3325;border-radius:12px;padding:12px 14px;font-size:13px;line-height:1.45;}
            .disclaimer-box{margin-top:16px;border:1px solid #e4d8bf;background:#fffaf0;border-radius:13px;padding:14px 16px;color:#4d584f;font-size:13px;line-height:1.55;}
            .limitations-list{margin:12px 0 0;padding-left:20px;color:#4d584f;font-size:13px;line-height:1.6;}
            .limitations-list li{margin-bottom:4px;}
            .contact-card .map-box{height:105px;}
            .contact-card .download-btn{font-size:14px;line-height:1.35;width:100%;text-align:left;}

            @media(max-width:1100px){
                .hero-content{grid-template-columns:1fr}.plant-visual{display:none}.mini-grid{grid-template-columns:1fr 1fr}.metrics-band{grid-template-columns:1fr 1fr}.nav-links{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;margin:10px 0}.top-nav{padding:12px 24px;flex-direction:column;align-items:flex-start}.workspace,.hero{padding-left:24px;padding-right:24px}.footer{grid-template-columns:1fr}.summary-grid{grid-template-columns:1fr 1fr}.contact-grid{grid-template-columns:1fr}.preview-box{grid-template-columns:1fr}.info-grid{grid-template-columns:1fr 1fr}.result-hero{grid-template-columns:1fr;text-align:center}.confidence-ring{margin:auto}
            }
            @media(max-width:700px){.hero h1{font-size:clamp(28px,8.5vw,38px)}.mini-grid{grid-template-columns:1fr}.metrics-band{grid-template-columns:1fr}.footer{grid-template-columns:1fr}.summary-grid{grid-template-columns:1fr}.similar-grid{grid-template-columns:repeat(2,1fr)}.steps{grid-template-columns:1fr}.info-grid{grid-template-columns:1fr}}
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

# -------------------- Helper functions --------------------

def describe_confidence(confidence_value: float) -> Tuple[str, str, str]:
    """Return confidence label, CSS class, and interpretation message."""
    if confidence_value >= HIGH_CONFIDENCE_THRESHOLD:
        return "High model score", "confidence-high", "High softmax support for this image; this score is not a calibrated probability."
    if confidence_value >= LOW_CONFIDENCE_THRESHOLD:
        return "Moderate model score", "confidence-moderate", "Moderate softmax support for this image; manual review is recommended."
    return "Low model score", "confidence-low", "Low softmax support for this image; manual verification is recommended."


def make_confidence_status(confidence_value: float):
    label, css_class, message = describe_confidence(confidence_value)
    return html.Div([
        html.I(className="fa-solid fa-gauge-high"),
        html.Span(label),
        html.Span(f"— {message}", style={"fontWeight": "700"}),
    ], className=f"confidence-status {css_class}")


def make_low_confidence_warning(confidence_value: float):
    if confidence_value >= LOW_CONFIDENCE_THRESHOLD:
        return html.Div()
    return html.Div([
        html.Strong("Low model score. "),
        "The model shows weak softmax support for its top-ranked class. Please verify manually or upload a clearer image showing diagnostic organs."
    ], className="warning-card")


def make_scientific_disclaimer():
    return html.Div([
        html.Strong("Scientific disclaimer: "),
        "AI predictions are intended to support preliminary identification only and should be verified by a taxonomist or Flora specialist before scientific, conservation, or management use."
    ], className="disclaimer-box")

def split_species_name(full_name: str):
    parts = full_name.strip().split()

    if len(parts) <= 2:
        # no authors or only minimal name
        return full_name, ""

    species_name = " ".join(parts[:2])   # first two words
    author_name = " ".join(parts[2:])    # rest = authors

    return species_name, author_name

def make_powo_section():
    items = []

    for sp, link in species_powo_links.items():
        species, author = split_species_name(sp)

        items.append(
            html.A(
                [
                    html.I(species),          # italic species
                    html.Span(f" {author}")   # normal author
                ],
                href=link,
                target="_blank",
                className="powo-item"
            )
        )

    return html.Section([
        html.Div([
            html.I(className="fa-solid fa-leaf"),
            html.H3("Species List")
        ], className="section-heading"),

        html.Div(items, className="powo-grid")
    ], className="about-section", id="covered-species-list")


    
def safe_info(class_info: Dict[str, Any], keys, default=PLACEHOLDER) -> str:
    """Read optional class metadata safely across different naming conventions."""
    if not isinstance(class_info, dict):
        return default
    for key in keys:
        value = class_info.get(key)
        if value not in (None, "", [], {}):
            if isinstance(value, (list, tuple)):
                return ", ".join(map(str, value))
            return str(value)
    return default


def load_species_json(species_name: str, author_name: str) -> Dict[str, Any]:
    """Load species JSON file based on species name."""
    try:
        file_name = f"{species_name} {author_name}.json"
        file_path = os.path.join(PLANTS_INFO_DIR, file_name)

        if not os.path.exists(file_path):
            return {}

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"Error loading JSON for {species_name} {author_name}: {e}")
        return {}


def parse_species_class(class_data: Any) -> Tuple[str, str]:
    """Supports your current class mapping: string or [species, author]."""
    if isinstance(class_data, list):
        if len(class_data) == 2:
            return str(class_data[0]), str(class_data[1])
        if len(class_data) == 1:
            return str(class_data[0]), ""
        raise ValueError(f"Invalid class_data list length: {len(class_data)}")
    if isinstance(class_data, str):
        return class_data, ""
    raise TypeError(f"Invalid class_data type: {type(class_data)}")


def format_uploaded_date(timestamp) -> str:
    try:
        return datetime.datetime.fromtimestamp(timestamp).strftime("%b %d, %Y • %H:%M")
    except Exception:
        return datetime.datetime.now().strftime("%b %d, %Y • %H:%M")


def make_header():
    nav_items = [
        ("Home", "#home", "nav-active"),
        ("Identify Plants", "#identify", ""),
        ("Species Guide", "#species-guide", ""),
        ("Species List", "#covered-species-list", ""),
        ("About the Project", "#about-project", ""),
        ("Contact", "#contact", ""),
    ]
    return html.Div([
        html.Div([
            html.Div("🌿", className="brand-mark"),
            html.Div([
                html.Div("Wadi Degla AI Plant Identifier", className="brand-title"),
            ]),
        ], className="brand"),
        html.Nav([
            html.A(label, href=href, className=class_name) for label, href, class_name in nav_items
        ], className="nav-links"),
    ], className="top-nav")

def make_hero():
    return html.Section([
        html.Div([
            html.Div([
                html.H1([html.Span("Explore the Wild Flora of", className="hero-title-line"), html.Span("Wadi Degla Protected Area", className="hero-title-line")]),
                html.P("An intelligent platform that helps researchers, students, visitors, and nature enthusiasts discover, identify, and learn about the wild plants of Wadi Degla Protected Area (WDPA)."),
                html.Div([
                    html.A([html.I(className="fa-solid fa-cloud-arrow-up"), "Upload Plant Image"], href="#identify", className="primary-btn"),
                    html.A([html.I(className="fa-regular fa-map"), "Explore Species and User Guide"], href="#species-guide", className="secondary-btn"),
                ], className="hero-actions"),
                html.P("Drag & drop an image or click to browse • JPG, JPEG, PNG, WEBP", className="hero-help"),
            ]),
            html.Div([
                html.Img(
                    src="/assets/wadi.png",
                    style={
                        "width": "100%",
                        "height": "100%",
                        "objectFit": "cover",
                        "borderRadius": "0 0 0 90px"
                    }
                )
            ], className="plant-visual"),
        ], className="hero-content")
    ], className="hero", id="home")


def initial_upload_state():
    return html.Div([
        html.I(className="fa-regular fa-image fa-2x mb-2"),
        html.Div("Your uploaded image will appear here."),
    ], className="empty-state")


def initial_result_state():
    return html.Div([
        html.I(className="fa-solid fa-seedling fa-2x mb-2"),
        html.Div("Upload a plant image to see identification results here."),
    ], className="empty-state")


def initial_description_state():
    return html.Div("Description of the identified plant will appear here.", className="description-box text-muted")


def initial_confusion_state():
    """Placeholder for confusion panel – these headings are inside the Model Confusion Insights card."""
    return html.Div([
        html.Div([
            html.Div("Top Alternative Prediction", className="confusion-title"),
            html.Div(PLACEHOLDER, className="placeholder"),
        ], className="confusion-card"),
        html.Div([
            html.Div("Likely Confused Species", className="confusion-title"),
            html.Div(PLACEHOLDER, className="placeholder"),
        ], className="confusion-card"),
    ], className="confusion-panel")


def make_upload_card():
    return html.Div([
        html.Div([
            html.Div([html.Span("1", className="step-badge"), html.Span("Upload & Preview")], className="title-wrap"),
        ], className="card-head"),
        html.Div([
            dcc.Upload(
                id="upload-image",
                children=html.Div([
                    html.I(className="fa-solid fa-cloud-arrow-up upload-icon"),
                    html.Div(["Drag & drop your image here"], className="fw-bold"),
                    html.Small("or click to select file • max 20MB", className="text-muted"),
                ], className="drop-zone"),
                multiple=False,
                accept="image/jpeg,image/jpg,image/png,image/webp",
            ),
            html.Div([
                html.Strong("Image quality guidance: "),
                "For best results, upload a clear photo showing leaves, flowers, fruits, or the whole plant under natural light. Avoid very dark, blurred, or heavily cropped images."
            ], className="upload-guidance"),
            html.Div(id="uploaded-image-display", children=initial_upload_state()),
        ], className="card-body-custom"),
    ], className="glass-card", id="identify")


def make_result_card():
    return html.Div([
        html.Div([
            html.Div([html.Span("2", className="step-badge"), html.Span("Identification Result")], className="title-wrap"),
        ], className="card-head"),
        html.Div(
            [
                dbc.Spinner([
                    html.Div(id="classification-result-display", children=initial_result_state()),
                    html.Div(id="plant-description-display", children=initial_description_state()),
                ], color="success", type="grow"),
                html.Div("Analyzing image may take a few seconds after upload.", className="analysis-message"),
            ],
            className="card-body-custom",
        ),
    ], className="glass-card")

def make_model_limitations_card():
    return html.Div([
        html.H5("Scientific Disclaimer"),
        html.Ul([
            html.Li("AI predictions are intended to support preliminary identification only and should be verified by a taxonomist or Flora specialist before scientific, conservation, or management use."),
            html.Li("Performance depends on image clarity, lighting, viewpoint, and the visibility of diagnostic plant organs."),
            html.Li("Visually similar species may be confused by the model, especially when flowers or fruits are absent."),
            html.Li("Displayed model scores are softmax outputs for the uploaded image and are not calibrated probabilities."),
        ], className="limitations-list")
    ], className="mini-card model-limitations-card")


def make_support_modules():
    return html.Section([
        html.Div([html.I(className="fa-solid fa-book-open"), html.H3("Species and User Guide")], className="section-heading"),
        html.Div([
            # --- Model Confusion Insights (includes both Top Alternative and Likely Confused) ---
            html.Div([
                html.Div([html.H5("Model Confusion Insights")], className="d-flex justify-content-between"),
                html.Div(id="model-confusion-display", children=initial_confusion_state()),
                html.Div([
                    html.Div([html.Strong("Top Alternative Prediction:"), " the second-ranked class produced by the currently deployed Top-30/215 model for this uploaded image."], className="mb-1"),
                    html.Div([html.Strong("Likely Confused Species:"), " target species most often misclassified as the displayed class on the WadiDegla model dataset validation set."]),
                ], className="text-muted small mt-2"),
            ], className="mini-card"),

            # --- Species Visual Reference (only image, no confusion headings) ---
            html.Div([
                html.H5("Species Visual Reference"),
                html.Div(
                    id="species-image-display",
                    children=html.Div(
                        "Upload an image to see the reference species visualization.",
                        className="placeholder"
                    )
                )
            ], className="mini-card"),

            html.Div([
                html.Div([
                    html.Div([html.H5("How it works"), html.Small("3 simple steps", className="text-muted")], className="d-flex justify-content-between"),
                    html.Div([
                        html.Div([html.Div(html.I(className="fa-solid fa-upload"), className="step-icon"), html.Strong("Upload Image"), html.P("Add a clear photo of the plant.")]),
                        html.Div([html.Div(html.I(className="fa-solid fa-magnifying-glass-chart"), className="step-icon"), html.Strong("AI Analysis"), html.P("The MobileNetV2 model analyzes visual traits.")]),
                        html.Div([html.Div(html.I(className="fa-solid fa-leaf"), className="step-icon"), html.Strong("Get Results"), html.P("Review species metadata and the model score.")]),
                    ], className="steps"),
                ], className="mini-card how-card"),
                make_model_limitations_card(),
            ], className="side-stack"),
        ], className="mini-grid"),
    ], className="support-section", id="species-guide")

def make_metrics_band():
    return html.Div([
        html.Div([html.Div(html.I(className="fa-solid fa-graduation-cap"), className="metric-icon"), html.Div([html.Div("Research Model Summary", className="fw-bold"), html.Div("MSc research dashboard for AI-assisted plant identification.", className="metric-label")])], className="metric-block"),
        html.Div([html.Div(html.I(className="fa-regular fa-images"), className="metric-icon"), html.Div([html.Div("22,564", className="metric-value"), html.Div("Model-dataset images", className="metric-label")])], className="metric-block"),
        html.Div([html.Div(html.I(className="fa-solid fa-seedling"), className="metric-icon"), html.Div([html.Div("33", className="metric-value"), html.Div("Classes: 32 species + others", className="metric-label")])], className="metric-block"),
        html.Div([html.Div(html.I(className="fa-solid fa-map-location-dot"), className="metric-icon"), html.Div([html.Div("WDPA", className="metric-value"), html.Div("Protected area focus", className="metric-label")])], className="metric-block"),
        html.Div([html.Div(html.I(className="fa-solid fa-microchip"), className="metric-icon"), html.Div([html.Div("MobileNetV2", className="metric-value"), html.Div("Deep learning model", className="metric-label")])], className="metric-block"),
        html.Div([html.Div(html.I(className="fa-solid fa-code-branch"), className="metric-icon"), html.Div([html.Div("Top-30/215", className="metric-value"), html.Div("Selected checkpoint", className="metric-label")])], className="metric-block"),
    ], className="metrics-band")

def make_footer():
    return html.Footer(
        html.Div("🌿 Wadi Degla AI Plant Identifier © 2026 Wadi Degla Plant Identifier", className="footer-single"),
        className="footer"
    )

def make_about_project_section():
    return html.Section([
        html.Div([html.I(className="fa-solid fa-flask"), html.H3("About the Project")], className="section-heading"),
        html.P(
            "This deep learning system was developed to support the identification of 32 target wild plant species from Wadi Degla Protected Area using computer vision. The application is configured to use the selected MobileNetV2 Top-30 checkpoint 215. Model development used the WadiDegla model dataset, comprising 22,064 field images of the target species plus 500 external plant images in the non-target others class (22,564 images; 33 model classes). This work is part of a Master’s degree project in Artificial Intelligence at the Faculty of Science, Al-Azhar University.",
            className="mb-0"
        ),
        make_metrics_band(),
    ], className="about-section", id="about-project")

def make_contact_section():
    return html.Section([
        html.Div([html.I(className="fa-solid fa-envelope"), html.H3("Contact")], className="section-heading"),
        html.Div([
            html.Div([
                html.H6("📍 Address"),
                html.P("Botany Department, Faculty of Science, Al-Azhar University, Cairo, Egypt", className="mb-0")
            ], className="contact-card"),
            html.Div([
                html.H6("📞 Phone / WhatsApp"),
                html.A("+20 10 12890605", href="https://wa.me/201012890605", target="_blank"),
                html.A("+20 10 97309134", href="https://wa.me/201097309134", target="_blank"),
            ], className="contact-card"),
            html.Div([
                html.H6("📧 Email us"),
                html.A("albraa.mahmoud@azhar.edu.eg", href="mailto:albraa.mahmoud@azhar.edu.eg"),
                html.A("mona_maze@yahoo.de", href="mailto:mona_maze@yahoo.de"),
                html.A("mohammed.morsy.elsayed94@gmail.com", href="mailto:mohammed.morsy.elsayed94@gmail.com"),
            ], className="contact-card"),
            html.Div([
                html.H6("📌 Location"),
                html.Div([
                    html.I(className="fa-solid fa-location-dot pin"),
                    html.Div(["Wadi Degla", html.Br(), "Protected Area"], className="map-label")
                ], className="map-box"),
                html.A(
                    [html.I(className="fa-solid fa-map-location-dot me-2"), "Open Location on Google Maps"],
                    href="https://maps.app.goo.gl/ayHZgm4aGVgf5BaX8",
                    target="_blank",
                    className="download-btn mt-2 d-inline-block text-decoration-none"
                ),
            ], className="contact-card"),
        ], className="contact-grid"),
    ], className="contact-section", id="contact")


def make_acknowledgement_section():
    return html.Section([
        html.Div([html.I(className="fa-solid fa-handshake"), html.H3("Acknowledgement")], className="section-heading"),
        html.P(
            "The authors would like to extend their deepest appreciation to the Ministry of Environment of Egypt, the Nature Conservation Sector, and the Administration of Wadi Degla Protected Area for granting access and permission to conduct field investigations within the protected area.",
            className="mb-0"
        ),
    ], className="about-section", id="acknowledgement")


# -------------------- Layout --------------------
app.layout = html.Div([
    make_header(),
    make_hero(),
    html.Main([
        dbc.Row([
            dbc.Col(make_upload_card(), lg=5, className="mb-4"),
            dbc.Col(make_result_card(), lg=7, className="mb-4"),
        ], className="g-4 align-items-stretch"),
        make_support_modules(),
        make_powo_section(),
        make_about_project_section(),
        make_contact_section(),
        make_acknowledgement_section(),
    ], className="workspace"),
    make_footer(),
], className="app-shell")


def load_species_image(species_name: str, author_name: str):
    """
    Load species reference image from assets folder.
    Supports case-insensitive extensions (.png, .PNG, .JPG, etc.)
    """

    base_name = f"{species_name} {author_name}".strip()

    possible_extensions = [".png", ".jpg", ".jpeg", ".webp"]

    assets_dir = "assets"

    if not os.path.isdir(assets_dir):
        logger.warning("Assets directory is missing; species reference images cannot be loaded.")
        return None

    for file in os.listdir(assets_dir):
        file_lower = file.lower()
        base_lower = base_name.lower()

        for ext in possible_extensions:
            if file_lower == (base_lower + ext):
                return f"/assets/{file}"

    return None

def species_label_from_index(class_index: int) -> Tuple[str, str]:
    try:
        if isinstance(index_to_class, dict) and class_index in index_to_class:
            return parse_species_class(index_to_class[class_index])
        if isinstance(index_to_class, dict) and str(class_index) in index_to_class:
            return parse_species_class(index_to_class[str(class_index)])
    except Exception:
        pass
    return PLACEHOLDER, ""


def parse_confused_item(item: Any) -> Dict[str, Any]:
    """Accept flexible confused-species item formats from PKL."""
    if isinstance(item, dict):
        species_idx = item.get("species_index", item.get("confused_with_index", item.get("index")))
        name = item.get("species_name", item.get("confused_with_name", item.get("name")))
        score = item.get("confusion_score", item.get("confusion_rate", item.get("score")))
        note = item.get("note", item.get("distinguishing_note", item.get("description", "")))
        return {"species_index": species_idx, "name": name, "score": score, "note": note}
    if isinstance(item, (list, tuple)):
        species_idx = item[0] if len(item) > 0 else None
        score = item[1] if len(item) > 1 else None
        note = item[2] if len(item) > 2 else ""
        return {"species_index": species_idx, "name": None, "score": score, "note": note}
    return {"species_index": None, "name": str(item), "score": None, "note": ""}


def make_model_confusion_output(
    species_name: str,
    author_name: str,
    class_info: Dict[str, Any],
    top_probs,
    top_indices
):
    """Build the Model Confusion Insights panel for the selected Top-30/215 model.

    The dynamic Top Alternative Prediction comes from the current uploaded image.
    Likely Confused Species is read from the current species JSON:
    confusion.likely_confused_species.
    """
    # =========================
    # PART A: TOP ALTERNATIVE PREDICTION
    # =========================
    secondary_block = html.Div()

    if top_probs is not None and top_indices is not None and top_probs.shape[1] >= 2:
        second_idx = int(top_indices[0, 1].item())
        second_prob = float(top_probs[0, 1].item()) * 100
        second_species, second_author = species_label_from_index(second_idx)

        if second_prob >= CONFIDENCE_THRESHOLD:
            secondary_block = html.Div([
                html.Div("Top Alternative Prediction", className="confusion-title"),
                html.Div([
                    html.Div([html.I(second_species), " ", html.Span(second_author)], className="confusion-species"),
                    html.Span(f"{second_prob:.2f}%", className="score-pill")
                ], className="confusion-card")
            ])
        else:
            secondary_block = html.Div([
                html.Div("Top Alternative Prediction", className="confusion-title"),
                html.Div("No alternative class reached the display threshold for this image.", className="confusion-species")
            ], className="confusion-card")

    # =========================
    # PART B: LIKELY CONFUSED SPECIES
    # =========================
    confusion_data = class_info.get("confusion", {}) if isinstance(class_info, dict) else {}
    confusion_list = confusion_data.get("likely_confused_species", [])
    if not isinstance(confusion_list, list):
        confusion_list = []

    if species_name.strip().lower() == "others":
        pattern_cards = [
            html.Div(
                "The non-target others class is not shown as a botanical confusion species.",
                className="confusion-species"
            )
        ]
    elif confusion_list:
        pattern_cards = [
            html.Div([html.Div(value, className="confusion-species")], className="confusion-card")
            for value in confusion_list
        ]
    else:
        pattern_cards = [
            html.Div(
                "No target-species false-positive confusion was recorded for this class on the WadiDegla validation set.",
                className="confusion-species"
            )
        ]

    pattern_block = html.Div([
        html.Div("Likely Confused Species", className="confusion-title"),
        html.Div(pattern_cards, className="confusion-panel")
    ], className="confusion-card")

    return html.Div([secondary_block, pattern_block], className="confusion-panel")

# -------------------- Processing --------------------
def process_and_get_results(contents, filename, date):
    """Decode image, run model prediction, and return Dash components."""
    if model is None or index_to_class is None:
        error_msg = dbc.Alert(
            "Model or class mapping was not loaded. Please check server logs and file paths.",
            color="danger",
            className="mt-3",
        )
        return initial_upload_state(), error_msg, initial_description_state(), initial_confusion_state(), html.Div("No reference image available.")

    if contents is None:
        return initial_upload_state(), initial_result_state(), initial_description_state(), initial_confusion_state(), html.Div("Upload an image to see reference visualization.", className="subtle-text")

    try:
        if not filename:
            filename = "uploaded_image"

        if "," not in contents:
            raise ValueError("Invalid upload data format.")

        content_type, content_string = contents.split(",", 1)
        mime_type = content_type.split(";")[0].replace("data:", "").strip().lower()
        if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
            raise ValueError("Unsupported file type. Please upload JPG, JPEG, PNG, or WEBP images only.")

        decoded_bytes = base64.b64decode(content_string)
        if len(decoded_bytes) > MAX_UPLOAD_SIZE_BYTES:
            raise ValueError(f"Uploaded file exceeds the {MAX_UPLOAD_SIZE_MB}MB size limit.")

        try:
            Image.open(io.BytesIO(decoded_bytes)).verify()
        except Exception as verify_error:
            raise ValueError("Uploaded file is not a valid readable image.") from verify_error

        pil_image = Image.open(io.BytesIO(decoded_bytes)).convert("RGB")
        original_width, original_height = pil_image.size

        # Display original image
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        encoded_original_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        original_image_src = f"data:image/png;base64,{encoded_original_image}"

        uploaded_image_output = html.Div([
            html.Div([
                html.Img(src=original_image_src, className="preview-img"),
                html.Div([
                    html.Div(filename, className="fw-bold mb-1"),
                    html.Div(f"Uploaded on {format_uploaded_date(date)}", className="text-muted small mb-1"),
                    html.Div(f"{original_width} × {original_height} px", className="text-muted small"),
                    html.Span([html.I(className="fa-solid fa-check"), "Image ready"], className="ready-pill"),
                ]),
            ], className="preview-box")
        ])

        # Model inference
        image_tensor = test_transforms(pil_image).unsqueeze(0).to(DEVICE)
        model.eval()
        model.to(DEVICE)

        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
            top_k = min(2, probabilities.shape[1])
            top_probs, top_indices = torch.topk(probabilities, k=top_k, dim=1)

        predicted_class_index = predicted_idx.item()
        confidence_value = confidence.item() * 100

        if predicted_class_index not in index_to_class:
            raise IndexError(f"Predicted class index ({predicted_class_index}) not found in index_to_class mapping.")

        species_name, author_name = parse_species_class(index_to_class[predicted_class_index])
        
        full_name = f"{species_name} {author_name}".strip()
        
        # apply taxonomic override if exists
        if full_name in SPECIES_NAME_OVERRIDES:
            corrected = SPECIES_NAME_OVERRIDES[full_name]
            species_name, author_name = split_species_name(corrected)

        is_others_class = species_name.strip().lower() == "others"
        class_info = load_species_json(species_name, author_name)

        # Load species details
        plant_description = class_info.get("About this species", PLACEHOLDER)
        family = class_info.get("Family", PLACEHOLDER)
        growth_form = class_info.get("Growth form", PLACEHOLDER)
        life_span = class_info.get("Life span", PLACEHOLDER)
        life_form = class_info.get("Life form", PLACEHOLDER)
        iucn_status = class_info.get("IUCN Status", PLACEHOLDER)
        endemism = class_info.get("Endemism in Egypt", PLACEHOLDER)
        geographical_distribution = class_info.get("Geographical distribution", PLACEHOLDER)

        links_data = class_info.get("Links", {})
        powo_link = links_data.get("POWO Link", "")
        gbif_link = links_data.get("GBIF Link", "")
        iucn_link = class_info.get("IUCN Link", "")

        score_degrees = f"{min(max(confidence_value, 0), 100) * 3.6:.1f}deg"
        confidence_status_output = make_confidence_status(confidence_value)
        low_confidence_warning = make_low_confidence_warning(confidence_value)

        # Classification output
        if is_others_class:
            classification_output = html.Div([
                html.Div([
                    html.Div(html.I(className="fa-solid fa-leaf"), className="species-icon"),
                    html.Div([html.Div("Predicted Species", className="small-label"), html.Div("others", className="species-name")]),
                    html.Div([
                        html.Div(html.Div(f"{confidence_value:.2f}%", className="confidence-inner"), className="confidence-ring", style={"--score": score_degrees}),
                        html.Div("Model Score", className="confidence-label"),
                    ], className="confidence-wrap"),
                ], className="result-hero"),
                confidence_status_output,
                low_confidence_warning,
            ])
            description_output = html.Div([
                html.Div("About this species:", className="fw-bold mb-2", style={"color": "var(--green-900)"}),
                html.Div("The model assigned its highest score to the trained non-target others class. This is not a taxonomic species identification; please review the image or upload a clearer photograph showing diagnostic plant organs."),
            ], className="description-box")
        else:
            classification_output = html.Div([
                html.Div([
                    html.Div(html.I(className="fa-solid fa-leaf"), className="species-icon"),
                    html.Div([
                        html.Div("Predicted Species", className="small-label"),
                        html.Div([html.I(species_name), " ", html.Span(author_name)], className="species-name"),
                        html.Div([html.Div(f"Family: {family}")], className="text-muted small mt-2"),
                    ]),
                    html.Div([
                        html.Div(html.Div(f"{confidence_value:.2f}%", className="confidence-inner"), className="confidence-ring", style={"--score": score_degrees}),
                        html.Div("Model Score", className="confidence-label"),
                    ], className="confidence-wrap"),
                ], className="result-hero"),
                confidence_status_output,
                low_confidence_warning,
                html.Div([
                    html.Div([html.I(className="fa-solid fa-tree"), html.Div([html.Strong("Growth Form"), html.Span(growth_form)])], className="info-chip"),
                    html.Div([html.I(className="fa-solid fa-hourglass-half"), html.Div([html.Strong("Life Span"), html.Span(life_span)])], className="info-chip"),
                    html.Div([html.I(className="fa-solid fa-seedling"), html.Div([html.Strong("Life Form"), html.Span(life_form)])], className="info-chip"),
                    html.Div([html.I(className="fa-solid fa-shield-heart"), html.Div([html.Strong("IUCN Status"), html.Span(iucn_status)])], className="info-chip"),
                    html.Div([html.I(className="fa-solid fa-location-dot"), html.Div([html.Strong("Endemism in Egypt"), html.Span(endemism)])], className="info-chip"),
                ], className="info-grid"),
            ])
            description_output = html.Div([
                html.Div("About this species:", className="fw-bold mb-2", style={"color": "var(--green-900)"}),
                html.Div(plant_description),
                html.Br(),
                html.Div([html.Strong("Geographical distribution: "), html.Span(geographical_distribution)]),
                html.Br(),
                html.Div("Sources:", className="fw-bold mb-2", style={"color": "var(--green-900)"}),
                html.Div([
                    html.A(html.Img(src="/assets/POWO.png", style={"height": "42px", "objectFit": "contain"}), href=powo_link, target="_blank") if powo_link else html.Div(),
                    html.A(html.Img(src="/assets/GBIF.png", style={"height": "40px", "objectFit": "contain"}), href=gbif_link, target="_blank") if gbif_link else html.Div(),
                    html.A(html.Img(src="/assets/IUCN.png", style={"height": "40px", "objectFit": "contain"}), href=iucn_link, target="_blank") if (iucn_status != "NE (Not Evaluated)" and iucn_link) else html.Div(),
                ], style={"display": "flex", "alignItems": "center", "gap": "18px", "flexWrap": "wrap", "marginTop": "8px"}),
            ], className="description-box")

        # Species image (for Species Visual Reference card)
        species_image_path = load_species_image(species_name, author_name)
        if species_image_path:
            species_image_output = html.Div([
                html.Div(f"Reference image of {species_name}", className="small-label"),
                html.Img(src=species_image_path, style={"width": "100%", "maxWidth": "900px", "height": "auto", "display": "block", "margin": "0 auto", "objectFit": "contain", "borderRadius": "14px", "border": "1px solid #e6e0d2", "background": "#fffefa", "padding": "10px", "boxShadow": "0 10px 25px rgba(0,0,0,0.08)"})
            ])
        else:
            species_image_output = html.Div("No reference image available for this species.", className="subtle-text")

        # Confusion output (goes to model-confusion-display)
        confusion_output = make_model_confusion_output(species_name, author_name, class_info, top_probs, top_indices)

        print(f"Successfully classified '{filename}'. Predicted: {species_name} {author_name} ({confidence_value:.2f}%)")
        return uploaded_image_output, classification_output, description_output, confusion_output, species_image_output

    except Exception as e:
        traceback.print_exc()
        error_alert = dbc.Alert([
            html.H5("Processing Error", className="alert-heading"),
            html.P(f"An error occurred while processing '{filename}': {e}"),
            html.Hr(),
            html.P("Please ensure the uploaded file is a valid JPG, JPEG, PNG, or WEBP image under the 20MB upload limit, and that the model/class mapping files are compatible.", className="mb-0"),
        ], color="danger", className="mt-3")
        return html.Div("Could not display this image.", className="empty-state text-danger"), error_alert, initial_description_state(), initial_confusion_state(), html.Div("No reference image available.")

@app.callback(
    Output("uploaded-image-display", "children"),
    Output("classification-result-display", "children"),
    Output("plant-description-display", "children"),
    Output("model-confusion-display", "children"),
    Output("species-image-display", "children"),
    Input("upload-image", "contents"),
    State("upload-image", "filename"),
    State("upload-image", "last_modified"),
)
def update_displays(contents, filename, date):
    return process_and_get_results(contents, filename, date)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
