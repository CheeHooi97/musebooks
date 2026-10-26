// Language URLs are public documents, independent of browser preferences.
export const CATALOG_LANGUAGES = [
  { code: 'en', segment: '', label: 'English', og: 'en_US' },
  { code: 'ja', segment: 'jp', label: '日本語', og: 'ja_JP' },
  { code: 'zh-Hant', segment: 'tw', label: '繁體中文', og: 'zh_TW' },
  { code: 'zh-Hans', segment: 'cn', label: '简体中文', og: 'zh_CN' },
  { code: 'ko', segment: 'kr', label: '한국어', og: 'ko_KR' },
]
export function hasLanguageEditions(route) {
  return ['/', '/books', '/models', '/publishers'].includes(route) || /^\/(books|models|publishers)\/[^/]+$/.test(route)
}
export function languagePath(route, language) {
  const entry = CATALOG_LANGUAGES.find(item => item.code === language)
  if (!entry) throw new Error(`Unsupported catalog language: ${language}`)
  return entry.segment ? `/${entry.segment}${route === '/' ? '' : route}` : route
}
export function languageAlternates(route, siteURL) {
  if (!hasLanguageEditions(route)) return []
  return [...CATALOG_LANGUAGES.map(language => ({ ...language, url: `${siteURL}${languagePath(route, language.code)}` })), { code: 'x-default', label: 'English', url: `${siteURL}${route}` }]
}
