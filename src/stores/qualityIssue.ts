import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { useProjectOrgStore } from './projectOrg'
import { createQualityIssueRepository } from '../repositories/qualityIssueRepository'

export type QualityLevel = '低' | '中' | '高' | '严重'
export type QualityStatus = '已上报' | '整改中' | '待复验' | '已闭环' | '驳回'

export interface QualityEvent {
  id: string
  issueId: string
  fromStatus: QualityStatus | null
  toStatus: QualityStatus
  note: string
  actor: string
  at: string
}

export interface QualityIssue {
  id: string
  code: string
  projectId: string
  projectName: string
  sectionCode: string
  title: string
  level: QualityLevel
  owner: string
  reporter: string
  status: QualityStatus
  deadline: string
  createdAt: string
  closedAt?: string
}

function uid() {
  return `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`
}

function nowText() {
  return new Date().toISOString().slice(0, 19).replace('T', ' ')
}

function ymdPlus(days: number) {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

const transitionMap: Record<QualityStatus, QualityStatus[]> = {
  已上报: ['整改中', '驳回'],
  整改中: ['待复验', '驳回'],
  待复验: ['已闭环', '整改中', '驳回'],
  已闭环: [],
  驳回: ['整改中'],
}

export const useQualityIssueStore = defineStore('quality-issue', () => {
  const issues = ref<QualityIssue[]>([])
  const events = ref<QualityEvent[]>([])
  const loaded = ref(false)
  const repository = createQualityIssueRepository()

  const openCount = computed(() =>
    issues.value.filter((item) => item.status !== '已闭环').length,
  )
  const closeRate = computed(() => {
    if (issues.value.length === 0) return 100
    const closed = issues.value.filter((item) => item.status === '已闭环').length
    return Number(((closed / issues.value.length) * 100).toFixed(1))
  })

  function persist() {
    repository.saveIssues(issues.value)
    repository.saveEvents(events.value)
  }

  function seedFromProjectStore() {
    const projectOrgStore = useProjectOrgStore()
    projectOrgStore.load()
    const p1 = projectOrgStore.projects[0]
    const p2 = projectOrgStore.projects[1] ?? projectOrgStore.projects[0]
    issues.value = [
      {
        id: uid(),
        code: 'Q-2026-001',
        projectId: p1?.id ?? '',
        projectName: p1?.name ?? '默认项目',
        sectionCode: p1?.sections[0]?.code ?? 'A1',
        title: '支护结构喷射厚度不足',
        level: '高',
        owner: '王工',
        reporter: '赵工',
        status: '整改中',
        deadline: ymdPlus(4),
        createdAt: nowText(),
      },
      {
        id: uid(),
        code: 'Q-2026-002',
        projectId: p1?.id ?? '',
        projectName: p1?.name ?? '默认项目',
        sectionCode: p1?.sections[0]?.code ?? 'A1',
        title: '钢筋绑扎间距偏差',
        level: '中',
        owner: '陈工',
        reporter: '赵工',
        status: '已闭环',
        deadline: ymdPlus(-1),
        createdAt: nowText(),
        closedAt: nowText(),
      },
      {
        id: uid(),
        code: 'Q-2026-003',
        projectId: p2?.id ?? '',
        projectName: p2?.name ?? '默认项目2',
        sectionCode: p2?.sections[0]?.code ?? 'B2',
        title: '防水层搭接长度不足',
        level: '严重',
        owner: '刘工',
        reporter: '李工',
        status: '待复验',
        deadline: ymdPlus(1),
        createdAt: nowText(),
      },
    ]
    events.value = issues.value.map((item) => ({
      id: uid(),
      issueId: item.id,
      fromStatus: null,
      toStatus: item.status,
      note: '初始化',
      actor: item.reporter,
      at: item.createdAt,
    }))
  }

  function load() {
    if (loaded.value) return
    const issueRows = repository.loadIssues()
    const eventRows = repository.loadEvents()
    if (issueRows.length > 0) {
      issues.value = issueRows
      events.value = eventRows
    } else {
      seedFromProjectStore()
      persist()
    }
    loaded.value = true
  }

  function canTransition(from: QualityStatus, to: QualityStatus) {
    return transitionMap[from].includes(to)
  }

  function createIssue(payload: Omit<QualityIssue, 'id' | 'createdAt' | 'closedAt' | 'status'>) {
    const issue: QualityIssue = {
      ...payload,
      id: uid(),
      createdAt: nowText(),
      status: '已上报',
    }
    issues.value.unshift(issue)
    events.value.unshift({
      id: uid(),
      issueId: issue.id,
      fromStatus: null,
      toStatus: '已上报',
      note: '问题上报',
      actor: issue.reporter,
      at: issue.createdAt,
    })
    persist()
  }

  function transitionIssue(issueId: string, toStatus: QualityStatus, note: string, actor: string) {
    const target = issues.value.find((item) => item.id === issueId)
    if (!target) return false
    if (!canTransition(target.status, toStatus)) return false
    const fromStatus = target.status
    target.status = toStatus
    if (toStatus === '已闭环') {
      target.closedAt = nowText()
    }
    if (toStatus !== '已闭环') {
      target.closedAt = undefined
    }
    events.value.unshift({
      id: uid(),
      issueId,
      fromStatus,
      toStatus,
      note,
      actor,
      at: nowText(),
    })
    persist()
    return true
  }

  function listEvents(issueId: string) {
    return events.value.filter((item) => item.issueId === issueId)
  }

  return {
    issues,
    events,
    openCount,
    closeRate,
    load,
    createIssue,
    transitionIssue,
    listEvents,
    canTransition,
  }
})
