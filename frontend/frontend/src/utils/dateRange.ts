export type DateRangeValue = [number, number] | null

export function createDateShortcuts() {
  return {
    '今天': () => [new Date().setHours(0, 0, 0, 0), Date.now()] as [number, number],
    '最近3天': () => [Date.now() - 3 * 86400000, Date.now()] as [number, number],
    '最近7天': () => [Date.now() - 7 * 86400000, Date.now()] as [number, number],
    '最近30天': () => [Date.now() - 30 * 86400000, Date.now()] as [number, number],
  }
}

export function inDateRange(value: string | null | undefined, range: DateRangeValue) {
  if (!range || !value) return true
  const ts = new Date(value).getTime()
  if (Number.isNaN(ts)) return false
  return ts >= range[0] && ts <= range[1]
}
