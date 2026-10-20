// Public ASCII route smoke checks, not a general URL-normalizing robots engine.
export function robotsAllows(text, agent, path) {
  const groups = []
  let group = null
  for (const line of text.split(/\r?\n/)) {
    const match = line.split('#')[0].match(/^\s*([^:]+):\s*(.*?)\s*$/)
    if (!match) continue
    const key = match[1].trim().toLowerCase(), value = match[2]
    if (key === 'user-agent') {
      if (!group || group.hasRules) {
        group = { agents: [], rules: [], hasRules: false }
        groups.push(group)
      }
      group.agents.push(value.toLowerCase())
    } else if (group && ['allow', 'disallow'].includes(key)) {
      group.hasRules = true
      if (value) group.rules.push({ allow: key === 'allow', value })
    }
  }
  const token = agent.toLowerCase()
  const specific = groups.filter((entry) => entry.agents.includes(token))
  const selected = specific.length ? specific : groups.filter((entry) => entry.agents.includes('*'))
  let best = { length: -1, allow: true }
  for (const { rules } of selected) for (const rule of rules) {
    const anchored = rule.value.endsWith('$')
    const raw = anchored ? rule.value.slice(0, -1) : rule.value
    const pattern = raw.split('*').map((part) => part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*')
    const length = Buffer.byteLength(raw.replaceAll('*', ''))
    if (new RegExp('^' + pattern + (anchored ? '$' : '')).test(path)
      && (length > best.length || (length === best.length && rule.allow))) best = { length, allow: rule.allow }
  }
  return best.allow
}
