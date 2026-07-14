import hashlib
from datetime import datetime
from textwrap import dedent

import streamlit as st

APP_VERSION = "v0.5.1"
APP_NAME = "EM Posting"

SHORT_DESCRIPTION = (
    "Creator workflow for reviewing approved eczema education videos and sending them to TikTok drafts."
)

APP_REVIEW_EXPLANATION = (
    "EM Posting is a creator workflow app used by the Eczema Mitten content team to prepare approved short-form "
    "educational videos and send them to TikTok for final review and posting. The workflow starts with finished MP4 "
    "videos created by our editorial process. An authorized team member opens EM Posting, selects a prepared video, "
    "reviews the caption and metadata, checks the approval steps, then uses the TikTok integration to upload the video "
    "to TikTok's posting/draft flow. The purpose of the Content Posting API integration is to reduce manual file "
    "transfer while preserving a human review step before publishing. The app is not a mass-posting platform and does "
    "not auto-generate or spam content. Access is limited to authorized creators and operators managing the Eczema "
    "Mitten / Reuben Eczema accounts."
)

SCOPE_JUSTIFICATION = dedent(
    """
    Requested TikTok product/scope: Content Posting API, preferably video.upload / upload-to-draft flow.

    EM Posting only needs permission to upload a prepared MP4 and associated caption/metadata into TikTok's posting or draft workflow for final human review. The app does not need follower data, analytics, direct messages, comments, or broad account management permissions.

    The integration is used by authorized creators to move approved eczema education and founder-story videos from our editorial workflow into TikTok without manual file transfer. A team member reviews the video and caption before sending it to TikTok, and final posting remains under human control.
    """
).strip()


PRODUCTION_INTEGRATION_NOTES = dedent(
    """
    Planned production integration:

    - Product: TikTok Content Posting API.
    - Preferred scope: video.upload, because EM Posting is designed for upload-to-draft / inbox handoff rather than automatic public publishing.
    - Expected endpoint: /v2/post/publish/inbox/video/init/.
    - Transfer method: FILE_UPLOAD for a creator-selected local MP4. PULL_FROM_URL should only be used later if the production video host/domain is verified in TikTok developer settings.
    - Creator control: after upload, the TikTok creator receives an inbox notification and completes final editing/posting in TikTok.
    - Rate/spam posture: the app is intentionally narrow and review-gated. It is not a bulk scheduler, scraper, engagement bot, or mass publisher.
    - Secrets: OAuth credentials and access tokens must be stored in Streamlit secrets or another private production secret store, never in this public repository.
    """
).strip()

REVIEW_READINESS_CHECKLIST = [
    "Public landing/dashboard explains the creator workflow.",
    "Terms of Service and Privacy Policy are accessible from the app navigation.",
    "Demo Guide gives a clear silent app-review video shot list.",
    "Creator Workspace shows asset selection, caption review, and consent checks.",
    "Handoff Queue shows a draft-upload style TikTok API handoff mock.",
    "TikTok Review Packet includes app description, review explanation, and scope justification.",
    "No production secrets, access tokens, private videos, cookies, or customer data are committed.",
]

SILENT_DEMO_SCRIPT = dedent(
    """
    0:00–0:05 — Dashboard: hold on the EM Posting hero and the Prepare → Review → Handoff cards.
    0:05–0:10 — Demo Guide: show that this recording uses the sample asset and does not require production credentials.
    0:10–0:25 — Creator Workspace: click Load sample asset, let the built-in sample video play, and show its file details.
    0:25–0:40 — Review metadata: keep the default account/category/caption, tick all five approval and consent checks, then click Approve for TikTok draft handoff.
    0:40–0:52 — Handoff Queue: show the approved item, creator consent, and the upload-to-draft endpoint mock. Click Send to TikTok Draft Flow (demo).
    0:52–1:00 — Handoff receipt: hold on the success receipt showing demo status, creator control, and no live API call.
    1:00–1:08 — TikTok Review Packet: briefly show video.upload, the app explanation, Terms, and Privacy links in the sidebar.
    """
).strip()

VOICEOVER_OPTION = dedent(
    """
    EM Posting helps our authorized creator team review prepared eczema education videos before sending them to TikTok's draft flow. A creator selects the finished MP4, checks the caption and account, confirms consent, and approves the handoff. The requested video.upload scope reduces manual file transfer while final editing and posting remain under human control in TikTok.
    """
).strip()

