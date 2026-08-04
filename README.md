# EM Posting

Creator publishing workspace for reviewing finished short-form videos and handing approved posts to TikTok drafts.

EM Posting is a focused creator product with a real TikTok Sandbox integration. The workspace is fully usable without TikTok credentials — the TikTok connection is required only for the final handoff step.

## Public workspace features (no credentials required)

The following features are publicly accessible without any login or TikTok authorization:

1. **Home** — Project library dashboard with workspace stats, quick actions, and activity log
2. **Review** — Full review workflow with project checklist, caption preparation, and approval flow
3. **Studio** — Add new projects (sample or uploaded MP4) to the library
4. **Legal** — Terms of Service and Privacy Policy

A bundled sample project is included in the library, allowing any visitor to:
- Open a project and preview the video
- Complete the full review checklist
- Prepare caption notes
- Approve the project for handoff

## TikTok handoff (authorized creators only)

The final handoff step requires an authorized TikTok Sandbox account:

1. **Handoff** — Connect TikTok and send approved projects to TikTok's draft/inbox flow

This step uses Login Kit and the Content Posting API with the `video.upload` scope.

## Positioning

EM Posting is a creator publishing workspace for people and small teams who already have a finished video and want a clean final review before platform handoff.

It is not a mass publisher, engagement bot, scraper, autonomous spam tool, or direct public-posting system. The intended TikTok integration is upload/draft handoff so a human creator keeps final control inside TikTok.

## Integration notes

- Login Kit requests only `user.info.basic` and `video.upload`.
- Draft upload uses `FILE_UPLOAD` with `/v2/post/publish/inbox/video/init/`; it never directly publishes.
- Credentials and tokens are server-side only and are never stored in this repository.
- The bundled sample MP4 is a generated public demo asset and contains no private footage.
- The externally-facing origin (Home, Terms, Privacy, sign-in link, and the OAuth redirect URI) is
  derived from the `EM_POSTING_PUBLIC_URL` environment variable. When it is unset, the app falls
  back to `https://posting-app-gvtf.onrender.com`, the current production Render domain.

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
- **Website domain:** the domain shown in the demo video must match the submitted Website, Terms, and Privacy URLs. The production Render domain is `posting-app-gvtf.onrender.com`.

EM Posting does not need follower data, analytics, direct messages, comments, or broad account-management permissions.

## Demo recording

A concise spoken 75–90 second walkthrough is recommended (a silent version also works):

1. **Home** — Show the project library dashboard with workspace stats, projects, and activity log.
2. **Review** — Open a sample project, show the video preview, complete the checklist, and approve.
3. **Handoff** — Connect the authorized Sandbox TikTok account and click **Upload to TikTok drafts**.
4. Hold on the receipt showing TikTok's real publish ID, then show the TikTok inbox notification.
5. Briefly show the **Legal** page (Terms and Privacy).

Recording rules:

- record the browser window only, at 100% zoom
- keep the browser address bar visible so the on-screen domain matches the submitted Website/Terms/Privacy URLs (the production custom domain, or the Render fallback for Sandbox-only demos)
- use the bundled sample asset for a clean, repeatable path
- show the TikTok consent screen, but never show tokens or secrets
- pause long enough on the handoff receipt for a reviewer to read it

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

Then open `http://localhost:10000` in a browser. The server runs Streamlit internally and serves the full workspace.

For Streamlit-only development (without the FastAPI proxy):

```bash
streamlit run streamlit_app.py
```

Python 3.12 is expected (see `.python-version` and `runtime.txt`).

### Running tests

```bash
pip install pytest
pytest test_tiktok_integration.py -v
```

Tests verify:
- Public workspace functionality (project library, review checklist, activity log)
- TikTok integration endpoints (session, upload, status)
- Favicon and icon consistency
- Legal page accessibility

## Deploy to Render

EM Posting runs on Render as a Web Service through `python server.py`. The FastAPI front controller binds Render's injected `PORT`, serves the required verification/API/OAuth routes, and proxies the Streamlit interface running privately on `127.0.0.1:8502`. It does not add credentials or turn the public demo into a live TikTok integration.

In Render's **New Web Service** form, use:

- **Name:** `em-posting` (or any available name)
- **Branch:** `main`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python server.py`
- **Instance Type:** Free is sufficient for the public workspace (expect a cold start after inactivity)
- **Environment Variables:** `SANDBOX_TIKTOK_CLIENT_KEY`, `SANDBOX_TIKTOK_CLIENT_SECRET`, `SANDBOX_TIKTOK_SESSION_SECRET`, and `EM_POSTING_PUBLIC_URL` (set to your public origin; required for a production custom domain, optional for the Sandbox fallback)

Render reads `.python-version` and uses Python 3.12. The `render.yaml` file provides the same settings for a Render Blueprint.

## Production domain and resubmission

Production uses `https://posting-app-gvtf.onrender.com`, which does not contain TikTok branding.
Set `EM_POSTING_PUBLIC_URL=https://posting-app-gvtf.onrender.com` in the Render service Environment
and redeploy. The app then uses that same origin for Home, Terms, Privacy, sign-in, and the OAuth
`redirect_uri`.

Update TikTok Developer Portal (Sandbox first, then Production):

- **Website URL:** `https://posting-app-gvtf.onrender.com/`
- **Terms of Service URL:** `https://posting-app-gvtf.onrender.com/?page=legal&policy=terms`
- **Privacy Policy URL:** `https://posting-app-gvtf.onrender.com/?page=legal&policy=privacy`
- **Login Kit → Redirect URI:** `https://posting-app-gvtf.onrender.com/auth/tiktok/callback/`

Re-verify the URL property using the exact file served at:

`https://posting-app-gvtf.onrender.com/tiktok8i8uszpdFElTqWKuJjxT8oFX5Gwx8T6z.txt`

Then re-record the demo with this domain visible in the browser address bar and resubmit. Do not
claim approval until TikTok completes review.

## What's publicly usable without credentials

- **Home:** Full project library dashboard with stats, quick actions, activity log
- **Review:** Complete review workflow for any project (sample or uploaded)
- **Studio:** Add videos to the library (sample or upload)
- **Legal:** Terms and Privacy pages

## What requires TikTok authorization

- **Handoff → Upload to TikTok drafts:** Requires connected TikTok Sandbox account

The workspace workflow is designed so reviewers can fully explore the product functionality without any test credentials. The TikTok authorization step is an explicit, optional connection for creators who want to use the handoff feature.

## Security notes

- Do not commit API tokens, cookies, customer files, private videos, or production secrets.
- OAuth tokens remain server-side and the public repository contains no TikTok credentials.
- Draft upload preserves creator consent and human final posting control inside TikTok.
