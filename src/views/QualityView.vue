<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useProjectOrgStore } from '../stores/projectOrg'
import { usePlatformScopeStore } from '../stores/platformScope'
import { useQualityIssueStore, type QualityIssue, type QualityStatus } from '../stores/qualityIssue'

const projectOrgStore = useProjectOrgStore()
const scopeStore = usePlatformScopeStore()
const issueStore = useQualityIssueStore()

const keyword = ref('')
const statusFilter = ref<'全部' | QualityStatus>('全部')
const historyVisible = ref(false)
const historyIssue = ref<QualityIssue | null>(null)
const createVisible = ref(false)

const createFormRef = ref<FormInstance>()
const createForm = reactive({
  projectId: '',
  sectionCode: '',
  code: '',
  title: '',
  level: '中' as '低' | '中' | '高' | '严重',
  owner: '',
  reporter: '系统管理员',
  deadline: '',
})

const createRules: FormRules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  sectionCode: [{ required: true, message: '请输入标段', trigger: 'blur' }],
  code: [{ required: true, message: '请输入问题编号', trigger: 'blur' }],
  title: [{ required: true, message: '请输入问题描述', trigger: 'blur' }],
  owner: [{ required: true, message: '请输入责任人', trigger: 'blur' }],
  deadline: [{ required: true, message: '请选择整改期限', trigger: 'change' }],
}

const scopedIssues = computed(() =>
  scopeStore.selectedProject
    ? issueStore.issues.filter((item) => item.projectId === scopeStore.selectedProject?.id)
    : issueStore.issues,
)

const tableIssues = computed(() => {
  const key = keyword.value.trim().toLowerCase()
  return scopedIssues.value.filter((item) => {
    const textMatch =
      !key ||
      [item.projectName, item.code, item.title, item.owner, item.sectionCode]
        .join('|')
        .toLowerCase()
        .includes(key)
    const statusMatch = statusFilter.value === '全部' || item.status === statusFilter.value
    return textMatch && statusMatch
  })
})

const overdueCount = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return scopedIssues.value.filter((item) => item.status !== '已闭环' && item.deadline < today).length
})

const projectOptions = computed(() => projectOrgStore.projects)

const historyEvents = computed(() =>
  historyIssue.value ? issueStore.listEvents(historyIssue.value.id) : [],
)

function levelTagType(level: string) {
  if (level === '严重') return 'danger'
  if (level === '高') return 'warning'
  return 'info'
}

function statusTagType(status: QualityStatus) {
  if (status === '已闭环') return 'success'
  if (status === '驳回') return 'danger'
  if (status === '待复验') return 'warning'
  return 'info'
}

function transition(issue: QualityIssue, toStatus: QualityStatus, note: string) {
  const ok = issueStore.transitionIssue(issue.id, toStatus, note, '系统管理员')
  if (!ok) {
    ElMessage.error('状态流转不合法')
    return
  }
  ElMessage.success(`已流转到${toStatus}`)
}

function openHistory(issue: QualityIssue) {
  historyIssue.value = issue
  historyVisible.value = true
}

function openCreate() {
  createForm.projectId = scopeStore.selectedProject?.id ?? ''
  createForm.sectionCode = ''
  createForm.code = ''
  createForm.title = ''
  createForm.level = '中'
  createForm.owner = ''
  createForm.reporter = '系统管理员'
  createForm.deadline = ''
  createVisible.value = true
}

async function submitCreate() {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return
  const project = projectOrgStore.projects.find((item) => item.id === createForm.projectId)
  if (!project) {
    ElMessage.error('项目不存在')
    return
  }
  issueStore.createIssue({
    projectId: createForm.projectId,
    projectName: project.name,
    sectionCode: createForm.sectionCode,
    code: createForm.code,
    title: createForm.title,
    level: createForm.level,
    owner: createForm.owner,
    reporter: createForm.reporter,
    deadline: createForm.deadline,
  })
  createVisible.value = false
  ElMessage.success('问题上报成功')
}

onMounted(() => {
  projectOrgStore.load()
  scopeStore.load()
  issueStore.load()
})
</script>

