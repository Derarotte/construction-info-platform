<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { usePlatformScopeStore } from '../stores/platformScope'
import { useProjectOrgStore } from '../stores/projectOrg'
import { usePlanningCostStore, type TaskNode } from '../stores/planningCost'

const scopeStore = usePlatformScopeStore()
const projectStore = useProjectOrgStore()
const planningStore = usePlanningCostStore()

const keyword = ref('')
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editingId = ref('')
const formRef = ref<FormInstance>()

const form = reactive({
  projectId: '',
  code: '',
  name: '',
  plannedDays: 1,
  actualDays: 0,
  plannedCost: 1,
  actualCost: 0,
  progress: 0,
  predecessors: [] as string[],
})

const rules: FormRules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  code: [{ required: true, message: '请输入任务编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
}

const tasksScoped = computed(() =>
  scopeStore.selectedProject
    ? planningStore.tasks.filter((item) => item.projectId === scopeStore.selectedProject?.id)
    : planningStore.tasks,
)

const tasksFiltered = computed(() => {
  const key = keyword.value.trim().toLowerCase()
  return tasksScoped.value.filter((item) => {
    if (!key) return true
    return [item.projectName, item.code, item.name].join('|').toLowerCase().includes(key)
  })
})

const projectOptions = computed(() => projectStore.projects)
const selectedProjectTasks = computed(() =>
  scopeStore.selectedProject
    ? planningStore.tasks.filter((item) => item.projectId === scopeStore.selectedProject?.id)
    : [],
)

const predecessorOptions = computed(() =>
  planningStore.tasks
    .filter((item) => item.projectId === form.projectId && item.id !== editingId.value)
    .map((item) => ({ label: `${item.code} ${item.name}`, value: item.id })),
)

const metrics = computed(() => {
  const rows = tasksScoped.value
  const pv = rows.reduce((sum, item) => sum + item.plannedCost * (item.progress / 100), 0)
  const ev = rows.reduce(
    (sum, item) =>
      sum +
      (item.plannedCost * (Math.min(item.progress, 100) / 100) * Math.min(item.actualDays / Math.max(item.plannedDays, 1), 1)),
    0,
  )
  const ac = rows.reduce((sum, item) => sum + item.actualCost, 0)

  const plannedDuration = rows.reduce((sum, item) => sum + item.plannedDays, 0)
  const actualDuration = rows.reduce((sum, item) => sum + item.actualDays, 0)
  const scheduleDeviation = actualDuration - plannedDuration
  const costDeviation = ac - rows.reduce((sum, item) => sum + item.plannedCost, 0)
  const spi = pv === 0 ? 1 : ev / pv
  const cpi = ac === 0 ? 1 : ev / ac

  return {
    plannedDuration,
    actualDuration,
    scheduleDeviation,
    costDeviation,
    spi: Number(spi.toFixed(2)),
    cpi: Number(cpi.toFixed(2)),
  }
})

const criticalPath = computed(() => {
  const rows = selectedProjectTasks.value
  if (rows.length === 0) return { plannedPath: [], actualPath: [], plannedLen: 0, actualLen: 0, cycle: false }

  const map = new Map<string, TaskNode>()
  for (const r of rows) map.set(r.id, r)
  const indegree = new Map<string, number>()
  const next = new Map<string, string[]>()
  for (const r of rows) {
    indegree.set(r.id, r.predecessors.filter((p) => map.has(p)).length)
    for (const p of r.predecessors) {
      if (!map.has(p)) continue
      if (!next.has(p)) next.set(p, [])
      next.get(p)!.push(r.id)
    }
  }
  const q: string[] = []
  for (const r of rows) {
    if ((indegree.get(r.id) ?? 0) === 0) q.push(r.id)
  }
  const order: string[] = []
  while (q.length > 0) {
    const cur = q.shift()!
    order.push(cur)
    for (const n of next.get(cur) ?? []) {
      indegree.set(n, (indegree.get(n) ?? 0) - 1)
      if ((indegree.get(n) ?? 0) === 0) q.push(n)
    }
  }
  if (order.length !== rows.length) {
    return { plannedPath: [], actualPath: [], plannedLen: 0, actualLen: 0, cycle: true }
  }

  const run = (weight: (task: TaskNode) => number) => {
    const dist = new Map<string, number>()
    const prev = new Map<string, string | null>()
    for (const id of order) {
      const t = map.get(id)!
      let bestPrev: string | null = null
      let bestDist = 0
      for (const p of t.predecessors.filter((x) => map.has(x))) {
        const d = dist.get(p) ?? 0
        if (d > bestDist) {
          bestDist = d
          bestPrev = p
        }
      }
      dist.set(id, bestDist + weight(t))
      prev.set(id, bestPrev)
    }
    const firstId = order[0]
    if (!firstId) {
      return { path: [] as TaskNode[], len: 0 }
    }
    let endId = firstId
    let maxLen = dist.get(endId) ?? 0
    for (const id of order) {
      const d = dist.get(id) ?? 0
      if (d > maxLen) {
        maxLen = d
        endId = id
      }
    }
    const path: TaskNode[] = []
    let cur: string | null = endId
    while (cur) {
      path.unshift(map.get(cur)!)
      const nextId = prev.get(cur)
      cur = nextId ?? null
    }
    return { path, len: maxLen }
  }

  const planned = run((t) => t.plannedDays)
  const actual = run((t) => t.actualDays)
  return {
    plannedPath: planned.path,
    actualPath: actual.path,
    plannedLen: planned.len,
    actualLen: actual.len,
    cycle: false,
  }
})

function resetForm() {
  form.projectId = scopeStore.selectedProject?.id ?? ''
  form.code = ''
  form.name = ''
  form.plannedDays = 1
  form.actualDays = 0
  form.plannedCost = 1
  form.actualCost = 0
  form.progress = 0
  form.predecessors = []
}

function openCreate() {
  dialogMode.value = 'create'
  editingId.value = ''
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: TaskNode) {
  dialogMode.value = 'edit'
  editingId.value = row.id
  form.projectId = row.projectId
  form.code = row.code
  form.name = row.name
  form.plannedDays = row.plannedDays
  form.actualDays = row.actualDays
  form.plannedCost = row.plannedCost
  form.actualCost = row.actualCost
  form.progress = row.progress
  form.predecessors = [...row.predecessors]
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const project = projectStore.projects.find((item) => item.id === form.projectId)
  if (!project) {
    ElMessage.error('项目不存在')
    return
  }

  if (dialogMode.value === 'create') {
    planningStore.addTask({
      projectId: form.projectId,
      projectName: project.name,
      code: form.code,
      name: form.name,
      plannedDays: form.plannedDays,
      actualDays: form.actualDays,
      plannedCost: form.plannedCost,
      actualCost: form.actualCost,
      progress: form.progress,
      predecessors: [...form.predecessors],
    })
  } else {
    planningStore.updateTask(editingId.value, {
      code: form.code,
      name: form.name,
      plannedDays: form.plannedDays,
      actualDays: form.actualDays,
      plannedCost: form.plannedCost,
      actualCost: form.actualCost,
      progress: form.progress,
      predecessors: [...form.predecessors],
    })
  }
  dialogVisible.value = false
  ElMessage.success('保存成功')
}

function removeTask(row: TaskNode) {
  planningStore.removeTask(row.id)
  ElMessage.success('任务已删除')
}

onMounted(() => {
  projectStore.load()
  scopeStore.load()
  planningStore.load()
})
</script>

<template>
  <div class="planning-page">
    <el-alert :title="scopeStore.scopeTitle" type="info" :closable="false" show-icon />

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-label">工期偏差</div>
          <div class="metric-value" :class="{ danger: metrics.scheduleDeviation > 0 }">
            {{ metrics.scheduleDeviation > 0 ? '+' : '' }}{{ metrics.scheduleDeviation }} 天
          </div>
          <div class="metric-desc">计划 {{ metrics.plannedDuration }} / 实际 {{ metrics.actualDuration }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-label">造价偏差</div>
          <div class="metric-value" :class="{ danger: metrics.costDeviation > 0 }">
            {{ metrics.costDeviation > 0 ? '+' : '' }}{{ metrics.costDeviation.toFixed(1) }} 万
          </div>
          <div class="metric-desc">正值表示超支，负值表示节约</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-label">执行指数（SPI/CPI）</div>
          <div class="metric-value">{{ metrics.spi }} / {{ metrics.cpi }}</div>
          <div class="metric-desc">SPI&lt;1 进度落后，CPI&lt;1 成本超支</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <div class="header-row">
          <span>任务网络与执行台账</span>
          <el-button type="primary" @click="openCreate">新增任务</el-button>
        </div>
      </template>
      <el-row :gutter="12" class="filters">
        <el-col :span="8">
          <el-input v-model="keyword" clearable placeholder="搜索项目/任务编号/任务名称" />
        </el-col>
      </el-row>
      <el-table :data="tasksFiltered" stripe>
        <el-table-column prop="projectName" label="项目" min-width="160" />
        <el-table-column prop="code" label="任务编号" width="110" />
        <el-table-column prop="name" label="任务名称" min-width="180" />
        <el-table-column prop="plannedDays" label="计划工期(天)" width="110" />
        <el-table-column prop="actualDays" label="实际工期(天)" width="110" />
        <el-table-column prop="plannedCost" label="计划造价(万)" width="110" />
        <el-table-column prop="actualCost" label="实际造价(万)" width="110" />
        <el-table-column prop="progress" label="进度(%)" width="95" />
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="removeTask(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card v-if="scopeStore.selectedProject" shadow="never">
      <template #header>关键路径分析（简化版）</template>
      <el-alert
        v-if="criticalPath.cycle"
        title="检测到任务依赖存在环，无法计算关键路径，请检查前置任务配置。"
        type="error"
        :closable="false"
        show-icon
      />
      <template v-else>
        <el-row :gutter="16">
          <el-col :span="12">
            <div class="path-title">计划关键路径（{{ criticalPath.plannedLen }} 天）</div>
            <div class="path-text">
              {{ criticalPath.plannedPath.map((item) => item.code).join(' -> ') || '-' }}
            </div>
          </el-col>
          <el-col :span="12">
            <div class="path-title">实际关键路径（{{ criticalPath.actualLen }} 天）</div>
            <div class="path-text">
              {{ criticalPath.actualPath.map((item) => item.code).join(' -> ') || '-' }}
            </div>
          </el-col>
        </el-row>
      </template>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增任务' : '编辑任务'" width="620px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-form-item label="所属项目" prop="projectId">
          <el-select v-model="form.projectId" class="full-width">
            <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务编号" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="计划工期(天)">
              <el-input-number v-model="form.plannedDays" :min="1" :step="1" class="full-width" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际工期(天)">
              <el-input-number v-model="form.actualDays" :min="0" :step="1" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="计划造价(万)">
              <el-input-number v-model="form.plannedCost" :min="1" :step="1" class="full-width" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际造价(万)">
              <el-input-number v-model="form.actualCost" :min="0" :step="1" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="完成进度(%)">
          <el-slider v-model="form.progress" :min="0" :max="100" :step="5" show-input />
        </el-form-item>
        <el-form-item label="前置任务">
          <el-select v-model="form.predecessors" multiple collapse-tags class="full-width">
            <el-option
              v-for="item in predecessorOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
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
.planning-page {
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

.metric-desc {
  margin-top: 8px;
  color: #627d98;
}

.danger {
  color: #d64545;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filters {
  margin-bottom: 12px;
}

.path-title {
  font-size: 14px;
  color: #486581;
  margin-bottom: 8px;
}

.path-text {
  font-size: 16px;
  font-weight: 600;
  color: #102a43;
}

.full-width {
  width: 100%;
}
</style>
