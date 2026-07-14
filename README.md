# EM Posting

Creator workflow app for Eczema Mitten / Reuben Eczema TikTok developer app review.

EM Posting demonstrates a real review-first short-form workflow:

1. public creator workflow dashboard
2. silent demo recording guide
3. creator workspace with a bundled public sample MP4 or user-selected mock MP4
4. caption, metadata, safety, and explicit creator-consent review
5. handoff queue that clearly mocks TikTok upload-to-draft behavior
6. readable success receipt confirming no live API call was made
7. TikTok review packet, production plan, terms, and privacy pages

## Positioning

EM Posting is a creator operations app for a small authorized content team. It supports approved eczema education, founder-story, product education, and care-routine videos.

It is not a mass publisher, engagement bot, scraper, autonomous spam tool, or direct public-posting system. The intended TikTok integration is upload/draft handoff so a human creator keeps final control in TikTok.

## TikTok developer fields

### Description under 120 chars

Creator workflow for reviewing approved eczema education videos and sending them to TikTok drafts.

### App review explanation under 1000 chars

EM Posting is a creator workflow app used by the Eczema Mitten content team to prepare approved short-form educational videos and send them to TikTok for final review and posting. The workflow starts with finished MP4 videos created by our editorial process. An authorized team member opens EM Posting, selects a prepared video, reviews the caption and metadata, checks the approval steps, then uses the TikTok integration to upload the video to TikTok's posting/draft flow. The purpose of the Content Posting API integration is to reduce manual file transfer while preserving a human review step before publishing. The app is not a mass-posting platform and does not auto-generate or spam content. Access is limited to authorized creators and operators managing the Eczema Mitten / Reuben Eczema accounts.

## Requested TikTok product/scope

- Product: Content Posting API
- Scope: `video.upload`
- Expected endpoint shape: `/v2/post/publish/inbox/video/init/`
- Intended result: upload to TikTok draft/inbox flow for final creator editing and posting

EM Posting does not need follower data, analytics, direct messages, comments, or broad account management permissions.

## Recommended demo recording

A simple **silent 60–70 second screen recording** is enough. Voiceover is optional.

1. Dashboard — hold on the app positioning and Prepare → Review → Handoff cards.
2. Demo Guide — show the silent shot list and no-live-credentials notice.
3. Creator Workspace — load the bundled sample asset and briefly play its preview.
4. Keep the default metadata, tick all five review/consent checks, and approve it.
5. Handoff Queue — show the approved asset, creator consent, and endpoint mock.
6. Click **Send to TikTok Draft Flow (demo)**.
7. Hold on the success receipt showing creator control and that no live API call occurred.
8. TikTok Review Packet — briefly show `video.upload`, Terms, and Privacy.

Recording rules:

- record the browser window only
- use 100% browser zoom
- use the bundled sample asset for a clean repeatable path
- do not show TikTok login, tokens, or secrets
- pause long enough on the handoff receipt for a reviewer to read it

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
- No secrets required for the public demo

`runtime.txt` is included as a hint, but Streamlit Community Cloud may require Python 3.12 to be selected in its settings UI.

## Security notes

- Do not commit API tokens, cookies, customer files, private videos, or production secrets.
- The bundled sample MP4 is a generated public demo asset and contains no private footage.
- The demo handoff does not call TikTok.
- Production TikTok integration must preserve creator consent and human final posting control.
