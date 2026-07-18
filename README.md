# EM Posting

Creator publishing workspace for reviewing finished short-form videos and handing approved posts to TikTok drafts.

EM Posting is a focused creator product with a real TikTok Sandbox integration. It demonstrates one review-first path from a finished video to an approved draft upload:

1. **Home** — a calm overview of the four-step workflow.
2. **Studio** — select the bundled sample or upload a finished MP4, then review the account, write the description, and explicitly approve.
3. **Publish** — connect an authorized TikTok Sandbox user and upload one approved MP4 to TikTok drafts.
4. **Legal** — Terms of Service and Privacy Policy.

## Positioning

EM Posting is a creator publishing workspace for people and small teams who already have a finished video and want a clean final review before platform handoff.

It is not a mass publisher, engagement bot, scraper, autonomous spam tool, or direct public-posting system. The intended TikTok integration is upload/draft handoff so a human creator keeps final control inside TikTok.

## Integration notes

- Login Kit requests only `user.info.basic` and `video.upload`.
- Draft upload uses `FILE_UPLOAD` with `/v2/post/publish/inbox/video/init/`; it never directly publishes.
- Credentials and tokens are server-side only and are never stored in this repository.
- The bundled sample MP4 is a generated public demo asset and contains no private footage.

## TikTok submission fields

This section is the submission copy for TikTok's developer portal. It is intentionally kept in the README, not in the app's navigation.

### Description (under 120 characters)

Creator workspace for reviewing finished videos and sending approved posts to TikTok drafts.

### App review explanation (under 1000 characters)

EM Posting uses Login Kit and TikTok's Content Posting API to upload one creator-approved MP4 to the authorized creator's TikTok draft/inbox flow. The creator signs in with TikTok and grants user.info.basic and video.upload. In EM Posting, the creator selects or uploads a finished MP4, previews it, confirms content rights and policy compliance, and explicitly approves the transfer. EM Posting initializes the upload through /v2/post/publish/inbox/video/init/ using FILE_UPLOAD and transfers the MP4 to TikTok's provided upload URL. The creator then opens the notification in TikTok to complete the caption, final editing, and posting. EM Posting does not directly publish, bulk post, scrape data, or automate engagement.

## Requested TikTok product / scope (submission only)

- **Product:** Content Posting API
- **Scope:** `video.upload`
- **Mode:** the app uploads a single creator-approved video to the TikTok draft/inbox flow; it does not publish directly.
- **First-time review:** demonstrate the real Login Kit authorization and draft upload using an authorized Sandbox target user.
- **Website domain:** the domain shown in the demo video must match the submitted website URL (`tiktok-posting.onrender.com`).

EM Posting does not need follower data, analytics, direct messages, comments, or broad account-management permissions.

## Demo recording

A concise spoken 75–90 second walkthrough is recommended (a silent version also works):

1. **Home** — establish EM Posting as a creator workspace.
2. **Studio** — choose the bundled sample video, review the account and caption, complete every final check, and click **Approve for handoff**.
3. **Publish** — connect the authorized Sandbox TikTok account and click **Upload to TikTok drafts**.
4. Hold on the receipt showing TikTok's real publish ID, then show the TikTok inbox notification.
5. Briefly show the **Legal** page (Terms and Privacy).

Recording rules:

- record the browser window only, at 100% zoom
- keep the browser address bar visible so the on-screen domain matches `tiktok-posting.onrender.com`
- use the bundled sample asset for a clean, repeatable path
- show the TikTok consent screen, but never show tokens or secrets
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
- **Start Command:** `python server.py`
- **Instance Type:** Free is sufficient for the public demo (expect a cold start after inactivity)
- **Environment Variables:** `SANDBOX_TIKTOK_CLIENT_KEY`, `SANDBOX_TIKTOK_CLIENT_SECRET`, and `SANDBOX_TIKTOK_SESSION_SECRET`

Render reads `.python-version` and uses Python 3.12. The `render.yaml` file provides the same settings for a Render Blueprint.

## Security notes

- Do not commit API tokens, cookies, customer files, private videos, or production secrets.
- OAuth tokens remain server-side and the public repository contains no TikTok credentials.
- Draft upload preserves creator consent and human final posting control inside TikTok.
