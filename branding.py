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


_LANDING_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{app_name}</title>
    <meta name="description" content="{description}" />
    <meta property="og:site_name" content="{app_name}" />
    <meta property="og:title" content="{app_name}" />
    <meta property="og:description" content="{description}" />
    <link rel="icon" href="/favicon.png" />
    <style>
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0; background: #f6f5f1; color: #1a1a1f;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.6;
      }}
      .wrap {{ max-width: 60rem; margin: 0 auto; padding: 2rem 1.25rem 3rem; }}
      header.top {{ display: flex; align-items: center; gap: .7rem; padding-bottom: 1.5rem; }}
      header.top img {{ width: 40px; height: 40px; border-radius: 9px; }}
      header.top .name {{ font-weight: 700; font-size: 1.15rem; }}
      .hero {{ background: #fff; border: 1px solid #e8e6e0; border-radius: 16px; padding: 2.5rem; }}
      .hero h1 {{ font-size: 2.1rem; margin: 0 0 .75rem; line-height: 1.25; }}
      .hero p.lede {{ font-size: 1.1rem; color: #3f3f46; margin: 0 0 1.5rem; max-width: 42rem; }}
      .cta {{ display: inline-block; background: #1a1a1f; color: #fff; text-decoration: none;
              padding: .8rem 1.4rem; border-radius: 10px; font-weight: 600; }}
      .cta.secondary {{ background: #fff; color: #1a1a1f; border: 1px solid #d4d4d8; margin-left: .5rem; }}
      h2 {{ font-size: 1.35rem; margin: 2.5rem 0 1rem; }}
      .steps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: 1rem; }}
      .step {{ background: #fff; border: 1px solid #e8e6e0; border-radius: 12px; padding: 1.25rem; }}
      .step .num {{ display: inline-flex; align-items: center; justify-content: center;
                    width: 26px; height: 26px; border-radius: 50%; background: #1a1a1f; color: #fff;
                    font-size: .85rem; font-weight: 700; margin-bottom: .6rem; }}
      .step h3 {{ margin: 0 0 .4rem; font-size: 1rem; }}
      .step p {{ margin: 0; font-size: .93rem; color: #52525b; }}
      ul.plain {{ padding-left: 1.1rem; }}
      ul.plain li {{ margin-bottom: .5rem; }}
      .panel {{ background: #fff; border: 1px solid #e8e6e0; border-radius: 12px; padding: 1.5rem; }}
      footer {{ margin-top: 3rem; padding-top: 1.25rem; border-top: 1px solid #e4e2dc;
                font-size: .9rem; color: #71717a; }}
      footer a {{ color: #4f46e5; }}
      a {{ color: #4f46e5; }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <header class="top">
        <img src="/favicon.png" alt="{app_name} icon" />
        <span class="name">{app_name}</span>
      </header>

      <section class="hero">
        <h1>{tagline}</h1>
        <p class="lede">{description}</p>
        <a class="cta" href="{workspace_path}">Open the workspace</a>
        <a class="cta secondary" href="#how-it-works">See how it works</a>
      </section>

      <h2 id="how-it-works">How it works</h2>
      <div class="steps">
        <div class="step">
          <span class="num">1</span>
          <h3>Bring in a finished video</h3>
          <p>Upload an already-edited MP4, or pick one from your workspace. {app_name} does not
             create or edit video; it starts from your final cut.</p>
        </div>
        <div class="step">
          <span class="num">2</span>
          <h3>Review before anything ships</h3>
          <p>Preview the video, write the caption, and work through a review checklist covering
             content rights and platform policy.</p>
        </div>
        <div class="step">
          <span class="num">3</span>
          <h3>Approve deliberately</h3>
          <p>A person has to approve each post. Nothing is queued for handoff until someone
             explicitly signs off on it.</p>
        </div>
        <div class="step">
          <span class="num">4</span>
          <h3>Hand off to TikTok drafts</h3>
          <p>Connect an authorized TikTok account and send the approved MP4 to that creator's
             TikTok drafts, where they finish and post it inside TikTok.</p>
        </div>
      </div>

      <h2>Why a review step</h2>
      <div class="panel">
        <p>Small teams lose track of which cut was approved, which account it belongs to, and what
           already shipped. {app_name} keeps that decision in one place: every post has a reviewer,
           an approval time, and a record of where it was sent.</p>
        <ul class="plain">
          <li><strong>Human approval required.</strong> No bulk publishing, no automated engagement,
              no scraping.</li>
          <li><strong>The creator stays in control.</strong> Content is only sent after the account
              owner authorizes the connection and approves the specific post.</li>
          <li><strong>Drafts, not direct posts.</strong> Video arrives in the creator's TikTok
              drafts/inbox so they complete the caption and publish from TikTok themselves.</li>
        </ul>
      </div>

      <h2>TikTok integration</h2>
      <div class="panel">
        <p>{app_name} uses TikTok Login Kit so a creator can connect their own account, and the
           TikTok Content Posting API to transfer one approved MP4 into that creator's drafts.</p>
        <ul class="plain">
          <li><strong>user.info.basic</strong> &mdash; shows which TikTok account is connected, so
              the video is never sent to the wrong profile.</li>
          <li><strong>video.upload</strong> &mdash; transfers a single approved MP4 to the creator's
              TikTok drafts after explicit approval.</li>
        </ul>
        <p>Connections can be disconnected at any time from the workspace.</p>
      </div>

      <footer>
        &copy; 2026 {app_name} &middot; Creator publishing workspace &middot;
        <a href="{terms_path}">Terms of Service</a> &middot;
        <a href="{privacy_path}">Privacy Policy</a> &middot;
        <a href="mailto:{contact}">{contact}</a>
      </footer>
    </div>
  </body>
</html>
"""

# The Streamlit workspace is served from this path; the landing page owns "/" so that reviewers and
# crawlers receive real HTML instead of Streamlit's JavaScript-only shell.
WORKSPACE_PATH = "/workspace"


def landing_page_html() -> str:
    """Server-rendered marketing/product homepage.

    TikTok rejected the site with "Website error, Website must be fully developed". The cause was
    that Streamlit renders entirely client-side, so a headless fetch of "/" returned 53 characters
    of visible text: "You need to enable JavaScript to run this app." This page describes the real
    product in plain HTML so the site is legible without executing JavaScript.
    """
    return _LANDING_TEMPLATE.format(
        app_name=html.escape(APP_NAME),
        tagline=html.escape(TAGLINE),
        description=html.escape(SHORT_DESCRIPTION),
        workspace_path=WORKSPACE_PATH,
        terms_path=TERMS_PATH,
        privacy_path=PRIVACY_PATH,
        contact=html.escape(CONTACT_EMAIL),
    )


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
