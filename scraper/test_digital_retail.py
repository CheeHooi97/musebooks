import unittest
from unittest.mock import patch
from marketplace_adapters import resolve_adapter
from photobook_worker import collect, digital_edition_variant, make_observation, detail_snapshot, NavigationRateLimiter, digital_retail_candidates
class DigitalRetailTests(unittest.TestCase):
 def test_new_store_identity_and_search(self):
  for sid,url,identity in [('pubu-tw','https://www.pubu.com.tw/ebook/690306?campaign=x','690306'),('kobo-tw','https://www.kobo.com/tw/zh/ebook/wlOqRz7qzzKU_ymKeFTsCQ?ssId=x','wlOqRz7qzzKU_ymKeFTsCQ')]:
   adapter=resolve_adapter(sid)
   self.assertTrue(adapter.is_result_url(url));self.assertEqual(adapter.extract_external_id(url),identity)
   self.assertNotIn('?',adapter.canonical_result_url(url))
   self.assertFalse(adapter.is_result_url(url.replace('www.', 'evil.')))
   self.assertIn('search?',adapter.build_search_url('林襄','active_discovery','digital'))
   with self.assertRaises(ValueError):adapter.build_search_url('林襄','sold_discovery','digital')
  self.assertFalse(resolve_adapter('kobo-tw').is_result_url('https://www.kobo.com/us/en/ebook/abc'))
  self.assertFalse(resolve_adapter('pubu-tw').is_result_url('https://www.pubu.com.tw/media/123'))
 def test_variants_are_distinct(self):
  self.assertEqual(digital_edition_variant('涵氧女孩(無影片)'),'without_video')
  self.assertEqual(digital_edition_variant('與你襄遇（APP含影音）'),'with_video')
  self.assertEqual(digital_edition_variant('涵氧女孩'),'unspecified')
 def test_digital_offer_metadata_and_identity(self):
  source={'id':'pubu-tw','kind':'digital_store','region':'TW','allowedHosts':['www.pubu.com.tw'],'allowedFormats':['digital']}
  candidate={'url':'https://www.pubu.com.tw/ebook/123','title':'元來有你－吳元元數位寫真書（含影音）'}
  detail={'body':'EBook NT$276 Buy Add To Cart','structured':{'price':276,'currency':'TWD','availability':'https://schema.org/InStock','isbn':'9786264555029','publisher':'尖端出版'}}
  item,reason=make_observation({'sourceId':'pubu-tw','format':'digital','humanModelKeywords':['吳元元']},source,candidate,detail,'active_discovery')
  self.assertEqual(reason,'accepted');self.assertEqual(item['priceType'],'digital');self.assertEqual(item['priceMinor'],27600);self.assertEqual(item['editionVariant'],'with_video');self.assertEqual(item['isbn'],'9786264555029')
 def test_digital_default_does_not_use_marketplace_gate(self):
  for sid,host in [('pubu-tw','www.pubu.com.tw'),('kobo-tw','www.kobo.com')]:
   with patch('photobook_worker.launch',side_effect=RuntimeError('browser reached')),self.assertRaisesRegex(RuntimeError,'browser reached'):
    collect({'sourceId':sid,'source':{'kind':'digital_store','region':'TW','allowedHosts':[host]},'query':'林襄','operation':'active_discovery'})

 def test_native_panels_keep_prices_authors_and_versions(self):
  fixtures = [
   ('bookwalker-tw','張雅涵-電子寫真書_涵氧女孩','作者 張雅涵 類型標籤 人物寫真 出版社 滾石移動 EPUB格式 固定版面 價格 $312 $395 查看券後更優惠 立即結帳', '312', '張雅涵'),
   ('kobo-tw','涵氧女孩','涵氧女孩 由 張雅涵 簡介 寫真集 購買電子書 價格： NT$395 TWD 新增至購物車 電子書詳細資料 莉奈文創 發布日期：2023年3月14日','395','張雅涵'),
   ('pubu-tw','瑟七數位寫真（含影音）','Author 瑟七 Follow Publisher 尖端出版 Follow ISBN 9786264555029 EBook NT$350 Get NT$52 off Buy Add To Cart Related Product Other Book NT$99','350','瑟七')]
  from unittest.mock import MagicMock
  for sid,title,body,price,author in fixtures:
   page=MagicMock();page.locator.return_value.count.return_value=0
   with patch('photobook_worker.navigate_page',return_value=body),patch('photobook_worker.page_body',return_value=body),patch('photobook_worker.structured_product',return_value={}),patch('photobook_worker.page_metadata',return_value={'name':title}),patch('photobook_worker.read_text',return_value=title):
    detail=detail_snapshot(page,'https://example.test/book',{'example.test'},sid,NavigationRateLimiter({},{}))
   self.assertEqual(detail['structured']['price'],price)
   self.assertEqual(detail['structured']['author'],author)
   self.assertEqual(detail['structured']['currency'],'TWD')
   if sid == 'kobo-tw':self.assertIn('寫真集',detail['structured']['description'])
 def test_retail_search_filters_before_detail_limit(self):
  candidates=[{'title':'Other Book','text':'元 字'},{'title':'元來有你－吳元元數位寫真','text':''}]
  self.assertEqual(len(digital_retail_candidates(candidates,{'query':'元來有你'},1)),1)
  self.assertIn('吳元元',digital_retail_candidates(candidates,{'query':'元來有你'},1)[0]['title'])

 def test_format_restriction_text_is_not_sold_evidence(self):
  source={'id':'pubu-tw','kind':'digital_store','region':'TW','allowedHosts':['www.pubu.com.tw'],'allowedFormats':['digital']}
  candidate={'url':'https://www.pubu.com.tw/ebook/123','title':'瑟七數位寫真（含影音）'}
  detail={'body':'EPUB not available EBook NT$350 Buy','structured':{'price':350,'currency':'TWD','availability':'https://schema.org/InStock'}}
  item,reason=make_observation({'sourceId':'pubu-tw','format':'digital','humanModelKeywords':['瑟七']},source,candidate,detail,'active_discovery')
  self.assertEqual(reason,'accepted');self.assertEqual(item['status'],'active')

 def test_author_search_can_reach_titles_without_author_name(self):
  candidate={'title':'涵氧女孩','text':''}
  self.assertEqual(digital_retail_candidates([candidate],{'query':'張雅涵','humanModelKeywords':['張雅涵']},1),[candidate])

 def test_model_matches_get_detail_budget_before_unrelated_results(self):
  candidates=[{'title':'Other Book','text':'涵 字'}, {'title':'24個Kimi 張雅涵寫真','text':''}, {'title':'涵氧女孩','text':''}]
  found=digital_retail_candidates(candidates,{'query':'張雅涵','humanModelKeywords':['張雅涵','Kimi']},1)
  self.assertEqual(found[0]['title'],'24個Kimi 張雅涵寫真')

 def test_named_store_photobook_need_not_end_in_book_or_collection(self):
  source={'id':'readmoo-tw','kind':'digital_store','region':'TW','allowedHosts':['readmoo.com'],'allowedFormats':['digital']}
  candidate={'url':'https://readmoo.com/book/210123456000101','title':'24個Kimi_張雅涵寫真-你的女朋友【1】'}
  detail={'body':'EPUB 電子書優惠價 NT$250 加入購物車','structured':{'price':'250','currency':'TWD','availability':'https://schema.org/InStock'}}
  item,reason=make_observation({'sourceId':'readmoo-tw','format':'digital','humanModelKeywords':['張雅涵','Kimi']},source,candidate,detail,'active_discovery')
  self.assertEqual(reason,'accepted');self.assertEqual(item['format'],'digital')
  candidate['title']='張雅涵 写真 photo card'
  item,reason=make_observation({'sourceId':'readmoo-tw','format':'digital','humanModelKeywords':['張雅涵','Kimi']},source,candidate,detail,'active_discovery')
  self.assertIsNone(item);self.assertEqual(reason,'not_a_photobook')
