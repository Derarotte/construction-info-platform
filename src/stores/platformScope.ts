import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { useProjectOrgStore } from './projectOrg'

const STORAGE_KEY = 'cip_platform_scope_v1'

export const usePlatformScopeStore = defineStore('platform-scope', () => {
  const selectedProjectId = ref<string>('')
  const loaded = ref(false)
  const projectOrgStore = useProjectOrgStore()

  const selectedProject = computed(() =>
    projectOrgStore.projects.find((item) => item.id === selectedProjectId.value),
  )

  const scopeMode = computed<'platform' | 'project'>(() =>
    selectedProjectId.value ? 'project' : 'platform',
  )

  const scopeTitle = computed(() =>
    selectedProject.value ? `项目视角 / ${selectedProject.value.name}` : '平台总览视角 / 全部项目',
  )

  function persist() {
    localStorage.setItem(STORAGE_KEY, selectedProjectId.value)
  }

  function load() {
    if (loaded.value) return
    selectedProjectId.value = localStorage.getItem(STORAGE_KEY) ?? ''
    loaded.value = true
  }

  function setProject(projectId: string) {
    selectedProjectId.value = projectId
    persist()
  }

  function clearProject() {
    selectedProjectId.value = ''
    persist()
  }

  return {
    selectedProjectId,
    selectedProject,
    scopeMode,
    scopeTitle,
    load,
    setProject,
    clearProject,
  }
})
