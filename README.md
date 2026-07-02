# EM Posting

Creator workflow app for Eczema Mitten / Reuben Eczema TikTok developer app review.

EM Posting is a Streamlit app that demonstrates a real review-first short-form posting workflow:

1. public creator workflow dashboard
2. guided demo recorder page
3. creator workspace for sample/uploaded MP4 review
4. handoff queue that mocks TikTok upload-to-draft behavior
5. TikTok review packet with copy/paste fields
6. production integration plan
7. review-readiness checklist
8. terms of service and privacy policy pages

## Positioning

EM Posting is a creator operations app for a small authorized content team. It is designed for approved eczema education, founder-story, product education, and care-routine videos.

It is not a mass publisher, engagement bot, scraper, autonomous spam tool, or direct public-posting system. The intended TikTok integration is upload/draft handoff so a human creator keeps final control in TikTok.

## TikTok developer fields

### Description under 120 chars

Creator workflow for reviewing approved eczema education videos and sending them to TikTok drafts.

### App review explanation under 1000 chars

EM Posting is a creator workflow app used by the Eczema Mitten content team to prepare approved short-form educational videos and send them to TikTok for final review and posting. The workflow starts with finished MP4 videos created by our editorial process. An authorized team member opens EM Posting, selects a prepared video, reviews the caption and metadata, checks the approval steps, then uses the TikTok integration to upload the video to TikTok's posting/draft flow. The purpose of the Content Posting API integration is to reduce manual file transfer while preserving a human review step before publishing. The app is not a mass-posting platform and does not auto-generate or spam content. Access is limited to authorized creators and operators managing the Eczema Mitten / Reuben Eczema accounts.

## Requested TikTok product/scope

Content Posting API, preferably `video.upload` / upload-to-draft flow.

Expected endpoint shape: `/v2/post/publish/inbox/video/init/`.

EM Posting only needs permission to upload a prepared MP4 and associated caption/metadata into TikTok's posting or draft workflow for final human review. It does not need follower data, analytics, direct messages, comments, or broad account management permissions.

## Demo recording path

1. Open **Dashboard** and explain the app: prepared MP4 → review → TikTok draft handoff.
2. Open **Demo Recorder** and show the guided script.
3. Open **Creator Workspace** and use the sample asset or upload a mock MP4.
4. Review account, category, caption, hashtags, and consent/safety checklist.
5. Approve the asset for TikTok draft handoff.
6. Open **Handoff Queue** and click the demo send action.
7. Open **TikTok Review Packet** and show the app description, review explanation, and scope justification.
8. Open **Terms** and **Privacy** if the reviewer asks where they are.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy to Streamlit Community Cloud

- Repository: `reubenloo/tiktok_posting`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Python: select Python 3.12 in Streamlit Cloud settings if available
- No secrets required for the demo app

Note: `runtime.txt` is included as a hint, but Streamlit Community Cloud may require the Python version to be selected in the app settings UI.

## Security notes

- Do not commit API tokens, cookies, customer files, private videos, or production secrets.
- The demo upload flow is local to the Streamlit session and does not call TikTok.
- Production TikTok integration should preserve human review before final posting.
