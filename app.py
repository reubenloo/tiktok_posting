import hashlib
from datetime import datetime
from textwrap import dedent

import streamlit as st

APP_VERSION = "v0.1.0"
APP_NAME = "EM Posting"

SHORT_DESCRIPTION = (
    "Private creator workflow for preparing approved eczema education videos and sending them to TikTok drafts."
)

APP_REVIEW_EXPLANATION = (
    "EM Posting is a private creator workflow tool used by the Eczema Mitten content team to prepare approved "
    "short-form educational videos and send them to TikTok for final review and posting. Our workflow starts with "
    "finished MP4 videos created by our internal editorial process. An authorized team member logs into EM Posting, "
    "selects a prepared video, reviews the caption and metadata, then uses the TikTok integration to upload the video "
    "to TikTok's posting/draft flow. The purpose of the Content Posting API integration is to reduce manual file "
    "transfer and preserve a human review step before publishing. The app is not a public mass-posting platform and "
    "does not auto-generate or spam content. Access is limited to authorized team members managing the Eczema Mitten "
    "/ Reuben Eczema accounts."
)

SCOPE_JUSTIFICATION = dedent(
    """
    Requested TikTok product/scope: Content Posting API, preferably video.upload / upload-to-draft flow.

    EM Posting only needs permission to upload a prepared MP4 and associated caption/metadata into TikTok's posting or draft workflow for final human review. The app does not need follower data, analytics, direct messages, comments, or broad account management permissions.

    The integration is used by authorized internal creators to move approved eczema education and founder-story videos from our editorial workflow into TikTok without manual file transfer. A team member reviews the video and caption before sending it to TikTok, and final posting remains under human control.
    """
).strip()

DEMO_SCRIPT = dedent(
    """
    1. Open EM Posting landing page and explain this is a private creator operations tool for Eczema Mitten / Reuben Eczema.
    2. Open the Workspace page and show that access is intended for authorized team members only.
    3. Upload or select a prepared MP4 from the editorial workflow.
    4. Review the generated file details, caption, account label, and approval checklist.
    5. Confirm that the video is approved eczema education / founder-story content and is not spam or auto-generated posting.
    6. Click the demo “Send to TikTok Draft Flow” button.
    7. Show the confirmation state: the demo records that the video would be uploaded to TikTok's draft/posting flow for final human review.
    8. Explain that the current demo does not publish directly and does not contain secrets; production TikTok API credentials would be configured only after app approval.
    """
).strip()

