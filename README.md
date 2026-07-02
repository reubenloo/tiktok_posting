# EM Posting

Private creator workflow demo for Eczema Mitten / Reuben Eczema TikTok developer app review.

EM Posting is a small Streamlit app that shows a legitimate internal creator operations flow:

1. public landing page
2. terms of service page
3. privacy policy page
4. private workspace/demo page
5. upload/review/send-to-tiktok-draft-flow mock
6. TikTok developer app review copy
7. demo video storyboard/script

## Positioning

This is not a public mass-posting platform. It is a private workflow tool for authorized team members who prepare and review approved eczema education / founder-story videos before sending them to TikTok's upload or draft flow for final human review.

The current app is a review/demo surface only. It does not include TikTok production credentials and does not publish videos.

## TikTok developer fields

### Description under 120 chars

Private creator workflow for preparing approved eczema education videos and sending them to TikTok drafts.

### App review explanation under 1000 chars

EM Posting is a private creator workflow tool used by the Eczema Mitten content team to prepare approved short-form educational videos and send them to TikTok for final review and posting. Our workflow starts with finished MP4 videos created by our internal editorial process. An authorized team member logs into EM Posting, selects a prepared video, reviews the caption and metadata, then uses the TikTok integration to upload the video to TikTok's posting/draft flow. The purpose of the Content Posting API integration is to reduce manual file transfer and preserve a human review step before publishing. The app is not a public mass-posting platform and does not auto-generate or spam content. Access is limited to authorized team members managing the Eczema Mitten / Reuben Eczema accounts.

## Requested TikTok product/scope

Content Posting API, preferably `video.upload` / upload-to-draft flow.

EM Posting only needs permission to upload a prepared MP4 and associated caption/metadata into TikTok's posting or draft workflow for final human review. The app does not need follower data, analytics, direct messages, comments, or broad account management permissions.

## Demo video storyboard/script

1. Open EM Posting landing page and explain this is a private creator operations tool for Eczema Mitten / Reuben Eczema.
2. Open the Workspace page and show that access is intended for authorized team members only.
3. Upload or select a prepared MP4 from the editorial workflow.
4. Review the generated file details, caption, account label, and approval checklist.
5. Confirm that the video is approved eczema education / founder-story content and is not spam or auto-generated posting.
6. Click the demo "Send to TikTok Draft Flow" button.
7. Show the confirmation state: the demo records that the video would be uploaded to TikTok's draft/posting flow for final human review.
8. Explain that the current demo does not publish directly and does not contain secrets; production TikTok API credentials would be configured only after app approval.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

- Repository: public GitHub repo
- Main file path: `app.py`
- No secrets required for the demo app
- If TikTok credentials are added later, store them only in Streamlit secrets, never in git

## Security notes

- Do not commit API tokens, cookies, customer files, private videos, or production secrets.
- The demo upload flow is local to the Streamlit session and does not call TikTok.
- Production TikTok integration should preserve human review before final posting.