TERMS = dedent(
    """
    # Terms of Service

    Last updated: July 2026

    EM Posting is a creator workflow app for authorized Eczema Mitten / Reuben Eczema team members. By using this app, you agree to use it only for approved short-form educational, founder-story, and ecommerce-related content managed by the team.

    ## Authorized use
    Access is limited to approved creators and operators. Users may review prepared videos, captions, metadata, and upload handoff steps connected to the team's social posting workflow.

    ## Human review
    Videos must be reviewed by an authorized team member before being sent to TikTok's upload, draft, or posting workflow. EM Posting is not intended for spam, mass publishing, deceptive automation, or bypassing platform review controls.

    ## User responsibilities
    Users are responsible for ensuring that content is accurate, lawful, brand-safe, and compliant with TikTok's policies and all applicable platform rules.

    ## No sensitive data in demos
    Public demos and open-source code must not contain production secrets, access tokens, private customer data, or unpublished confidential business information.

    ## Changes
    We may update these terms as the workflow and TikTok integration mature.

    ## Contact
    Contact the Eczema Mitten team through the official business channels connected to the Eczema Mitten / Reuben Eczema accounts.
    """
).strip()

PRIVACY = dedent(
    """
    # Privacy Policy

    Last updated: July 2026

    EM Posting is a creator workflow app for authorized Eczema Mitten / Reuben Eczema team members.

    ## Information processed
    The app may process prepared MP4 videos, captions, account labels, internal approval status, and basic technical metadata such as filename, file size, and upload time.

    ## Purpose
    This information is used to help authorized creators review approved eczema education and founder-story videos before sending them to TikTok's upload, draft, or posting workflow.

    ## TikTok data
    The requested TikTok integration is limited to content posting/upload functionality. EM Posting does not request direct messages, comments, follower lists, or unrelated TikTok account data.

    ## Storage
    This demo app does not permanently store uploaded files. A production deployment may temporarily process files only as needed to support the upload workflow.

    ## Sharing
    Content is shared with TikTok only when an authorized team member chooses to send an approved video through the TikTok integration. We do not sell personal information.

    ## Security
    Production API credentials must be stored in secure deployment secrets, never in the public repository.

    ## Contact
    Contact the Eczema Mitten team through official business channels for privacy questions.
    """
).strip()

