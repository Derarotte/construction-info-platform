import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { useProjectOrgStore } from './projectOrg'

export type DocumentStatus = '草稿' | '生效' | '归档'

export interface DocumentRecord {
  id: string
  projectId: string
  projectName: string
  sectionCode: string
  title: string
  category: string
  version: number
  fileName: string
  fileSize: number
  uploadedBy: string
  status: DocumentStatus
  createdAt: string
  updatedAt: string
}

const STORAGE_KEY = 'cip_document_center_v1'

function uid() {
  return `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`
}

function nowText() {
  return new Date().toISOString().slice(0, 19).replace('T', ' ')
}

export const useDocumentCenterStore = defineStore('document-center', () => {
  const documents = ref<DocumentRecord[]>([])
  const loaded = ref(false)

  const activeCount = computed(() => documents.value.filter((item) => item.status === '生效').length)
  const archiveCount = computed(() => documents.value.filter((item) => item.status === '归档').length)

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(documents.value))
  }

  function seedFromProjectStore() {
    const projectOrgStore = useProjectOrgStore()
    projectOrgStore.load()
    const p1 = projectOrgStore.projects[0]
    const p2 = projectOrgStore.projects[1] ?? projectOrgStore.projects[0]
    documents.value = [
      {
        id: uid(),
        projectId: p1?.id ?? '',
        projectName: p1?.name ?? '默认项目',
        sectionCode: p1?.sections[0]?.code ?? 'A1',
        title: '监理日志周报',
        category: '周报',
        version: 4,
        fileName: 'monitor-weekly-report-v4.pdf',
        fileSize: 2048,
        uploadedBy: '刘工',
        status: '生效',
        createdAt: nowText(),
        updatedAt: nowText(),
      },
      {
        id: uid(),
        projectId: p1?.id ?? '',
        projectName: p1?.name ?? '默认项目',
        sectionCode: p1?.sections[0]?.code ?? 'A1',
        title: 'A1 标段施工方案',
        category: '方案',
        version: 2,
        fileName: 'A1-construct-plan-v2.docx',
        fileSize: 1536,
        uploadedBy: '赵工',
        status: '生效',
        createdAt: nowText(),
        updatedAt: nowText(),
      },
      {
        id: uid(),
        projectId: p2?.id ?? '',
        projectName: p2?.name ?? '默认项目2',
        sectionCode: p2?.sections[0]?.code ?? 'B2',
        title: '质量巡检记录',
        category: '巡检',
        version: 2,
        fileName: 'quality-inspection-v2.xlsx',
        fileSize: 980,
        uploadedBy: '孙工',
        status: '归档',
        createdAt: nowText(),
        updatedAt: nowText(),
      },
    ]
  }

  function load() {
    if (loaded.value) return
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      documents.value = JSON.parse(raw) as DocumentRecord[]
    } else {
      seedFromProjectStore()
      persist()
    }
    loaded.value = true
  }

  function createDocument(payload: Omit<DocumentRecord, 'id' | 'version' | 'status' | 'createdAt' | 'updatedAt'>) {
    const now = nowText()
    documents.value.unshift({
      ...payload,
      id: uid(),
      version: 1,
      status: '生效',
      createdAt: now,
      updatedAt: now,
    })
    persist()
  }

  function createNewVersion(
    id: string,
    payload: Pick<DocumentRecord, 'fileName' | 'fileSize' | 'uploadedBy'>,
  ) {
    const target = documents.value.find((item) => item.id === id)
    if (!target) return false
    target.version += 1
    target.fileName = payload.fileName
    target.fileSize = payload.fileSize
    target.uploadedBy = payload.uploadedBy
    target.updatedAt = nowText()
    if (target.status === '归档') {
      target.status = '生效'
    }
    persist()
    return true
  }

  function setStatus(id: string, status: DocumentStatus) {
    const target = documents.value.find((item) => item.id === id)
    if (!target) return false
    target.status = status
    target.updatedAt = nowText()
    persist()
    return true
  }

  return {
    documents,
    activeCount,
    archiveCount,
    load,
    createDocument,
    createNewVersion,
    setStatus,
  }
})
