import hashlib
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

import streamlit as st

APP_VERSION = "v0.8.2"
APP_NAME = "EM Posting"
TAGLINE = "One calm place to take a finished video from final cut to an approved TikTok draft."

# Public demo home. The domain shown in a submission demo video must match this URL.
WEBSITE_URL = "https://tiktok-posting.onrender.com"
WEBSITE_DOMAIN = "tiktok-posting.onrender.com"

# Creator post limit. TikTok developer-form limits belong in README, not the product UI.
CAPTION_MAX = 2200

WORKSPACE = "Creator Studio"

SHORT_DESCRIPTION = (
    "Creator workspace for reviewing finished videos and sending approved posts to TikTok drafts."
)

# Kept in sync with the submission copy in README.md (App review explanation, under 1000 chars).
APP_REVIEW_EXPLANATION = (
    "EM Posting is a creator workflow app for preparing finished short-form videos for TikTok. "
    "An authorized creator selects or uploads a completed MP4, reviews the account, description, "
    "and content confirmations, then explicitly approves the video for TikTok's draft flow. The "
    "requested Content Posting API integration reduces manual file transfer while preserving human "
    "review and final posting control inside TikTok. It is a focused creator publishing workspace, "
    "not a mass-posting service. It does not scrape data, automate engagement, or publish spam."
)

TERMS = dedent(
    """
    # Terms of Service

    **Last updated: July 2026**

    EM Posting is a creator workflow product for preparing, reviewing, and handing approved
    short-form videos to supported social platforms.

    ## Account and workspace use
    You may use EM Posting only for workspaces and creator accounts you are authorized to manage.
    You are responsible for the videos, descriptions, approvals, and account selections made in your
    workspace.

    ## Creator approval
    EM Posting is designed around deliberate human review. A creator or authorized team member must
    review each post before initiating a platform handoff. The service may not be used for spam,
    deceptive automation, unauthorized account access, or attempts to bypass platform controls.

    ## Platform services
    Platform integrations remain subject to each platform's terms, permissions, technical limits, and
    review requirements. A successful handoff does not guarantee publication. Final editing and
    posting may continue inside the destination platform.

    ## Content rights
    You must have the rights and permissions required to upload and publish the content you submit.

    ## Availability
    Features may change as integrations mature. This public build is a workflow preview: it does not
    connect to a live platform account, and preview features must not be represented as completed
    production integrations.

    ## Contact
    Product and policy questions may be sent to eczemamitten@gmail.com while EM Posting is in its
    initial creator pilot.
    """
).strip()

PRIVACY = dedent(
    """
    # Privacy Policy

    **Last updated: July 2026**

    EM Posting is a creator workflow product. This policy describes the information the service may
    process to prepare and hand creator-approved posts to supported platforms.

    ## Information processed
    EM Posting may process creator account labels, finished video files, descriptions, review notes,
    approval choices, file metadata, and workflow activity such as review and handoff timestamps.

    ## How information is used
    This information is used to display the creator workspace, preserve review decisions, prepare
    platform handoffs, and show workflow receipts to authorized users.

    ## Platform data
    The intended TikTok integration is limited to uploading a creator-approved video to the draft
    flow. EM Posting does not request TikTok direct messages, comments, follower lists, or unrelated
    account data.

    ## Storage
    This public build uses session-only state and does not permanently store uploaded videos. A
    production service would temporarily process files and retain workflow records only as needed to
    provide the creator-requested service.

    ## Sharing
    Content would be sent to a platform only after an authorized creator initiates the handoff. EM
    Posting does not sell personal information.

    ## Security
    Any future production credentials must be stored in private deployment secrets and are never
    included in the public source repository.

    ## Contact
    Privacy questions may be sent to eczemamitten@gmail.com during the initial pilot.
    """
).strip()

