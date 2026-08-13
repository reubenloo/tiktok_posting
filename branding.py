"""Single source of truth for product identity and legal copy.

TikTok app review requires the app name, the website title, and the domain to match exactly.
Streamlit sets the browser tab title from JavaScript *after* the page loads, so a reviewer or
crawler fetching the raw HTML only ever sees Streamlit's default "Streamlit" title. The FastAPI
layer in server.py therefore rewrites the served HTML using APP_NAME from this module, and serves
the legal pages below as real, crawlable HTML documents at their own URL paths.

APP_NAME is overridable via EM_POSTING_APP_NAME so the deployed name can be aligned with whatever
domain the app is finally hosted on without a code change.
"""

from __future__ import annotations

import html
import os
import re
from textwrap import dedent

APP_NAME = os.environ.get("EM_POSTING_APP_NAME", "EM Posting").strip() or "EM Posting"

TAGLINE = "One calm place to take a finished video from final cut to an approved TikTok draft."

SHORT_DESCRIPTION = (
    "Creator workspace for reviewing finished videos and sending approved posts to TikTok drafts."
)

CONTACT_EMAIL = os.environ.get("EM_POSTING_CONTACT_EMAIL", "contact@eczemamitten.com").strip()

# Path -> (page title suffix, markdown body). These paths are what TikTok asks for explicitly:
# https://<domain>/privacy-policy and https://<domain>/terms-of-service
TERMS_PATH = "/terms-of-service"
PRIVACY_PATH = "/privacy-policy"


TERMS = dedent(
    f"""
    # Terms of Service

    **Last updated: July 2026**

    {APP_NAME} is a creator workflow product for preparing, reviewing, and handing approved
    short-form videos to supported social platforms.

    ## Account and workspace use
    You may use {APP_NAME} only for workspaces and creator accounts you are authorized to manage.
    You are responsible for the videos, descriptions, approvals, and account selections made in your
    workspace.

    ## Creator approval
    {APP_NAME} is designed around deliberate human review. A creator or authorized team member must
    review each post before initiating a platform handoff. The service may not be used for spam,
    deceptive automation, unauthorized account access, or attempts to bypass platform controls.

    ## Platform services
    Platform integrations remain subject to each platform's terms, permissions, technical limits, and
    review requirements. A successful handoff does not guarantee publication. Final editing and
    posting may continue inside the destination platform.

    ## Content rights
    You must have the rights and permissions required to upload and publish the content you submit.

    ## Availability
    Features may change as integrations mature. TikTok Sandbox connections and draft uploads are
    available only to authorized pilot users. A successful draft upload does not guarantee that the
    creator will complete or publish the post inside TikTok.

    ## Contact
    Product and policy questions may be sent to {CONTACT_EMAIL} while {APP_NAME} is in its
    initial creator pilot.
    """
).strip()


PRIVACY = dedent(
    f"""
    # Privacy Policy

    **Last updated: July 2026**

    {APP_NAME} is a creator workflow product. This policy describes the information the service may
    process to prepare and hand creator-approved posts to supported platforms.

    ## Information processed
    {APP_NAME} may process creator account labels, finished video files, descriptions, review notes,
    approval choices, file metadata, and workflow activity such as review and handoff timestamps.

    ## How information is used
    This information is used to display the creator workspace, preserve review decisions, prepare
    platform handoffs, and show workflow receipts to authorized users.

    ## Platform data
    The TikTok integration uses Login Kit to access the connected creator's basic identity and uses
    video.upload only after explicit approval to transfer one MP4 to the draft/inbox flow. {APP_NAME}
    does not request direct messages, comments, follower lists, analytics, or unrelated account data.

    ## Storage
    This pilot uses session-only application state and does not permanently store uploaded videos.
    TikTok access and refresh tokens are kept server-side for the active pilot session and are never
    exposed in the browser or public source repository. Sessions can be disconnected at any time.

    ## Sharing
    Content would be sent to a platform only after an authorized creator initiates the handoff.
    {APP_NAME} does not sell personal information.

    ## Security
    Any future production credentials must be stored in private deployment secrets and are never
    included in the public source repository.

    ## Contact
    Privacy questions may be sent to {CONTACT_EMAIL} during the initial pilot.
    """
).strip()


