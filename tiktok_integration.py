"""Real TikTok Sandbox Login Kit and draft-upload integration."""

from __future__ import annotations

import hashlib
import html
import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Cookie, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

TIKTOK_AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_USER_URL = "https://open.tiktokapis.com/v2/user/info/"
TIKTOK_UPLOAD_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
TIKTOK_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
# Externally-facing origin used to build the OAuth redirect URI. In production this MUST be an
# owned custom domain that does not contain "tiktok"; set EM_POSTING_PUBLIC_URL to it and register
# the same value's /auth/tiktok/callback/ path as the Login Kit Redirect URI in the developer
# portal. The Render URL below is only a documented Sandbox/local verification fallback.
PUBLIC_URL_FALLBACK = "https://posting-app-gvtf.onrender.com"
CALLBACK_PATH = "/auth/tiktok/callback/"
SCOPES = "user.info.basic,video.upload"
SESSION_COOKIE = "em_tiktok_session"
OAUTH_COOKIE = "em_tiktok_oauth"
MAX_VIDEO_BYTES = 50 * 1024 * 1024
SESSION_STORE = Path(os.getenv("EM_POSTING_SESSION_STORE", "/tmp/em-posting-tiktok-sessions.json"))


@dataclass
class TikTokSession:
    access_token: str
    refresh_token: str
    open_id: str
    scopes: str
    profile: dict[str, Any]


router = APIRouter()


def _load_sessions() -> dict[str, TikTokSession]:
    if not SESSION_STORE.exists():
        return {}
    try:
        import json

        raw = json.loads(SESSION_STORE.read_text(encoding="utf-8"))
        return {key: TikTokSession(**value) for key, value in raw.items()}
    except (OSError, ValueError, TypeError):
        return {}


_sessions: dict[str, TikTokSession] = _load_sessions()


def _save_sessions() -> None:
    import json

    SESSION_STORE.parent.mkdir(parents=True, exist_ok=True)
    payload = {key: session.__dict__ for key, session in _sessions.items()}
    temporary = SESSION_STORE.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload), encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(SESSION_STORE)


def _cookie_options() -> dict[str, Any]:
    return {
        "secure": os.getenv("EM_POSTING_COOKIE_SECURE", "true").lower() != "false",
        "httponly": True,
        "samesite": "lax",
        "path": "/",
    }


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise HTTPException(status_code=503, detail=f"TikTok integration is not configured: {name} is missing")
    return value


def public_base_url() -> str:
    """Externally-facing origin. Prefers EM_POSTING_PUBLIC_URL (the owned production domain);
    falls back to the documented Render URL for Sandbox/local verification."""
    configured = os.getenv("EM_POSTING_PUBLIC_URL", "").strip().rstrip("/")
    return configured or PUBLIC_URL_FALLBACK


def redirect_uri() -> str:
    """OAuth callback URI. Must exactly match the Login Kit Redirect URI registered in the portal,
    so it is derived from the configured public origin rather than a request header."""
    return f"{public_base_url()}{CALLBACK_PATH}"


def _client_key() -> str:
    return _env("SANDBOX_TIKTOK_CLIENT_KEY")


def _client_secret() -> str:
    return _env("SANDBOX_TIKTOK_CLIENT_SECRET")


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(_env("SANDBOX_TIKTOK_SESSION_SECRET"), salt="em-posting-tiktok")


def _session_id(cookie: str | None) -> str:
    if not cookie:
        raise HTTPException(status_code=401, detail="Connect a TikTok account first")
    try:
        session_id = _serializer().loads(cookie, max_age=60 * 60 * 24)
    except (BadSignature, SignatureExpired) as exc:
        raise HTTPException(status_code=401, detail="TikTok session expired; connect again") from exc
    if session_id not in _sessions:
        raise HTTPException(status_code=401, detail="TikTok session is no longer active; connect again")
    return session_id


def _error_detail(payload: dict[str, Any], fallback: str) -> str:
    error = payload.get("error")
    if isinstance(error, dict):
        return error.get("message") or error.get("code") or fallback
    return payload.get("error_description") or payload.get("message") or fallback


