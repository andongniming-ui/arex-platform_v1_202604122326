import { reactive, readonly } from 'vue'

const summaryState = reactive({
  text: '',
  visible: false,
})

export function usePageSummary() {
  function setPageSummary(text: string) {
    const normalized = text.trim()
    summaryState.text = normalized
    summaryState.visible = normalized.length > 0
  }

  function clearPageSummary() {
    summaryState.text = ''
    summaryState.visible = false
  }

  return {
    pageSummary: readonly(summaryState),
    setPageSummary,
    clearPageSummary,
  }
}
