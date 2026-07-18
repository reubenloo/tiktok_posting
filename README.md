# EM Posting

Creator publishing workspace for reviewing finished short-form videos and handing approved posts to TikTok drafts.

EM Posting is being developed as a focused creator product, with the Eczema Mitten / Reuben Eczema team as its initial workspace. The public build demonstrates a real review-first short-form workflow:

1. polished creator home and studio
2. finished-video content library
3. caption, metadata, rights, policy, and consent review
4. deliberate one-post-at-a-time publish queue
5. TikTok draft handoff preview with a readable receipt
6. activity history, connection status, terms, and privacy

## Positioning

EM Posting is a creator publishing workspace for people and small teams who already have a finished video and want a clean final review before platform handoff. The initial pilot workspace belongs to the Reuben creator team.

It is not a mass publisher, engagement bot, scraper, autonomous spam tool, or direct public-posting system. The intended TikTok integration is upload/draft handoff so a human creator keeps final control in TikTok.

## TikTok developer fields

### Description under 120 chars

Creator workspace for reviewing finished videos and sending approved posts to TikTok drafts.

### App review explanation under 1000 chars

EM Posting is a creator workflow app for preparing finished short-form videos for TikTok. An authorized creator selects a completed MP4, reviews the account, caption, metadata, and content checks, then explicitly approves the video for TikTok's draft flow. The requested Content Posting API integration will reduce manual file transfer while preserving human review and final posting control in TikTok. The initial workspace is used by the Reuben creator team, but the product is designed as a focused creator publishing workspace rather than a mass-posting service. It does not scrape data, automate engagement, or publish spam.

## Requested TikTok product/scope

- Product: Content Posting API
- Scope: `video.upload`
- Planned production endpoint: `/v2/post/publish/inbox/video/init/`
- Intended result after approval and OAuth configuration: upload to TikTok draft/inbox flow for final creator editing and posting

EM Posting does not need follower data, analytics, direct messages, comments, or broad account management permissions.

## Recommended demo recording

A concise **spoken 75–90 second walkthrough** is recommended. A silent version also works.

1. Home — establish EM Posting as a creator workspace.
2. Studio — choose the bundled library video and review its post details.
3. Complete all final checks and click **Approve for publishing**.
4. Publish — show the approved post and click **Send to TikTok drafts**.
5. Hold on the handoff receipt showing creator control and preview status.
6. Connections — show the TikTok approval state.
7. Briefly show Terms and Privacy in the navigation.

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

## Deploy to Render

EM Posting can also run as a Render Web Service. The included `render.yaml` binds Streamlit to Render's injected `PORT` on `0.0.0.0`; it does not add credentials or change the public demo into a live TikTok integration.

In Render's **New Web Service** form, use:

- **Name:** `em-posting` (or any available name)
- **Branch:** `main`
- **Region:** Singapore
- **Root Directory:** leave blank
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
- **Instance Type:** Free is sufficient for the public demo (expect a cold start after inactivity)
- **Environment Variables:** none required for the public demo

Render reads `.python-version` and will use Python 3.12. The `render.yaml` file provides the same deploy settings if you later create the service through a Render Blueprint.

## Security notes

- Do not commit API tokens, cookies, customer files, private videos, or production secrets.
- The bundled sample MP4 is a generated public demo asset and contains no private footage.
- The demo handoff does not call TikTok.
- Production TikTok integration must preserve creator consent and human final posting control.
