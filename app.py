import hashlib
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

import streamlit as st

APP_VERSION = "v0.7.0"
APP_NAME = "EM Posting"
TAGLINE = "From final cut to creator-ready draft."

SHORT_DESCRIPTION = "Creator workspace for reviewing finished videos and sending approved posts to TikTok drafts."

APP_REVIEW_EXPLANATION = (
    "EM Posting is a creator workflow app for preparing finished short-form videos for TikTok. "
    "An authorized creator selects a completed MP4, reviews the account, caption, metadata, and content checks, "
    "then explicitly approves the video for TikTok's draft flow. The requested Content Posting API integration "
    "reduces manual file transfer while preserving human review and final posting control in TikTok. The initial "
    "workspace is used by the Eczema Mitten / Reuben Eczema creator team, but the product is designed as a focused "
    "creator publishing workspace rather than a mass-posting service. It does not scrape data, automate engagement, "
    "or publish spam."
)

SCOPE_JUSTIFICATION = dedent(
    """
    Requested product: TikTok Content Posting API
    Requested scope: video.upload

    EM Posting needs video.upload to transfer one creator-approved MP4 and its reviewed metadata into TikTok's draft/inbox workflow. The creator deliberately initiates each handoff and completes final editing and posting in TikTok. The app does not need follower lists, analytics, comments, direct messages, engagement automation, or broad account-management permissions.
    """
).strip()

TERMS = dedent(
    """
    # Terms of Service

    **Last updated: July 2026**

    EM Posting is a creator workflow product for preparing, reviewing, and handing approved short-form videos to supported social platforms.

    ## Account and workspace use
    You may use EM Posting only for workspaces and creator accounts you are authorized to manage. You are responsible for the videos, captions, metadata, approvals, and account selections made in your workspace.

    ## Creator approval
    EM Posting is designed around deliberate human review. A creator or authorized team member must review each post before initiating a platform handoff. The service may not be used for spam, deceptive automation, unauthorized account access, or attempts to bypass platform controls.

    ## Platform services
    Platform integrations remain subject to each platform's terms, permissions, technical limits, and review requirements. A successful handoff does not guarantee publication. Final editing and posting may continue inside the destination platform.

    ## Content rights
    You must have the rights and permissions required to upload and publish the content you submit.

    ## Availability
    Features may change as integrations mature. Preview features are identified in the interface and must not be represented as completed production integrations.

    ## Contact
    Product and policy questions may be sent to eczemamitten@gmail.com while EM Posting is in its initial creator pilot.
    """
).strip()

PRIVACY = dedent(
    """
    # Privacy Policy

    **Last updated: July 2026**

    EM Posting is a creator workflow product. This policy describes the information the service may process to prepare and hand creator-approved posts to supported platforms.

    ## Information processed
    EM Posting may process creator account labels, finished video files, captions, hashtags, content categories, approval choices, file metadata, and workflow activity such as review and handoff timestamps.

    ## How information is used
    This information is used to display the creator workspace, preserve review decisions, prepare platform handoffs, and show workflow receipts to authorized users.

    ## Platform data
    The requested TikTok integration is limited to content upload functionality. EM Posting does not request TikTok direct messages, comments, follower lists, or unrelated account data.

    ## Storage
    The public review build uses session-only state and does not permanently store uploaded videos. A production service may temporarily process files and retain workflow records only as needed to provide the creator-requested service.

    ## Sharing
    Content is sent to a platform only after an authorized creator initiates the handoff. EM Posting does not sell personal information.

    ## Security
    Production credentials and access tokens must be stored in private deployment secrets and are never included in the public source repository.

    ## Contact
    Privacy questions may be sent to eczemamitten@gmail.com during the initial pilot.
    """
).strip()