TERMS = dedent(
    """
    # Terms of Service

    Last updated: July 2026

    EM Posting is a private creator workflow tool for authorized Eczema Mitten / Reuben Eczema team members. By using this app, you agree to use it only for approved short-form educational, founder-story, and ecommerce-related content managed by the team.

    ## Authorized use
    Access is limited to approved internal users. Users may review prepared videos, captions, metadata, and demo upload steps connected to the team's social posting workflow.

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

    EM Posting is a private creator workflow tool for authorized Eczema Mitten / Reuben Eczema team members.

    ## Information processed
    The app may process prepared MP4 videos, captions, account labels, internal approval status, and basic technical metadata such as filename, file size, and upload time.

    ## Purpose
    This information is used to help authorized team members review approved eczema education and founder-story videos before sending them to TikTok's upload, draft, or posting workflow.

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

if "demo_events" not in st.session_state:
    st.session_state.demo_events = []


def file_fingerprint(uploaded_file):
    data = uploaded_file.getvalue()
    return hashlib.sha256(data).hexdigest()[:16], len(data)


def add_event(message):
    st.session_state.demo_events.append({
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "event": message,
    })


def render_header():
    st.title("EM Posting")
    st.caption(f"{APP_VERSION} - private creator review and TikTok draft handoff demo")


def render_landing():
    render_header()
    st.subheader("Private creator workflow for approved eczema education videos")
    st.write(
        "EM Posting helps authorized Eczema Mitten / Reuben Eczema team members review prepared short-form videos, "
        "confirm captions and metadata, and send approved MP4 files into TikTok's upload or draft flow for final human posting."
    )
    st.info("This public demo shows the review workflow. It does not include production TikTok credentials and does not publish directly.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 1. Prepared videos")
        st.write("Finished MP4 files come from the internal editorial workflow, not from automated spam generation.")
    with col2:
        st.markdown("### 2. Human review")
        st.write("An authorized team member checks the content, caption, account label, and approval checklist.")
    with col3:
        st.markdown("### 3. TikTok draft handoff")
        st.write("The requested API access uploads approved videos to TikTok's posting/draft flow for final review.")

    st.markdown("### TikTok developer app fields")
    st.text_area("Description under 120 characters", SHORT_DESCRIPTION, height=80)
    st.text_area("App review explanation under 1000 characters", APP_REVIEW_EXPLANATION, height=180)
    st.text_area("Scope/product justification", SCOPE_JUSTIFICATION, height=180)


def render_workspace():
    render_header()
    st.subheader("Private workspace / demo flow")
    st.warning("Demo mode: no TikTok API call is made. Production credentials must be stored only in deployment secrets after approval.")

    with st.form("review_form"):
        uploaded = st.file_uploader("Prepared MP4 video", type=["mp4"])
        account = st.selectbox("Target account label", ["Reuben Eczema", "Eczema Mitten SG", "Eczema Mitten US"])
        caption = st.text_area(
            "Caption / post text",
            "Approved eczema education video. Final caption reviewed by an authorized team member.",
            height=120,
        )
        col1, col2 = st.columns(2)
        with col1:
            approved = st.checkbox("Video is approved educational/founder-story content")
            reviewed = st.checkbox("Caption and metadata reviewed")
        with col2:
            no_spam = st.checkbox("Not spam, not mass publishing, not deceptive automation")
            human_final = st.checkbox("Final TikTok posting remains human-reviewed")
        submitted = st.form_submit_button("Review video")

    if submitted:
        if not uploaded:
            st.error("Upload a prepared MP4 to continue the demo.")
        elif not all([approved, reviewed, no_spam, human_final]):
            st.error("Complete the approval checklist before the TikTok draft handoff step.")
        else:
            digest, size = file_fingerprint(uploaded)
            st.session_state.review = {
                "filename": uploaded.name,
                "size_mb": round(size / (1024 * 1024), 2),
                "fingerprint": digest,
                "account": account,
                "caption": caption,
            }
            add_event(f"Reviewed {uploaded.name} for {account}")
            st.success("Review complete. Ready for TikTok draft handoff demo.")

    review = st.session_state.get("review")
    if review:
        st.markdown("### Review summary")
        st.json(review)
        if st.button("Send to TikTok Draft Flow (demo)"):
            add_event(f"Demo handoff queued for {review['filename']} to TikTok draft flow")
            st.success("Demo complete: this would upload the approved MP4 to TikTok's draft/posting flow for final human review.")

    st.markdown("### Demo event log")
    if st.session_state.demo_events:
        st.table(st.session_state.demo_events)
    else:
        st.write("No demo events yet.")


def render_terms():
    render_header()
    st.markdown(TERMS)


def render_privacy():
    render_header()
    st.markdown(PRIVACY)


def render_review_packet():
    render_header()
    st.subheader("TikTok app review packet")
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

page = st.sidebar.radio(
    "Navigation",
    ["Landing", "Workspace Demo", "Terms of Service", "Privacy Policy", "TikTok Review Packet"],
)

st.sidebar.divider()
st.sidebar.caption("Open-source demo. No secrets. No direct publishing claim.")

if page == "Landing":
    render_landing()
elif page == "Workspace Demo":
    render_workspace()
elif page == "Terms of Service":
    render_terms()
elif page == "Privacy Policy":
    render_privacy()
else:
    render_review_packet()
