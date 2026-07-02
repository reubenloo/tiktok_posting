import hashlib
from datetime import datetime
from textwrap import dedent

import streamlit as st

APP_VERSION = "v0.2.0"
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

DEMO_SCRIPT = dedent(
    """
    1. Open the EM Posting dashboard and show the creator workflow overview.
    2. Open Creator Workspace and explain that a prepared MP4 is selected from the editorial workflow.
    3. Upload a mock MP4 or use the sample video metadata.
    4. Review the caption, target account, content category, and compliance checklist.
    5. Click Approve for TikTok draft handoff.
    6. Open the Handoff Queue and show the video marked as ready for TikTok draft upload.
    7. Click the demo Send to TikTok Draft Flow action.
    8. Explain that production credentials are not stored in the public demo, and the app does not publish directly; the intended TikTok API scope is upload/draft handoff for final human review.
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
    .stApp { background: linear-gradient(135deg, #fbf7ef 0%, #f7efe2 45%, #eef3ef 100%); }
    section[data-testid="stSidebar"] { background: #111827; }
    section[data-testid="stSidebar"] * { color: #f9fafb !important; }
    .hero-card { padding: 2rem; border-radius: 24px; background: linear-gradient(135deg, #111827 0%, #20312a 100%); color: white; box-shadow: 0 18px 45px rgba(17,24,39,.18); }
    .hero-card h1 { font-size: 3.2rem; line-height: 1; margin-bottom: .5rem; color: white; }
    .hero-card p { font-size: 1.05rem; color: #e5e7eb; }
    .pill { display: inline-block; padding: .35rem .7rem; border-radius: 999px; background: rgba(255,255,255,.12); margin: .15rem; font-size: .85rem; }
    .panel { background: rgba(255,255,255,.82); border: 1px solid rgba(17,24,39,.08); border-radius: 20px; padding: 1.2rem; box-shadow: 0 8px 24px rgba(17,24,39,.06); min-height: 145px; }
    .panel h3 { margin-top: 0; }
    .metric-card { background: #ffffff; border-radius: 18px; padding: 1rem; border-left: 5px solid #315c45; box-shadow: 0 7px 20px rgba(17,24,39,.07); }
    .status-ready { color: #065f46; font-weight: 700; }
    .status-waiting { color: #92400e; font-weight: 700; }
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


def add_event(message):
    st.session_state.events.insert(0, {
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "event": message,
    })


def fingerprint(uploaded_file):
    data = uploaded_file.getvalue()
    return hashlib.sha256(data).hexdigest()[:16], len(data)


def sample_asset():
    return {
        "filename": "eczema-night-routine-founder-story.mp4",
        "size_mb": 18.4,
        "fingerprint": "sample-a7f42c91",
        "source": "Sample review asset",
        "status": "Ready for approval",
    }


def render_version():
    st.caption(f"{APP_VERSION} - polished creator workflow and TikTok draft handoff mock")


def render_hero():
    st.markdown(
        """
        <div class="hero-card">
            <div class="pill">creator operations</div>
            <div class="pill">human review</div>
            <div class="pill">TikTok draft handoff</div>
            <h1>EM Posting</h1>
            <p>A focused workflow app for reviewing approved eczema education videos before sending them into TikTok's upload or draft flow.</p>
            <p>No mass publishing. No secret tokens in this demo. Just a clean creator review lane from prepared MP4 → caption check → approval → draft handoff.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard():
    render_hero()
    render_version()
    st.write("")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><b>Workflow</b><br><span class="status-ready">review-first</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><b>Posting mode</b><br><span class="status-ready">draft handoff</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><b>Users</b><br>authorized creators</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><b>API request</b><br>video.upload</div>', unsafe_allow_html=True)

    st.markdown("## How the creator workflow works")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="panel"><h3>1. ingest asset</h3><p>Select a finished MP4 from the editorial workflow. The app reads basic file metadata and prepares a review card.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><h3>2. review story + caption</h3><p>Confirm the content category, caption, creator account, and approval checklist before handoff.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="panel"><h3>3. send to draft flow</h3><p>The intended TikTok integration uploads approved videos into TikTok draft/posting flow for final human control.</p></div>', unsafe_allow_html=True)

    st.markdown("## Why this exists")
    st.write(
        "Eczema Mitten / Reuben Eczema creates educational short-form content around eczema care, founder-story moments, and product education. "
        "EM Posting gives the creator team a simple review station so prepared videos are checked before they leave the editorial workflow."
    )


def render_workspace():
    st.title("Creator Workspace")
    render_version()
    st.info("This is a functional mock workflow for app review. The final TikTok API call is intentionally disabled until app approval and secure credentials are configured.")

    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader("1. Select prepared video")
        mode = st.radio("Asset source", ["Use sample review asset", "Upload mock MP4"], horizontal=True)
        uploaded = None
        if mode == "Upload mock MP4":
            uploaded = st.file_uploader("Prepared MP4", type=["mp4"])

        if st.button("Load asset for review", type="primary"):
            if mode == "Use sample review asset":
                st.session_state.asset = sample_asset()
                add_event("Loaded sample review asset")
            elif uploaded is None:
                st.error("Upload a mock MP4 first, or use the sample asset.")
            else:
                digest, size = fingerprint(uploaded)
                st.session_state.asset = {
                    "filename": uploaded.name,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "fingerprint": digest,
                    "source": "Uploaded demo file",
                    "status": "Ready for approval",
                }
                add_event(f"Loaded uploaded asset: {uploaded.name}")

        if st.session_state.asset:
            st.markdown("### Asset card")
            st.json(st.session_state.asset)

    with right:
        st.subheader("2. Review metadata")
        account = st.selectbox("TikTok account label", ["Reuben Eczema", "Eczema Mitten SG", "Eczema Mitten US"])
        category = st.selectbox("Content category", ["Eczema education", "Founder story", "Product education", "Care routine"])
        caption = st.text_area(
            "Caption",
            "Night routine for eczema flare protection. Reviewed by the Eczema Mitten creator team before TikTok draft handoff.",
            height=130,
        )
        st.subheader("3. Approval checklist")
        approved = st.checkbox("Content is approved eczema education / founder-story material")
        reviewed = st.checkbox("Caption and account label reviewed")
        safe = st.checkbox("No spam, deception, or mass-publishing behavior")
        human = st.checkbox("Final TikTok posting remains human-reviewed")

        if st.button("Approve for TikTok draft handoff"):
            if not st.session_state.asset:
                st.error("Load an asset first.")
            elif not all([approved, reviewed, safe, human]):
                st.error("Complete all approval checks before queueing.")
            else:
                item = {
                    **st.session_state.asset,
                    "account": account,
                    "category": category,
                    "caption": caption,
                    "queued_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "handoff_status": "Ready for TikTok draft flow",
                }
                st.session_state.queue.insert(0, item)
                add_event(f"Approved {item['filename']} for TikTok draft handoff")
                st.success("Approved. The asset is now in the handoff queue.")


def render_queue():
    st.title("Handoff Queue")
    render_version()
    st.write("Approved videos waiting for TikTok upload/draft handoff.")

    if not st.session_state.queue:
        st.warning("No approved videos yet. Open Creator Workspace and approve a sample asset.")
        return

    for index, item in enumerate(st.session_state.queue):
        with st.container(border=True):
            col1, col2 = st.columns([0.75, 0.25])
            with col1:
                st.markdown(f"### {item['filename']}")
                st.write(f"**Account:** {item['account']}  |  **Category:** {item['category']}  |  **Size:** {item['size_mb']} MB")
                st.write(f"**Caption:** {item['caption']}")
                st.markdown(f"<span class='status-ready'>{item['handoff_status']}</span>", unsafe_allow_html=True)
            with col2:
                if st.button("Send to TikTok Draft Flow", key=f"send_{index}"):
                    item["handoff_status"] = "Demo sent to TikTok draft flow"
                    add_event(f"Demo TikTok draft handoff completed for {item['filename']}")
                    st.success("Demo handoff complete. In production this would call TikTok's upload/draft endpoint.")


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

## Demo video storyboard/script
{DEMO_SCRIPT}
"""
    st.download_button("Download review packet", packet, file_name="em-posting-tiktok-review-packet.md", mime="text/markdown")
    st.markdown(packet)


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
        ["Dashboard", "Creator Workspace", "Handoff Queue", "TikTok Review Packet", "Terms", "Privacy", "Activity Log"],
    )
    st.divider()
    st.caption("Public review demo. Production credentials are not included.")

if page == "Dashboard":
    render_dashboard()
elif page == "Creator Workspace":
    render_workspace()
elif page == "Handoff Queue":
    render_queue()
elif page == "TikTok Review Packet":
    render_review_packet()
elif page == "Terms":
    render_terms()
elif page == "Privacy":
    render_privacy()
else:
    render_events()