st.set_page_config(page_title=APP_NAME, page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    :root { --ink:#171a22; --muted:#6e7280; --line:#e6e5e1; --paper:#f7f7f4; --card:#ffffff; --violet:#7057ff; --violet2:#9c7cff; --green:#167c5a; }
    .stApp { background: var(--paper); color: var(--ink); }
    .block-container { max-width: 1240px; padding-top: 2.2rem; padding-bottom: 4rem; }
    section[data-testid="stSidebar"] { background: #111218; border-right: 1px solid rgba(255,255,255,.08); }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #f5f4ff !important; }
    section[data-testid="stSidebar"] label { color: #efeff5 !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] label { padding: .34rem .45rem; border-radius: 10px; }
    h1, h2, h3 { letter-spacing: -.035em; }
    h1 { font-size: 2.55rem !important; }
    .brand { font-size:1.18rem; font-weight:850; letter-spacing:-.04em; color:white; }
    .brand-mark { display:inline-grid; place-items:center; width:29px; height:29px; margin-right:8px; border-radius:9px; background:linear-gradient(135deg,#7057ff,#ba76ff); color:white; }
    .workspace-chip { margin-top:.75rem; padding:.72rem .8rem; border:1px solid rgba(255,255,255,.12); background:rgba(255,255,255,.06); border-radius:12px; color:#efeff5; font-size:.83rem; }
    .eyebrow { text-transform:uppercase; letter-spacing:.16em; font-size:.7rem; font-weight:800; color:#7057ff; margin-bottom:.65rem; }
    .hero { padding:2.35rem 2.45rem; border-radius:26px; color:white; background:radial-gradient(circle at 80% 10%,rgba(183,132,255,.52),transparent 35%),linear-gradient(135deg,#171825 0%,#31275c 58%,#7057ff 100%); box-shadow:0 28px 70px rgba(48,36,105,.18); overflow:hidden; }
    .hero h1 { color:white; font-size:3.35rem !important; line-height:1.01; max-width:760px; margin:.2rem 0 .85rem; }
    .hero p { color:#e9e6ff; font-size:1.08rem; line-height:1.65; max-width:760px; }
    .hero-badge { display:inline-block; padding:.4rem .7rem; border:1px solid rgba(255,255,255,.18); background:rgba(255,255,255,.1); border-radius:999px; font-size:.76rem; margin-right:.35rem; }
    .card { background:var(--card); border:1px solid var(--line); border-radius:18px; padding:1.2rem 1.25rem; box-shadow:0 10px 28px rgba(24,23,34,.045); height:100%; }
    .card h3 { margin:.1rem 0 .4rem; font-size:1.08rem; }
    .card p { color:var(--muted); font-size:.91rem; line-height:1.55; }
    .stat { background:white; border:1px solid var(--line); border-radius:16px; padding:1rem 1.1rem; min-height:102px; }
    .stat-label { color:var(--muted); font-size:.72rem; text-transform:uppercase; letter-spacing:.1em; font-weight:750; }
    .stat-value { font-size:1.48rem; font-weight:850; margin-top:.35rem; letter-spacing:-.04em; }
    .status { display:inline-flex; align-items:center; gap:.38rem; font-size:.76rem; font-weight:750; border-radius:999px; padding:.33rem .58rem; }
    .status-ready { color:#116247; background:#e7f6ef; }
    .status-preview { color:#665114; background:#fff4cf; }
    .status-neutral { color:#555969; background:#eff0f3; }
    .flow { display:flex; align-items:center; gap:.65rem; flex-wrap:wrap; margin:.7rem 0 1rem; }
    .flow-node { padding:.6rem .78rem; border-radius:12px; border:1px solid var(--line); background:white; font-size:.82rem; font-weight:760; }
    .flow-arrow { color:#9b9da7; font-weight:800; }
    .video-shell { padding:.75rem; background:#12131a; border-radius:20px; border:1px solid #292b35; }
    .receipt { padding:1.2rem; border-radius:16px; border:1px solid #bde5d4; background:linear-gradient(135deg,#edfbf5,#f9fffc); }
    .small-note { color:var(--muted); font-size:.82rem; }
    [data-testid="stForm"] { background:white; border:1px solid var(--line); border-radius:18px; padding:1.2rem; }
    div[data-testid="stButton"] > button[kind="primary"], div[data-testid="stFormSubmitButton"] > button[kind="primary"] { background:linear-gradient(135deg,#6550ee,#8a62ff); border:none; }
    div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button { border-radius:11px; min-height:2.65rem; font-weight:700; }
    [data-testid="stFileUploader"] { background:#fbfbfa; border-radius:14px; padding:.35rem; }
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
        "events": [],
        "handoff_receipt": None,
        "sent_count": 0,
        "workspace": "Reuben Creator Studio",
        "review_started": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_event(action, detail, status="Complete"):
    st.session_state.events.insert(0, {"Time": utc_now(), "Action": action, "Detail": detail, "Status": status})


def fingerprint(uploaded_file):
    data = uploaded_file.getvalue()
    return hashlib.sha256(data).hexdigest()[:16], len(data)


def sample_asset():
    sample_path = Path(__file__).parent / "assets" / "sample_creator_video.mp4"
    data = sample_path.read_bytes()
    return {
        "filename": "founder-night-routine.mp4",
        "title": "A founder's night routine",
        "size_mb": round(len(data) / (1024 * 1024), 2),
        "duration": "00:08",
        "fingerprint": hashlib.sha256(data).hexdigest()[:16],
        "source": "Creator library",
        "status": "Ready for review",
        "path": str(sample_path),
    }


def version_caption():
    st.caption(f"{APP_VERSION} · creator publishing workspace")


def page_header(eyebrow, title, subtitle):
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.write(subtitle)
    version_caption()


def progress_strip():
    has_asset = st.session_state.asset is not None
    reviewed = st.session_state.review_started or bool(st.session_state.queue)
    approved = bool(st.session_state.queue)
    sent = st.session_state.sent_count > 0
    stages = [("1", "Select", has_asset), ("2", "Review", reviewed), ("3", "Approve", approved), ("4", "Send", sent)]
    html = '<div class="flow">'
    for index, (number, label, done) in enumerate(stages):
        status = "✓" if done else number
        html += f'<span class="flow-node">{status} &nbsp; {label}</span>'
        if index < len(stages) - 1:
            html += '<span class="flow-arrow">→</span>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_home():
    st.markdown(
        """
        <div class="hero">
          <span class="hero-badge">creator workspace</span><span class="hero-badge">review-first publishing</span>
          <h1>Ship the post.<br>Keep the final say.</h1>
          <p>EM Posting gives creators one calm place to review finished videos, lock the caption, confirm the destination, and hand an approved post to TikTok drafts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    version_caption()
    st.write("")
    a, b, c, d = st.columns(4)
    stats = [
        (a, "Workspace", st.session_state.workspace),
        (b, "Ready to review", "1 video" if not st.session_state.asset else "Active"),
        (c, "Approved queue", str(len(st.session_state.queue))),
        (d, "TikTok connection", "Preview mode"),
    ]
    for col, label, value in stats:
        with col:
            st.markdown(f'<div class="stat"><div class="stat-label">{label}</div><div class="stat-value">{value}</div></div>', unsafe_allow_html=True)

    st.markdown("## Today in your studio")
    left, right = st.columns([1.35, .65])
    with left:
        st.markdown(
            """
            <div class="card">
              <span class="status status-ready">● Ready for review</span>
              <h3>A founder's night routine</h3>
              <p>Founder story · 00:08 · vertical MP4<br>Final cut is waiting for caption and destination review.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.button("Open in Studio", type="primary", use_container_width=True, on_click=lambda: st.session_state.update(nav="Studio"))
    with right:
        st.markdown(
            """
            <div class="card">
              <span class="status status-preview">● Connection preview</span>
              <h3>TikTok</h3>
              <p>Draft handoff is designed for human final review. Production OAuth will be configured after platform approval.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## A publishing flow built around creator control")
    x, y, z = st.columns(3)
    for col, icon, title, copy in [
        (x, "01", "Bring the final cut", "Choose a finished MP4 from your creator library or upload one directly."),
        (y, "02", "Review the post", "Lock the account, caption, hashtags, category, and content confirmations."),
        (z, "03", "Send to drafts", "Initiate a single approved handoff, then finish editing and posting in TikTok."),
    ]:
        with col:
            st.markdown(f'<div class="card"><div class="eyebrow">{icon}</div><h3>{title}</h3><p>{copy}</p></div>', unsafe_allow_html=True)


def render_studio():
    page_header("Create", "Publishing Studio", "Prepare one finished short-form video for a deliberate, creator-approved platform handoff.")
    progress_strip()

    left, right = st.columns([1.02, .98], gap="large")
    with left:
        st.markdown("### Video")
        source = st.segmented_control("Source", ["Creator library", "Upload MP4"], default="Creator library")
        uploaded = None
        if source == "Upload MP4":
            uploaded = st.file_uploader("Choose a finished vertical video", type=["mp4"], help="MP4 only. The public build keeps uploads in session memory.")
            if uploaded:
                st.video(uploaded)
        if st.button("Use this video", type="primary", use_container_width=True):
            if source == "Creator library":
                st.session_state.asset = sample_asset()
                st.session_state.review_started = True
                add_event("Video selected", "A founder's night routine")
            elif uploaded is None:
                st.error("Choose an MP4 first.")
            else:
                digest, size = fingerprint(uploaded)
                st.session_state.asset = {
                    "filename": uploaded.name,
                    "title": Path(uploaded.name).stem.replace("-", " ").replace("_", " ").title(),
                    "size_mb": round(size / (1024 * 1024), 2),
                    "duration": None,
                    "fingerprint": digest,
                    "source": "Direct upload",
                    "status": "Ready for review",
                    "video_data": uploaded.getvalue(),
                }
                st.session_state.review_started = True
                add_event("Video uploaded", uploaded.name)

        if st.session_state.asset:
            asset = st.session_state.asset
            st.write("")
            if asset.get("path"):
                st.video(asset["path"], autoplay=True, muted=True)
            elif asset.get("video_data"):
                st.video(asset["video_data"])
            duration_copy = f" · {asset['duration']}" if asset.get("duration") else ""
            st.markdown(
                f"""
                <div class="card">
                  <span class="status status-ready">● {asset['status']}</span>
                  <h3>{asset['title']}</h3>
                  <p>{asset['filename']}{duration_copy} · {asset['size_mb']} MB<br>Asset ID <code>{asset['fingerprint']}</code></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="card"><span class="status status-neutral">No video selected</span><h3>Start with a finished cut</h3><p>Select the sample from the creator library for the review walkthrough, or upload your own MP4.</p></div>', unsafe_allow_html=True)

    with right:
        st.markdown("### Post details")
        with st.form("post_review"):
            title = st.text_input("Internal title", "A founder's night routine")
            account = st.selectbox("Publish as", ["Reuben Creator", "Studio Brand", "Personal Creator"])
            category = st.selectbox("Content category", ["Founder story", "Education", "Product story", "Routine", "Community"])
            caption = st.text_area("Caption", "The night routine that helped me turn a difficult season into a repeatable system. Sharing what finally made the evenings feel manageable.", height=130)
            hashtags = st.text_input("Hashtags", "#founderstory #creatordiary #nighttimeroutine")
            st.markdown("#### Final checks")
            rights = st.checkbox("I have the rights and permission to publish this video")
            metadata = st.checkbox("I reviewed the account, caption, and hashtags")
            policy = st.checkbox("This post follows TikTok and workspace content policies")
            control = st.checkbox("I understand final editing and posting continue in TikTok")
            consent = st.checkbox("I approve sending this video to TikTok drafts")
            submitted = st.form_submit_button("Approve for publishing", type="primary", use_container_width=True)

        if submitted:
            if not st.session_state.asset:
                st.error("Select a video before approving the post.")
            elif not all([rights, metadata, policy, control, consent]):
                st.error("Complete every final check to approve this post.")
            else:
                item = {
                    **st.session_state.asset,
                    "title": title,
                    "account": account,
                    "category": category,
                    "caption": caption,
                    "hashtags": hashtags,
                    "queued_at": utc_now(),
                    "creator_consent": "Confirmed",
                    "handoff_status": "Approved",
                }
                st.session_state.queue.insert(0, item)
                st.session_state.handoff_receipt = None
                add_event("Post approved", f"{title} → {account}")
                st.success("Approved. Your post is ready in Publish Queue.")


def render_library():
    page_header("Library", "Content Library", "A focused home for finished cuts that are ready to become posts.")
    q = st.text_input("Search finished videos", placeholder="Search by title, filename, or category")
    matches = not q or q.lower() in "a founder's night routine founder story founder-night-routine.mp4".lower()
    st.caption(f"{1 if matches else 0} finished video · public product preview")
    st.write("")
    if not matches:
        st.markdown('<div class="card"><span class="status status-neutral">No results</span><h3>No finished videos match that search</h3><p>Try a title, filename, or content category.</p></div>', unsafe_allow_html=True)
        return
    left, middle, right = st.columns([.42, .35, .23])
    with left:
        path = str(Path(__file__).parent / "assets" / "sample_creator_video.mp4")
        st.video(path, muted=True)
    with middle:
        st.markdown(
            """
            <div class="card">
              <span class="status status-ready">● Final cut</span>
              <h3>A founder's night routine</h3>
              <p>Founder story<br>Vertical MP4 · 00:08<br>Added to creator library</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="card"><div class="stat-label">Publishing status</div><div class="stat-value">Ready</div><p>No active handoff. Open this cut in Studio when the caption is ready.</p></div>', unsafe_allow_html=True)
        def open_library_asset():
            st.session_state.asset = sample_asset()
            st.session_state.review_started = True
            st.session_state.nav = "Studio"
            add_event("Video opened", "A founder's night routine")
        st.button("Review in Studio", type="primary", use_container_width=True, on_click=open_library_asset)


def render_publish():
    page_header("Publish", "Publish Queue", "Only creator-approved posts appear here. Every handoff is initiated one post at a time.")
    ready = len(st.session_state.queue)
    a, b, c = st.columns(3)
    for col, label, value in [(a, "Approved", str(ready)), (b, "Sent this session", str(st.session_state.sent_count)), (c, "Destination", "TikTok drafts")]:
        with col:
            st.markdown(f'<div class="stat"><div class="stat-label">{label}</div><div class="stat-value">{value}</div></div>', unsafe_allow_html=True)

    if not st.session_state.queue:
        st.write("")
        st.markdown('<div class="card"><span class="status status-neutral">Queue is clear</span><h3>No approved posts yet</h3><p>Open Publishing Studio, select a final cut, review the post details, and approve it for publishing.</p></div>', unsafe_allow_html=True)
        st.button("Create a post", type="primary", on_click=lambda: st.session_state.update(nav="Studio"))
        return

    st.markdown("## Ready to send")
    for index, item in enumerate(st.session_state.queue):
        with st.container(border=True):
            left, right = st.columns([.72, .28])
            with left:
                st.markdown('<span class="status status-ready">● Creator approved</span>', unsafe_allow_html=True)
                st.markdown(f"### {item['title']}")
                duration_copy = f" · {item['duration']}" if item.get("duration") else ""
                st.write(f"**{item['account']}** · {item['category']}{duration_copy}")
                st.write(item["caption"])
                st.caption(f"{item['hashtags']}  ·  Approved {item['queued_at']}")
            with right:
                st.markdown("#### TikTok drafts")
                st.write("Final editing and posting remain in TikTok.")
                st.markdown('<span class="status status-preview">Preview integration</span>', unsafe_allow_html=True)
                if st.button("Send to TikTok drafts", type="primary", key=f"send_{index}", use_container_width=True):
                    item["handoff_status"] = "Preview handoff complete"
                    st.session_state.sent_count += 1
                    st.session_state.handoff_receipt = {
                        "Post": item["title"],
                        "Creator": item["account"],
                        "Destination": "TikTok draft / inbox flow",
                        "Requested scope": "video.upload",
                        "Creator control": "Final editing and posting remain in TikTok",
                        "Integration status": "Preview — no TikTok request made",
                        "Preview generated": utc_now(),
                    }
                    add_event("Draft handoff preview", f"{item['title']} → TikTok drafts")
                    st.rerun()

    if st.session_state.handoff_receipt:
        st.markdown("## Handoff receipt")
        receipt = st.session_state.handoff_receipt
        st.markdown(
            f"""
            <div class="receipt">
              <span class="status status-neutral">Preview · no TikTok request made</span>
              <h3>{receipt['Post']}</h3>
              <p>This receipt previews the information EM Posting will preserve after a creator-initiated handoff. No request was sent to TikTok. In production, the creator continues final editing and posting inside TikTok.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.json(receipt)


def render_activity():
    page_header("Workspace", "Activity", "A lightweight record of creator decisions made during this session.")
    if st.session_state.events:
        st.dataframe(st.session_state.events, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="card"><span class="status status-neutral">No activity yet</span><h3>Your workflow history starts here</h3><p>Select a video, approve a post, or run a draft handoff preview to create activity.</p></div>', unsafe_allow_html=True)


def render_connections():
    page_header("Settings", "Connections", "Manage where approved creator posts can go.")
    left, right = st.columns([1, 1])
    with left:
        st.markdown(
            """
            <div class="card">
              <span class="status status-preview">● Approval pending</span>
              <h3>TikTok</h3>
              <p>Content Posting API · requested scope <code>video.upload</code><br>Designed for draft/inbox handoff with creator final control.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Connect TikTok after approval", disabled=True, use_container_width=True)
    with right:
        st.markdown(
            """
            <div class="card">
              <span class="status status-neutral">Coming later</span>
              <h3>Additional channels</h3>
              <p>EM Posting is starting with a focused TikTok draft workflow. New destinations will be evaluated without turning the product into a bulk publisher.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.info("Public review environment: OAuth credentials and production tokens are intentionally not configured.")



def render_terms():
    page_header("Legal", "Terms of Service", "Terms for the EM Posting creator workflow product.")
    st.markdown(TERMS)


def render_privacy():
    page_header("Legal", "Privacy Policy", "How EM Posting handles creator workflow information.")
    st.markdown(PRIVACY)


init_state()

NAV_ITEMS = ["Home", "Studio", "Library", "Publish", "Activity", "Connections", "Terms", "Privacy"]
if "nav" not in st.session_state:
    st.session_state.nav = "Home"

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">✦</span>EM Posting</div>', unsafe_allow_html=True)
    st.markdown('<div class="workspace-chip"><b>Reuben Creator Studio</b><br><span style="color:#aaa9b5">Creator workspace · Owner</span></div>', unsafe_allow_html=True)
    st.write("")
    st.radio("Workspace navigation", NAV_ITEMS, key="nav", label_visibility="collapsed")
    st.divider()
    st.caption("Creator-controlled publishing")
    st.caption(f"{APP_VERSION} · public product preview")

page = st.session_state.nav
if page == "Home":
    render_home()
elif page == "Studio":
    render_studio()
elif page == "Library":
    render_library()
elif page == "Publish":
    render_publish()
elif page == "Activity":
    render_activity()
elif page == "Connections":
    render_connections()
elif page == "Terms":
    render_terms()
else:
    render_privacy()
