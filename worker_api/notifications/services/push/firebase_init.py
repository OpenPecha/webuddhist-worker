import os

import firebase_admin

from worker_api.config import get


def initialize_firebase() -> firebase_admin.App:
    cred_path = get("GOOGLE_APPLICATION_CREDENTIALS").strip()
    if cred_path:
        os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", cred_path)
    try:
        return firebase_admin.get_app()
    except ValueError:
        return firebase_admin.initialize_app()
