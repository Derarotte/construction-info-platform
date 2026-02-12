<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useProjectOrgStore } from '../stores/projectOrg'
import { usePlatformScopeStore } from '../stores/platformScope'

type NodeKind = 'project' | 'section' | 'workArea'
type DialogMode = 'create' | 'edit'
type DialogType = 'project' | 'section' | 'workArea'

interface TreeRow {
  id: string
  projectId: string
  sectionId?: string
  kind: NodeKind
  name: string
  code: string
  manager: string
  location: string
  status: string
  children?: TreeRow[]
}

const store = useProjectOrgStore()
const scopeStore = usePlatformScopeStore()

const keyword = ref('')
const statusFilter = ref<'全部' | '正常' | '关注' | '预警'>('全部')

const dialogVisible = ref(false)
const dialogMode = ref<DialogMode>('create')
const dialogType = ref<DialogType>('project')
const selectedProjectId = ref<string>('')
const selectedSectionId = ref<string>('')
const selectedRowId = ref<string>('')

const formRef = ref<FormInstance>()
const form = reactive({
  name: '',
  code: '',
  manager: '',
  location: '',
  status: '正常' as '正常' | '关注' | '预警',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  manager: [{ required: true, message: '请输入负责人', trigger: 'blur' }],
}

const tableRows = computed<TreeRow[]>(() =>
  store.projects.map((project) => ({
    id: project.id,
    projectId: project.id,
    kind: 'project',
    name: project.name,
    code: '-',
    manager: project.manager,
    location: project.location,
    status: '-',
    children: project.sections.map((section) => ({
      id: section.id,
      projectId: project.id,
      sectionId: section.id,
      kind: 'section',
      name: section.name,
      code: section.code,
      manager: section.manager,
      location: project.location,
      status: '-',
      children: section.workAreas.map((area) => ({
        id: area.id,
        projectId: project.id,
        sectionId: section.id,
        kind: 'workArea',
        name: area.name,
        code: section.code,
        manager: area.manager,
        location: project.location,
        status: area.status,
      })),
    })),
  })),
)

const filteredRows = computed(() => {
  const key = keyword.value.trim().toLowerCase()

  const matchText = (value: string) => value.toLowerCase().includes(key)

  const applyFilter = (rows: TreeRow[]): TreeRow[] => {
    const result: TreeRow[] = []
    for (const row of rows) {
      const children = row.children ? applyFilter(row.children) : []
      const selfMatch =
        (!key || [row.name, row.code, row.manager, row.location].some(matchText)) &&
        (statusFilter.value === '全部' || row.kind !== 'workArea' || row.status === statusFilter.value)
      if (selfMatch || children.length > 0) {
        result.push({ ...row, children })
      }
    }
    return result
  }

  return applyFilter(tableRows.value)
})

const dialogTitle = computed(() => {
  const modeText = dialogMode.value === 'create' ? '新增' : '编辑'
  if (dialogType.value === 'project') return `${modeText}项目`
  if (dialogType.value === 'section') return `${modeText}标段`
  return `${modeText}工区`
})

function resetForm() {
  form.name = ''
  form.code = ''
  form.manager = ''
  form.location = ''
  form.status = '正常'
  formRef.value?.clearValidate()
}

function openCreate(type: DialogType, row?: TreeRow) {
  dialogMode.value = 'create'
  dialogType.value = type
  selectedRowId.value = ''
  selectedProjectId.value = row?.projectId ?? ''
  selectedSectionId.value = row?.sectionId ?? ''
  resetForm()
  if (type === 'section' && row?.kind === 'project') {
    form.location = row.location
  }
  if (type === 'workArea' && row?.kind === 'section') {
    form.code = row.code
  }
  dialogVisible.value = true
}

function openEdit(row: TreeRow) {
  dialogMode.value = 'edit'
  dialogType.value = row.kind
  selectedRowId.value = row.id
  selectedProjectId.value = row.projectId
  selectedSectionId.value = row.sectionId ?? ''
  form.name = row.name
  form.code = row.kind === 'section' ? row.code : ''
  form.manager = row.manager
  form.location = row.kind === 'project' ? row.location : ''
  form.status = row.kind === 'workArea' ? (row.status as '正常' | '关注' | '预警') : '正常'
  dialogVisible.value = true
}

async function removeRow(row: TreeRow) {
  const label = row.kind === 'project' ? '项目' : row.kind === 'section' ? '标段' : '工区'
  await ElMessageBox.confirm(`确认删除${label}“${row.name}”？`, '删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  if (row.kind === 'project') store.deleteProject(row.id)
  if (row.kind === 'section') store.deleteSection(row.projectId, row.id)
  if (row.kind === 'workArea' && row.sectionId) store.deleteWorkArea(row.projectId, row.sectionId, row.id)
  ElMessage.success('删除成功')
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  if (dialogType.value === 'project') {
    const payload = { name: form.name, manager: form.manager, location: form.location || '未设置' }
    if (dialogMode.value === 'create') store.addProject(payload)
    else store.updateProject(selectedRowId.value, payload)
  }

  if (dialogType.value === 'section') {
    if (!selectedProjectId.value) return
    const payload = { code: form.code || '未设置', name: form.name, manager: form.manager }
    if (dialogMode.value === 'create') store.addSection(selectedProjectId.value, payload)
    else store.updateSection(selectedProjectId.value, selectedRowId.value, payload)
  }

  if (dialogType.value === 'workArea') {
    if (!selectedProjectId.value || !selectedSectionId.value) return
    const payload = { name: form.name, manager: form.manager, status: form.status }
    if (dialogMode.value === 'create') store.addWorkArea(selectedProjectId.value, selectedSectionId.value, payload)
    else store.updateWorkArea(selectedProjectId.value, selectedSectionId.value, selectedRowId.value, payload)
  }

  ElMessage.success('保存成功')
  dialogVisible.value = false
}

onMounted(() => {
  store.load()
  scopeStore.load()
})
</script>

<template>
  <div class="org-page">
    <el-row :gutter="16" class="summary-row">
      <el-col :span="8">
        <el-card shadow="never" class="summary-card">
          <div class="summary-label">项目数</div>
          <div class="summary-value">{{ store.projectCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="summary-card">
          <div class="summary-label">标段数</div>
          <div class="summary-value">{{ store.sectionCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="summary-card">
          <div class="summary-label">工区数</div>
          <div class="summary-value">{{ store.workAreaCount }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <div class="table-header">
          <span>项目-标段-工区分层管理</span>
          <el-button type="primary" @click="openCreate('project')">新增项目</el-button>
        </div>
      </template>

      <el-row :gutter="12" class="filters">
        <el-col :span="10">
          <el-input v-model="keyword" placeholder="按名称/标段/负责人/地区检索" clearable />
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" class="full-width">
            <el-option label="全部状态" value="全部" />
            <el-option label="正常" value="正常" />
            <el-option label="关注" value="关注" />
            <el-option label="预警" value="预警" />
          </el-select>
        </el-col>
      </el-row>

      <el-table
        :data="filteredRows"
        row-key="id"
        stripe
        default-expand-all
        :tree-props="{ children: 'children' }"
      >
        <el-table-column label="层级" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.kind === 'project'" type="success">项目</el-tag>
            <el-tag v-else-if="row.kind === 'section'" type="warning">标段</el-tag>
            <el-tag v-else>工区</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="220" />
        <el-table-column prop="code" label="标段编号" width="120" />
        <el-table-column prop="manager" label="负责人" width="120" />
        <el-table-column prop="location" label="所在地区" width="120" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.kind === 'workArea'" :type="row.status === '正常' ? 'success' : row.status === '关注' ? 'warning' : 'danger'">
              {{ row.status }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.kind === 'project'" link type="primary" @click="openCreate('section', row)">新增标段</el-button>
            <el-button
              v-if="row.kind === 'project'"
              link
              type="warning"
              @click="scopeStore.setProject(row.id)"
            >
              设为当前项目
            </el-button>
            <el-button v-if="row.kind === 'section'" link type="primary" @click="openCreate('workArea', row)">新增工区</el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="removeRow(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item v-if="dialogType === 'section'" label="标段编号">
          <el-input v-model="form.code" placeholder="例如 A1" />
        </el-form-item>
        <el-form-item v-if="dialogType === 'project'" label="所在地区">
          <el-input v-model="form.location" placeholder="例如 南京" />
        </el-form-item>
        <el-form-item label="负责人" prop="manager">
          <el-input v-model="form.manager" placeholder="请输入负责人" />
        </el-form-item>
        <el-form-item v-if="dialogType === 'workArea'" label="状态">
          <el-segmented
            v-model="form.status"
            :options="[
              { label: '正常', value: '正常' },
              { label: '关注', value: '关注' },
              { label: '预警', value: '预警' },
            ]"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.org-page {
  display: grid;
  gap: 16px;
}

.summary-row {
  margin: 0;
}

.summary-card {
  border: 1px solid #d9e2ec;
}

.summary-label {
  color: #627d98;
  font-size: 13px;
}

.summary-value {
  margin-top: 8px;
  color: #102a43;
  font-size: 30px;
  font-weight: 700;
}

.table-header {
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
