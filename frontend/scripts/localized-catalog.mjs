import { escape, json } from './seo-content.mjs'
import { pageSeo, publicationDate } from '../src/lib/seo.js'
import { languagePath, languageAlternates } from '../src/lib/catalog-languages.js'

// Only fixed editorial text is translated. Names, dates, ISBNs and cited source
// facts retain their recorded value; no biography or bibliographic fact is invented.
const keys = ['catalog', 'intro', 'books', 'models', 'publishers', 'editions', 'format', 'publisher', 'published', 'language', 'pages', 'dimensions', 'source', 'people', 'photographer', 'origin', 'originalName', 'englishName', 'physical', 'digital', 'note', 'methodology', 'correction', 'open', 'unknown']
const copy = {
  ja: ['写真集・雑誌カタログ', 'モデル、アイドル、著名人の写真集と雑誌を探せます。紙版と電子版の出版社、発売日、ISBN、出典を確認できます。', '写真集・雑誌', 'モデル・出演者', '出版社', '収録されている版', '形式', '出版社', '発売日', '言語', 'ページ数', 'サイズ', '情報の出典', '出演者', '撮影者', '地域', '原語名', '英語名', '紙版', '電子版', '未記録の情報は不明です。原題と出典の表記を保持しています。価格、在庫、確認日は英語版で比較できます。販売終了は成約を意味しません。', '収録方針と出典（英語）', '訂正を送る', '価格と販売記録を見る', '未記録'],
  'zh-Hant': ['寫真集與雜誌目錄', '探索模特兒、偶像及名人的寫真集與雜誌，查閱實體版和電子版的出版社、出版日期、ISBN 與資料來源。', '寫真集與雜誌', '模特兒與演出者', '出版社', '已收錄版本', '格式', '出版社', '出版日期', '語言', '頁數', '尺寸', '資料來源', '演出者', '攝影師', '地區', '原文姓名', '英文姓名', '實體版', '電子版', '未記錄的資料視為未知。作品原名及來源文字保留原樣。價格、庫存及觀察日期可在英文版比較。刊登結束不代表已成交。', '收錄方法與來源（英文）', '提供更正', '查看價格與銷售記錄', '未記錄'],
  'zh-Hans': ['写真集与杂志目录', '探索模特、偶像及名人的写真集与杂志，查阅实体版和电子版的出版社、出版日期、ISBN 与资料来源。', '写真集与杂志', '模特与出演者', '出版社', '已收录版本', '格式', '出版社', '出版日期', '语言', '页数', '尺寸', '资料来源', '出演者', '摄影师', '地区', '原文姓名', '英文姓名', '实体版', '电子版', '未记录的资料视为未知。作品原名及来源文字保留原样。价格、库存及观察日期可在英文版比较。刊登结束不代表已成交。', '收录方法与来源（英文）', '提供更正', '查看价格与销售记录', '未记录'],
  ko: ['사진집·잡지 카탈로그', '모델, 아이돌, 유명인의 사진집과 잡지를 찾아보세요. 종이책과 전자책의 출판사, 발행일, ISBN 및 자료 출처를 확인할 수 있습니다.', '사진집·잡지', '모델·출연자', '출판사', '수록된 판본', '형식', '출판사', '발행일', '언어', '쪽수', '크기', '자료 출처', '출연자', '사진가', '지역', '원어 이름', '영문 이름', '종이책', '전자책', '기록되지 않은 정보는 알 수 없습니다. 작품 원제와 출처의 표기를 유지합니다. 가격, 재고 및 확인 날짜는 영어판에서 비교할 수 있습니다. 판매 종료가 거래 완료를 뜻하지는 않습니다.', '수록 기준과 출처 (영어)', '정보 수정 요청', '가격과 판매 기록 보기', '미기록'],
}
const texts = language => Object.fromEntries(keys.map((key, index) => [key, copy[language][index]]))
export function languageNavigation(route, siteURL = '') {
  return `<nav aria-label="Languages">${languageAlternates(route, siteURL).filter(item => item.code !== 'x-default').map(item => `<a data-reload href="${escape(item.url)}" lang="${item.code}" hreflang="${item.code}">${item.label}</a>`).join(' · ')}</nav>`
}
export function localizedCatalog(route, data, language, siteURL) {
  const t = texts(language)
  const { book, profile, books = [], profiles = [] } = data
  const people = book?.publicationType === 'magazine_issue' && book.coverModels?.length ? book.coverModels : book?.models || []
  const url = `${siteURL}${languagePath(route, language)}`
  const link = (path, label) => `<a href="${escape(languagePath(path, language))}">${escape(label)}</a>`
  const external = (url, label) => /^https?:\/\//i.test(url || '') ? `<a href="${escape(url)}" rel="noreferrer">${escape(label)}</a>` : ''
  const facts = pairs => `<dl>${pairs.filter(([, value]) => value !== undefined && value !== null && value !== '').map(([label, value]) => `<dt>${escape(label)}</dt><dd>${escape(value)}</dd>`).join('')}</dl>`
  const list = items => `<ul>${items.map(item => `<li>${link(`/books/${encodeURIComponent(item.slug)}`, item.originalTitle)}${item.englishTitle ? ` — ${escape(item.englishTitle)}` : ''}</li>`).join('')}</ul>`
  const heading = book?.originalTitle || profile?.name || (route === '/models' ? t.models : route === '/publishers' ? t.publishers : route === '/books' ? t.books : t.catalog)
  let body = `<h1>${escape(heading)}</h1><p>${escape(t.intro)}</p>`
  if (book) {
    body = `<h1>${escape(heading)}</h1>${/^https?:\/\//i.test(book.coverUrl || '') ? `<img src="${escape(book.coverUrl)}" alt="${escape(book.originalTitle)}" width="240" style="max-width:100%;height:auto"/>` : ''}${book.englishTitle ? `<p>${escape(book.englishTitle)}</p>` : ''}`
    body += facts([[t.photographer, book.photographer], [t.origin, book.origin?.name]])
    body += `<h2>${t.people}</h2><ul>${people.map(person => `<li>${link(`/models/${encodeURIComponent(person.id)}`, person.name)}</li>`).join('')}</ul><h2>${t.editions}</h2>`
    body += (book.editions || []).map(edition => `<section><h3>${escape(edition.editionLabel || t.editions)}</h3>${facts([[t.format, t[edition.format] || edition.format], [t.publisher, edition.publisher], [t.published, publicationDate(edition)], ['ISBN', edition.isbn], [t.language, edition.language], [t.pages, edition.pageCount], [t.dimensions, edition.dimensions]])}${edition.publisherProfile?.id ? `<p>${link(`/publishers/${encodeURIComponent(edition.publisherProfile.id)}`, edition.publisherProfile.name)}</p>` : ''}<p>${external(edition.metadataSourceUrl, t.source)}</p></section>`).join('')
    body += `<p><a href="${escape(route)}" lang="en">${t.open}</a></p>`
  } else if (profile) {
    body += facts([[t.originalName, profile.originalName], [t.englishName, profile.englishName]]) + `<p>${external(profile.officialUrl, t.source)}</p><h2>${t.books}</h2>${list(books)}`
  } else if (route === '/models' || route === '/publishers') {
    body += `<ul>${profiles.map(entry => `<li>${link(`${route}/${encodeURIComponent(entry.id)}`, entry.name)}</li>`).join('')}</ul>`
  } else body += list(books)
  body += `<p>${t.note}</p>`
  const seo = pageSeo(route, book, profile, siteURL)
  // Rewrite only site entity URLs, preserving external sources and entity types.
  const graph = JSON.parse(JSON.stringify(seo.structuredData), (key, value) => {
    if (key === 'description') return undefined
    if (typeof value !== 'string' || !value.startsWith(`${siteURL}/`)) return value
    const parsed = new URL(value)
    return /^\/(books|models|publishers)(\/|$)/.test(parsed.pathname) || parsed.pathname === '/' ? `${siteURL}${languagePath(parsed.pathname, language)}${parsed.hash}` : value
  })
  const title = `${heading} — ${t.catalog} — MuseBooks`
  // The page language and the publication's recorded inLanguage are distinct.
  graph['@graph'].push({ '@type': 'WebPage', '@id': `${url}#page`, url, name: title, description: t.intro, inLanguage: language })
  return { title, description: t.intro, url, structuredData: graph, body: `<div class="site-shell"><header class="site-header"><a href="${languagePath('/', language)}">MuseBooks</a><nav>${link('/books', t.books)} · ${link('/models', t.models)} · ${link('/publishers', t.publishers)}</nav>${languageNavigation(route)}</header><main id="main-content" class="seo-static-content page-width">${body}</main><footer><a href="/about" lang="en">${t.methodology}</a> · <a href="mailto:musecards67@gmail.com">${t.correction}</a></footer></div>` }
}
export function localizedMarkdown(route, data, language, siteURL) {
  const t = texts(language)
  const { book, profile, books = [], profiles = [] } = data
  const people = book?.publicationType === 'magazine_issue' && book.coverModels?.length ? book.coverModels : book?.models || []
  const text = value => String(value ?? '').replace(/([\\`*_[\]<>])/g, '\\$1').replace(/\s+/g, ' ').trim()
  const link = (route, name) => `[${text(name)}](${siteURL}${languagePath(route, language)})`
  const lines = [`# ${text(book?.originalTitle || profile?.name || t.catalog)}`, '', `${t.source}: ${siteURL}${languagePath(route, language)}`, '', t.intro, '']
  if (book) {
    lines.push(`## ${t.people}`, '', ...people.map(person => `- ${link(`/models/${encodeURIComponent(person.id)}`, person.name)}`), '', `## ${t.editions}`, '')
    for (const edition of book.editions || []) {
      lines.push(`### ${text(edition.editionLabel || t.editions)}`, '')
      for (const [label, value] of [[t.format, t[edition.format] || edition.format], [t.publisher, edition.publisher], [t.published, publicationDate(edition)], ['ISBN', edition.isbn], [t.language, edition.language], [t.pages, edition.pageCount], [t.dimensions, edition.dimensions]]) if (value) lines.push(`- ${label}: ${text(value)}`)
      if (/^https?:\/\//i.test(edition.metadataSourceUrl || '')) lines.push(`- ${t.source}: ${edition.metadataSourceUrl}`)
      lines.push('')
    }
    lines.push(`[${t.open}](${siteURL}${route})`, '')
  } else if (route === '/models' || route === '/publishers') lines.push(...profiles.map(entry => `- ${link(`${route}/${encodeURIComponent(entry.id)}`, entry.name)}`), '')
  else lines.push(...books.map(book => `- ${link(`/books/${encodeURIComponent(book.slug)}`, book.originalTitle)}`), '')
  lines.push(t.note, '', ...languageAlternates(route, siteURL).filter(item => item.code !== 'x-default').map(item => `[${item.label}](${item.url})`), '')
  return lines.join('\n')
}
export function renderLocalizedCatalog(template, route, data, language, siteURL) {
  const page = localizedCatalog(route, data, language, siteURL)
  const meta = (name, content, attribute = 'name') => `<meta ${attribute}="${name}" content="${escape(content)}"/>`
  const head = `<title>${escape(page.title)}</title>${meta('description', page.description)}${meta('robots', 'index,follow,max-image-preview:large')}<link rel="canonical" href="${escape(page.url)}"/><link rel="alternate" type="text/markdown" href="${escape(page.url)}.md"/>${languageAlternates(route, siteURL).map(item => `<link rel="alternate" hreflang="${item.code}" href="${escape(item.url)}"/>`).join('')}${meta('og:title', page.title, 'property')}${meta('og:description', page.description, 'property')}${meta('og:url', page.url, 'property')}${meta('og:type', 'website', 'property')}${meta('og:locale', languageAlternates(route, siteURL).find(item => item.code === language).og, 'property')}<script id="musebooks-seo-jsonld" type="application/ld+json">${json(page.structuredData)}</script>`
  // Public language editions are complete static documents. Do not let the
  // English-only SPA router overwrite their content, metadata or language.
  return template.replace(/<html\b[^>]*>/i, `<html lang="${language}">`).replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '').replace(/<link\b[^>]*(?:rel=["'](?:modulepreload|canonical)["']|hreflang=["'][^"']+["']|type=["']text\/markdown["'])[^>]*>/gi, '').replace(/<title>[\s\S]*?<\/title>/i, '').replace(/<meta\b[^>]*(?:name=["'](?:description|robots|twitter:[^"']+)["']|property=["']og:[^"']+["'])[^>]*>/gi, '').replace(/(<div id="root">)[\s\S]*(<\/body>)/, '$1</div>$2').replace('</head>', () => `${head}</head>`).replace('<div id="root"></div>', () => `<div id="root">${page.body}</div>`)
}
