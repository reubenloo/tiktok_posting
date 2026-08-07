import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

import streamlit as st
import httpx

APP_VERSION = "v0.11.2"
APP_NAME = "EM Posting"
TAGLINE = "One calm place to take a finished video from final cut to an approved TikTok draft."
APP_ICON_PATH = Path(__file__).parent / "assets" / "em-posting-icon.png"

# Externally-facing origin for browser links (Home, legal, sign-in). Production must set
# EM_POSTING_PUBLIC_URL to an owned custom domain that does not contain "tiktok"; this Render URL
# is only a documented Sandbox/local verification fallback. Do not hard-code it anywhere else.
PUBLIC_URL_FALLBACK = "https://posting-app-gvtf.onrender.com"
CONTACT_EMAIL = "contact@eczemamitten.com"

# Creator post limit. TikTok developer-form limits belong in README, not the product UI.
CAPTION_MAX = 2200

WORKSPACE = "Creator Studio"

SHORT_DESCRIPTION = (
    "Creator workspace for reviewing finished videos and sending approved posts to TikTok drafts."
)

# Kept in sync with the submission copy in README.md (App review explanation, under 1000 chars).
APP_REVIEW_EXPLANATION = (
    "EM Posting uses Login Kit and TikTok's Content Posting API to upload one creator-approved MP4 "
    "to the authorized creator's TikTok draft/inbox flow. The creator signs in with TikTok and "
    "grants user.info.basic and video.upload. In EM Posting, the creator selects or uploads a "
    "finished MP4, previews it, confirms content rights and policy compliance, and explicitly "
    "approves the transfer. EM Posting initializes the upload through "
    "/v2/post/publish/inbox/video/init/ using FILE_UPLOAD and transfers the MP4 to TikTok's "
    "provided upload URL. The creator then opens the notification in TikTok to complete the "
    "caption, final editing, and posting. EM Posting does not directly publish, bulk post, scrape "
    "data, or automate engagement."
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
    Features may change as integrations mature. TikTok Sandbox connections and draft uploads are
    available only to authorized pilot users. A successful draft upload does not guarantee that the
    creator will complete or publish the post inside TikTok.

    ## Contact
    Product and policy questions may be sent to contact@eczemamitten.com while EM Posting is in its
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
    The TikTok integration uses Login Kit to access the connected creator's basic identity and uses
    video.upload only after explicit approval to transfer one MP4 to the draft/inbox flow. EM Posting
    does not request direct messages, comments, follower lists, analytics, or unrelated account data.

    ## Storage
    This pilot uses session-only application state and does not permanently store uploaded videos.
    TikTok access and refresh tokens are kept server-side for the active pilot session and are never
    exposed in the browser or public source repository. Sessions can be disconnected at any time.

    ## Sharing
    Content would be sent to a platform only after an authorized creator initiates the handoff. EM
    Posting does not sell personal information.

    ## Security
    Any future production credentials must be stored in private deployment secrets and are never
    included in the public source repository.

    ## Contact
    Privacy questions may be sent to contact@eczemamitten.com during the initial pilot.
    """
).strip()

st.set_page_config(
    page_title=APP_NAME,
    page_icon=str(APP_ICON_PATH),
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
    .brand-mark { display:inline-block; width:28px; height:28px; margin-right:9px; border-radius:9px; vertical-align:-8px; }
    .brand-mark img { display:block; width:28px; height:28px; border-radius:9px; }
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
    .pill-accent { color:var(--accent); background:var(--accent-soft); }
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
    .project-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap:1rem; }
    .project-card { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1rem; cursor:pointer; transition:border-color .15s, box-shadow .15s; }
    .project-card:hover { border-color:var(--accent); box-shadow:0 8px 24px rgba(79,70,229,.12); }
    .project-thumb { width:100%; aspect-ratio:9/16; max-height:180px; object-fit:cover; border-radius:10px; background:#e0e0e0; margin-bottom:.7rem; }
    .project-title { font-weight:700; font-size:.95rem; margin:0 0 .25rem; }
    .project-meta { font-size:.78rem; color:var(--muted); }
    .activity-item { display:flex; align-items:flex-start; gap:.7rem; padding:.65rem 0; border-bottom:1px solid var(--line); }
    .activity-item:last-child { border-bottom:none; }
    .activity-dot { width:8px; height:8px; border-radius:50%; margin-top:6px; flex-shrink:0; }
    .activity-dot.review { background:var(--accent); }
    .activity-dot.approve { background:var(--ok); }
    .activity-dot.upload { background:#2563eb; }
    .activity-dot.create { background:#8b5cf6; }
    .activity-text { flex:1; font-size:.85rem; line-height:1.4; }
    .activity-time { font-size:.72rem; color:var(--faint); white-space:nowrap; }
    .checklist-item { display:flex; align-items:center; gap:.5rem; padding:.4rem 0; }
    .checklist-done { color:var(--ok); }
    .checklist-pending { color:var(--faint); }
    </style>
    """,
    unsafe_allow_html=True,
)


