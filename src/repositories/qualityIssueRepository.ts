import type { QualityEvent, QualityIssue } from '../stores/qualityIssue'
import { getDataSourceMode, warnApiFallback } from './dataSource'

const ISSUE_KEY = 'cip_quality_issues_v1'
const EVENT_KEY = 'cip_quality_events_v1'

export interface QualityIssueRepository {
  loadIssues(): QualityIssue[]
  loadEvents(): QualityEvent[]
  saveIssues(issues: QualityIssue[]): void
  saveEvents(events: QualityEvent[]): void
}

class LocalQualityIssueRepository implements QualityIssueRepository {
  loadIssues() {
    const raw = localStorage.getItem(ISSUE_KEY)
    return raw ? (JSON.parse(raw) as QualityIssue[]) : []
  }

  loadEvents() {
    const raw = localStorage.getItem(EVENT_KEY)
    return raw ? (JSON.parse(raw) as QualityEvent[]) : []
  }

  saveIssues(issues: QualityIssue[]) {
    localStorage.setItem(ISSUE_KEY, JSON.stringify(issues))
  }

  saveEvents(events: QualityEvent[]) {
    localStorage.setItem(EVENT_KEY, JSON.stringify(events))
  }
}

export function createQualityIssueRepository(): QualityIssueRepository {
  const mode = getDataSourceMode()
  if (mode === 'api') {
    warnApiFallback('quality-issue')
  }
  return new LocalQualityIssueRepository()
}
