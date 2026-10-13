"""Recover short-title covers from retained selected-product evidence only."""
import argparse
import json
from pathlib import Path
from kobo_cover_match import selected_cover_images

ROOT = Path(__file__).resolve().parent / 'japan-models'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    repairs = []
    for path in ROOT.glob('*/kobo-state.json'):
        state = json.loads(path.read_text(encoding='utf-8'))
        if state.get('status') not in ('public_search_exhausted', 'detail_failures'):
            continue
        changed = False
        for item in state.get('items', {}).values():
            if item.get('imageUrl'):
                continue
            cache_path = ROOT / 'shared-details/kobo' / (item['externalId'] + '.json')
            if not cache_path.exists():
                continue
            cache = json.loads(cache_path.read_text(encoding='utf-8'))
            images = selected_cover_images(cache['images'], item['title'])
            if not images:
                continue
            repairs.append(dict(modelId=path.parent.name, url=item['url'], title=item['title'],
                images=images, evidence=str(cache_path.relative_to(ROOT))))
            if args.apply:
                item.update(imageUrl=images[0], imageUrls=images)
                changed = True
        if changed:
            temporary = path.with_suffix('.new.json')
            temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(path)
    (ROOT / 'cover-repair-report.json').write_text(json.dumps(dict(applied=args.apply, repairs=repairs),
        ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(repairs)} completed-capture covers recovered; applied={args.apply}')


if __name__ == '__main__':
    main()