def _popup_close_html(*, connected: bool, error: str | None = None) -> str:
    """Tiny page rendered inside the OAuth popup window, never the main workspace tab.

    Posts the outcome to window.opener (same-origin, so this is safe) and closes itself. The
    opener is responsible for re-checking /api/tiktok/session and updating its own UI; this page
    never redirects anywhere so the workspace tab's Streamlit session is never touched.
    """
    safe_error = html.escape(error or "", quote=True)
    status_text = "TikTok connected. You can close this window." if connected else "TikTok connection failed."
    message = {"source": "em-posting-tiktok-oauth", "connected": connected}
    if error:
        message["error"] = safe_error
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>EM Posting · TikTok</title>
<style>
  body {{ font-family: system-ui, sans-serif; background:#f6f5f1; color:#1a1a1f;
          display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }}
  .box {{ text-align:center; padding:1.5rem 2rem; }}
  p {{ color:#71717a; }}
</style></head>
<body>
  <div class="box">
    <h3>{status_text}</h3>
    {f'<p>{safe_error}</p>' if error else ''}
  </div>
  <script>
    (function () {{
      var message = {json.dumps(message)};
      if (window.opener) {{
        try {{ window.opener.postMessage(message, window.location.origin); }} catch (e) {{}}
      }}
      setTimeout(function () {{ window.close(); }}, {800 if connected else 2500});
    }})();
  </script>
</body></html>"""


@router.get("/auth/tiktok/login")
async def login_with_tiktok() -> RedirectResponse:
    state = secrets.token_urlsafe(32)
    signed_state = _serializer().dumps(state)
    query = urlencode(
        {
            "client_key": _client_key(),
            "scope": SCOPES,
            "response_type": "code",
            "redirect_uri": redirect_uri(),
            "state": state,
            "disable_auto_auth": "1",
        }
    )
    response = RedirectResponse(f"{TIKTOK_AUTHORIZE_URL}?{query}", status_code=302)
    response.set_cookie(
        OAUTH_COOKIE,
        signed_state,
        max_age=600,
        **_cookie_options(),
    )
    return response


@router.get("/auth/tiktok/callback/", response_model=None)
async def tiktok_callback(
    request: Request,
    em_tiktok_oauth: str | None = Cookie(default=None),
) -> HTMLResponse | RedirectResponse:
    error = request.query_params.get("error")
    if error:
        detail = request.query_params.get("error_description", error)
        return HTMLResponse(_popup_close_html(connected=False, error=detail))

    code = request.query_params.get("code")
    returned_state = request.query_params.get("state")
    if not code or not returned_state or not em_tiktok_oauth:
        raise HTTPException(status_code=400, detail="Incomplete TikTok authorization response")
    try:
        expected_state = _serializer().loads(em_tiktok_oauth, max_age=600)
    except (BadSignature, SignatureExpired) as exc:
        raise HTTPException(status_code=400, detail="TikTok authorization state expired") from exc
    if not secrets.compare_digest(returned_state, expected_state):
        raise HTTPException(status_code=400, detail="TikTok authorization state mismatch")

    async with httpx.AsyncClient(timeout=30) as client:
        token_response = await client.post(
            TIKTOK_TOKEN_URL,
            data={
                "client_key": _client_key(),
                "client_secret": _client_secret(),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri(),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_payload = token_response.json()
        if token_response.is_error or "access_token" not in token_payload:
            raise HTTPException(status_code=502, detail=_error_detail(token_payload, "TikTok token exchange failed"))

        profile_response = await client.get(
            TIKTOK_USER_URL,
            params={"fields": "open_id,avatar_url,display_name"},
            headers={"Authorization": f"Bearer {token_payload['access_token']}"},
        )
        profile_payload = profile_response.json()
        if profile_response.is_error or profile_payload.get("error", {}).get("code") not in (None, "ok"):
            raise HTTPException(status_code=502, detail=_error_detail(profile_payload, "TikTok profile lookup failed"))

    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = TikTokSession(
        access_token=token_payload["access_token"],
        refresh_token=token_payload.get("refresh_token", ""),
        open_id=token_payload.get("open_id", ""),
        scopes=token_payload.get("scope", ""),
        profile=profile_payload.get("data", {}).get("user", {}),
    )
    _save_sessions()
    # This callback is opened in a popup window (see /auth/tiktok/login), not the main workspace
    # tab. Redirecting the popup to "/" would load a brand-new Streamlit session there and leave
    # the real workspace tab none the wiser. Instead: set the session cookie (shared across tabs,
    # since it's not tab-scoped), tell the opener via postMessage that TikTok is connected, and
    # let the popup close itself. The opener polls /api/tiktok/session on that signal.
    html = _popup_close_html(connected=True)
    response = HTMLResponse(html)
    response.delete_cookie(OAUTH_COOKIE, path="/")
    response.set_cookie(
        SESSION_COOKIE,
        _serializer().dumps(session_id),
        max_age=60 * 60 * 24,
        **_cookie_options(),
    )
    return response


@router.get("/api/tiktok/session")
async def session_status(em_tiktok_session: str | None = Cookie(default=None)) -> JSONResponse:
    try:
        session = _sessions[_session_id(em_tiktok_session)]
    except HTTPException as exc:
        return JSONResponse({"connected": False, "detail": exc.detail}, status_code=exc.status_code)
    return JSONResponse(
        {
            "connected": True,
            "profile": session.profile,
            "scopes": [scope for scope in session.scopes.split(",") if scope],
        }
    )


@router.post("/api/tiktok/disconnect")
async def disconnect(em_tiktok_session: str | None = Cookie(default=None)) -> JSONResponse:
    try:
        session_id = _session_id(em_tiktok_session)
        _sessions.pop(session_id, None)
        _save_sessions()
    except HTTPException:
        pass
    response = JSONResponse({"connected": False})
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@router.post("/api/tiktok/upload")
async def upload_draft(
    video: UploadFile = File(...),
    em_tiktok_session: str | None = Cookie(default=None),
) -> JSONResponse:
    session = _sessions[_session_id(em_tiktok_session)]
    if "video.upload" not in session.scopes.split(","):
        raise HTTPException(status_code=403, detail="The connected account did not grant video.upload")
    if video.content_type not in {"video/mp4", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Upload a valid MP4 video")

    video_data = await video.read(MAX_VIDEO_BYTES + 1)
    if not video_data:
        raise HTTPException(status_code=400, detail="The selected video is empty")
    if len(video_data) > MAX_VIDEO_BYTES:
        raise HTTPException(status_code=413, detail="The current pilot accepts videos up to 50 MB")

    size = len(video_data)
    async with httpx.AsyncClient(timeout=120) as client:
        init_response = await client.post(
            TIKTOK_UPLOAD_INIT_URL,
            json={
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": size,
                    "chunk_size": size,
                    "total_chunk_count": 1,
                }
            },
            headers={
                "Authorization": f"Bearer {session.access_token}",
                "Content-Type": "application/json; charset=UTF-8",
            },
        )
        init_payload = init_response.json()
        if init_response.is_error or init_payload.get("error", {}).get("code") != "ok":
            raise HTTPException(status_code=502, detail=_error_detail(init_payload, "TikTok upload initialization failed"))

        upload_url = init_payload.get("data", {}).get("upload_url")
        publish_id = init_payload.get("data", {}).get("publish_id")
        if not upload_url or not publish_id:
            raise HTTPException(status_code=502, detail="TikTok did not return an upload URL and publish ID")

        upload_response = await client.put(
            upload_url,
            content=video_data,
            headers={
                "Content-Type": "video/mp4",
                "Content-Length": str(size),
                "Content-Range": f"bytes 0-{size - 1}/{size}",
            },
        )
        if upload_response.status_code not in {200, 201, 204, 206}:
            raise HTTPException(status_code=502, detail=f"TikTok file transfer failed with HTTP {upload_response.status_code}")

    return JSONResponse(
        {
            "ok": True,
            "publish_id": publish_id,
            "filename": video.filename,
            "size_bytes": size,
            "fingerprint": hashlib.sha256(video_data).hexdigest()[:16],
            "destination": "TikTok draft/inbox",
            "next_step": "Open the TikTok inbox notification to finish editing and post.",
        }
    )


@router.get("/api/tiktok/status/{publish_id}")
async def upload_status(
    publish_id: str,
    em_tiktok_session: str | None = Cookie(default=None),
) -> JSONResponse:
    session = _sessions[_session_id(em_tiktok_session)]
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            TIKTOK_STATUS_URL,
            json={"publish_id": publish_id},
            headers={
                "Authorization": f"Bearer {session.access_token}",
                "Content-Type": "application/json; charset=UTF-8",
            },
        )
    payload = response.json()
    if response.is_error or payload.get("error", {}).get("code") != "ok":
        raise HTTPException(status_code=502, detail=_error_detail(payload, "TikTok status lookup failed"))
    return JSONResponse(payload)
