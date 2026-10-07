import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from prepare_catalog_import import prepare, canonical_title, work_identity
from r2_covers import download_cover

class CatalogImportTests(unittest.TestCase):
 def test_masked_cover_is_rejected_even_when_cached(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   image='https://taiwan-image.bookwalker.com.tw/product/236738/236738_1_mask.jpg'
   row={'model':'羽庭','title':'惑之庭','body':'羽庭','url':'https://www.bookwalker.com.tw/product/236738','imageUrl':image,'format':'digital'}
   pub.write_text(json.dumps([row]),encoding='utf-8');live.write_text('[]',encoding='utf-8')
   out.with_suffix('.covers.json').write_text(json.dumps({image:{'url':'https://example.com/cached.jpg','originalUrl':image,'key':'cached'}}),encoding='utf-8')
   prepare(live,pub,out)
   record=json.loads(out.read_text(encoding='utf-8'))[0]
   self.assertEqual(record['edition']['coverUrl'],'')
   self.assertEqual(record['work']['coverUrl'],'')
   with self.assertRaises(ValueError):download_cover(image)

 def test_group_photobook_is_kept_when_source_names_each_model_separately(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   model='陳白白、葉蛋蛋、波奇、莉亞'
   row={'model':model,'title':'MotoH車漾女神誌 - 女神降臨寫真集',
        'body':'陳白白（阿白）、葉蛋蛋、波奇、Liya莉亞。四位車模共同拍攝。',
        'url':'https://play.google.com/store/books/details?id=m4cgEQAAQBAJ&hl=zh_TW&gl=TW',
        'imageUrl':'https://example.com/motoh.jpg','format':'digital','pageCount':160,
        'releaseDate':'2024-04-01','releasePrecision':'month','editionLabel':'Google Play ebook',
        'editionVariant':'unspecified','publisher':'子席國際股份有限公司',
        'photographer':'測試攝影師',
        'contentSummary':'160頁數位寫真；由四位車模共同拍攝。'}
   pub.write_text(json.dumps([row],ensure_ascii=False),encoding='utf-8');live.write_text('[]',encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(len(result),1)
   self.assertEqual(result[0]['work']['featuredNames'],model)
   self.assertEqual(result[0]['work']['photographer'],'測試攝影師')
   self.assertEqual(result[0]['edition']['format'],'digital')

 def test_publisher_ebook_stays_digital_without_marketplace_prices(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   pub.write_text(json.dumps([{'model':'波波蓁','title':'蓁・時：波波蓁電子寫真','body':'波波蓁 出版日期：2022-05-20','url':'https://redboy.com.tw/product/redboy0049','imageUrl':'https://example.com/cover.jpg','format':'digital','language':'ja'}]),encoding='utf-8')
   live.write_text('[]',encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(result[0]['edition']['format'],'digital')
   self.assertEqual(result[0]['edition']['language'],'ja')
   self.assertEqual(result[0]['edition']['editionVariant'],'unspecified')
   self.assertIn('數位',result[0]['edition']['contentSummary'])
   self.assertEqual(result[0]['batch'],{})
 def test_matching_ebook_isbn_merges_offer_without_merging_print_edition(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   rows=[
    {'model':'吳俊','title':'Your Man：吳俊junwu185寫真書','body':'ISBN：9789865245689 出版社：台灣角川 出版日期：2021-05-26 160頁','url':'https://www.kadokawa.com.tw/zh-hant/products/9789865245689','imageUrl':'https://example.com/print.jpg','format':'physical','editionLabel':'標準版','editionVariant':'standard'},
    {'model':'吳俊','title':'Your Man：吳俊junwu185寫真書（數位特別版）','body':'EISBN：9789865245801 出版社：台灣角川 出版日期：2021-06 160頁','url':'https://play.google.com/store/books/details?id=LdQ3EAAAQBAJ','imageUrl':'https://example.com/ebook.jpg','format':'digital','editionLabel':'數位特別版','editionVariant':'unspecified'},
   ]
   item={'title':'Your Man：吳俊junwu185寫真書（數位特別版）','format':'digital','status':'active','priceType':'digital','digitalAccess':'authorized_store','currency':'TWD','priceMinor':28500,'isbn':'9789865245801','externalId':'LdQ3EAAAQBAJ','url':'https://play.google.com/store/books/details?id=LdQ3EAAAQBAJ','imageUrl':'https://example.com/ebook.jpg'}
   request={'format':'digital','source':{'kind':'digital_store','allowedHosts':['play.google.com']}}
   pub.write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
   live.write_text(json.dumps([{'model':'吳俊','request':request,'batch':{'sourceId':'google-play-books-tw','items':[item]}}],ensure_ascii=False),encoding='utf-8')
   prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(len({r['edition']['id'] for r in result}),2)
   self.assertEqual({r['edition']['format'] for r in result},{'physical','digital'})
   digital=[r for r in result if r['edition']['format']=='digital']
   self.assertEqual(len(digital),2)
   self.assertEqual(len({r['edition']['id'] for r in digital}),1)
   self.assertEqual(sum(bool(r['batch'].get('items')) for r in digital),1)
   self.assertTrue(all(r['edition']['isbn']=='9789865245801' for r in digital))
 def test_reviewed_cover_editions_share_work_but_remain_separate(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   rows=[]
   for number,label in enumerate(('透明夢境款書衣','藍調節奏款書衣')):
    rows.append({'model':'陳紫渝','title':f'初年：陳紫渝寫真({label})','body':'陳紫渝 ISBN：9786263741232 144頁','url':f'https://www.kingstone.com.tw/basic/{number}/','imageUrl':f'https://example.com/{number}.jpg','editionLabel':label,'editionVariant':'alternate_cover','contentSummary':'寫真書1本；版次封面不同。'})
   pub.write_text(json.dumps(rows),encoding='utf-8');live.write_text('[]',encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(len({r['work']['id'] for r in result}),1)
   self.assertEqual(len({r['edition']['id'] for r in result}),2)
   self.assertEqual({r['edition']['editionVariant'] for r in result},{'alternate_cover'})
   self.assertTrue(all(r['edition']['contentSummary']=='寫真書1本；版次封面不同。' for r in result))
 def test_shared_photobook_cover_orders_resolve_to_same_work(self):
  self.assertEqual(canonical_title('林孟潔','bestie閨蜜 孟潔×菲菲 數位寫真（含影音）'),canonical_title('李恩菲','bestie閨蜜 菲菲×孟潔 數位寫真（含影音）'))
  self.assertEqual(canonical_title('巫苡萱','《苡見鍾情》巫苡萱寫真書'),canonical_title('巫苡萱','苡見鍾情 巫苡萱數位寫真（含影音）'))
  self.assertEqual(canonical_title('阿部瑪利亞','半分はんぶん：阿部瑪利亞寫真(電子書)'),canonical_title('阿部瑪利亞','半分 はんぶん：阿部瑪利亞寫真【收藏卡版】'))
  self.assertEqual(canonical_title('寶兒','Babe Fantasy‧寶兒寫真書(電子書)'),canonical_title('寶兒','Babe Fantasy‧寶兒寫真書【隨書附贈寫真海報（四款隨機投入一款）】'))
  self.assertEqual(canonical_title('妮可','想見妮‧Nicole妮可寫真書(電子書)'),canonical_title('妮可','想見妮‧Nicole妮可寫真書【附海報】'))
  self.assertEqual(work_identity('妮可','想見妮‧Nicole妮可寫真書'),'work-tw-e23888df7c68a3c7d3bc18ea')
  self.assertEqual(canonical_title('邊荷律','《荷止微甜》邊荷律影像紀實'),canonical_title('邊荷律','【精裝典藏版】《荷止微甜》邊荷律影像紀實'))
  self.assertEqual(canonical_title('李雅英','沿著海，遇見你：英為你心動 李雅英1st台灣感性紙上電影系列'),canonical_title('李雅英','沿著海，遇見你－英為你心動：李雅英1st台灣感性紙上電影系列 數位版(電子書)'))
  self.assertEqual(canonical_title('李珠珢','FIGHT FOR ALL 李珠珢的主場日記'),canonical_title('李珠珢','FIGHT FOR ALL 李珠珢的主場日記【精裝典藏版】'))
  physical='Your Man：吳俊junwu185寫真書'
  ebook='Your Man：吳俊junwu185寫真書（數位特別版）'
  self.assertEqual(canonical_title('吳俊',physical),canonical_title('吳俊',ebook))
  self.assertEqual(work_identity('吳俊',physical),work_identity('吳俊',ebook))
 def test_recent_cheerleader_books_keep_physical_and_digital_editions_separate(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   rows=[
    {'model':'邊荷律','title':'《荷止微甜》邊荷律影像紀實','body':'ISBN：9786264550413 出版社：尖端 出版日期：2026/05/20 裝訂／頁數：平裝／176頁 規格：25.6cm*18cm*1.3cm','url':'https://www.sanmin.com.tw/product/index/015514569','imageUrl':'https://example.com/byun-paper.jpg','format':'physical','editionLabel':'標準版','editionVariant':'standard','contentSummary':'176頁平裝；首刷附贈2張燙金寫真卡，8款隨機。'},
    {'model':'邊荷律','title':'《荷止微甜》邊荷律影像紀實精裝典藏版','body':'條碼：4717702300906 書號：3F000064 作者：邊荷律 攝影師：李彥勳 出版社：尖端 上市日：2026/05/20','url':'https://www.spp.com.tw/SalePage/Index/11579526','imageUrl':'https://example.com/byun-collector.jpg','format':'physical','editionLabel':'精裝典藏版','editionVariant':'collector','contentSummary':'精裝書1本、典藏書盒、抱枕套、底片膠卷鑰匙圈及4張隨機燙金寫真卡。'},
    {'model':'李雅英','title':'沿著海，遇見你：英為你心動 李雅英1st台灣感性紙上電影系列','body':'ISBN：9786264349130 出版社：尖端 出版日：2026/03/20 裝訂／頁數：平裝／176頁 規格：25.6cm*18cm*1.3cm','url':'https://www.sanmin.com.tw/product/index/015267268','imageUrl':'https://example.com/lee-paper.jpg','format':'physical','editionLabel':'標準版','editionVariant':'standard','contentSummary':'176頁平裝；台灣山海與生活場景寫真，首刷附燙金寫真卡系列。'},
    {'model':'李雅英','title':'沿著海，遇見你：英為你心動 李雅英1st台灣感性紙上電影系列精裝典藏版','body':'條碼：4717702300647 書號：3F000059 作者：李雅英 攝影師：李彥勳 出版社：尖端 上市日：2026/03/20','url':'https://www.spp.com.tw/SalePage/Index/11508984','imageUrl':'https://example.com/lee-collector.jpg','format':'physical','editionLabel':'精裝典藏版','editionVariant':'collector','contentSummary':'精裝書1本與典藏書盒、附錄收藏盒；160×50cm抱枕套、不含枕心；11×6.8cm卡套及寫真卡。'},
    {'model':'李雅英','title':'沿著海，遇見你－英為你心動：李雅英1st台灣感性紙上電影系列 數位版(電子書)','body':'EISBN：9786264551892 出版社：尖端 出版日：2026/04/24 裝訂：電子書 檔案格式：EPUB版式 全新272張美照 附側拍花絮影音','url':'https://www.sanmin.com.tw/product/index/015487069','imageUrl':'https://example.com/lee-digital.png','format':'digital','contentSummary':'EPUB fixed-layout edition with 272 photos not included in print and behind-the-scenes footage; digital-only content.'},
    {'model':'李珠珢','title':'FIGHT FOR ALL 李珠珢的主場日記','body':'ISBN：9786264342247 出版社：尖端 出版日：2025/11/04 裝訂／頁數：平裝／176頁 規格：25.6cm*18cm*1.3cm','url':'https://www.sanmin.com.tw/product/index/014740702','imageUrl':'https://example.com/jueun-paper.jpg','format':'physical','editionLabel':'標準版','editionVariant':'standard','contentSummary':'176頁平裝；新莊棒球場影像紀實，首刷隨書附2張不同通路款式寫真卡。'},
    {'model':'李珠珢','title':'FIGHT FOR ALL 李珠珢的主場日記精裝典藏版','body':'ISBN：9786264342254 條碼：4717702299392 出版社：尖端 作者：李珠珢 攝影師：藍陳福堂 出版日：2025/09/02 裝訂／頁數：精裝／176頁 規格：28cm','url':'https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1752563403.pdf','imageUrl':'https://example.com/jueun-collector.jpg','format':'physical','editionLabel':'精裝典藏版','editionVariant':'collector','contentSummary':'176頁精裝書、附錄收藏盒及典藏書盒；抱枕套、流砂造型書籤及4張雷射燙金寫真卡。'},
   ]
   pub.write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8');live.write_text('[]',encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(len(result),7)
   for model in ('邊荷律','李雅英','李珠珢'):
    group=[row for row in result if row['work']['featuredNames']==model]
    self.assertEqual(len({row['work']['id'] for row in group}),1)
   byun=[row for row in result if row['work']['featuredNames']=='邊荷律']
   self.assertEqual({row['edition']['format'] for row in byun},{'physical'})
   self.assertEqual(len({row['edition']['id'] for row in byun}),2)
   young=[row for row in result if row['work']['featuredNames']=='李雅英']
   digital=next(row for row in young if row['edition']['format']=='digital')
   self.assertEqual({row['edition']['format'] for row in young},{'physical','digital'})
   self.assertEqual(digital['edition']['isbn'],'9786264551892')
   self.assertEqual(digital['edition']['pageCount'],0)
   self.assertEqual(digital['edition']['dimensions'],'')
   self.assertIn('272',digital['edition']['contentSummary'])
   self.assertEqual(sum(row['edition']['format']=='physical' for row in young),2)
   jueun=[row for row in result if row['work']['featuredNames']=='李珠珢']
   self.assertEqual({row['edition']['isbn'] for row in jueun},{'9786264342247','9786264342254'})
   self.assertEqual(len({row['edition']['editionVariant'] for row in jueun}),2)
 def test_yuri_new_name_links_to_existing_catalog_work(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   pub.write_text(json.dumps([{'model':'陳怡叡','title':'洛入你心：YURI陳洛心日本寫真(電子書)','body':'陳洛心YURI 出版日：2025/09/05 EISBN：9786264196291 出版社：時報文化 裝訂：電子書 檔案格式：EPUB版式','url':'https://www.sanmin.com.tw/product/index/014791167','imageUrl':'https://example.com/yuri-ebook.jpg','format':'digital','contentSummary':'日本寫真；EPUB固定版式。'}]),encoding='utf-8')
   live.write_text('[]',encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(len(result),1)
   self.assertEqual(result[0]['work']['id'],'work-tw-47da677df17f8ec405473a4f')
   self.assertEqual(result[0]['edition']['isbn'],'9786264196291')
   self.assertEqual(result[0]['edition']['format'],'digital')
 def test_baoer_ebook_links_to_existing_print_work(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   row={'model':'寶兒','title':'Babe Fantasy‧寶兒寫真書(電子書)','body':'寶兒 EISBN：9786267683781 出版社：創意市集 出版日：2025/12/11 裝訂：電子書 檔案格式：EPUB','url':'https://www.sanmin.com.tw/product/index/015552499','imageUrl':'https://example.com/baoer-ebook.jpg','format':'digital','contentSummary':'EPUB電子寫真；未公開照片數量未確認。'}
   pub.write_text(json.dumps([row],ensure_ascii=False),encoding='utf-8');live.write_text('[]',encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(len(result),1)
   self.assertEqual(result[0]['work']['id'],'work-tw-6bfdeef40b49b66040c85d2e')
   self.assertEqual(result[0]['edition']['isbn'],'9786267683781')
   self.assertEqual(result[0]['edition']['format'],'digital')
   self.assertEqual(result[0]['edition']['pageCount'],0)
   self.assertNotIn('海報',result[0]['edition']['contentSummary'])
 def test_nicole_print_edition_links_to_existing_ebook_work(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   row={'model':'妮可','title':'想見妮‧Nicole妮可寫真書【隨書附贈：未公開寫真海報四款隨機一款】','body':'妮可 ISBN13：9786267683088 出版社：創意市集 作者：妮可-著；陳伸維-攝影 出版日：2025/05/02 裝訂／頁數：平裝／144頁 規格：26cm*18.50cm*1.1cm 海報尺寸：33cm X 49cm 四款隨機一款。','url':'https://www.sanmin.com.tw/product/index/014272084','imageUrl':'https://example.com/nicole-print.jpg','format':'physical','releaseDate':'2025-04-29','contentSummary':'144頁紙本寫真書，收錄妮可球場與生活影像，由陳伸維攝影；附33×49公分海報一張，四款隨機。'}
   pub.write_text(json.dumps([row],ensure_ascii=False),encoding='utf-8');live.write_text('[]',encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))[0]
   self.assertEqual(result['work']['id'],'work-tw-e23888df7c68a3c7d3bc18ea')
   self.assertEqual(result['work']['originalTitle'],'想見妮‧Nicole妮可寫真書')
   self.assertEqual(result['edition']['format'],'physical')
   self.assertEqual(result['edition']['isbn'],'9786267683088')
   self.assertEqual(result['edition']['pageCount'],144)
   self.assertEqual(result['edition']['dimensions'],'26cm*18.50cm*1.1cm')
   self.assertEqual(result['edition']['releaseDate'],'2025-04-29T00:00:00Z')
   self.assertIn('海報',result['edition']['contentSummary'])
 def test_sanmin_print_and_ebook_share_work_but_keep_format_metadata_separate(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   description='阿部瑪利亞首部寫真；神奈川海岸與街巷場景，攝影師KRIS KANG。'
   rows=[
    {'model':'阿部瑪利亞','title':'半分はんぶん：阿部瑪利亞寫真【隨書加贈收藏卡】','body':'阿部瑪利亞 ISBN：9786264199285 出版社：時報文化 出版日：2025/11/07 裝訂／頁數：平裝／128頁 規格：28cm*21cm*0.95cm','url':'https://www.sanmin.com.tw/product/index/014936599','imageUrl':'https://example.com/print.jpg','format':'physical','contentSummary':description+' 紙本含隨機收藏卡1張（2款之一）。'},
    {'model':'阿部瑪利亞','title':'半分 はんぶん：阿部瑪利亞寫真(電子書)','body':'阿部瑪利亞 ISBN：9786264199285 EISBN：9786264199193 出版社：時報文化 出版日：2025/11/07 裝訂：電子書 檔案格式：EPUB版式','url':'https://www.sanmin.com.tw/product/index/015064155','imageUrl':'https://example.com/digital.jpg','format':'digital','contentSummary':description+' EPUB版式電子書。'}]
   pub.write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8');live.write_text('[]',encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'));physical,digital=result
   self.assertEqual(physical['work']['id'],digital['work']['id'])
   self.assertEqual(physical['work']['originalTitle'],'半分 はんぶん：阿部瑪利亞寫真')
   self.assertEqual(physical['edition']['isbn'],'9786264199285')
   self.assertEqual(physical['edition']['pageCount'],128)
   self.assertEqual(physical['edition']['dimensions'],'28cm*21cm*0.95cm')
   self.assertEqual(digital['edition']['isbn'],'9786264199193')
   self.assertEqual(digital['edition']['pageCount'],0)
   self.assertEqual(digital['edition']['dimensions'],'')
   self.assertEqual({physical['edition']['format'],digital['edition']['format']},{'physical','digital'})
   self.assertIn('收藏卡',physical['edition']['contentSummary'])
   self.assertNotIn('收藏卡',digital['edition']['contentSummary'])
 def test_separate_editions_and_no_ambiguous_price(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   pub.write_text(json.dumps([{'model':'吳元元','title':'《元氣東京》吳婕安寫真書 特裝版','body':'吳婕安 出版日期：2019-12-17 ISBN：9789571081663 規格：144頁','url':'https://www.cite.com.tw/book?id=82767','imageUrl':'https://example.com/cover.jpg'}]),encoding='utf-8')
   item={'title':'元氣東京 吳婕安寫真書 數位完全版（含影音）','format':'digital','externalId':'123','url':'https://readmoo.com/book/123','imageUrl':'https://example.com/digital.jpg','editionVariant':'with_video','isbn':'9789571095769'}
   source={'kind':'digital_store','allowedHosts':['readmoo.com']}
   records=[{'model':'吳元元','request':{'format':'digital','source':source},'batch':{'sourceId':'readmoo-tw','items':[item]}}]
   records.append({'model':'吳元元','request':{'format':'physical','source':{'kind':'marketplace','allowedHosts':['www.ruten.com.tw']}},'batch':{'sourceId':'ruten-tw','items':[{'title':'元氣東京 吳婕安寫真書','url':'https://www.ruten.com.tw/item/123/'}]}})
   live.write_text(json.dumps(records),encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(len({r['work']['id'] for r in result if r['work'].get('id')}),1)
   self.assertEqual({r['edition']['format'] for r in result if r['edition'].get('format')},{'physical','digital'})
   self.assertIn('抱枕套',result[0]['edition']['contentSummary'])
   self.assertEqual(sum(len(r['batch'].get('items',[])) for r in result),2)
   unlinked=[r for r in result if not r['edition']]
   self.assertEqual(unlinked[0]['batch']['items'][0]['editionId'],'')
 def test_cover_rejects_private_addresses(self):
  with patch('r2_covers.socket.getaddrinfo',return_value=[(None,None,None,None,('127.0.0.1',443))]):
   with self.assertRaises(ValueError):download_cover('https://example.com/cover.jpg')

 def test_separately_sold_parts_without_isbn_remain_distinct(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   pub.write_text('[]',encoding='utf-8')
   rows=[]
   for number in (1,2):
    item={'title':f'鄭家純十週年紀念寫真28純熟 Part.{number}','format':'digital','externalId':str(number),'url':f'https://readmoo.com/book/{number}','imageUrl':f'https://example.com/{number}.jpg'}
    rows.append({'model':'鄭家純','request':{'format':'digital','source':{'kind':'digital_store','allowedHosts':['readmoo.com']}},'batch':{'sourceId':'readmoo-tw','items':[item]}})
   live.write_text(json.dumps(rows),encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(len({r['work']['id'] for r in result}),1)
   self.assertEqual(len({r['edition']['id'] for r in result}),2)

 def test_multiline_retail_metadata_and_calendar_exclusion(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);pub=root/'pub.json';live=root/'live.json';out=root/'out.json'
   body='郭鬼鬼\nISBN\n：9789865245795\n出版社\n：台灣角川\n出版日\n：2021/08/26\n裝訂／頁數\n：平裝／144頁'
   rows=[{'model':'郭鬼鬼','title':'魔鬼與天使：郭鬼鬼Angela寫真書','url':'https://www.sanmin.com.tw/product/index/009466007','imageUrl':'https://example.com/cover.jpg','body':body}]
   rows.append({**rows[0],'title':'郭鬼鬼2026寫真掛曆'})
   pub.write_text(json.dumps(rows),encoding='utf-8');live.write_text('[]',encoding='utf-8');prepare(live,pub,out)
   result=json.loads(out.read_text(encoding='utf-8'))
   self.assertEqual(len(result),1);edition=result[0]['edition']
   self.assertEqual(edition['isbn'],'9789865245795');self.assertEqual(edition['publisher'],'台灣角川');self.assertEqual(edition['pageCount'],144);self.assertEqual(edition['releaseDate'],'2021-08-26T00:00:00Z')


