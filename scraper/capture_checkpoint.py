"""Replace capture checkpoints atomically, tolerating brief Windows file locks."""
import json
import os
import tempfile
import time
from pathlib import Path


def save_json(path, value):
    path = Path(path)
    serialized = json.dumps(value, ensure_ascii=False, indent=2)
    temporary = None
    try:
        # Distinct staging files cannot overwrite another writer's pending data.
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                dir=path.parent, prefix=path.name + '.', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        for attempt in range(5):
            try:
                os.replace(temporary, path)
                return
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.2 * (attempt + 1))
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