st.set_page_config(
    page_title=APP_NAME,
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
      --ink:#1a1a1f; --muted:#71717a; --faint:#a1a1aa; --line:#e8e6e0;
      --paper:#f6f5f1; --card:#ffffff; --accent:#4f46e5; --accent-soft:#eef0ff;
      --ok:#0f7a52; --ok-soft:#e7f6ef; --warn:#8a6d1a; --warn-soft:#fbf3d9;
    }
    .stApp { background: var(--paper); color: var(--ink); }
    .block-container { max-width: 1080px; padding-top: 2.4rem; padding-bottom: 5rem; }
    section[data-testid="stSidebar"] { background:#141418; border-right:1px solid rgba(255,255,255,.07); }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#f4f4f6 !important; }
    section[data-testid="stSidebar"] label { color:#e7e7ec !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] label { padding:.36rem .5rem; border-radius:10px; }
    h1,h2,h3 { letter-spacing:-.03em; color:var(--ink); }
    h1 { font-size:2.4rem !important; }
    .brand { font-size:1.14rem; font-weight:800; letter-spacing:-.03em; color:#fff; display:flex; align-items:center; }
    .brand-mark { display:inline-grid; place-items:center; width:28px; height:28px; margin-right:9px; border-radius:9px; background:linear-gradient(135deg,#4f46e5,#8b7bff); color:#fff; }
    .ws-chip { margin-top:.8rem; padding:.7rem .78rem; border:1px solid rgba(255,255,255,.1); background:rgba(255,255,255,.05); border-radius:12px; color:#e7e7ec; font-size:.8rem; }
    .eyebrow { text-transform:uppercase; letter-spacing:.16em; font-size:.68rem; font-weight:800; color:var(--accent); margin-bottom:.55rem; }
    .hero { padding:2.3rem 2.4rem; border-radius:22px; color:#fff; background:linear-gradient(135deg,#17171f 0%,#2b2860 60%,#4f46e5 100%); box-shadow:0 24px 60px rgba(31,29,84,.16); }
    .hero h1 { color:#fff; font-size:2.9rem !important; line-height:1.04; max-width:640px; margin:.4rem 0 .7rem; }
    .hero p { color:#e4e3f5; font-size:1.04rem; line-height:1.6; max-width:620px; margin:0; }
    .hero-badge { display:inline-block; padding:.34rem .66rem; border:1px solid rgba(255,255,255,.18); background:rgba(255,255,255,.08); border-radius:999px; font-size:.74rem; margin-right:.4rem; }
    .card { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1.15rem 1.2rem; box-shadow:0 8px 22px rgba(23,22,32,.04); height:100%; }
    .card h3 { margin:.15rem 0 .4rem; font-size:1.04rem; }
    .card p { color:var(--muted); font-size:.9rem; line-height:1.55; margin:0; }
    .stat { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:.95rem 1.05rem; }
    .stat-label { color:var(--muted); font-size:.7rem; text-transform:uppercase; letter-spacing:.1em; font-weight:750; }
    .stat-value { font-size:1.36rem; font-weight:800; margin-top:.32rem; letter-spacing:-.03em; }
    .pill { display:inline-flex; align-items:center; gap:.36rem; font-size:.74rem; font-weight:750; border-radius:999px; padding:.3rem .56rem; }
    .pill-ok { color:var(--ok); background:var(--ok-soft); }
    .pill-preview { color:var(--warn); background:var(--warn-soft); }
    .pill-neutral { color:#52525b; background:#eef0f2; }
    .flow { display:flex; align-items:center; gap:.55rem; flex-wrap:wrap; margin:.4rem 0 1.4rem; }
    .flow-node { padding:.5rem .72rem; border-radius:11px; border:1px solid var(--line); background:var(--card); font-size:.8rem; font-weight:730; color:var(--muted); }
    .flow-node.done { color:var(--accent); border-color:#d7d5ff; background:var(--accent-soft); }
    .flow-arrow { color:var(--faint); font-weight:800; }
    .receipt { padding:1.15rem 1.2rem; border-radius:15px; border:1px solid #cfd2fb; background:linear-gradient(135deg,#f3f4ff,#fbfbff); }
    .note { color:var(--muted); font-size:.82rem; line-height:1.5; }
    [data-testid="stForm"] { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1.25rem; }
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] { background:linear-gradient(135deg,#4b43dd,#6f63ff); border:none; }
    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button { border-radius:11px; min-height:2.6rem; font-weight:700; }
    [data-testid="stFileUploader"] { background:#fbfbfa; border-radius:13px; padding:.35rem; }
    footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def utc_now():
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


def init_state():
    defaults = {
        "asset": None,
        "queue": [],
        "receipt": None,
        "sent_count": 0,
        "reviewed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value



def sample_path():
    return Path(__file__).parent / "assets" / "sample_creator_video.mp4"


def sample_asset():
    data = sample_path().read_bytes()
    return {
        "filename": "founder-night-routine.mp4",
        "title": "A founder's night routine",
        "size_mb": round(len(data) / (1024 * 1024), 2),
        "duration": "00:08",
        "fingerprint": hashlib.sha256(data).hexdigest()[:16],
        "source": "Sample library",
        "path": str(sample_path()),
    }


def version_caption():
    st.caption(f"{APP_VERSION} · creator publishing workspace · workflow preview")


def page_header(eyebrow, title, subtitle):
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.write(subtitle)


def progress_strip():
    has_asset = st.session_state.asset is not None
    reviewed = st.session_state.reviewed or bool(st.session_state.queue)
    approved = bool(st.session_state.queue)
    sent = st.session_state.sent_count > 0
    stages = [("Select", has_asset), ("Review", reviewed), ("Approve", approved), ("Handoff", sent)]
    html = '<div class="flow">'
    for index, (label, done) in enumerate(stages):
        mark = "✓" if done else str(index + 1)
        cls = "flow-node done" if done else "flow-node"
        html += f'<span class="{cls}">{mark}&nbsp;&nbsp;{label}</span>'
        if index < len(stages) - 1:
            html += '<span class="flow-arrow">→</span>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def goto(page):
    st.session_state.nav = page


# --------------------------------------------------------------------------- Home


def render_home():
    st.markdown(
        f"""
        <div class="hero">
          <span class="hero-badge">creator workspace</span><span class="hero-badge">review-first</span>
          <h1>Final cut in.<br>Approved TikTok draft out.</h1>
          <p>{TAGLINE} Select a finished video, review the account and description, give an
          explicit approval, and preview an honest draft handoff — you keep the final say.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    version_caption()
    st.write("")

    a, b, c = st.columns(3)
    stats = [
        (a, "Workspace", WORKSPACE),
        (b, "Approved queue", str(len(st.session_state.queue))),
        (c, "Handoffs this session", str(st.session_state.sent_count)),
    ]
    for col, label, value in stats:
        with col:
            st.markdown(
                f'<div class="stat"><div class="stat-label">{label}</div><div class="stat-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    st.button("Start in Studio", type="primary", use_container_width=True, on_click=goto, args=("Studio",))

    st.markdown("## One workflow, four steps")
    x, y, z, w = st.columns(4)
    steps = [
        (x, "01", "Select", "Pick the bundled sample video or upload a finished MP4."),
        (y, "02", "Review", "Confirm the account and write the description sent to TikTok."),
        (z, "03", "Approve", "Complete the checks and explicitly approve the post."),
        (w, "04", "Handoff", "Preview a Sandbox draft handoff receipt — nothing is sent."),
    ]
    for col, num, title, copy in steps:
        with col:
            st.markdown(
                f'<div class="card"><div class="eyebrow">{num}</div><h3>{title}</h3><p>{copy}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("## Honest by design")
    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            <div class="card">
              <span class="pill pill-preview">● Workflow preview</span>
              <h3>No live platform calls</h3>
              <p>This public build never contacts TikTok. The handoff step produces a readable
              receipt so a reviewer can see exactly what a real submission would carry.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="card">
              <span class="pill pill-ok">● Creator control</span>
              <h3>Final editing stays in TikTok</h3>
              <p>The intended integration uploads to the draft flow only. Publishing, scheduling,
              and final edits always happen inside TikTok, by the creator.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------------- Studio


def render_studio():
    page_header("Create", "Studio", "Prepare one finished video for a deliberate, creator-approved TikTok draft handoff.")
    version_caption()
    progress_strip()

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("### 1 · Video")
        source = st.segmented_control("Source", ["Sample library", "Upload MP4"], default="Sample library")
        uploaded = None
        if source == "Upload MP4":
            uploaded = st.file_uploader(
                "Choose a finished vertical video",
                type=["mp4"],
                help="MP4 only. This public build keeps uploads in session memory and never sends them anywhere.",
            )
            if uploaded is not None:
                st.video(uploaded)

        if st.button("Use this video", type="primary", use_container_width=True):
            if source == "Sample library":
                st.session_state.asset = sample_asset()
                st.session_state.reviewed = True

            elif uploaded is None:
                st.warning("Choose an MP4 to continue.")
            else:
                data = uploaded.getvalue()
                st.session_state.asset = {
                    "filename": uploaded.name,
                    "title": Path(uploaded.name).stem.replace("-", " ").replace("_", " ").title(),
                    "size_mb": round(len(data) / (1024 * 1024), 2),
                    "duration": None,
                    "fingerprint": hashlib.sha256(data).hexdigest()[:16],
                    "source": "Direct upload",
                    "video_data": data,
                }
                st.session_state.reviewed = True


        asset = st.session_state.asset
        st.write("")
        if asset:
            if asset.get("path"):
                st.video(asset["path"], muted=True)
            elif asset.get("video_data"):
                st.video(asset["video_data"])
            duration = f" · {asset['duration']}" if asset.get("duration") else ""
            st.markdown(
                f"""
                <div class="card">
                  <span class="pill pill-ok">● Ready for review</span>
                  <h3>{asset['title']}</h3>
                  <p>{asset['filename']}{duration} · {asset['size_mb']} MB · source: {asset['source']}<br>
                  Asset ID <code>{asset['fingerprint']}</code></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="card"><span class="pill pill-neutral">No video selected</span>'
                "<h3>Start with a finished cut</h3><p>Use the bundled sample for a clean walkthrough, "
                "or upload your own finished MP4.</p></div>",
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("### 2 · Review & 3 · Approve")
        with st.form("post_review"):
            account = st.selectbox("Publish as", ["Creator (primary)", "Studio brand", "Personal creator"])
            caption = st.text_area(
                "Caption",
                "The night routine that turned a hard season into a repeatable system.",
                max_chars=CAPTION_MAX,
                height=120,
                help="This caption accompanies the creator-approved video.",
            )
            st.markdown("#### Final checks")
            rights = st.checkbox("I have the rights and permission to publish this video")
            reviewed = st.checkbox("I reviewed the account and description")
            policy = st.checkbox("This post follows TikTok and workspace content policies")
            control = st.checkbox("I understand final editing and posting continue in TikTok")
            consent = st.checkbox("I approve sending this video to TikTok drafts")
            submitted = st.form_submit_button("Approve for handoff", type="primary", use_container_width=True)

        if submitted:
            if not st.session_state.asset:
                st.warning("Select a video before approving.")
            elif not caption.strip():
                st.warning("Add a caption before approving.")
            elif not all([rights, reviewed, policy, control, consent]):
                st.warning("Complete every final check to approve this post.")
            else:
                item = {
                    **st.session_state.asset,
                    "account": account,
                    "caption": caption.strip(),
                    "approved_at": utc_now(),
                }
                st.session_state.queue.insert(0, item)
                st.success("Approved. Open **Publish** to preview the draft handoff.")
                st.button("Go to Publish", type="primary", on_click=goto, args=("Publish",))


# ------------------------------------------------------------------------ Publish


def render_publish():
    page_header("Publish", "Publish", "Only creator-approved posts appear here. Each handoff is previewed one post at a time.")
    version_caption()

    a, b, c = st.columns(3)
    for col, label, value in [
        (a, "Approved", str(len(st.session_state.queue))),
        (b, "Handoffs this session", str(st.session_state.sent_count)),
        (c, "Destination", "TikTok drafts"),
    ]:
        with col:
            st.markdown(
                f'<div class="stat"><div class="stat-label">{label}</div><div class="stat-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    if not st.session_state.queue:
        st.write("")
        st.markdown(
            '<div class="card"><span class="pill pill-neutral">Queue is clear</span>'
            "<h3>No approved posts yet</h3><p>Open Studio, choose a finished cut, review the details, "
            "and approve it for handoff.</p></div>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.button("Go to Studio", type="primary", on_click=goto, args=("Studio",))
        return

    st.markdown("## Ready to hand off")
    for index, item in enumerate(st.session_state.queue):
        with st.container(border=True):
            left, right = st.columns([.66, .34])
            with left:
                st.markdown('<span class="pill pill-ok">● Creator approved</span>', unsafe_allow_html=True)
                st.markdown(f"### {item['title']}")
                duration = f" · {item['duration']}" if item.get("duration") else ""
                st.write(f"**{item['account']}**{duration}")
                st.write(item["caption"])
                st.caption(f"Approved {item['approved_at']} · asset {item['fingerprint']}")
            with right:
                st.markdown("#### TikTok drafts")
                st.markdown('<span class="pill pill-preview">● Sandbox preview</span>', unsafe_allow_html=True)
                st.write("Final editing and posting remain in TikTok.")
                if st.button("Preview draft handoff", type="primary", key=f"send_{index}", use_container_width=True):
                    st.session_state.sent_count += 1
                    st.session_state.receipt = {
                        "Post": item["title"],
                        "Account": item["account"],
                        "Caption": item["caption"],
                        "Destination": "TikTok draft / inbox flow",
                        "Requested product": "Content Posting API",
                        "Requested scope": "video.upload",
                        "Website domain": WEBSITE_DOMAIN,
                        "Creator control": "Final editing and posting remain in TikTok",
                        "Integration status": "Preview — no request was sent to TikTok",
                        "Preview generated": utc_now(),
                    }
                    st.rerun()

    if st.session_state.receipt:
        st.markdown("## Handoff receipt")
        receipt = st.session_state.receipt
        st.markdown(
            f"""
            <div class="receipt">
              <span class="pill pill-preview">● Preview · no TikTok request made</span>
              <h3>{receipt['Post']}</h3>
              <p class="note">This receipt previews what a real, creator-initiated submission would
              carry. Nothing was sent to TikTok. In production,
              the creator continues final editing and posting inside TikTok.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.json(receipt)
        left, right = st.columns(2)
        with left:
            st.button(
                "View terms & privacy",
                use_container_width=True,
                on_click=goto,
                args=("Legal",),
            )
        with right:
            st.button(
                "Prepare another post",
                type="primary",
                use_container_width=True,
                on_click=goto,
                args=("Studio",),
            )


# -------------------------------------------------------------------------- Legal


def render_legal():
    page_header("Legal", "Terms & Privacy", "The policies for the EM Posting creator workflow product.")
    version_caption()
    policy = st.query_params.get("policy")
    if policy == "terms":
        st.markdown(TERMS)
        st.link_button("View Privacy Policy", f"{WEBSITE_URL}/?page=legal&policy=privacy")
    elif policy == "privacy":
        st.markdown(PRIVACY)
        st.link_button("View Terms of Service", f"{WEBSITE_URL}/?page=legal&policy=terms")
    else:
        terms_tab, privacy_tab = st.tabs(["Terms of Service", "Privacy Policy"])
        with terms_tab:
            st.markdown(TERMS)
        with privacy_tab:
            st.markdown(PRIVACY)


# --------------------------------------------------------------------------- Shell


init_state()

NAV_ITEMS = ["Home", "Studio", "Publish", "Legal"]
if "nav" not in st.session_state:
    requested_page = st.query_params.get("page", "home").lower()
    st.session_state.nav = "Legal" if requested_page == "legal" else "Home"

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">✦</span>EM Posting</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ws-chip"><b>{WORKSPACE}</b><br><span style="color:#a1a1aa">Creator workspace · Owner</span></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.radio("Workspace navigation", NAV_ITEMS, key="nav", label_visibility="collapsed")
    st.divider()
    st.caption("Creator-controlled publishing")
    st.caption(f"{APP_VERSION} · workflow preview")

page = st.session_state.nav
if page == "Studio":
    render_studio()
elif page == "Publish":
    render_publish()
elif page == "Legal":
    render_legal()
else:
    render_home()
