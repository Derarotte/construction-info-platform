<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useProjectOrgStore } from '../stores/projectOrg'
import { usePlatformScopeStore } from '../stores/platformScope'

const projectOrgStore = useProjectOrgStore()
const scopeStore = usePlatformScopeStore()

const documentsPool = [
  {
    project: '江北快速路项目',
    name: '监理日志周报.pdf',
    category: '周报',
    version: 'v1.4',
    updatedAt: '2026-02-11 17:22',
    owner: '刘工',
  },
  {
    project: '江北快速路项目',
    name: 'A1 标段施工方案.docx',
    category: '方案',
    version: 'v2.0',
    updatedAt: '2026-02-10 09:14',
    owner: '赵工',
  },
  {
    project: '城南隧道项目',
    name: '质量巡检记录.xlsx',
    category: '巡检',
    version: 'v1.9',
    updatedAt: '2026-02-12 08:45',
    owner: '孙工',
  },
]

const documents = computed(() =>
  scopeStore.selectedProject
    ? documentsPool.filter((item) => item.project === scopeStore.selectedProject?.name)
    : documentsPool,
)

onMounted(() => {
  projectOrgStore.load()
  scopeStore.load()
})
</script>

<template>
  <el-card shadow="never">
    <template #header>资料管理（上传/分类/版本）</template>
    <el-alert :title="scopeStore.scopeTitle" type="info" :closable="false" show-icon class="scope-alert" />
    <el-row :gutter="12" class="toolbar">
      <el-col :span="8">
        <el-input placeholder="按资料名称搜索" />
      </el-col>
      <el-col :span="16" class="toolbar-actions">
        <el-button type="primary">上传资料</el-button>
        <el-button>批量导入</el-button>
      </el-col>
    </el-row>
    <el-table :data="documents" stripe>
      <el-table-column prop="project" label="项目" min-width="160" />
      <el-table-column prop="name" label="资料名称" min-width="220" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="version" label="版本" width="100" />
      <el-table-column prop="updatedAt" label="更新时间" width="170" />
      <el-table-column prop="owner" label="上传人" width="110" />
    </el-table>
  </el-card>
</template>

<style scoped>
.scope-alert {
  margin-bottom: 12px;
}

.toolbar {
  margin-bottom: 12px;
}

.toolbar-actions {
  text-align: right;
}
</style>
