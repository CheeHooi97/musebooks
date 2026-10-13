"""Save explicitly collected product assets locally with source provenance."""
import argparse
import hashlib
import json
from pathlib import Path

import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--books', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    output = (root / args.output).resolve()
    if not output.is_relative_to(root):
        parser.error('Output must stay inside the repository')
    output.mkdir(parents=True, exist_ok=True)
    books = json.loads((root / args.books).read_text(encoding='utf-8'))['books']
    records = []
    for book in books:
        for asset in book.get('images', []):
            record = dict(asset, bookId=book['id'])
            try:
                with requests.get(asset['url'], timeout=20, stream=True) as response:
                    response.raise_for_status()
                    mime = response.headers.get('Content-Type', '').split(';')[0]
                    suffix = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp'}.get(mime)
                    if not suffix:
                        raise ValueError('Asset is not a supported image')
                    content = bytearray()
                    for chunk in response.iter_content(65536):
                        content.extend(chunk)
                        if len(content) > 10_000_000:
                            raise ValueError('Asset exceeds 10 MB')
                    digest = hashlib.sha256(content).hexdigest()
                    path = output / (digest + suffix)
                    path.write_bytes(content)
                    record.update(localPath=str(path.relative_to(root)), sha256=digest, byteSize=len(content), mimeType=mime, status='downloaded')
            except Exception as exc:
                record.update(status='unavailable', error=f'{type(exc).__name__}: {exc}')
            records.append(record)
            print(book['title'], asset['role'], record['status'], flush=True)
            (output / 'assets.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
