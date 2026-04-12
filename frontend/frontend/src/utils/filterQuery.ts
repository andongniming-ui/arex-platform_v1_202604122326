import type { LocationQuery, LocationQueryRaw } from 'vue-router'
import type { DateRangeValue } from './dateRange'

function firstValue(value: string | string[] | null | undefined) {
  if (Array.isArray(value)) return value[0] ?? null
  return value ?? null
}

export function getQueryText(query: LocationQuery, key: string) {
  const value = firstValue(query[key] as string | string[] | undefined)
  return value ? String(value) : null
}

export function getQueryDateRange(query: LocationQuery, fromKey: string, toKey: string): DateRangeValue {
  const from = getQueryText(query, fromKey)
  const to = getQueryText(query, toKey)
  if (!from || !to) return null
  const fromTs = Date.parse(from)
  const toTs = Date.parse(to)
  if (Number.isNaN(fromTs) || Number.isNaN(toTs)) return null
  return [fromTs, toTs]
}

export function setQueryText(target: LocationQueryRaw, key: string, value: string | null | undefined) {
  if (value == null || value === '') return
  target[key] = value
}

export function setQueryDateRange(target: LocationQueryRaw, range: DateRangeValue, fromKey: string, toKey: string) {
  if (!range) return
  target[fromKey] = new Date(range[0]).toISOString()
  target[toKey] = new Date(range[1]).toISOString()
}
