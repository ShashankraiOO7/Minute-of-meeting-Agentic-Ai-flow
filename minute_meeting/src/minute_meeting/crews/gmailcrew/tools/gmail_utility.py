# gmail_utility.py  (fixed authorize error)

from __future__ import annotations
import os, socket, base64, email.message
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth_httplib2 import AuthorizedHttp  
import httplib2
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

_original_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = _ipv4_getaddrinfo    # override once at import


# ────────────────────────────────────────────────────────────
# 1.  Config & paths
# ────────────────────────────────────────────────────────────
load_dotenv()

SCOPES: List[str] = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
]

ENV_PATH = os.getenv("GMAIL_CREDENTIALS")
if ENV_PATH and Path(ENV_PATH).expanduser().exists():
    CREDS_PATH = Path(ENV_PATH).expanduser().resolve()
else:
    local = Path(__file__).resolve().parent / "credentials.json"
    CREDS_PATH = local if local.exists() else Path("credentials.json").resolve()

TOKEN_PATH = CREDS_PATH.with_name("token.json")


# ────────────────────────────────────────────────────────────
# 2.  OAuth helper
# ────────────────────────────────────────────────────────────
def _build_service(creds: Credentials, timeout=90):
    # AuthorisedHttp gives us creds-aware httplib2 client
    http = AuthorizedHttp(creds, http=httplib2.Http(timeout=timeout))
    return build("gmail", "v1", http=http, cache_discovery=False)

def authenticate_gmail():
    creds: Credentials | None = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_PATH.exists():
                raise FileNotFoundError(
                    f"Gmail credentials.json not found at {CREDS_PATH}\n"
                    "Set GMAIL_CREDENTIALS env var or move the file."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

    return _build_service(creds, timeout=90)


# ────────────────────────────────────────────────────────────
# 3.  Message helper
# ────────────────────────────────────────────────────────────
def create_message(sender: str, to: str, subject: str, text: str) -> dict:
    msg = email.message.EmailMessage()
    msg["To"], msg["From"], msg["Subject"] = to, sender, subject
    msg.set_content(text)
    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": encoded}


# ────────────────────────────────────────────────────────────
# 4.  Draft / Send helpers with retry (3×, 5 s gap)
# ────────────────────────────────────────────────────────────
_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)

@_retry
def create_draft(service, user_id: str, message: dict) -> dict:
    return (
        service.users()
        .drafts()
        .create(userId=user_id, body={"message": message})
        .execute()
    )

@_retry
def send_message(service, user_id: str, message: dict) -> dict:
    return (
        service.users()
        .messages()
        .send(userId=user_id, body=message)
        .execute()
    )
