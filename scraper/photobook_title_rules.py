"""Pure title rules shared by catalog and digital-store classification."""
import re
import unicodedata

STRONG_PHOTOBOOK_SIGNAL_RE = re.compile(
    r"(?:\bphoto\s*book\b|\bphotobook\b|\bphotography\s*book\b|"
    r"\bphoto(?:graphic)?\s+(?:essay|monograph|album)\b|"
    r"写真集|フォトブック|寫真集|寫真書|數位寫真|数字写真|數字寫真|攝影集|摄影集|攝影書|摄影书|照片集|"
    r"写真本|写真帖|寫真帖|写真フォトブック|写真画集|攝影畫冊|摄影画册|"
    r"攝影作品集|摄影作品集|影像集|影像作品集)",
    re.IGNORECASE,
)

def photobook_title_exclusion(title: str) -> str:
    title = unicodedata.normalize("NFKC", title)
    if re.search(r"リカちゃん人形|LICCA\s+IN\s+SOUTHERN\s+ISLAND", title, re.I):
        return "nonhuman_subject"
    if re.search(r"生写真.*ブロマイド.*セット.*ポストカード|写真集.*映画パンフレット", title):
        return "nonbook_product"
    if re.search(r"写真集系雑誌|グラビアマガジン.*コスプレ.*ポトレアーカイブス|月刊メルフレボンバー", title):
        return "magazine_only"
    if re.search(r"テレホンカード.*度数", title):
        return "nonbook_product"
    if re.search(r"表紙.*洋書\s*ELLE|NEO\s*GRAVURE\s*MAGAZINE", title, re.I):
        return "magazine_only"
    if re.search(r"17ans.*川上礼", title, re.I):
        return "subject_publication_age_unverified"
    if re.search(r"漫画アクション|ヤングジャンプ.*\d+号", title):
        return "magazine_or_supplement"
    if re.search(r"小泉今日子.*デラックス近代映画.*水着", title):
        return "subject_publication_age_unverified"
    if re.search(r"BRODY.*月号|旧雑誌|SIX\s*PAPER.*表紙", title, re.I):
        return "magazine_only"
    if re.search(r"AIポスター", title, re.I):
        return "synthetic_subject"
    if re.search(r"ROM写真集", title, re.I):
        return "disc_only"
    if re.search(r"^チバゆな\s*ブロマイド", title):
        return "nonbook_product"
    if re.search(r"スクールガール.*小林基行", title):
        return "artist_monograph"
    if re.search(r"感性のバケモノになりたい.*十文字美信", title):
        return "artist_monograph"
    if re.search(r"名作写真集ガイド", title):
        return "reference_book"
    if re.search(r"アクチュール.*表紙.*インタビュー", title):
        return "magazine_only"
    if re.search(r"畠田理恵.*RIE.*水着", title, re.I):
        return "subject_publication_age_unverified"
    if re.search(r"柏原芳恵.*17歳|鈴木杏.*小学校卒業", title):
        return "subject_publication_age_unverified"
    if re.search(r"雑誌付録DVD|写真集SE\s*DVD", title, re.I):
        return "disc_only"
    if re.search(r"^DVD\s*写真集|DVD写真集\[", title, re.I):
        return "disc_only"
    if re.search(r"\[中古[^\]]*DVD\]|写真集.*メイキングDVD.*枚セット", title, re.I):
        return "disc_only"
    if re.search(r"L判写真\s*\d+枚", title, re.I):
        return "nonbook_product"
    if "ボールマーカー" in title:
        return "nonbook_product"
    if re.search(r"田村りおん.*まぶしいあの夏の日", title):
        return "subject_publication_age_unverified"
    if re.search(r"石田未来.*sugar\s*time|sugar\s*time.*石田未来|浅川梨奈.*なないろ|なないろ.*浅川梨奈|新関亜希.*HEAT\s*UP|河合美果.*風がおしえて", title, re.I):
        return "subject_publication_age_unverified"
    if re.search(r"ミニ写真集付き.*漫画アクション", title):
        return "magazine_or_supplement"
    if re.search(r"アート\s*ポスター|\[(?:中古(?:\s*セル版)?|新品\s*未開封)\s*DVD\]|カレンダーブック|フォトCD|Photo\s*CD|額入り|舞台.*パンフレット|振袖カタログ", title, re.I):
        return "nonbook_product"
    if re.search(r"\d{4}年\s*\d{1,2}月(?:\d{1,2}日)?号|週刊現代|週刊プレイボーイ|TVガイド\s*Stage\s*Stars|EX大衆|UTB.*アップ|ヤングチャンピオン.*袋とじ|Cream\s*クリーム|映画ファン.*臨時増刊", title, re.I):
        return "magazine_only"
    if re.search(r"制コレ.*水着|石川佳奈.*kana|前田愛.*眠り姫|宮沢ゆうな.*Pretty\s*Peach|菅谷梨沙子.*梨想|かわいい同級生|石川花.*写真集|写真集.*石川花|新原里彩.*学校なう", title, re.I):
        return "subject_publication_age_unverified"
    if re.search(r"Moecco|モエッコ", title, re.I):
        return "junior_gravure"
    if re.search(r"学校なう.*水着|水着.*学校なう", title):
        return "junior_gravure"
    if re.search(r"宮脇咲良.*さくら.*水着|水谷果穂.*写真集3冊", title):
        return "subject_publication_age_unverified"
    if re.search(r"宝生舞.*17歳|外岡えりか.*ひまわり|山中知恵.*花鳥風月|咲坂あいり.*Colorful", title, re.I):
        return "subject_publication_age_unverified"
    if re.search(r"グラビアチャンピオン|月刊(?:ザ・)?テンメイ", title):
        return "magazine_only"
    if re.search(r"透けパイ.*青山裕企", title):
        return "artist_monograph"
    if re.search(r"写真集クオリティ|グラビアザテレビジョン|特別付録.*MINIブック", title, re.I):
        return "magazine_or_supplement"
    if re.search(r"ギュンター.?ブルム|G[uü]nter\s+Blum|村田\s*兼一写真集", title, re.I):
        return "artist_monograph"
    if re.search(r"染色体.*野川イサム|野川イサム.*染色体|快楽の館", title):
        return "artist_monograph"
    if re.search(r"(?:CD|BD|Blu[ -]?ray|ブルーレイ)\s*写真集|^アイドルDVD", title, re.I):
        return "disc_only"
    if re.search(r"DVD|Blu[ -]?ray|ブルーレイ", title, re.I) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(title):
        return "disc_only"
    if re.search(r"増刊|FRIDAY\s*GOLD", title, re.I) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(title):
        return "magazine_only"
    if re.search(r"\bJK\b|女子高生|制服なう|エンジェルプロダクション|エンプロ|お菓子系|大倉梓|折山みゆ", title, re.I):
        return "junior_gravure"
    if re.search(r"AI[\s・_-]*(?:アート|美女|生成|グラビア)|生成AI|AI-generated", title, re.I):
        return "synthetic_subject"
    if re.search(r"写真データ|画像データ|ダウンロード販売", title):
        return "download_resale"
    if re.search(r"(?:ジュニア|Jr\.).*(?:グラビア|水着)|(?:グラビア|水着).*(?:ジュニア|Jr\.)", title, re.I):
        return "junior_gravure"
    if re.search(r"Chu[→\s-]*Boh|チューボー|ホイップ", title, re.I):
        return "junior_gravure"
    if re.search(r"\d{4}年\d{1,2}月号|特集号|(?:熱烈投稿|雑誌)", title) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(title):
        return "magazine_only"
    if re.search(r"插畫|插画|イラスト|illustrat(?:ed|ion)", title, re.I):
        return "illustrated_book"
    if re.search(r"月曆|月历|桌曆|桌历|日曆|日历|掛曆|挂历|年曆|年历|カレンダー|\bcalendar\b", title, re.I) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(title):
        return "calendar_only"
    return ""
