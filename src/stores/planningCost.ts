import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { useProjectOrgStore } from './projectOrg'

export interface TaskNode {
  id: string
  projectId: string
  projectName: string
  code: string
  name: string
  plannedDays: number
  actualDays: number
  plannedCost: number
  actualCost: number
  progress: number
  predecessors: string[]
}

const STORAGE_KEY = 'cip_planning_cost_v1'

function uid() {
  return `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`
}

export const usePlanningCostStore = defineStore('planning-cost', () => {
  const tasks = ref<TaskNode[]>([])
  const loaded = ref(false)

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks.value))
  }

  function seed() {
    const projectStore = useProjectOrgStore()
    projectStore.load()
    const p1 = projectStore.projects[0]
    const p2 = projectStore.projects[1] ?? projectStore.projects[0]

    const t1 = uid()
    const t2 = uid()
    const t3 = uid()
    const t4 = uid()
    const t5 = uid()

    tasks.value = [
      {
        id: t1,
        projectId: p1?.id ?? '',
        projectName: p1?.name ?? '默认项目',
        code: 'A1-T01',
        name: '临建及场地平整',
        plannedDays: 8,
        actualDays: 9,
        plannedCost: 32,
        actualCost: 35,
        progress: 100,
        predecessors: [],
      },
      {
        id: t2,
        projectId: p1?.id ?? '',
        projectName: p1?.name ?? '默认项目',
        code: 'A1-T02',
        name: '路基开挖',
        plannedDays: 14,
        actualDays: 16,
        plannedCost: 86,
        actualCost: 94,
        progress: 90,
        predecessors: [t1],
      },
      {
        id: t3,
        projectId: p1?.id ?? '',
        projectName: p1?.name ?? '默认项目',
        code: 'A1-T03',
        name: '支护结构施工',
        plannedDays: 12,
        actualDays: 11,
        plannedCost: 74,
        actualCost: 70,
        progress: 100,
        predecessors: [t2],
      },
      {
        id: t4,
        projectId: p1?.id ?? '',
        projectName: p1?.name ?? '默认项目',
        code: 'A1-T04',
        name: '排水系统施工',
        plannedDays: 10,
        actualDays: 0,
        plannedCost: 38,
        actualCost: 0,
        progress: 0,
        predecessors: [t2],
      },
      {
        id: t5,
        projectId: p2?.id ?? '',
        projectName: p2?.name ?? '默认项目2',
        code: 'B2-T01',
        name: '隧道初支',
        plannedDays: 18,
        actualDays: 20,
        plannedCost: 120,
        actualCost: 133,
        progress: 65,
        predecessors: [],
      },
    ]
  }

  function load() {
    if (loaded.value) return
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      tasks.value = JSON.parse(raw) as TaskNode[]
    } else {
      seed()
      persist()
    }
    loaded.value = true
  }

  function addTask(payload: Omit<TaskNode, 'id'>) {
    tasks.value.unshift({ id: uid(), ...payload })
    persist()
  }

  function updateTask(taskId: string, payload: Omit<TaskNode, 'id' | 'projectId' | 'projectName'>) {
    const target = tasks.value.find((item) => item.id === taskId)
    if (!target) return false
    target.code = payload.code
    target.name = payload.name
    target.plannedDays = payload.plannedDays
    target.actualDays = payload.actualDays
    target.plannedCost = payload.plannedCost
    target.actualCost = payload.actualCost
    target.progress = payload.progress
    target.predecessors = payload.predecessors
    persist()
    return true
  }

  function removeTask(taskId: string) {
    tasks.value = tasks.value
      .filter((item) => item.id !== taskId)
      .map((item) => ({
        ...item,
        predecessors: item.predecessors.filter((id) => id !== taskId),
      }))
    persist()
  }

  const byProject = computed(() => {
    const map: Record<string, TaskNode[]> = {}
    for (const task of tasks.value) {
      const bucket = map[task.projectId] ?? []
      bucket.push(task)
      map[task.projectId] = bucket
    }
    return map
  })

  return {
    tasks,
    byProject,
    load,
    addTask,
    updateTask,
    removeTask,
  }
})