st.set_page_config(page_title=APP_NAME, page_icon="🧤", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #fbf7ef 0%, #f5ead8 45%, #eaf1ec 100%); }
    section[data-testid="stSidebar"] { background: #111827; }
    section[data-testid="stSidebar"] * { color: #f9fafb !important; }
    .hero-card { padding: 2.4rem; border-radius: 28px; background: radial-gradient(circle at top right, #3b6b50 0%, #111827 48%, #0b111c 100%); color: white; box-shadow: 0 20px 60px rgba(17,24,39,.22); }
    .hero-card h1 { font-size: 3.7rem; line-height: .95; margin: .4rem 0 .8rem; color: white; letter-spacing: -0.06em; }
    .hero-card p { font-size: 1.08rem; color: #e5e7eb; max-width: 880px; }
    .pill { display: inline-block; padding: .38rem .72rem; border-radius: 999px; background: rgba(255,255,255,.13); margin: .15rem; font-size: .84rem; border: 1px solid rgba(255,255,255,.16); }
    .panel { background: rgba(255,255,255,.88); border: 1px solid rgba(17,24,39,.08); border-radius: 22px; padding: 1.2rem; box-shadow: 0 9px 26px rgba(17,24,39,.07); min-height: 150px; }
    .panel h3 { margin-top: 0; letter-spacing: -0.03em; }
    .metric-card { background: #ffffff; border-radius: 18px; padding: 1rem; border-left: 5px solid #315c45; box-shadow: 0 7px 20px rgba(17,24,39,.07); min-height: 86px; }
    .step { padding: .9rem 1rem; border-radius: 16px; background: white; border: 1px solid rgba(17,24,39,.08); margin-bottom: .55rem; }
    .step-ready { border-left: 6px solid #047857; }
    .step-wait { border-left: 6px solid #d97706; }
    .status-ready { color: #065f46; font-weight: 800; }
    .status-waiting { color: #92400e; font-weight: 800; }
    .muted { color: #6b7280; font-size: .92rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "events" not in st.session_state:
    st.session_state.events = []
if "asset" not in st.session_state:
    st.session_state.asset = None
if "queue" not in st.session_state:
    st.session_state.queue = []
if "demo_started" not in st.session_state:
    st.session_state.demo_started = False
if "sent_count" not in st.session_state:
    st.session_state.sent_count = 0
if "handoff_receipt" not in st.session_state:
    st.session_state.handoff_receipt = None


def add_event(message):
    st.session_state.events.insert(0, {
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "event": message,
    })


def fingerprint(uploaded_file):
    data = uploaded_file.getvalue()
    return hashlib.sha256(data).hexdigest()[:16], len(data)


def sample_asset():
    sample_path = Path(__file__).parent / "assets" / "sample_creator_video.mp4"
    data = sample_path.read_bytes()
    return {
        "filename": "eczema-night-routine-founder-story.mp4",
        "size_mb": round(len(data) / (1024 * 1024), 2),
        "duration": "00:08",
        "fingerprint": hashlib.sha256(data).hexdigest()[:16],
        "source": "Bundled public demo asset",
        "status": "Ready for approval",
        "path": str(sample_path),
    }


def render_version():
    st.caption(f"{APP_VERSION} - reviewer-ready creator workflow and TikTok draft handoff demo")


def render_hero():
    st.markdown(
        """
        <div class="hero-card">
            <div class="pill">creator operations</div>
            <div class="pill">human review</div>
            <div class="pill">TikTok draft handoff</div>
            <div class="pill">prepared MP4 workflow</div>
            <h1>EM Posting</h1>
            <p>A creator workflow app for reviewing approved eczema education videos before sending them into TikTok's upload or draft flow.</p>
            <p>Built for a small authorized content team: select the prepared video, confirm the story and caption, complete the approval checks, then queue a draft-style TikTok handoff. No mass publishing, no hidden credentials, no autoposting theater.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def workflow_progress():
    has_asset = st.session_state.asset is not None
    has_queue = len(st.session_state.queue) > 0
    has_sent = st.session_state.sent_count > 0
    steps = [
        ("asset selected", has_asset),
        ("caption reviewed", has_queue),
        ("approved for handoff", has_queue),
        ("draft handoff demo sent", has_sent),
    ]
    for label, done in steps:
        klass = "step step-ready" if done else "step step-wait"
        icon = "✅" if done else "⏳"
        st.markdown(f'<div class="{klass}">{icon} <b>{label}</b></div>', unsafe_allow_html=True)


def render_dashboard():
    render_hero()
    render_version()
    st.write("")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><b>workflow</b><br><span class="status-ready">review-first</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><b>posting mode</b><br><span class="status-ready">draft handoff</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><b>users</b><br>authorized creators</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><b>requested API</b><br>Content Posting / video.upload</div>', unsafe_allow_html=True)

    st.markdown("## Product walkthrough")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="panel"><h3>1. prepare</h3><p>Select a finished MP4 from the editorial workflow. The app creates a clean review card with file metadata.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><h3>2. review</h3><p>Choose the account, content category, caption, and safety approvals before anything leaves the workspace.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="panel"><h3>3. handoff</h3><p>Queue the video for TikTok draft upload. The public demo simulates the API action without storing credentials.</p></div>', unsafe_allow_html=True)

    left, right = st.columns([0.62, 0.38])
    with left:
        st.markdown("## Why this exists")
        st.write(
            "Eczema Mitten / Reuben Eczema creates educational short-form content around eczema care, founder-story moments, and product education. "
            "EM Posting gives the creator team a simple review station so prepared videos are checked before they move into TikTok."
        )
        st.markdown("## Record the clean 60-second demo")
        st.write("Use **Demo Guide → Creator Workspace → Handoff Queue → TikTok Review Packet**. Voiceover is optional; the interface and success receipt carry the story on-screen.")
        st.info("Recommended: record the browser window only at 100% zoom, use the bundled sample video, and keep the final clip around 60–70 seconds.")
    with right:
        st.markdown("## Current demo progress")
        workflow_progress()


def render_demo_recorder():
    st.title("Demo Guide")
    render_version()
    st.success("Best review video: a simple 60–70 second silent screen recording. Voiceover is optional, not required.")

    top1, top2, top3 = st.columns(3)
    top1.metric("Target length", "60–70 sec")
    top2.metric("Demo asset", "Bundled MP4")
    top3.metric("Live TikTok call", "No — clearly mocked")

    if st.button("Prepare clean demo state", type="primary"):
        st.session_state.asset = None
        st.session_state.queue = []
        st.session_state.sent_count = 0
        st.session_state.events = []
        st.session_state.handoff_receipt = None
        st.session_state.demo_started = True
        add_event("Prepared clean demo recording state")
        st.success("Clean state ready. Start recording, open Dashboard for five seconds, then return here and follow the shot list.")

    left, right = st.columns([0.62, 0.38])
    with left:
        st.markdown("## Silent shot list")
        shots = [
            ("00:00–00:05", "Dashboard", "Hold on the hero and Prepare → Review → Handoff cards."),
            ("00:05–00:10", "Demo Guide", "Show this checklist and the no-live-credentials notice."),
            ("00:10–00:25", "Creator Workspace", "Load the sample asset, play the preview briefly, and show file metadata."),
            ("00:25–00:40", "Review + consent", "Tick all five checks and approve the asset for TikTok draft handoff."),
            ("00:40–00:52", "Handoff Queue", "Show account, caption, consent, endpoint mock, then click the demo send button."),
            ("00:52–01:00", "Success receipt", "Hold long enough for the reviewer to read creator control and no-live-call status."),
            ("01:00–01:08", "Review Packet", "Show video.upload, review copy, Terms, and Privacy navigation."),
        ]
        for timing, page, action in shots:
            st.markdown(f"**{timing} · {page}**  \n{action}")
    with right:
        st.markdown("## Recording rules")
        st.checkbox("Browser window only", value=True, disabled=True)
        st.checkbox("100% browser zoom", value=True, disabled=True)
        st.checkbox("Use bundled sample asset", value=True, disabled=True)
        st.checkbox("No secrets or TikTok login shown", value=True, disabled=True)
        st.checkbox("Pause on final receipt", value=True, disabled=True)
        st.markdown("## Optional voiceover")
        st.text_area("One-paragraph narration", VOICEOVER_OPTION, height=180)

    with st.expander("Exact timeline text"):
        st.text(SILENT_DEMO_SCRIPT)
        st.download_button("Download silent shot list", SILENT_DEMO_SCRIPT, file_name="em-posting-silent-demo.txt")


def render_workspace():
    st.title("Creator Workspace")
    render_version()
    st.info("Functional mock for app review: you can use the sample asset or upload a mock MP4. The final TikTok API call is disabled until approval and secure credentials are configured.")

    left, right = st.columns([1.05, 0.95])
    with left:
        st.subheader("1. Select prepared video")
        mode = st.radio("Asset source", ["Use sample review asset", "Upload mock MP4"], horizontal=True)
        uploaded = None
        if mode == "Upload mock MP4":
            uploaded = st.file_uploader("Prepared MP4", type=["mp4"])
            if uploaded:
                st.video(uploaded)

        if st.button("Load asset for review", type="primary"):
            if mode == "Use sample review asset":
                st.session_state.asset = sample_asset()
                add_event("Loaded bundled sample review asset")
            elif uploaded is None:
                st.error("Upload a mock MP4 first, or use the sample asset.")
            else:
                digest, size = fingerprint(uploaded)
                st.session_state.asset = {
                    "filename": uploaded.name,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "duration": "uploaded file",
                    "fingerprint": digest,
                    "source": "Uploaded demo file",
                    "status": "Ready for approval",
                }
                add_event(f"Loaded uploaded asset: {uploaded.name}")

        if st.session_state.asset:
            a = st.session_state.asset
            if a.get("path"):
                st.video(a["path"], autoplay=True, muted=True)
            st.markdown("### Asset review card")
            with st.container(border=True):
                st.markdown(f"#### {a['filename']}")
                st.write(f"**Source:** {a['source']}  |  **Size:** {a['size_mb']} MB  |  **Duration:** {a['duration']}")
                st.write(f"**Fingerprint:** `{a['fingerprint']}`")
                st.markdown(f"<span class='status-ready'>{a['status']}</span>", unsafe_allow_html=True)
        else:
            st.markdown("### Asset review card")
            st.markdown("<div class='panel'><h3>No asset loaded yet</h3><p>Use the sample asset for a clean demo recording, or upload a mock MP4 if you want to show the file picker.</p></div>", unsafe_allow_html=True)

    with right:
        st.subheader("2. Review metadata")
        account = st.selectbox("TikTok account label", ["Reuben Eczema", "Eczema Mitten SG", "Eczema Mitten US"])
        category = st.selectbox("Content category", ["Eczema education", "Founder story", "Product education", "Care routine"])
        caption = st.text_area(
            "Caption",
            "Night routine for eczema flare protection. Reviewed by the Eczema Mitten creator team before TikTok draft handoff.",
            height=125,
        )
        hashtags = st.text_input("Hashtags", "#eczema #eczemacare #sensitiveskin #eczemamitten")
        st.subheader("3. Approval checklist")
        approved = st.checkbox("Content is approved eczema education / founder-story material")
        reviewed = st.checkbox("Caption, hashtags, and account label reviewed")
        safe = st.checkbox("No spam, deception, or mass-publishing behavior")
        human = st.checkbox("Final TikTok posting remains human-reviewed")
        consent = st.checkbox("Creator expressly consents to send this approved video to TikTok draft flow")

        if st.button("Approve for TikTok draft handoff"):
            if not st.session_state.asset:
                st.error("Load an asset first.")
            elif not all([approved, reviewed, safe, human, consent]):
                st.error("Complete all approval checks before queueing.")
            else:
                item = {
                    **st.session_state.asset,
                    "account": account,
                    "category": category,
                    "caption": caption,
                    "hashtags": hashtags,
                    "queued_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "creator_consent": "Confirmed",
                    "handoff_status": "Ready for TikTok draft flow",
                }
                st.session_state.queue.insert(0, item)
                add_event(f"Approved {item['filename']} for TikTok draft handoff")
                st.success("Approved. The asset is now in the handoff queue.")


def render_queue():
    st.title("Handoff Queue")
    render_version()
    st.write("Approved videos waiting for TikTok upload/draft handoff.")
    st.info("TikTok upload API note: after a successful upload-to-draft/inbox handoff, the creator continues final editing and posting from TikTok. This demo intentionally stops before any real API call.")
    if len(st.session_state.queue) >= 5:
        st.warning("Review guardrail: TikTok documents pending-share limits. Keep the queue small and creator-reviewed; this app is not a bulk publisher.")

    if not st.session_state.queue:
        st.warning("No approved videos yet. Open Creator Workspace and approve a sample asset.")
        return

    for index, item in enumerate(st.session_state.queue):
        with st.container(border=True):
            col1, col2 = st.columns([0.72, 0.28])
            with col1:
                st.markdown(f"### {item['filename']}")
                st.write(f"**Account:** {item['account']}  |  **Category:** {item['category']}  |  **Size:** {item['size_mb']} MB")
                st.write(f"**Caption:** {item['caption']}")
                st.write(f"**Hashtags:** {item['hashtags']}")
                st.write(f"**Creator consent:** {item.get('creator_consent', 'Confirmed during review')}")
                st.markdown(f"<span class='status-ready'>{item['handoff_status']}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown("#### API handoff mock")
                st.code("POST /v2/post/publish/inbox/video/init/", language="http")
                if st.button("Send to TikTok Draft Flow (demo)", key=f"send_{index}"):
                    item["handoff_status"] = "Demo sent to TikTok draft flow"
                    st.session_state.sent_count += 1
                    st.session_state.handoff_receipt = {
                        "status": "Demo handoff complete",
                        "destination": "TikTok draft / inbox flow",
                        "scope": "video.upload",
                        "creator_control": "Final editing and posting remain in TikTok",
                        "live_api_call": "No — public review demo",
                        "asset": item["filename"],
                        "completed_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    }
                    add_event(f"Demo TikTok draft handoff completed for {item['filename']}")
                    st.success("Demo handoff complete. No live TikTok API call was made.")

    if st.session_state.handoff_receipt:
        st.markdown("## Handoff receipt")
        st.success("The approved video completed the public demo handoff. The creator would finish editing and posting inside TikTok.")
        st.json(st.session_state.handoff_receipt)


def render_review_packet():
    st.title("TikTok Review Packet")
    render_version()
    packet = f"""# EM Posting - TikTok App Review Packet

## Short description
{SHORT_DESCRIPTION}

## Review explanation
{APP_REVIEW_EXPLANATION}

## Scope/product justification
{SCOPE_JUSTIFICATION}

## Silent demo video shot list
{SILENT_DEMO_SCRIPT}

## Optional voiceover
{VOICEOVER_OPTION}
"""
    st.download_button("Download review packet", packet, file_name="em-posting-tiktok-review-packet.md", mime="text/markdown")
    st.markdown("## Copy/paste fields")
    st.text_area("Description under 120 characters", SHORT_DESCRIPTION, height=80)
    st.text_area("App review explanation under 1000 characters", APP_REVIEW_EXPLANATION, height=190)
    st.text_area("Scope/product justification", SCOPE_JUSTIFICATION, height=180)
    st.markdown("## Full packet")
    st.markdown(packet)


def render_production_plan():
    st.title("Production Integration Plan")
    render_version()
    st.write("This page is here for app review and implementation clarity. It separates the public demo from the intended production TikTok integration.")

    col1, col2 = st.columns([0.55, 0.45])
    with col1:
        st.markdown("## Requested TikTok API use")
        st.markdown(PRODUCTION_INTEGRATION_NOTES)
    with col2:
        st.markdown("## What EM Posting is not")
        st.markdown("- Not a direct mass publisher")
        st.markdown("- Not an engagement, comment, or scraping bot")
        st.markdown("- Not an auto-generated content spam system")
        st.markdown("- Not requesting analytics, follower, DM, or comment scopes")
        st.markdown("- Not storing production tokens in this public app")

    st.markdown("## Upload flow shape")
    st.code(
        """1. Authorized creator selects an approved MP4
2. Creator reviews caption, hashtags, and account label
3. Creator confirms consent and safety checklist
4. Production app initializes TikTok video.upload inbox flow
5. Video transfers to TikTok
6. Creator receives TikTok inbox notification
7. Creator completes final editing/posting in TikTok""",
        language="text",
    )


def render_readiness():
    st.title("Review Readiness")
    render_version()
    st.write("Final checklist before recording or submitting for TikTok developer review.")
    for item in REVIEW_READINESS_CHECKLIST:
        st.checkbox(item, value=True, disabled=True)
    st.divider()
    st.markdown("## Recommended recording path")
    st.markdown("1. Dashboard → 2. Demo Guide → 3. Creator Workspace → 4. Handoff Queue → 5. TikTok Review Packet → 6. Terms/Privacy")
    st.markdown("## Streamlit deploy settings")
    st.code(
        "Repository: reubenloo/tiktok_posting\n"
        "Branch: main\n"
        "Main file path: streamlit_app.py\n"
        "Python: select 3.12 in Streamlit Cloud settings if available",
        language="text",
    )


def render_terms():
    st.title("Terms of Service")
    render_version()
    st.markdown(TERMS)


def render_privacy():
    st.title("Privacy Policy")
    render_version()
    st.markdown(PRIVACY)


def render_events():
    st.title("Activity Log")
    render_version()
    if st.session_state.events:
        st.table(st.session_state.events)
    else:
        st.write("No activity yet. Load and approve a sample asset to generate demo events.")


with st.sidebar:
    st.markdown("# 🧤 EM Posting")
    page = st.radio(
        "Navigate",
        ["Dashboard", "Demo Guide", "Creator Workspace", "Handoff Queue", "TikTok Review Packet", "Production Plan", "Review Readiness", "Terms", "Privacy", "Activity Log"],
    )
    st.divider()
    st.caption("Public review demo. Production credentials are not included.")

if page == "Dashboard":
    render_dashboard()
elif page == "Demo Guide":
    render_demo_recorder()
elif page == "Creator Workspace":
    render_workspace()
elif page == "Handoff Queue":
    render_queue()
elif page == "TikTok Review Packet":
    render_review_packet()
elif page == "Production Plan":
    render_production_plan()
elif page == "Review Readiness":
    render_readiness()
elif page == "Terms":
    render_terms()
elif page == "Privacy":
    render_privacy()
else:
    render_events()