def _markdown_to_html(markdown_text: str) -> str:
    """Convert the small markdown subset used above into HTML.

    Deliberately dependency-free: only headings, bold, and paragraphs are used in the legal copy.
    """
    lines = markdown_text.splitlines()
    parts: list[str] = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            text = " ".join(paragraph).strip()
            if text:
                parts.append(f"<p>{text}</p>")
            paragraph.clear()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if line.startswith("## "):
            flush()
            parts.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("# "):
            flush()
            parts.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
        else:
            escaped = html.escape(line)
            escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            paragraph.append(escaped)
    flush()
    return "\n      ".join(parts)


_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <meta name="description" content="{description}" />
    <meta property="og:site_name" content="{app_name}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <link rel="icon" href="/favicon.png" />
    <style>
      body {{
        margin: 0; padding: 3rem 1.25rem; background: #f6f5f1; color: #1a1a1f;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.65;
      }}
      main {{ max-width: 46rem; margin: 0 auto; background: #fff; border: 1px solid #e8e6e0;
              border-radius: 14px; padding: 2.5rem; }}
      h1 {{ font-size: 1.9rem; margin: 0 0 1.25rem; }}
      h2 {{ font-size: 1.15rem; margin: 2rem 0 .5rem; }}
      a {{ color: #4f46e5; }}
      nav {{ max-width: 46rem; margin: 0 auto 1.25rem; font-size: .95rem; }}
      footer {{ max-width: 46rem; margin: 1.25rem auto 0; font-size: .85rem; color: #71717a; }}
    </style>
  </head>
  <body>
    <nav><a href="/">&larr; {app_name}</a></nav>
    <main>
      {body}
    </main>
    <footer>
      <a href="{terms_path}">Terms of Service</a> &middot;
      <a href="{privacy_path}">Privacy Policy</a> &middot;
      <a href="mailto:{contact}">{contact}</a>
    </footer>
  </body>
</html>
"""


def legal_page_html(policy: str) -> str:
    """Full standalone HTML for a legal page, crawlable without running JavaScript."""
    if policy == "terms":
        heading, markdown_text = "Terms of Service", TERMS
    else:
        heading, markdown_text = "Privacy Policy", PRIVACY
    return _PAGE_TEMPLATE.format(
        title=html.escape(f"{APP_NAME} - {heading}"),
        description=html.escape(SHORT_DESCRIPTION),
        app_name=html.escape(APP_NAME),
        body=_markdown_to_html(markdown_text),
        terms_path=TERMS_PATH,
        privacy_path=PRIVACY_PATH,
        contact=html.escape(CONTACT_EMAIL),
    )


def rewrite_document_head(html_text: str) -> str:
    """Replace Streamlit's placeholder title/description in served HTML with the real app identity.

    Streamlit ships a static index.html containing `<title>Streamlit</title>`; the real title is
    only applied client-side once the app boots. Reviewers and crawlers read the raw HTML, so the
    served document must already carry the correct name.
    """
    title_tag = f"<title>{html.escape(APP_NAME)}</title>"
    if "<title>" in html_text:
        html_text = re.sub(r"<title>.*?</title>", title_tag, html_text, count=1, flags=re.S)
    else:
        html_text = html_text.replace("<head>", f"<head>{title_tag}", 1)

    description = html.escape(SHORT_DESCRIPTION)
    html_text = re.sub(
        r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',
        f'<meta name="description" content="{description}" />',
        html_text,
        count=1,
    )
    if 'name="description"' not in html_text:
        html_text = html_text.replace("</title>", f'</title><meta name="description" content="{description}" />', 1)

    if 'property="og:title"' not in html_text:
        og_tags = (
            f'<meta property="og:site_name" content="{html.escape(APP_NAME)}" />'
            f'<meta property="og:title" content="{html.escape(APP_NAME)}" />'
            f'<meta property="og:description" content="{description}" />'
        )
        html_text = html_text.replace("</title>", f"</title>{og_tags}", 1)
    return html_text
