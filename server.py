"""Render entrypoint: serve TikTok verification and proxy the Streamlit app."""

from __future__ import annotations

import asyncio
import os
import signal
import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import uvicorn
import websockets
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, StreamingResponse

from tiktok_integration import router as tiktok_router

ROOT = Path(__file__).resolve().parent
VERIFICATION_FILENAME = "tiktokn4FgVVIg3PMCSpkEskVM1xXLvescL2S3.txt"
VERIFICATION_TEXT = (ROOT / VERIFICATION_FILENAME).read_text(encoding="utf-8").strip()
STREAMLIT_HOST = "127.0.0.1"
STREAMLIT_PORT = 8502
STREAMLIT_HTTP = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"
STREAMLIT_WS = f"ws://{STREAMLIT_HOST}:{STREAMLIT_PORT}"


@asynccontextmanager
async def lifespan(_: FastAPI):
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.address",
        STREAMLIT_HOST,
        "--server.port",
        str(STREAMLIT_PORT),
        "--server.headless",
        "true",
        cwd=ROOT,
    )
    try:
        for attempt in range(100):
            try:
                async with httpx.AsyncClient(timeout=1.0) as client:
                    response = await client.get(f"{STREAMLIT_HTTP}/_stcore/health")
                if response.status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.1)
        else:
            raise RuntimeError("Streamlit did not become ready")
        yield
    finally:
        if process.returncode is None:
            process.send_signal(signal.SIGTERM)
            try:
                await asyncio.wait_for(process.wait(), timeout=10)
            except TimeoutError:
                process.kill()
                await process.wait()


app = FastAPI(lifespan=lifespan)
app.include_router(tiktok_router)


@app.get(f"/{VERIFICATION_FILENAME}", response_class=PlainTextResponse)
async def tiktok_verification():
    return PlainTextResponse(VERIFICATION_TEXT, media_type="text/plain")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy_http(request: Request, path: str):
    target = f"{STREAMLIT_HTTP}/{path}"
    headers = dict(request.headers)
    headers.pop("host", None)
    headers["x-em-posting-origin"] = str(request.base_url).rstrip("/")
    body = await request.body()
    client = httpx.AsyncClient(timeout=None, follow_redirects=False)
    upstream = await client.send(
        client.build_request(request.method, target, params=request.query_params, headers=headers, content=body),
        stream=True,
    )
    response_headers = dict(upstream.headers)
    for header in ("content-length", "transfer-encoding", "connection", "content-encoding"):
        response_headers.pop(header, None)

    async def body_stream():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(body_stream(), status_code=upstream.status_code, headers=response_headers)


@app.websocket("/{path:path}")
async def proxy_websocket(websocket: WebSocket, path: str):
    requested_protocols = websocket.headers.get("sec-websocket-protocol")
    subprotocols = requested_protocols.split(", ") if requested_protocols else None
    selected_protocol = subprotocols[0] if subprotocols else None
    await websocket.accept(subprotocol=selected_protocol)
    target = f"{STREAMLIT_WS}/{path}"
    if websocket.url.query:
        target += f"?{websocket.url.query}"
    headers = [(key, value) for key, value in websocket.headers.items() if key.lower() not in {
        "host", "origin", "connection", "upgrade", "sec-websocket-key", "sec-websocket-version", "sec-websocket-extensions", "sec-websocket-protocol"
    }]
    forwarded_proto = websocket.headers.get("x-forwarded-proto", "https")
    forwarded_host = websocket.headers.get("x-forwarded-host") or websocket.headers.get("host", "")
    headers.append(("x-em-posting-origin", f"{forwarded_proto}://{forwarded_host}"))
    try:
        async with websockets.connect(
            target,
            additional_headers=headers,
            origin=STREAMLIT_HTTP,
            subprotocols=subprotocols,
        ) as upstream:
            async def client_to_upstream():
                while True:
                    message = await websocket.receive()
                    if message.get("bytes") is not None:
                        await upstream.send(message["bytes"])
                    elif message.get("text") is not None:
                        await upstream.send(message["text"])
                    else:
                        break

            async def upstream_to_client():
                async for message in upstream:
                    if isinstance(message, bytes):
                        await websocket.send_bytes(message)
                    else:
                        await websocket.send_text(message)

            tasks = [asyncio.create_task(client_to_upstream()), asyncio.create_task(upstream_to_client())]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except (WebSocketDisconnect, websockets.ConnectionClosed):
        pass
    except Exception:
        traceback.print_exc()
        await websocket.close(code=1011)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