def utc_now():
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


def short_time():
    return datetime.now(UTC).strftime("%H:%M UTC")


def deduplicate_queue(queue):
    unique = []
    fingerprints = set()
    for item in queue:
        fingerprint = item.get("fingerprint")
        if fingerprint and fingerprint in fingerprints:
            continue
        unique.append(item)
        if fingerprint:
            fingerprints.add(fingerprint)
    return unique


# Bundled sample-project records deliberately refer to the one shipped sample asset.  Do not add
# cosmetic rows that claim different files or durations: every public project must preview and
# hand off the asset named in its record.
def get_sample_projects():
    return [
        {
            "id": "proj-001",
            "title": "A founder's night routine",
            "filename": "founder-night-routine.mp4",
            "duration": "00:08",
            "size_mb": 0.11,
            "creator": "Creator (primary)",
            "status": "ready",
            "caption": "The night routine that turned a hard season into a repeatable system.",
            "created": "2026-08-02 14:30 UTC",
            "reviewed": False,
            "approved": False,
            "checks": {"rights": False, "reviewed": False, "policy": False, "control": False, "consent": False},
            "is_sample": True,
        },

    ]


def init_state():
    defaults = {
        "asset": None,
        "queue": [],
        "receipt": None,
        "receipts": [],
        "sent_count": 0,
        "reviewed": False,
        "projects": get_sample_projects(),
        "current_project": None,
        "activity_log": [
            {"type": "create", "text": "Sample project 'A founder's night routine' added to library", "time": "14:30 UTC"},
        ],
        "readiness_queue": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    st.session_state.queue = deduplicate_queue(st.session_state.queue)
    if st.session_state.receipt and not st.session_state.receipts:
        st.session_state.receipts.append(st.session_state.receipt)


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
    st.caption(f"{APP_VERSION} · creator publishing workspace · TikTok Sandbox")


def configured_public_url():
    """Configured externally-facing origin: EM_POSTING_PUBLIC_URL, else the documented fallback."""
    configured = os.getenv("EM_POSTING_PUBLIC_URL", "").strip().rstrip("/")
    return configured or PUBLIC_URL_FALLBACK


def public_base_url():
    """Configured public origin for all browser-facing links and OAuth entry points.

    This deliberately does not use the incoming request host: Login Kit sets its state cookie on
    the sign-in origin, so it must match the environment-derived callback origin exactly.
    """
    return configured_public_url()


def legal_url(policy):
    """Public URL for a directly linkable legal page (policy is 'terms' or 'privacy')."""
    return f"{public_base_url()}/?page=legal&policy={policy}"


def backend_origin():
    forwarded = st.context.headers.get("x-em-posting-origin")
    return forwarded or "http://127.0.0.1:10000"


def backend_cookies():
    return dict(st.context.cookies)


def backend_json(method, path, **kwargs):
    try:
        response = httpx.request(
            method,
            f"{backend_origin()}{path}",
            cookies=backend_cookies(),
            timeout=150,
            **kwargs,
        )
        payload = response.json()
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        return None, f"EM Posting could not reach its TikTok service: {exc}"
    if response.is_error:
        return None, payload.get("detail", f"TikTok service returned HTTP {response.status_code}")
    return payload, None


def tiktok_session():
    payload, error = backend_json("GET", "/api/tiktok/session")
    return payload if payload and payload.get("connected") else None, error


def should_show_empty_queue(queue, receipt):
    return not queue and not receipt


def is_duplicate_approval(queue, asset):
    fingerprint = (asset or {}).get("fingerprint")
    return bool(fingerprint) and any(item.get("fingerprint") == fingerprint for item in queue)


def tiktok_status_copy(status, fail_reason=None):
    if status == "SEND_TO_USER_INBOX":
        return "Inbox notification sent", "TikTok reports that the creator inbox notification was delivered. Open TikTok → Inbox to continue editing."
    if status == "PUBLISH_COMPLETE":
        return "Creator completed the post", "The creator opened TikTok's inbox flow and successfully posted from this upload."
    if status == "FAILED":
        reason = fail_reason or "TikTok did not provide a failure reason"
        return "TikTok processing failed", f"The transfer did not reach the creator inbox. TikTok reason: {reason}."
    if status == "PROCESSING_UPLOAD":
        return "TikTok is processing the upload", "No inbox notification is expected yet. Wait briefly, then refresh this status."
    return "Transfer accepted; delivery unconfirmed", "TikTok returned a publish ID, but inbox delivery is not confirmed yet. Refresh the status before checking TikTok."


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
    """Schedule navigation without mutating the sidebar widget state during a script run."""
    st.session_state.pending_nav = page


def project_asset(project):
    """Return the precise asset data represented by a project, for preview and final handoff."""
    if project.get("is_sample"):
        return sample_asset()
    return {
        "filename": project["filename"],
        "title": project["title"],
        "size_mb": project["size_mb"],
        "duration": project.get("duration"),
        "fingerprint": project["fingerprint"],
        "source": "Direct upload",
        "video_data": project["video_data"],
    }


def add_activity(activity_type, text):
    st.session_state.activity_log.insert(0, {
        "type": activity_type,
        "text": text,
        "time": short_time(),
    })
    if len(st.session_state.activity_log) > 50:
        st.session_state.activity_log = st.session_state.activity_log[:50]


def get_project_by_id(project_id):
    for p in st.session_state.projects:
        if p["id"] == project_id:
            return p
    return None


def update_project(project_id, updates):
    for i, p in enumerate(st.session_state.projects):
        if p["id"] == project_id:
            st.session_state.projects[i] = {**p, **updates}
            return st.session_state.projects[i]
    return None


# --------------------------------------------------------------------------- Home


def render_home():
    # Dashboard header with workspace stats
    st.markdown(
        f"""
        <div class="hero" style="padding:1.8rem 2rem;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
            <div>
              <span class="hero-badge">creator workspace</span>
              <h1 style="font-size:2.2rem !important;margin:.3rem 0 .5rem;">Welcome to {APP_NAME}</h1>
              <p style="font-size:.95rem;">{TAGLINE}</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    version_caption()

    # Quick stats row
    st.write("")
    cols = st.columns(4)
    total_projects = len(st.session_state.projects)
    ready_count = sum(1 for p in st.session_state.projects if p["status"] == "ready")
    in_review = sum(1 for p in st.session_state.projects if p["status"] == "in_review")
    approved_count = sum(1 for p in st.session_state.projects if p["status"] == "approved") + len(st.session_state.queue)

    stats = [
        (cols[0], "Projects", str(total_projects)),
        (cols[1], "Needs review", str(ready_count)),
        (cols[2], "In review", str(in_review)),
        (cols[3], "Ready for handoff", str(approved_count)),
    ]
    for col, label, value in stats:
        with col:
            st.markdown(
                f'<div class="stat"><div class="stat-label">{label}</div><div class="stat-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown("## Project library")
    st.write("Review finished videos and prepare them for platform handoff. Select a project to begin the review workflow.")

    # Project grid
    project_cols = st.columns(3)
    for idx, project in enumerate(st.session_state.projects):
        with project_cols[idx % 3]:
            status_pill = {
                "ready": '<span class="pill pill-neutral">● Needs review</span>',
                "in_review": '<span class="pill pill-preview">● In review</span>',
                "approved": '<span class="pill pill-ok">● Approved</span>',
            }.get(project["status"], '<span class="pill pill-neutral">● Unknown</span>')

            st.markdown(
                f"""
                <div class="card" style="margin-bottom:1rem;">
                  {status_pill}
                  <h3 style="margin-top:.5rem;">{project["title"]}</h3>
                  <p style="margin-bottom:.5rem;">{project["filename"]} · {project["duration"]} · {project["size_mb"]} MB</p>
                  <p style="font-size:.78rem;color:var(--faint);">Creator: {project["creator"]} · Added {project["created"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            def open_project(project_id=project["id"]):
                st.session_state.current_project = project_id
                goto("Review")

            st.button(
                "Open project",
                key=f"open_{project['id']}",
                use_container_width=True,
                on_click=open_project,
            )

    st.write("")

    # Recent activity section
    left, right = st.columns([1.5, 1])
    with left:
        st.markdown("## Quick actions")
        action_cols = st.columns(3)
        with action_cols[0]:
            st.button("📁 New project", use_container_width=True, on_click=goto, args=("Studio",))
        with action_cols[1]:
            st.button("✓ Review queue", use_container_width=True, on_click=goto, args=("Review",))
        with action_cols[2]:
            session, _ = tiktok_session()
            if session:
                st.button("📤 Handoff ready", type="primary", use_container_width=True, on_click=goto, args=("Handoff",))
            else:
                st.button("🔗 Connect TikTok", use_container_width=True, on_click=goto, args=("Handoff",))

        st.write("")
        st.markdown("### How it works")
        st.markdown(
            """
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:.8rem;">
              <div class="card" style="padding:.9rem;">
                <div class="eyebrow">01</div>
                <h3 style="font-size:.9rem;">Select</h3>
                <p style="font-size:.8rem;">Choose from the library or upload a finished MP4.</p>
              </div>
              <div class="card" style="padding:.9rem;">
                <div class="eyebrow">02</div>
                <h3 style="font-size:.9rem;">Review</h3>
                <p style="font-size:.8rem;">Check the account, write the caption, verify rights.</p>
              </div>
              <div class="card" style="padding:.9rem;">
                <div class="eyebrow">03</div>
                <h3 style="font-size:.9rem;">Approve</h3>
                <p style="font-size:.8rem;">Complete the checklist and confirm the post.</p>
              </div>
              <div class="card" style="padding:.9rem;">
                <div class="eyebrow">04</div>
                <h3 style="font-size:.9rem;">Handoff</h3>
                <p style="font-size:.8rem;">Send to TikTok drafts for final editing.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("## Activity")
        activity_html = '<div style="max-height:280px;overflow-y:auto;">'
        for item in st.session_state.activity_log[:8]:
            activity_html += f'''
                <div class="activity-item">
                  <span class="activity-dot {item["type"]}"></span>
                  <span class="activity-text">{item["text"]}</span>
                  <span class="activity-time">{item["time"]}</span>
                </div>
            '''
        activity_html += '</div>'
        st.markdown(activity_html, unsafe_allow_html=True)

    st.write("")
    st.markdown("---")

    # Integration status
    st.markdown("## Platform connections")
    session, _ = tiktok_session()
    conn_cols = st.columns([2, 1])
    with conn_cols[0]:
        if session:
            profile = session.get("profile", {})
            st.markdown(
                f"""
                <div class="card">
                  <span class="pill pill-ok">● Connected</span>
                  <h3>TikTok · {profile.get('display_name', 'Creator')}</h3>
                  <p>Authorized for draft uploads via Content Posting API (Sandbox). Scopes: {', '.join(session.get('scopes', []))}.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="card">
                  <span class="pill pill-neutral">● Not connected</span>
                  <h3>TikTok</h3>
                  <p>Connect an authorized TikTok account to enable draft uploads. The workspace review workflow is fully usable without a connection.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with conn_cols[1]:
        if session:
            if st.button("Disconnect TikTok", use_container_width=True):
                backend_json("POST", "/api/tiktok/disconnect")
                st.rerun()
        else:
            st.link_button("Connect with TikTok", f"{public_base_url()}/auth/tiktok/login", use_container_width=True)
            st.caption("TikTok Sandbox · Login Kit")

    # Footer
    st.write("")
    st.markdown(
        f"""
        <hr style="border:none;border-top:1px solid var(--line);margin:2rem 0 1rem;">
        <div class="note">
          © 2026 EM Posting · Creator publishing workspace ·
          <a href="{legal_url('terms')}">Terms of Service</a> ·
          <a href="{legal_url('privacy')}">Privacy Policy</a> ·
          <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- Review


def render_review():
    page_header("Review", "Project review", "Complete the review checklist and approve projects for platform handoff.")
    version_caption()

    current_id = st.session_state.get("current_project")
    project = get_project_by_id(current_id) if current_id else None

    if not project:
        # Show review queue
        st.markdown("## Review queue")
        st.write("Select a project from the library to begin the review workflow.")

        needs_review = [p for p in st.session_state.projects if p["status"] in ("ready", "in_review")]
        if needs_review:
            for proj in needs_review:
                status_pill = {
                    "ready": '<span class="pill pill-neutral">● Needs review</span>',
                    "in_review": '<span class="pill pill-preview">● In review</span>',
                }.get(proj["status"], "")

                with st.container(border=True):
                    cols = st.columns([2, 1])
                    with cols[0]:
                        st.markdown(f'{status_pill}<h3 style="margin-top:.4rem;">{proj["title"]}</h3>', unsafe_allow_html=True)
                        st.write(f'{proj["filename"]} · {proj["duration"]} · {proj["creator"]}')
                    with cols[1]:
                        def begin_review(project_id=proj["id"], project_title=proj["title"]):
                            st.session_state.current_project = project_id
                            update_project(project_id, {"status": "in_review"})
                            add_activity("review", f"Started review of '{project_title}'")

                        st.button(
                            "Review this project",
                            key=f"review_{proj['id']}",
                            use_container_width=True,
                            on_click=begin_review,
                        )
        else:
            st.info("No projects need review. Add a new project from the Studio.")

        st.write("")
        st.button("← Back to workspace", use_container_width=False, on_click=goto, args=("Home",))
        return

    # Project review interface
    st.markdown(f"### {project['title']}")

    left, right = st.columns([1.2, 1])

    with left:
        # Video preview
        st.markdown("#### Video preview")
        if project.get("is_sample") and sample_path().exists():
            st.video(str(sample_path()), muted=True)
        elif project.get("video_data"):
            st.video(project["video_data"], muted=True)
        else:
            st.info("Video preview is unavailable for this project.")
        st.markdown(
            f"""
            <div class="card" style="margin-top:.5rem;">
              <p><strong>File:</strong> {project["filename"]}</p>
              <p><strong>Duration:</strong> {project["duration"]} · <strong>Size:</strong> {project["size_mb"]} MB</p>
              <p><strong>Creator:</strong> {project["creator"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("#### Caption & metadata")
        caption = st.text_area(
            "Caption notes",
            value=project.get("caption", ""),
            max_chars=CAPTION_MAX,
            height=100,
            help="Draft notes for finishing the caption inside TikTok.",
            key=f"caption_{project['id']}",
        )

        creator = st.selectbox(
            "Creator account",
            ["Creator (primary)", "Studio brand", "Personal creator"],
            index=["Creator (primary)", "Studio brand", "Personal creator"].index(project.get("creator", "Creator (primary)")),
            key=f"creator_{project['id']}",
        )

        st.markdown("#### Review checklist")
        checks = project.get("checks", {})

        with st.form(f"review_form_{project['id']}"):
            rights = st.checkbox("I have the rights and permission to publish this video", value=checks.get("rights", False))
            reviewed = st.checkbox("I reviewed the account and description", value=checks.get("reviewed", False))
            policy = st.checkbox("This post follows TikTok and workspace content policies", value=checks.get("policy", False))
            control = st.checkbox("I understand final editing and posting continue in TikTok", value=checks.get("control", False))
            consent = st.checkbox("I approve sending this video to TikTok drafts", value=checks.get("consent", False))

            cols = st.columns(2)
            with cols[0]:
                save = st.form_submit_button("Save progress", use_container_width=True)
            with cols[1]:
                approve = st.form_submit_button("Approve for handoff", type="primary", use_container_width=True)

        if save or approve:
            new_checks = {
                "rights": rights,
                "reviewed": reviewed,
                "policy": policy,
                "control": control,
                "consent": consent,
            }
            updates = {
                "caption": caption,
                "creator": creator,
                "checks": new_checks,
                "status": "in_review",
            }

            if approve:
                if not all([rights, reviewed, policy, control, consent]):
                    st.warning("Complete all checklist items before approving.")
                elif not caption.strip():
                    st.warning("Add caption notes before approving.")
                else:
                    updates["status"] = "approved"
                    updates["approved"] = True
                    update_project(project["id"], updates)
                    add_activity("approve", f"'{project['title']}' approved for handoff")

                    # Add to handoff queue
                    asset = project_asset(project)
                    item = {
                        **asset,
                        "account": creator,
                        "caption": caption.strip(),
                        "approved_at": utc_now(),
                        "project_id": project["id"],
                    }
                    if not is_duplicate_approval(st.session_state.queue, asset):
                        st.session_state.queue.insert(0, item)

                    st.success("Project approved and added to the handoff queue.")
                    st.session_state.current_project = None
                    st.rerun()
            else:
                update_project(project["id"], updates)
                st.success("Progress saved.")
                st.rerun()

    st.write("")
    nav_cols = st.columns([1, 1, 1])
    with nav_cols[0]:
        def back_to_library():
            st.session_state.current_project = None
            goto("Home")

        st.button("← Back to library", use_container_width=True, on_click=back_to_library)
    with nav_cols[2]:
        if project.get("status") == "approved":
            st.button("Go to Handoff →", type="primary", use_container_width=True, on_click=goto, args=("Handoff",))


# ------------------------------------------------------------------------- Studio


def render_studio():
    page_header("Studio", "New project", "Add a new video to the project library for review.")
    version_caption()
    progress_strip()

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("### Select video")
        source = st.segmented_control("Source", ["Sample library", "Upload MP4"], default="Sample library")
        uploaded = None
        if source == "Upload MP4":
            uploaded = st.file_uploader(
                "Choose a finished vertical video",
                type=["mp4"],
                help="MP4 only. The file stays in session memory until you explicitly upload it to TikTok drafts.",
            )
            if uploaded is not None:
                st.video(uploaded)

        def add_sample_project():
            st.session_state.asset = sample_asset()
            st.session_state.reviewed = True
            existing_ids = [p["id"] for p in st.session_state.projects]
            if "proj-001" not in existing_ids:
                st.session_state.projects.insert(0, get_sample_projects()[0])
            add_activity("create", "Added 'A founder's night routine' to library")
            st.session_state.current_project = "proj-001"
            goto("Review")

        if source == "Sample library":
            st.button("Add to library", type="primary", use_container_width=True, on_click=add_sample_project)
        elif st.button("Add to library", type="primary", use_container_width=True):
            if uploaded is None:
                st.warning("Choose an MP4 to continue.")
            else:
                data = uploaded.getvalue()
                fingerprint = hashlib.sha256(data).hexdigest()[:16]
                title = Path(uploaded.name).stem.replace("-", " ").replace("_", " ").title()
                new_project = {
                    "id": f"proj-{fingerprint[:6]}",
                    "title": title,
                    "filename": uploaded.name,
                    "duration": None,
                    "size_mb": round(len(data) / (1024 * 1024), 2),
                    "creator": "Creator (primary)",
                    "status": "ready",
                    "caption": "",
                    "created": utc_now(),
                    "reviewed": False,
                    "approved": False,
                    "checks": {"rights": False, "reviewed": False, "policy": False, "control": False, "consent": False},
                    "is_sample": False,
                    "video_data": data,
                    "fingerprint": fingerprint,
                }
                st.session_state.projects.insert(0, new_project)
                st.session_state.asset = {
                    "filename": uploaded.name,
                    "title": title,
                    "size_mb": new_project["size_mb"],
                    "duration": None,
                    "fingerprint": fingerprint,
                    "source": "Direct upload",
                    "video_data": data,
                }
                st.session_state.reviewed = True
                add_activity("create", f"Added '{title}' to library")
                st.success("Project added to library.")
                st.session_state.current_project = new_project["id"]
                goto("Review")
                st.rerun()

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
        st.markdown("### Workflow overview")
        st.markdown(
            """
            Adding a video to the library creates a project that can be reviewed and approved for
            platform handoff. The review process includes:

            1. **Caption preparation** — Draft the text for the TikTok post
            2. **Rights verification** — Confirm you have permission to publish
            3. **Policy compliance** — Ensure content meets platform guidelines
            4. **Explicit approval** — Sign off on the handoff

            Only approved projects can be sent to TikTok drafts. Final editing and posting
            always happens inside TikTok.
            """,
        )

        st.markdown("### Current library")
        for proj in st.session_state.projects[:3]:
            status_text = {"ready": "Needs review", "in_review": "In review", "approved": "Approved"}.get(proj["status"], "")
            st.markdown(f"- **{proj['title']}** — {status_text}")
        if len(st.session_state.projects) > 3:
            st.caption(f"+{len(st.session_state.projects) - 3} more projects")


# ------------------------------------------------------------------------ Handoff


def render_handoff():
    page_header("Handoff", "Platform handoff", "Connect an authorized TikTok account and send approved projects to TikTok's inbox flow.")
    version_caption()

    session, _ = tiktok_session()
    st.markdown("## TikTok connection")
    if session:
        profile = session.get("profile", {})
        left, right = st.columns([.72, .28])
        with left:
            st.success(f"Connected as **{profile.get('display_name', 'TikTok creator')}**")
            st.caption("Authorized scopes: " + ", ".join(session.get("scopes", [])))
        with right:
            if st.button("Disconnect TikTok", use_container_width=True):
                backend_json("POST", "/api/tiktok/disconnect")
                st.rerun()
    else:
        st.info("Connect TikTok before uploading. TikTok will ask for user.info.basic and video.upload consent.")
        st.link_button("Connect with TikTok", f"{public_base_url()}/auth/tiktok/login", type="primary", use_container_width=True)
        st.caption("The full workspace workflow is usable without a connection. TikTok authorization is required only for the final handoff step.")

    a, b, c = st.columns(3)
    for col, label, value in [
        (a, "Approved", str(len(st.session_state.queue))),
        (b, "Handoffs this session", str(st.session_state.sent_count)),
        (c, "Destination", "TikTok inbox"),
    ]:
        with col:
            st.markdown(
                f'<div class="stat"><div class="stat-label">{label}</div><div class="stat-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    if should_show_empty_queue(st.session_state.queue, st.session_state.receipt):
        st.write("")
        st.markdown(
            '<div class="card"><span class="pill pill-neutral">Queue is clear</span>'
            "<h3>No approved posts yet</h3><p>Review and approve projects from the library to add them to the handoff queue.</p></div>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.button("Go to Review", type="primary", on_click=goto, args=("Review",))
        return

    if st.session_state.queue:
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
                st.markdown("#### TikTok inbox handoff")
                st.markdown('<span class="pill pill-ok">● Sandbox draft upload</span>', unsafe_allow_html=True)
                st.write("The MP4 is transferred to TikTok; captioning, final editing, and posting remain in TikTok.")
                if st.button("Upload to TikTok drafts", type="primary", key=f"send_{index}", use_container_width=True, disabled=not session):
                    if item.get("video_data"):
                        video_data = item["video_data"]
                    else:
                        video_data = Path(item["path"]).read_bytes()
                    with st.spinner("Uploading the approved MP4 to TikTok drafts…"):
                        st.session_state.receipt = None
                        receipt, error = backend_json(
                            "POST",
                            "/api/tiktok/upload",
                            files={"video": (item["filename"], video_data, "video/mp4")},
                        )
                    if error:
                        st.error(error)
                    else:
                        assert receipt is not None
                        assert session is not None
                        status_payload, status_error = backend_json(
                            "GET",
                            f"/api/tiktok/status/{receipt['publish_id']}",
                        )
                        status = (
                            (status_payload or {}).get("data", {}).get("status")
                            or "TRANSFER_ACCEPTED"
                        )
                        fail_reason = (status_payload or {}).get("data", {}).get("fail_reason")
                        st.session_state.sent_count += 1
                        new_receipt = {
                            "Post": item["title"],
                            "Account": session.get("profile", {}).get("display_name", item["account"]),
                            "Caption notes": item["caption"],
                            "Destination": receipt["destination"],
                            "Product": "Content Posting API",
                            "Scope": "video.upload",
                            "Publish ID": receipt["publish_id"],
                            "TikTok status": status,
                            "Failure reason": fail_reason,
                            "Asset ID": receipt["fingerprint"],
                            "Next step": receipt["next_step"],
                            "Uploaded": utc_now(),
                        }
                        if status_error:
                            new_receipt["Status note"] = (
                                "The MP4 transfer succeeded; TikTok status was not available yet."
                            )
                        st.session_state.receipt = new_receipt
                        st.session_state.receipts.insert(0, new_receipt)
                        st.session_state.queue.pop(index)
                        add_activity("upload", f"Handed off '{item['title']}' to TikTok drafts")
                        if (
                            st.session_state.asset
                            and st.session_state.asset.get("fingerprint") == item.get("fingerprint")
                        ):
                            st.session_state.asset = None
                            st.session_state.reviewed = False
                        st.rerun()

    if st.session_state.receipts:
        st.markdown("## Upload history")
        st.caption("A publish ID proves TikTok accepted a transfer task. Only SEND_TO_USER_INBOX confirms inbox delivery.")
        for receipt_index, receipt in enumerate(st.session_state.receipts):
            status = receipt.get("TikTok status", "TRANSFER_ACCEPTED")
            title, copy = tiktok_status_copy(status, receipt.get("Failure reason"))
            pill_class = "pill-ok" if status in {"SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"} else "pill-preview"
            with st.container(border=True):
                st.markdown(
                    f'<span class="pill {pill_class}">● {title}</span><h3>{receipt["Post"]}</h3><p class="note">{copy}</p>',
                    unsafe_allow_html=True,
                )
                st.caption(f'Publish ID: {receipt["Publish ID"]} · uploaded {receipt["Uploaded"]}')
                if st.button("Refresh TikTok status", key=f"status_{receipt_index}_{receipt['Publish ID']}"):
                    status_payload, status_error = backend_json(
                        "GET", f"/api/tiktok/status/{receipt['Publish ID']}"
                    )
                    if status_error:
                        st.error(status_error)
                    else:
                        status_data = (status_payload or {}).get("data", {})
                        receipt["TikTok status"] = status_data.get("status", status)
                        receipt["Failure reason"] = status_data.get("fail_reason")
                        receipt["Uploaded bytes"] = status_data.get("uploaded_bytes")
                        st.session_state.receipt = st.session_state.receipts[0]
                        st.rerun()
                with st.expander("Receipt details"):
                    st.json({key: value for key, value in receipt.items() if value is not None})

        left, right = st.columns(2)
        with left:
            st.button("View terms & privacy", use_container_width=True, on_click=goto, args=("Legal",))
        with right:
            st.button("Review more projects", type="primary", use_container_width=True, on_click=goto, args=("Review",))


# -------------------------------------------------------------------------- Legal


def render_legal():
    page_header("Legal", "Terms & Privacy", "The policies for the EM Posting creator workflow product.")
    version_caption()
    policy = st.query_params.get("policy")
    if policy == "terms":
        st.markdown(TERMS)
        st.link_button("View Privacy Policy", legal_url("privacy"))
    elif policy == "privacy":
        st.markdown(PRIVACY)
        st.link_button("View Terms of Service", legal_url("terms"))
    else:
        terms_tab, privacy_tab = st.tabs(["Terms of Service", "Privacy Policy"])
        with terms_tab:
            st.markdown(TERMS)
        with privacy_tab:
            st.markdown(PRIVACY)


# --------------------------------------------------------------------------- Shell


init_state()

NAV_ITEMS = ["Home", "Review", "Studio", "Handoff", "Legal"]
if "nav" not in st.session_state:
    requested_page = st.query_params.get("page", "home").lower()
    st.session_state.nav = "Legal" if requested_page == "legal" else "Home"
if "pending_nav" in st.session_state:
    st.session_state.nav = st.session_state.pop("pending_nav")

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark"><img src="/app/static/assets/em-posting-icon.png" '
        'alt="EM Posting icon"></span>EM Posting</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="ws-chip"><b>{WORKSPACE}</b><br><span style="color:#a1a1aa">Creator workspace · Owner</span></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.radio("Workspace navigation", NAV_ITEMS, key="nav", label_visibility="collapsed")
    st.divider()
    st.caption("Creator-controlled publishing")
    st.caption(f"{APP_VERSION} · TikTok Sandbox")

page = st.session_state.nav
if page == "Review":
    render_review()
elif page == "Studio":
    render_studio()
elif page == "Handoff":
    render_handoff()
elif page == "Legal":
    render_legal()
else:
    render_home()
