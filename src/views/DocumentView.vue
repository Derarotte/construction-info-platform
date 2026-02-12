<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useProjectOrgStore } from '../stores/projectOrg'
import { usePlatformScopeStore } from '../stores/platformScope'
import { useDocumentCenterStore, type DocumentRecord } from '../stores/documentCenter'

const projectOrgStore = useProjectOrgStore()
const scopeStore = usePlatformScopeStore()
const documentStore = useDocumentCenterStore()

const keyword = ref('')
const statusFilter = ref<'全部' | '草稿' | '生效' | '归档'>('全部')
const categoryFilter = ref<'全部' | '周报' | '方案' | '巡检' | '图纸' | '交底'>('全部')

const uploadVisible = ref(false)
const versionVisible = ref(false)
const uploadRef = ref<FormInstance>()
const versionRef = ref<FormInstance>()
const selectedDocumentId = ref('')

const uploadForm = reactive({
  projectId: '',
  sectionCode: '',
  title: '',
  category: '周报',
  fileName: '',
  fileSize: 1024,
  uploadedBy: '系统管理员',
})

const versionForm = reactive({
  fileName: '',
  fileSize: 1024,
  uploadedBy: '系统管理员',
})

const uploadRules: FormRules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  sectionCode: [{ required: true, message: '请输入标段', trigger: 'blur' }],
  title: [{ required: true, message: '请输入资料标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  fileName: [{ required: true, message: '请输入文件名', trigger: 'blur' }],
  uploadedBy: [{ required: true, message: '请输入上传人', trigger: 'blur' }],
}

const versionRules: FormRules = {
  fileName: [{ required: true, message: '请输入新版本文件名', trigger: 'blur' }],
  uploadedBy: [{ required: true, message: '请输入上传人', trigger: 'blur' }],
}

const scopedDocs = computed(() =>
  scopeStore.selectedProject
    ? documentStore.documents.filter((item) => item.projectId === scopeStore.selectedProject?.id)
    : documentStore.documents,
)

const filteredDocs = computed(() => {
  const key = keyword.value.trim().toLowerCase()
  return scopedDocs.value.filter((item) => {
    const textMatch =
      !key ||
      [item.projectName, item.title, item.fileName, item.sectionCode, item.uploadedBy]
        .join('|')
        .toLowerCase()
        .includes(key)
    const statusMatch = statusFilter.value === '全部' || item.status === statusFilter.value
    const categoryMatch = categoryFilter.value === '全部' || item.category === categoryFilter.value
    return textMatch && statusMatch && categoryMatch
  })
})

const scopedTotal = computed(() => scopedDocs.value.length)
const scopedActive = computed(() => scopedDocs.value.filter((item) => item.status === '生效').length)
const scopedArchive = computed(() => scopedDocs.value.filter((item) => item.status === '归档').length)

const projectOptions = computed(() => projectOrgStore.projects)

function formatSizeKB(size: number) {
  return `${size} KB`
}

function versionText(row: DocumentRecord) {
  return `v${row.version}.0`
}

function openUpload() {
  uploadForm.projectId = scopeStore.selectedProject?.id ?? ''
  uploadForm.sectionCode = ''
  uploadForm.title = ''
  uploadForm.category = '周报'
  uploadForm.fileName = ''
  uploadForm.fileSize = 1024
  uploadForm.uploadedBy = '系统管理员'
  uploadVisible.value = true
}

async function submitUpload() {
  const valid = await uploadRef.value?.validate().catch(() => false)
  if (!valid) return
  const project = projectOrgStore.projects.find((item) => item.id === uploadForm.projectId)
  if (!project) {
    ElMessage.error('项目不存在')
    return
  }
  documentStore.createDocument({
    projectId: uploadForm.projectId,
    projectName: project.name,
    sectionCode: uploadForm.sectionCode,
    title: uploadForm.title,
    category: uploadForm.category,
    fileName: uploadForm.fileName,
    fileSize: uploadForm.fileSize,
    uploadedBy: uploadForm.uploadedBy,
  })
  uploadVisible.value = false
  ElMessage.success('资料上传建档成功')
}

function openVersion(row: DocumentRecord) {
  selectedDocumentId.value = row.id
  versionForm.fileName = row.fileName
  versionForm.fileSize = row.fileSize
  versionForm.uploadedBy = '系统管理员'
  versionVisible.value = true
}

async function submitVersion() {
  const valid = await versionRef.value?.validate().catch(() => false)
  if (!valid) return
  const ok = documentStore.createNewVersion(selectedDocumentId.value, {
    fileName: versionForm.fileName,
    fileSize: versionForm.fileSize,
    uploadedBy: versionForm.uploadedBy,
  })
  if (!ok) {
    ElMessage.error('资料不存在')
    return
  }
  versionVisible.value = false
  ElMessage.success('新版本已发布')
}

function archive(row: DocumentRecord) {
  const ok = documentStore.setStatus(row.id, '归档')
  if (!ok) return
  ElMessage.success('资料已归档')
}

function activate(row: DocumentRecord) {
  const ok = documentStore.setStatus(row.id, '生效')
  if (!ok) return
  ElMessage.success('资料已恢复生效')
}

onMounted(() => {
  projectOrgStore.load()
  scopeStore.load()
  documentStore.load()
})
</script>

<template>
  <div class="document-page">
    <el-alert :title="scopeStore.scopeTitle" type="info" :closable="false" show-icon />

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-label">当前范围资料总数</div>
          <div class="metric-value">{{ scopedTotal }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-label">生效资料</div>
          <div class="metric-value">{{ scopedActive }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-label">归档资料</div>
          <div class="metric-value">{{ scopedArchive }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <div class="header-row">
          <span>资料中心（上传/分类/版本/归档）</span>
          <el-button type="primary" @click="openUpload">上传资料</el-button>
        </div>
      </template>
      <el-row :gutter="12" class="filters">
        <el-col :span="8">
          <el-input v-model="keyword" clearable placeholder="按标题/文件名/负责人搜索" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="categoryFilter" class="full-width">
            <el-option label="全部分类" value="全部" />
            <el-option label="周报" value="周报" />
            <el-option label="方案" value="方案" />
            <el-option label="巡检" value="巡检" />
            <el-option label="图纸" value="图纸" />
            <el-option label="交底" value="交底" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="statusFilter" class="full-width">
            <el-option label="全部状态" value="全部" />
            <el-option label="草稿" value="草稿" />
            <el-option label="生效" value="生效" />
            <el-option label="归档" value="归档" />
          </el-select>
        </el-col>
      </el-row>

      <el-table :data="filteredDocs" stripe>
        <el-table-column prop="projectName" label="项目" min-width="170" />
        <el-table-column prop="sectionCode" label="标段" width="90" />
        <el-table-column prop="title" label="资料标题" min-width="180" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column label="版本" width="90">
          <template #default="{ row }">{{ versionText(row) }}</template>
        </el-table-column>
        <el-table-column prop="fileName" label="文件名" min-width="180" />
        <el-table-column label="大小" width="90">
          <template #default="{ row }">{{ formatSizeKB(row.fileSize) }}</template>
        </el-table-column>
        <el-table-column prop="uploadedBy" label="上传人" width="100" />
        <el-table-column prop="updatedAt" label="更新时间" width="165" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === '生效' ? 'success' : row.status === '归档' ? 'info' : 'warning'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openVersion(row)">新版本</el-button>
            <el-button v-if="row.status !== '归档'" link type="warning" @click="archive(row)">归档</el-button>
            <el-button v-else link type="success" @click="activate(row)">激活</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="uploadVisible" title="上传资料" width="560px">
      <el-form ref="uploadRef" :model="uploadForm" :rules="uploadRules" label-width="92px">
        <el-form-item label="项目" prop="projectId">
          <el-select v-model="uploadForm.projectId" class="full-width">
            <el-option v-for="item in projectOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标段" prop="sectionCode">
          <el-input v-model="uploadForm.sectionCode" placeholder="例如 A1" />
        </el-form-item>
        <el-form-item label="资料标题" prop="title">
          <el-input v-model="uploadForm.title" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="uploadForm.category" class="full-width">
            <el-option label="周报" value="周报" />
            <el-option label="方案" value="方案" />
            <el-option label="巡检" value="巡检" />
            <el-option label="图纸" value="图纸" />
            <el-option label="交底" value="交底" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件名" prop="fileName">
          <el-input v-model="uploadForm.fileName" placeholder="例如 quality-report.pdf" />
        </el-form-item>
        <el-form-item label="大小(KB)">
          <el-input-number v-model="uploadForm.fileSize" :min="1" :step="100" />
        </el-form-item>
        <el-form-item label="上传人" prop="uploadedBy">
          <el-input v-model="uploadForm.uploadedBy" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpload">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="versionVisible" title="发布新版本" width="520px">
      <el-form ref="versionRef" :model="versionForm" :rules="versionRules" label-width="92px">
        <el-form-item label="文件名" prop="fileName">
          <el-input v-model="versionForm.fileName" />
        </el-form-item>
        <el-form-item label="大小(KB)">
          <el-input-number v-model="versionForm.fileSize" :min="1" :step="100" />
        </el-form-item>
        <el-form-item label="上传人" prop="uploadedBy">
          <el-input v-model="versionForm.uploadedBy" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="versionVisible = false">取消</el-button>
        <el-button type="primary" @click="submitVersion">发布版本</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.document-page {
  display: grid;
  gap: 16px;
}

.metric-card {
  border: 1px solid #d9e2ec;
}

.metric-label {
  color: #627d98;
  font-size: 13px;
}

.metric-value {
  margin-top: 8px;
  font-size: 30px;
  font-weight: 700;
  color: #102a43;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filters {
  margin-bottom: 12px;
}

.full-width {
  width: 100%;
}
</style>
