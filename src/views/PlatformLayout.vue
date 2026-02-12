<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectOrgStore } from '../stores/projectOrg'
import { usePlatformScopeStore } from '../stores/platformScope'

const route = useRoute()
const router = useRouter()
const runMode = window.platformInfo?.desktop ? '桌面端运行中' : 'Web 预览模式'
const today = computed(() =>
  new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }),
)
const projectOrgStore = useProjectOrgStore()
const scopeStore = usePlatformScopeStore()

const projectSelector = computed({
  get: () => scopeStore.selectedProjectId || 'all',
  set: (value: string) => {
    if (value === 'all') scopeStore.clearProject()
    else scopeStore.setProject(value)
  },
})

onMounted(() => {
  projectOrgStore.load()
  scopeStore.load()
})

const menus = [
  { path: '/dashboard', label: '运营看板', icon: 'DataLine' },
  { path: '/project-org', label: '项目与组织', icon: 'OfficeBuilding' },
  { path: '/quality', label: '质量管理', icon: 'CircleCheck' },
  { path: '/planning-cost', label: '工期与造价', icon: 'TrendCharts' },
  { path: '/documents', label: '资料管理', icon: 'FolderOpened' },
  { path: '/gis', label: 'GIS 地图', icon: 'LocationInformation' },
  { path: '/ai-assist', label: 'AI 辅助', icon: 'MagicStick' },
]

function handleMenuSelect(path: string) {
  router.push(path)
}
</script>

<template>
  <el-container class="layout">
    <el-aside width="220px" class="sider">
      <div class="brand">
        <div class="brand-title">施工信息化平台</div>
        <div class="brand-subtitle">Web + Desktop MVP</div>
      </div>
      <el-menu :default-active="route.path" class="menu" @select="handleMenuSelect">
        <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-main">
          <div class="title">{{ route.meta.title }}</div>
          <div class="subtitle">施工信息化一体化平台 / 统一运营入口</div>
        </div>
        <div class="header-actions">
          <el-select v-model="projectSelector" class="project-switcher">
            <el-option label="平台总览（全部项目）" value="all" />
            <el-option
              v-for="project in projectOrgStore.projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
          <el-tag type="warning">{{ scopeStore.scopeTitle }}</el-tag>
          <el-tag type="success" effect="dark">{{ runMode }}</el-tag>
          <el-tag type="info">日期 {{ today }}</el-tag>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  min-height: 100vh;
}

.sider {
  background: linear-gradient(180deg, #12395f 0%, #0d2f4d 100%);
  color: #fff;
}

.brand {
  padding: 18px 16px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.brand-title {
  font-size: 18px;
  font-weight: 700;
}

.brand-subtitle {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.76);
}

.menu {
  border-right: none;
  background: transparent;
}

.menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.84);
}

.menu :deep(.el-menu-item.is-active) {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.12);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid #e8edf3;
  background: #ffffff;
}

.header-main {
  min-width: 300px;
}

.title {
  font-size: 20px;
  font-weight: 600;
  color: #102a43;
}

.subtitle {
  margin-top: 4px;
  color: #627d98;
  font-size: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.project-switcher {
  width: 220px;
}

.main-content {
  background: #f5f7fb;
}
</style>