<template>
  <div class="quality-page">
    <el-alert :title="scopeStore.scopeTitle" type="info" :closable="false" show-icon />

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-label">待闭环问题</div>
          <div class="metric-value">{{ issueStore.openCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="metric-card">
          <div class="metric-label">闭环率</div>
          <div class="metric-value">{{ issueStore.closeRate }}%</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="metric-card danger-card">
          <div class="metric-label">超期问题</div>
          <div class="metric-value">{{ overdueCount }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <template #header>
        <div class="header-row">
          <span>质量问题上报与整改闭环</span>
          <el-button type="primary" @click="openCreate">上报问题</el-button>
        </div>
      </template>
      <el-row :gutter="12" class="filters">
        <el-col :span="10">
          <el-input v-model="keyword" clearable placeholder="搜索项目/编号/问题/负责人" />
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" class="full-width">
            <el-option label="全部状态" value="全部" />
            <el-option label="已上报" value="已上报" />
            <el-option label="整改中" value="整改中" />
            <el-option label="待复验" value="待复验" />
            <el-option label="已闭环" value="已闭环" />
            <el-option label="驳回" value="驳回" />
          </el-select>
        </el-col>
      </el-row>

      <el-table :data="tableIssues" stripe>
        <el-table-column prop="projectName" label="项目" min-width="180" />
        <el-table-column prop="sectionCode" label="标段" width="90" />
        <el-table-column prop="code" label="问题编号" width="130" />
        <el-table-column prop="title" label="问题描述" min-width="220" />
        <el-table-column prop="level" label="等级" width="90">
          <template #default="{ row }">
            <el-tag :type="levelTagType(row.level)">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner" label="责任人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="整改期限" width="120" />
        <el-table-column label="操作" width="290" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="issueStore.canTransition(row.status, '整改中')"
              link
              type="primary"
              @click="transition(row, '整改中', '进入整改')"
            >
              转整改
            </el-button>
            <el-button
              v-if="issueStore.canTransition(row.status, '待复验')"
              link
              type="warning"
              @click="transition(row, '待复验', '提交复验')"
            >
              提交复验
            </el-button>
            <el-button
              v-if="issueStore.canTransition(row.status, '已闭环')"
              link
              type="success"
              @click="transition(row, '已闭环', '复验通过')"
            >
              闭环
            </el-button>
            <el-button
              v-if="issueStore.canTransition(row.status, '驳回')"
              link
              type="danger"
              @click="transition(row, '驳回', '复验未通过')"
            >
              驳回
            </el-button>
            <el-button link @click="openHistory(row)">记录</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createVisible" title="质量问题上报" width="560px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="92px">
        <el-form-item label="项目" prop="projectId">
          <el-select v-model="createForm.projectId" class="full-width">
            <el-option
              v-for="item in projectOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标段" prop="sectionCode">
          <el-input v-model="createForm.sectionCode" placeholder="例如 A1" />
        </el-form-item>
        <el-form-item label="问题编号" prop="code">
          <el-input v-model="createForm.code" placeholder="例如 Q-2026-004" />
        </el-form-item>
        <el-form-item label="问题描述" prop="title">
          <el-input v-model="createForm.title" type="textarea" />
        </el-form-item>
        <el-form-item label="等级">
          <el-segmented
            v-model="createForm.level"
            :options="[
              { label: '低', value: '低' },
              { label: '中', value: '中' },
              { label: '高', value: '高' },
              { label: '严重', value: '严重' },
            ]"
          />
        </el-form-item>
        <el-form-item label="责任人" prop="owner">
          <el-input v-model="createForm.owner" />
        </el-form-item>
        <el-form-item label="整改期限" prop="deadline">
          <el-date-picker
            v-model="createForm.deadline"
            value-format="YYYY-MM-DD"
            type="date"
            class="full-width"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">提交</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="historyVisible" title="流转记录" size="460px">
      <el-timeline v-if="historyIssue">
        <el-timeline-item
          v-for="item in historyEvents"
          :key="item.id"
          :timestamp="item.at"
          :type="item.toStatus === '已闭环' ? 'success' : item.toStatus === '驳回' ? 'danger' : 'primary'"
        >
          <div>{{ item.fromStatus ? `${item.fromStatus} -> ${item.toStatus}` : item.toStatus }}</div>
          <div class="event-note">{{ item.note }} / {{ item.actor }}</div>
        </el-timeline-item>
      </el-timeline>
    </el-drawer>
  </div>
</template>

<style scoped>
.quality-page {
  display: grid;
  gap: 16px;
}

.metric-card {
  border: 1px solid #d9e2ec;
}

.danger-card {
  border-color: #f8d7da;
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

.event-note {
  color: #627d98;
}
</style>
