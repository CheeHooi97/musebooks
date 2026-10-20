"""Persist marketplace access blocks and enforce a quiet cooldown."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from capture_checkpoint import save_json


ROOT = Path(__file__).resolve().parent.parent
SOURCE_BLOCKS_PATH = ROOT / 'scraper/japan-models/physical-source-blocks.json'
DEFAULT_COOLDOWN = timedelta(hours=24)


def load_source_blocks(path=SOURCE_BLOCKS_PATH):
    path = Path(path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_source_blocks(blocks, path=SOURCE_BLOCKS_PATH):
    save_json(path, blocks)


def block_is_active(block, now=None):
    if not isinstance(block, dict) or block.get('status') != 'source_blocked':
        return False
    retry_after = block.get('retryAfter')
    if not retry_after:
        return True
    try:
        retry_at = datetime.fromisoformat(str(retry_after).replace('Z', '+00:00'))
    except ValueError:
        return True
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc) < retry_at.astimezone(timezone.utc)


def source_is_blocked(source_id, path=SOURCE_BLOCKS_PATH, now=None):
    return block_is_active(load_source_blocks(path).get(source_id), now)


def record_source_block(source_id, reason, *, details=None, path=SOURCE_BLOCKS_PATH,
        now=None, cooldown=DEFAULT_COOLDOWN):
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    record = dict(status='source_blocked', reason=str(reason),
        blockedAt=current.isoformat().replace('+00:00', 'Z'),
        retryAfter=(current + cooldown).isoformat().replace('+00:00', 'Z'))
    if details:
        record.update(details)
    blocks = load_source_blocks(path)
    blocks[source_id] = record
    save_source_blocks(blocks, path)
    return record
