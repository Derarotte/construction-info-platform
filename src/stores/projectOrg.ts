import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export interface WorkArea {
  id: string
  name: string
  manager: string
  status: '正常' | '关注' | '预警'
}

export interface Section {
  id: string
  code: string
  name: string
  manager: string
  workAreas: WorkArea[]
}

export interface Project {
  id: string
  name: string
  manager: string
  location: string
  sections: Section[]
}

const STORAGE_KEY = 'cip_project_org_v1'

function uuid() {
  return `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`
}

const seedData: Project[] = [
  {
    id: uuid(),
    name: '江北快速路项目',
    manager: '赵工',
    location: '南京',
    sections: [
      {
        id: uuid(),
        code: 'A1',
        name: '江北路基标段',
        manager: '王工',
        workAreas: [
          { id: uuid(), name: '北段工区', manager: '刘工', status: '正常' },
          { id: uuid(), name: '互通工区', manager: '孙工', status: '关注' },
        ],
      },
    ],
  },
  {
    id: uuid(),
    name: '城南隧道项目',
    manager: '李工',
    location: '苏州',
    sections: [
      {
        id: uuid(),
        code: 'B2',
        name: '西线隧道标段',
        manager: '陈工',
        workAreas: [{ id: uuid(), name: '隧道西工区', manager: '周工', status: '预警' }],
      },
    ],
  },
]

export const useProjectOrgStore = defineStore('project-org', () => {
  const projects = ref<Project[]>([])
  const loaded = ref(false)

  const projectCount = computed(() => projects.value.length)
  const sectionCount = computed(() =>
    projects.value.reduce((sum, item) => sum + item.sections.length, 0),
  )
  const workAreaCount = computed(() =>
    projects.value.reduce(
      (sum, item) => sum + item.sections.reduce((inner, section) => inner + section.workAreas.length, 0),
      0,
    ),
  )

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects.value))
  }

  function load() {
    if (loaded.value) return
    const raw = localStorage.getItem(STORAGE_KEY)
    projects.value = raw ? (JSON.parse(raw) as Project[]) : seedData
    loaded.value = true
  }

  function addProject(payload: Omit<Project, 'id' | 'sections'>) {
    projects.value.unshift({ id: uuid(), ...payload, sections: [] })
    persist()
  }

  function updateProject(projectId: string, payload: Omit<Project, 'id' | 'sections'>) {
    const target = projects.value.find((item) => item.id === projectId)
    if (!target) return
    target.name = payload.name
    target.manager = payload.manager
    target.location = payload.location
    persist()
  }

  function deleteProject(projectId: string) {
    projects.value = projects.value.filter((item) => item.id !== projectId)
    persist()
  }

  function addSection(projectId: string, payload: Omit<Section, 'id' | 'workAreas'>) {
    const target = projects.value.find((item) => item.id === projectId)
    if (!target) return
    target.sections.unshift({ id: uuid(), ...payload, workAreas: [] })
    persist()
  }

  function updateSection(projectId: string, sectionId: string, payload: Omit<Section, 'id' | 'workAreas'>) {
    const target = projects.value.find((item) => item.id === projectId)
    if (!target) return
    const section = target.sections.find((item) => item.id === sectionId)
    if (!section) return
    section.code = payload.code
    section.name = payload.name
    section.manager = payload.manager
    persist()
  }

  function deleteSection(projectId: string, sectionId: string) {
    const target = projects.value.find((item) => item.id === projectId)
    if (!target) return
    target.sections = target.sections.filter((item) => item.id !== sectionId)
    persist()
  }

  function addWorkArea(projectId: string, sectionId: string, payload: Omit<WorkArea, 'id'>) {
    const target = projects.value.find((item) => item.id === projectId)
    const section = target?.sections.find((item) => item.id === sectionId)
    if (!section) return
    section.workAreas.unshift({ id: uuid(), ...payload })
    persist()
  }

  function updateWorkArea(
    projectId: string,
    sectionId: string,
    areaId: string,
    payload: Omit<WorkArea, 'id'>,
  ) {
    const target = projects.value.find((item) => item.id === projectId)
    const section = target?.sections.find((item) => item.id === sectionId)
    const area = section?.workAreas.find((item) => item.id === areaId)
    if (!area) return
    area.name = payload.name
    area.manager = payload.manager
    area.status = payload.status
    persist()
  }

  function deleteWorkArea(projectId: string, sectionId: string, areaId: string) {
    const target = projects.value.find((item) => item.id === projectId)
    const section = target?.sections.find((item) => item.id === sectionId)
    if (!section) return
    section.workAreas = section.workAreas.filter((item) => item.id !== areaId)
    persist()
  }

  return {
    projects,
    projectCount,
    sectionCount,
    workAreaCount,
    load,
    addProject,
    updateProject,
    deleteProject,
    addSection,
    updateSection,
    deleteSection,
    addWorkArea,
    updateWorkArea,
    deleteWorkArea,
  }
})
