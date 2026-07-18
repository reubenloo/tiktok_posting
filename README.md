# EM Posting

Creator publishing workspace for reviewing finished short-form videos and handing approved posts to TikTok drafts.

EM Posting is a focused creator product. The public build is a **workflow preview** — it never contacts TikTok — that demonstrates one review-first path from a finished video to an approved draft handoff:

1. **Home** — a calm overview of the four-step workflow.
2. **Studio** — select the bundled sample or upload a finished MP4, then review the account, write the description, and explicitly approve.
3. **Publish** — a one-post-at-a-time queue that previews an honest draft handoff receipt.
4. **Legal** — Terms of Service and Privacy Policy.

## Positioning

EM Posting is a creator publishing workspace for people and small teams who already have a finished video and want a clean final review before platform handoff.

It is not a mass publisher, engagement bot, scraper, autonomous spam tool, or direct public-posting system. The intended TikTok integration is upload/draft handoff so a human creator keeps final control inside TikTok.

## Honesty notes

- This public build does **not** call any TikTok API and performs **no OAuth**. The "Preview draft handoff" action produces a local, readable receipt only.
- No credentials, tokens, or secrets are stored in this repository or required to run the demo.
- The bundled sample MP4 is a generated public demo asset and contains no private footage.

## TikTok submission fields

This section is the submission copy for TikTok's developer portal. It is intentionally kept in the README, not in the app's navigation.

### Description (under 120 characters)

Creator workspace for reviewing finished videos and sending approved posts to TikTok drafts.

### App review explanation (under 1000 characters)

EM Posting is a creator workflow app for preparing finished short-form videos for TikTok. An authorized creator selects or uploads a completed MP4, reviews the account, description, and content confirmations, then explicitly approves the video for TikTok's draft flow. The requested Content Posting API integration reduces manual file transfer while preserving human review and final posting control inside TikTok. It is a focused creator publishing workspace, not a mass-posting service. It does not scrape data, automate engagement, or publish spam.

## Requested TikTok product / scope (submission only)

- **Product:** Content Posting API
- **Scope:** `video.upload`
- **Mode:** submission-only — the app uploads a single creator-approved video to the TikTok draft/inbox flow; it does not publish directly.
- **First-time review:** TikTok requires the real integration to be demonstrated in **Sandbox**. The current public build is an honest workflow preview and does not substitute for that API proof.
- **Website domain:** the domain shown in the demo video must match the submitted website URL (`tiktok-posting.onrender.com`).

EM Posting does not need follower data, analytics, direct messages, comments, or broad account-management permissions.

## Demo recording

A concise spoken 75–90 second walkthrough is recommended (a silent version also works):

1. **Home** — establish EM Posting as a creator workspace.
2. **Studio** — choose the bundled sample video, review the account and caption, complete every final check, and click **Approve for handoff**.
3. **Publish** — show the approved post and click **Preview draft handoff**.
4. Hold on the handoff receipt showing creator control and the preview-only notice.
5. Briefly show the **Legal** page (Terms and Privacy).

Recording rules:

- record the browser window only, at 100% zoom
- keep the browser address bar visible so the on-screen domain matches `tiktok-posting.onrender.com`
- use the bundled sample asset for a clean, repeatable path
- do not show TikTok login, tokens, or secrets
- pause long enough on the handoff receipt for a reviewer to read it

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Python 3.12 is expected (see `.python-version` and `runtime.txt`).

## Deploy to Streamlit Community Cloud

- Repository: `reubenloo/tiktok_posting`
- Branch: `main`
- Main file path: `streamlit_app.py` (it executes `app.py` via `runpy` on every script run)
- Python: select Python 3.12 in Streamlit Cloud settings if available
- No secrets required for the public demo

## Deploy to Render

EM Posting can also run as a Render Web Service. The included `render.yaml` runs `app.py` directly and binds Streamlit to Render's injected `PORT` on `0.0.0.0`; it does not add credentials or turn the public demo into a live TikTok integration.

In Render's **New Web Service** form, use:

- **Name:** `em-posting` (or any available name)
- **Branch:** `main`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
- **Instance Type:** Free is sufficient for the public demo (expect a cold start after inactivity)
- **Environment Variables:** none required

Render reads `.python-version` and uses Python 3.12. The `render.yaml` file provides the same settings for a Render Blueprint.

## Security notes

- Do not commit API tokens, cookies, customer files, private videos, or production secrets.
- The demo handoff does not call TikTok and performs no OAuth.
- Any future production integration must preserve creator consent and human final posting control.
