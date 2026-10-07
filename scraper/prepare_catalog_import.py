"""Build a reviewed Taiwan catalog manifest and mirror source covers to R2.

Inputs are live worker batches and publisher metadata, not arbitrary web titles.
Unmatched marketplace observations are left in the review report.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from r2_covers import R2Covers, load_env
from cover_policy import validate_cover_url
from photobook_worker import photobook_title_exclusion, marketplace_subject_matches


def identity(prefix, value):
    return prefix + hashlib.sha256(value.encode()).hexdigest()[:24]


def canonical_model(model):
    if model in {'Yilian', 'Yilianboy', 'Yilianboy游泳教練'}:
        return 'Yilian'
    if model in {'馮子紜', 'Teresa', '緹芝'}:
        return '馮子紜'
    if model in {'林育品', '阿喜'}:
        return '林育品'
    if model in {'嚴正嵐', 'Vera', 'Vera Yen'}:
        return '嚴正嵐'
    if model in {'海倫清桃', 'Helen Thanh Đào', 'Helen Thanh Dao'}:
        return '海倫清桃'
    if model in {'羽庭', '羽婷', '廖欣寧'}:
        return '羽庭'
    return model


def canonical_title(model, title):
    model = canonical_model(model)
    # Explicitly reviewed work relationships; full/abridged editions remain distinct.
    if model == 'Yilian' and title.startswith('SECRET：游泳教練寫真書'):
        return 'SECRET：游泳教練寫真書'
    if model == '吳俊' and 'Your Man' in title:
        return 'Your Man：吳俊junwu185寫真書'
    if model == '妮可' and '想見妮' in title:
        return '想見妮‧Nicole妮可寫真書'
    if model == '邊荷律' and '荷止微甜' in title:
        return '荷止微甜：邊荷律影像紀實'
    if model == '李雅英' and '沿著海' in title and '英為你心動' in title:
        return '沿著海，遇見你：英為你心動 李雅英寫真書'
    if model == '李珠珢' and 'FIGHT FOR ALL' in title.upper():
        return 'FIGHT FOR ALL：李珠珢的主場日記'
    if model == '寶兒' and 'Babe Fantasy' in title:
        return 'Babe Fantasy‧寶兒寫真書【隨書附贈寫真海報（四款隨機投入一款）】'
    if model == '阿部瑪利亞' and '半分はんぶん' in re.sub(r'[．。・·\s]', '', title):
        return '半分 はんぶん：阿部瑪利亞寫真'
    for name, term in [('張雅涵','Kimi23'),('許薇安','薇愛'),('謝侑芯','天使芯'),('湘綾','我愛綾520'),('羽晴','羽過天晴'),('籃籃','籃得遇見你'),('林岱縈','答應你'),('林岱縈','想鹿非非'),('黃上晏','仲夏晏之夢'),('張景嵐','嵐色花漾'),('張景嵐','夏日霓嵐'),('陳怡叡','洛入你心'),('陳怡叡','與你'),('陳紫渝','初年')]:
        if model == name and term in title: return term+'：'+name+'寫真'
    if 'bestie' in title.casefold() and '閨蜜' in title:
        return 'bestie閨蜜：孟潔×菲菲寫真'
    if model == '鄭家純' and '28純熟' in title:
        return '28純熟：鄭家純十週年紀念寫真'
    for term, expected_model in [('天天和你在苡起','巫苡萱'),('苡見鍾情','巫苡萱'),('孟幻旅程','林孟潔'),('菲常幸福','李恩菲'),('真心真亦','林真亦'),('亦如初見','林真亦'),('艾在你身邊','林艾融'),('玲距離的戀愛','許玲玲'),('一棋一會','斐棋'),('畇許曖昧','畇二'),('倪式暄言','倪暄'),('愛倪暄言','倪暄')]:
        if model == expected_model and term in title: return term+'：'+model+'寫真'
    for term, title_name in [('元氣東京','元氣東京：吳婕安寫真書'),('元氣滿滿','元氣滿滿：吳元元寫真書'),('與你襄遇','與你襄遇：林襄寫真書')]:
        if term in title: return title_name
    if (title.startswith('元元 ') or '《元元》' in title) and model == '吳元元': return '元元：吳婕安寫真書'
    normalized = re.sub(r'[．。・·\s]', '', title)
    for term, expected_model, canonical in [('揭開面莎','林莎','揭開．面莎：林莎寫真書'),('微澀微瑟','瑟七','微澀・微瑟：瑟七寫真書'),('一見峮心','峮峮','一見峮心：峮峮寫真書')]:
        if model == expected_model and term in normalized: return canonical
    return title.split(' | ')[0].strip()


def work_identity(model, title):
    model = canonical_model(model)
    # Stable identity retained while correcting this older digital-only work title.
    if model == '妮可' and '想見妮' in title:
        return 'work-tw-e23888df7c68a3c7d3bc18ea'
    return identity('work-tw-',model+'\0'+canonical_title(model,title))


def prepare(live_path, publisher_path, output, upload=False):
    live=json.loads(Path(live_path).read_text(encoding='utf-8-sig'))
    publishers=json.loads(Path(publisher_path).read_text(encoding='utf-8-sig'))
    cache_path=Path(output).with_suffix('.covers.json')
    cache=json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else {}
    store=R2Covers() if upload else None
    records=[];review=[];work_covers={}
    def cover(url):
        url=re.sub(r'^http://img\.91app\.com/', 'https://img.91app.com/', url)
        if not url: raise ValueError('No verified cover')
        validate_cover_url(url)
        if url not in cache:
            if not store: return {'url':url,'originalUrl':url,'key':''}
            cache[url]=store.upload(url)
            cache_path.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8')
        return cache[url]
    def entry(model,title,fmt,edition_id,source_url,image,**fields):
        model = canonical_model(model)
        if 'bestie' in title.casefold() and '閨蜜' in title and model in {'林孟潔','李恩菲'}:
            model='林孟潔、李恩菲'
        if model == '伊梓帆': model='陳伊、董梓甯、楊曉帆'
        photographer=fields.pop('photographer','')
        work_id=work_identity(model,title)
        if not work_covers.get(work_id): work_covers[work_id]=image['url']
        work={'id':work_id,'slug':work_id,'originalTitle':canonical_title(model,title),'originCode':'TW','featuredNames':model,'photographer':photographer,'coverUrl':work_covers[work_id],'summary':model+'的寫真作品；各版本內容以版次資料為準。'}
        edition={'id':edition_id,'workId':work_id,'format':fmt,'language':fields.pop('language','zh-Hant'),'editionMarket':'TW','coverUrl':image['url'],'originalCoverUrl':image['originalUrl'],'coverObjectKey':image['key'],'metadataSourceUrl':source_url,**fields}
        return {'work':work,'edition':edition,'source':{},'batch':{}}
    compositions={
        '76596':'寫真書1本、隨機海報1張（2款）、隨機A5資料夾2個（4款）、隨機抱枕套1個（2款），含外盒。',
        '82767':'寫真書1本、隨機海報1張（2款）、隨機抱枕套1個（2款），含外盒。',
        '84369':'144頁寫真書。通路限定贈品為4款親簽寫真卡中的隨機1款，數量有限；是否仍隨書附贈須向賣家確認。',
    }
    for product in publishers:
        title=product['title'].split('-城邦')[0].split(' | ')[0];body=product['body']
        fmt=product.get('format','physical')
        if fmt not in {'physical','digital'}:
            raise ValueError('Publisher format must be physical or digital')
        if photobook_title_exclusion(title):
            review.append({'url':product['url'],'reason':photobook_title_exclusion(title)});continue
        identity_text = title + '\n' + body
        model_names = [name.strip() for name in product['model'].split('、') if name.strip()]
        if not any(name in identity_text for name in model_names) and not (product['model']=='吳元元' and '吳婕安' in identity_text) and not (product['model']=='陳怡叡' and '陳洛心' in identity_text and 'YURI' in title): continue
        def match(pattern):
            found=re.search(pattern,body);return found.group(1).strip() if found else ''
        label='特裝版' if '特裝版' in title else '通路限定版' if '通路限定版' in title else '慶功版' if '慶功版' in title else '親簽限定版' if '親簽' in title else '襄吻唇印限定版' if '襄吻唇印限定版' in title else '限定版' if re.search('限定版|限量版',title) else '二刷版' if '二刷版' in title else '標準版'
        # Reviewed publisher metadata can identify cover-order and boxed editions.
        label=product.get('editionLabel') or ('數位版' if fmt=='digital' else label)
        isbn=match(r'(?:ISBN(?:13)?|條\s*碼)\s*[：:]?\s*(\d{13})');isbn=isbn if isbn.startswith(('978','979')) else ''
        if fmt=='digital': isbn=match(r'EISBN\s*[：:]?\s*(\d{13})') or isbn
        page=match(r'(\d+)頁') or match(r'頁數\s*[：:]?\s*(\d+)')
        date=match(r'(?:出版日期|出版日|上市日)\s*[：:]?\s*(\d{4}[-/]\d{2}[-/]\d{2})').replace('/','-')
        code=product['url'].split('id=')[-1].split('&')[0]
        try:
            try:
                image=cover(product['imageUrl'])
            except Exception as exc:
                review.append({'url':product['url'],'reason':'Cover pending; verified metadata retained','error':str(exc)})
                image={'url':'','originalUrl':product['imageUrl'],'key':''}
            dimensions = '' if fmt == 'digital' else match(r'(\d+(?:\.\d+)?\s*cm\s*[*x×]\s*\d+(?:\.\d+)?\s*cm\s*[*x×]\s*\d+(?:\.\d+)?\s*cm)') or match(r'(\d+(?:\.\d+)?\s*cm\s*[*x×]\s*\d+(?:\.\d+)?\s*cm)')
            page_count = product.get('pageCount') or page or 0
            fields={'editionLabel':label,'editionVariant':product.get('editionVariant') or ('unspecified' if fmt=='digital' else {'標準版':'standard','特裝版':'special','通路限定版':'limited','慶功版':'celebration','親簽限定版':'signed_limited','襄吻唇印限定版':'lipprint_limited','限定版':'limited','二刷版':'second_printing'}[label]), 'photographer':product.get('photographer',''),'publisher':product.get('publisher') or match(r'出版社\s*[：:]\s*([^\n]+)') or match(r'出版社\n([^\n]+)') or ('尖端' if 'spp.com.tw' in product['url'] else ''),'isbn':isbn,'pageCount':int(page_count),'dimensions':product.get('dimensions') or dimensions, 'seriesName':'襄水' if '襄水' in title else '', 'contentSummary':product.get('contentSummary') or ('數位寫真書；影音內容未確認。' if fmt=='digital' else compositions.get(code,('紙本寫真書，共'+page+'頁。') if page else '紙本寫真書；未確認額外贈品。'))}
            if date:fields.update(releaseDate=date+'T00:00:00Z',releasePrecision='day')
            if product.get('releaseDate'):
                fields.update(releaseDate=product['releaseDate']+'T00:00:00Z',releasePrecision=product.get('releasePrecision','day'))
            record=entry(product['model'],title,fmt,identity('edition-',product['url']+'\0'+label),product['url'],image,language=product.get('language') or 'zh-Hant',**fields)
            records.append(record)
        except Exception as e: review.append({'url':product['url'],'error':str(e)})
    for result in live:
        batch=result.get('batch',{});fmt=result['request']['format'];model=canonical_model(result['model'])
        if result.get('error'):review.append({'source':result['request']['sourceId'],'model':model,'error':result['error']})
        for item in batch.get('items',[]):
            exclusion=photobook_title_exclusion(item['title'])
            if exclusion:
                review.append({'url':item['url'],'sourceId':batch['sourceId'],'externalId':item['externalId'],'reason':exclusion});continue
            subject_request={**result['request'],'catalogModelNames':['吳元元','吳婕安','林襄','張雅涵','禾羽','林莎','峮峮','吳函峮','瑟七','Yilian','Yilianboy','Yilianboy游泳教練','吳翔震','馮子紜','Teresa','緹芝']}
            if fmt=='physical' and not marketplace_subject_matches(subject_request,item['title']):
                review.append({'url':item['url'],'reason':'Seller keywords mention target; primary subject is another model'});continue

            if fmt=='physical':
                # Require a verified edition ISBN or an unambiguous complete work title.
                def matches(record):
                    edition=record['edition']
                    if edition.get('format')!='physical' or record['work']['featuredNames']!=model:return False
                    if item.get('isbn') and edition.get('isbn'):return item['isbn']==edition['isbn']
                    if edition['editionVariant']!='standard' or re.search('特裝|限定|親簽|簽名|套組|合售',item['title']):return False
                    title=record['work']['originalTitle']
                    core=re.search(r'《([^》]+)》',title)
                    core=core.group(1) if core else title.split('：')[0]
                    return len(core)>=3 and core in item['title']
                candidates=[r for r in records if matches(r)]
                if len({(r['work']['id'],r['edition']['editionVariant'],r['edition']['editionLabel']) for r in candidates})!=1:
                    review.append({'url':item['url'],'reason':'Verified marketplace observation retained without an edition link'})
                    record={'work':{},'edition':{},'source':{},'batch':{}}
                    image_url=''
                    if item.get('imageUrl'):
                        try:image_url=cover(item['imageUrl'])['url']
                        except Exception as exc:review.append({'url':item['url'],'reason':'Unlinked marketplace cover pending','error':str(exc)})
                    sid=batch['sourceId'];source=result['request']['source']
                    record['source']={'id':sid,'name':sid,'kind':source['kind'],'region':'TW','accessMethod':'browser','defaultFormat':'physical','allowedFormats':'physical','allowedHosts':','.join(source['allowedHosts']),'enabled':True,'accessStatus':'browser_review','capabilities':'active_discovery,sold_discovery,listing_detail','ratePerMinute':6}
                    record['batch']={**batch,'items':[{**item,'editionId':'','imageUrl':image_url}],'jobId':'','leaseToken':'','workerId':''}
                    records.append(record);continue
                record=json.loads(json.dumps(candidates[0]));image_url=record['edition']['coverUrl']
                if not image_url and item.get('imageUrl'):
                    try:
                        image=cover(item['imageUrl']);record['edition'].update(coverUrl=image['url'],originalCoverUrl=image['originalUrl'],coverObjectKey=image['key']);record['work']['coverUrl']=image['url'];image_url=image['url']
                    except Exception as exc:review.append({'url':item['url'],'reason':'Marketplace cover pending','error':str(exc)})
            else:
                try:image=cover(item['imageUrl'])
                except Exception as e:review.append({'url':item['url'],'error':str(e)});continue
                variant=item.get('editionVariant') or 'unspecified'
                label='數位特別版' if '數位特別版' in item['title'] else '數位完全版' if '完全版' in item['title'] else '數位精華版' if '精華版' in item['title'] else '數位版'
                series=item.get('seriesName','')
                if not series:
                    for term in ['24個Kimi','25.kimi醬','襄水']:
                        if term.casefold() in item['title'].casefold():series=term;break
                content='電子寫真，附影音。' if variant=='with_video' else '電子寫真，不含影片。' if variant=='without_video' else '電子寫真；平台未明確標示是否含影音。'
                edition_id=identity('edition-',fmt+'\0'+(item.get('isbn') or batch['sourceId']+'\0'+item['externalId'])+'\0'+label+'\0'+variant)
                record=entry(model,item['title'],fmt,edition_id,item['url'],image,language=item.get('language') or 'zh-Hant',editionLabel=label,editionVariant=variant,isbn=item.get('isbn',''),publisher=item.get('publisher',''),pageCount=item.get('pageCount',0),contentSummary=content,seriesName=series)
                date=re.match(r'\d{4}-\d{2}-\d{2}',str(item.get('releaseDate','')))
                if date:record['edition'].update(releaseDate=date[0]+'T00:00:00Z',releasePrecision='day')
                image_url=image['url']
            sid=batch['sourceId'];source=result['request']['source']
            record['source']={'id':sid,'name':{'readmoo-tw':'Readmoo 讀墨','ruten-tw':'Ruten 露天','rakuten-kobo-tw':'Rakuten Kobo Taiwan 樂天Kobo','fan520-tw':'Fan520 女神範'}.get(sid,sid),'kind':source['kind'],'region':'TW','locale':'zh-TW','timezone':'Asia/Taipei','accessMethod':'browser','adapter':sid.replace('-','_'),'defaultFormat':fmt,'allowedFormats':fmt,'allowedHosts':','.join(source['allowedHosts']),'enabled':True,'accessStatus':'browser_review','capabilities':'active_discovery,listing_detail'+(',sold_discovery' if fmt=='physical' else ''),'ratePerMinute':6}
            listing={**item,'editionId':record['edition']['id'],'imageUrl':image_url}
            record['batch']={**batch,'items':[listing],'jobId':'','leaseToken':'','workerId':''}
            records.append(record)
    # Stores without ISBNs can reuse an exact titled, same-variant edition.
    # Never merge different ISBNs, full/abridged labels, or explicit video variants.
    digital_titles = {}
    for record in records:
        edition = record['edition']
        if edition.get('format') != 'digital': continue
        # Shared work names are not sufficient edition evidence: cover-order
        # editions and separately sold parts must retain their product titles.
        raw_title=record['batch'].get('items',[{}])[0].get('title',record['work']['originalTitle'])
        part = re.search(r'\bpart\s*[._-]?\s*(\d+)\b', raw_title, re.IGNORECASE)
        title=canonical_title(record['work']['featuredNames'],raw_title)
        part_key = 'part' + part.group(1) if part else ''
        key=(record['work']['featuredNames'], re.sub(r'[^\w]+', '', title).casefold(), edition['editionLabel'], edition['editionVariant'], part_key)
        previous=digital_titles.get(key)
        same_isbn = bool(edition.get('isbn')) and edition.get('isbn') == previous['edition'].get('isbn') if previous else False
        if previous and (not edition.get('isbn') or not previous['edition'].get('isbn') or same_isbn):
            publishers=(edition.get('publisher',''), previous['edition'].get('publisher',''))
            if not all(publishers) or publishers[0]==publishers[1]:
                record['supersedesEditionId']=edition['id']
                edition['id']=previous['edition']['id']
                for item in record['batch'].get('items',[]): item['editionId']=edition['id']
        else: digital_titles.setdefault(key,record)
    physical_editions = {}
    for record in records:
        edition = record['edition']
        if edition.get('format') != 'physical': continue
        key = (record['work']['id'], edition['editionVariant'], edition['editionLabel'])
        if key in physical_editions:
            edition['id'] = physical_editions[key]
            for item in record['batch'].get('items', []): item['editionId'] = edition['id']
        else: physical_editions[key] = edition['id']
    # One edition identity must resolve to one work even when stores vary punctuation.
    edition_works = {}
    for record in records:
        edition_id = record['edition'].get('id')
        if not edition_id: continue
        if edition_id in edition_works:
            record['work'] = dict(edition_works[edition_id])
            record['edition']['workId'] = record['work']['id']
        else:
            edition_works[edition_id] = dict(record['work'])
    Path(output).write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    Path(output).with_suffix('.review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={'works':len({r['work']['id'] for r in records if r['work'].get('id')}),'editions':len({r['edition']['id'] for r in records if r['edition'].get('id')}),'physical':len({r['edition']['id'] for r in records if r['edition'].get('format')=='physical'}),'digital':len({r['edition']['id'] for r in records if r['edition'].get('format')=='digital'}),'listings':sum(len(r['batch'].get('items',[])) for r in records),'covers':len(cache),'review':len(review)}
    print(json.dumps(summary));return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--live',required=True);parser.add_argument('--publisher',required=True);parser.add_argument('--output',required=True);parser.add_argument('--upload',action='store_true');args=parser.parse_args()
    load_env('backend/.env');prepare(args.live,args.publisher,args.output,args.upload)
