"""Export the reviewed import as a source-linked bibliography for each model."""
import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

PHYSICAL_MARKETPLACE_KINDS = {"marketplace", "marketplace_c2c", "auction", "flea_market"}


def export(manifest_path, publisher_path, output):
    records = json.loads(Path(manifest_path).read_text(encoding="utf-8-sig"))
    publishers = {row["url"]: row for row in json.loads(Path(publisher_path).read_text(encoding="utf-8-sig"))}
    editions = {}
    for record in records:
        edition, work = record["edition"], record["work"]
        if not edition.get("id"):
            continue
        row = editions.setdefault(edition["id"], {
            "editionId": edition["id"], "workId": work["id"], "models": work["featuredNames"].split("、"),
            "workTitle": work["originalTitle"], "publishedTitles": [], "format": edition["format"],
            "label": edition["editionLabel"], "variant": edition.get("editionVariant", ""), "language": "",
            "isbn": "", "publisher": "", "releaseDate": "", "pageCount": 0,
            "coverUrl": "", "coverObjectKey": "", "contentSummary": "", "seriesName": "", "sourceUrls": [],
            "activeMarketplaceListings": [], "soldMarketplaceListings": [],
            "physicalRetailOffers": [], "retailOffers": [],
        })
        for key in ("isbn", "publisher", "releaseDate", "pageCount", "coverUrl", "coverObjectKey", "contentSummary", "seriesName", "language"):
            if edition.get(key):
                row[key] = edition[key]
        source = edition["metadataSourceUrl"]
        if source not in row["sourceUrls"]:
            row["sourceUrls"].append(source)
        title = publishers.get(source, {}).get("title") or work["originalTitle"]
        items = record["batch"].get("items", [])
        if title and title not in row["publishedTitles"]:
            row["publishedTitles"].append(title)
        source_kind = (record.get("source", {}).get("kind") or "").lower()
        for item in items:
            item_format = item.get("format") or edition["format"]
            offer = {"sourceId": record["batch"]["sourceId"], "url": item["url"],
                "priceMinor": item.get("priceMinor", 0), "currency": item.get("currency", ""),
                "observedAt": item.get("observedAt", ""), "status": item.get("status", "unknown"),
                "format": item_format, "priceType": item.get("priceType", "")}
            target = None
            if item_format == "digital" and item.get("priceType") == "digital":
                target = row["retailOffers"]
            elif item_format == "physical" and source_kind == "bookstore":
                target = row["physicalRetailOffers"]
            elif item_format == "physical" and source_kind in PHYSICAL_MARKETPLACE_KINDS and item.get("status") == "active":
                target = row["activeMarketplaceListings"]
            elif item_format == "physical" and source_kind in PHYSICAL_MARKETPLACE_KINDS and item.get("status") == "completed":
                target = row["soldMarketplaceListings"]
            source_id = record["batch"]["sourceId"]
            if target is not None and not any(offer["sourceId"] == source_id and offer["url"] == item["url"] for offer in target):
                target.append(offer)
    rows = sorted(editions.values(), key=lambda row: (row["models"], row["workTitle"], row["format"], row["label"]))
    models = defaultdict(list)
    for row in rows:
        for model in row["models"]:
            models[model].append(row)
    def cell(value):
        return str(value or "—").replace("|", "\\|").replace("\n", " ")
    lines = ["# 台灣市場寫真書目：依模特兒／藝人整理", "", f"核對日期：{date.today().isoformat()}。以下是本次已核對並提交資料庫的書目；不是完整出版史。共同作品會列在每位成員名下，但資料庫只保留一個作品。", "",
        f"涵蓋 **{len(models)} 個模特兒／藝人署名、{len({row['workId'] for row in rows})} 個作品、{len(rows)} 個版次**。", "",
        "數位售價、實體零售價、實體市場刊登價和成交價分開列出；實體書店售價不會算成市場刊登或成交。空白欄位表示尚未核實。封面連結指向已驗證的 R2 圖片。", ""]
    for model, entries in sorted(models.items()):
        lines += [f"## {model}", "", "| 已核對出版名稱 | 格式／版次 | ISBN | 出版日期 | 頁數 | 封面 |", "| --- | --- | --- | --- | --- | --- |"]
        for row in entries:
            title = row["publishedTitles"][0] if row["publishedTitles"] else row["workTitle"]
            title = title.split('-城邦')[0]
            source = row["sourceUrls"][0]
            fmt = "實體" if row["format"] == "physical" else "數位"
            variant = {"with_video": "含影音", "without_video": "不含影片", "unspecified": "影音未確認"}.get(row["variant"], "") if row["format"] == "digital" else ""
            version = fmt + "／" + row["label"] + ("／" + variant if variant else "")
            cover = f"[R2]({row['coverUrl']})" if row["coverObjectKey"] else "待補"
            lines.append(f"| [{cell(title)}]({source}) | {cell(version)} | {cell(row['isbn'])} | {cell(row['releaseDate'][:10])} | {cell(row['pageCount'])} | {cover} |")
        lines.append("")
    lines += ["## 尚待補查", "", "- 部分年齡限制或驗證頁無法匿名讀取，未繞過驗證。", "- 以姓名查詢可能回傳大量無關書籍；重複無結果的查詢有收集上限，已核對書名另行查詢。", "- 董梓甯的部分實體自出版賣場已下架；《夢想の赤木晴梓》實體版本及《全給你》仍需可核對的出版／零售頁與封面。", "- 短今《今夏戀愛中》、鄭家純《十八歲的禮物》等舊版仍需補齊可核對的書籍資料與封面。", "- 本批沒有核實到可作成交價格的售出記錄；售出數量與目前售價不能替代最終成交價。", ""]
    target = Path(output)
    target.write_text("\n".join(lines), encoding="utf-8")
    target.with_suffix(".json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"models": len(models), "works": len({row["workId"] for row in rows}), "editions": len(rows),
        "physical": sum(row["format"] == "physical" for row in rows), "digital": sum(row["format"] == "digital" for row in rows)}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--publisher", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    export(args.manifest, args.publisher, args.output)
