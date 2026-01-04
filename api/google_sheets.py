import os
import time
import logging
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache = {
    'accounts': None,
    'fetched_at': 0,
}

CACHE_TTL = int(os.environ.get('ACCOUNTS_CACHE_TTL', '120'))  # seconds

# Fallback accounts for testing/development
FALLBACK_ACCOUNTS = [
    '600000',  # Sandbox ShortCode
    '600001',
    '600002',
    'TEST001',
    'TEST002',
]


def _get_service():
    keyfile = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE')
    if not keyfile:
        raise RuntimeError('GOOGLE_SERVICE_ACCOUNT_FILE not set')
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)
    return build('sheets', 'v4', credentials=creds)


def get_accounts(spreadsheet_id: str = None) -> List[str]:
    """Return list of account identifiers from Google Sheets or fallback.

    If GOOGLE_SHEET_ID or spreadsheet_id is not provided, returns fallback accounts.
    Caches results for CACHE_TTL seconds.
    """
    if not spreadsheet_id:
        spreadsheet_id = os.environ.get('GOOGLE_SHEET_ID')

    # If no spreadsheet ID, return fallback accounts
    if not spreadsheet_id:
        logger.warning('No GOOGLE_SHEET_ID configured, using fallback accounts')
        return FALLBACK_ACCOUNTS

    now = time.time()
    if _cache['accounts'] is not None and now - _cache['fetched_at'] < CACHE_TTL:
        return _cache['accounts']

    try:
        service = _get_service()
        range_name = 'Accounts!A:A'
        resp = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = resp.get('values', [])
        accounts = [row[0].strip() for row in values if row]
        _cache['accounts'] = accounts
        _cache['fetched_at'] = now
        return accounts
    except Exception as e:
        logger.exception('Failed to fetch accounts from Google Sheets: %s', e)
        # Fallback to hardcoded accounts on error
        logger.warning('Falling back to hardcoded accounts')
        return FALLBACK_ACCOUNTS


def clear_cache():
    """Clear the accounts cache (useful for testing)."""
    _cache['accounts'] = None
    _cache['fetched_at'] = 0
