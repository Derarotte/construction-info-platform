<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useProjectOrgStore } from '../stores/projectOrg'
import { usePlatformScopeStore } from '../stores/platformScope'

const projectOrgStore = useProjectOrgStore()
const scopeStore = usePlatformScopeStore()

const scopedProjects = computed(() =>
  scopeStore.selectedProject ? [scopeStore.selectedProject] : projectOrgStore.projects,
)

const metrics = computed(() => {
  const projects = scopedProjects.value
  const sections = projects.flatMap((item) => item.sections)
  const workAreas = sections.flatMap((item) => item.workAreas)
  const riskCount = workAreas.filter((item) => item.status !== '正常').length
  const closedRate = workAreas.length === 0 ? 100 : Math.max(65, 100 - riskCount * 12.5)
  const delayRate = projects.length === 0 ? 0 : Number((riskCount * 100 / Math.max(workAreas.length, 1)).toFixed(1))
  const hazardDays = Number((1.8 + riskCount * 0.6).toFixed(1))
  return {
    delayRate,
    closedRate: Number(closedRate.toFixed(1)),
    hazardDays,
  }
})

const tableData = computed(() =>
  scopedProjects.value.flatMap((project) =>
    project.sections.map((section) => {
      const risk = section.workAreas.filter((area) => area.status !== '正常').length
      return {
        project: project.name,
        section: section.code,
        progress: `${Math.max(45, 80 - risk * 8)}%`,
        qualityIssue: risk * 2 + 2,
        status: risk > 0 ? '关注' : '正常',
      }
    }),
  ),
)

onMounted(() => {
  projectOrgStore.load()
  scopeStore.load()
})
</script>

<template>
  <el-alert
    :title="scopeStore.scopeTitle"
    type="info"
    :closable="false"
    show-icon
    class="scope-alert"
  />
  <el-row :gutter="16">
    <el-col :span="8">
      <el-card shadow="hover">
        <div class="metric-title">延期率</div>
        <div class="metric-value">{{ metrics.delayRate }}%</div>
        <div class="metric-desc">由风险工区占比折算</div>
      </el-card>
    </el-col>
    <el-col :span="8">
      <el-card shadow="hover">
        <div class="metric-title">问题闭环率</div>
        <div class="metric-value">{{ metrics.closedRate }}%</div>
        <div class="metric-desc">风险数越高，闭环率越低</div>
      </el-card>
    </el-col>
    <el-col :span="8">
      <el-card shadow="hover">
        <div class="metric-title">隐患处理时长</div>
        <div class="metric-value">{{ metrics.hazardDays }} 天</div>
        <div class="metric-desc">目标阈值 3 天</div>
      </el-card>
    </el-col>
  </el-row>

  <el-card class="panel" shadow="never">
    <template #header>项目运行概览</template>
    <el-table :data="tableData" stripe>
      <el-table-column prop="project" label="项目" min-width="180" />
      <el-table-column prop="section" label="标段" width="120" />
      <el-table-column prop="progress" label="进度" width="120" />
      <el-table-column prop="qualityIssue" label="质量问题数" width="120" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.status === '正常' ? 'success' : 'warning'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<style scoped>
.scope-alert {
  margin-bottom: 16px;
}

.metric-title {
  font-size: 14px;
  color: #486581;
}

.metric-value {
  margin-top: 12px;
  font-size: 30px;
  font-weight: 700;
  color: #102a43;
}

.metric-desc {
  margin-top: 8px;
  color: #829ab1;
}

.panel {
  margin-top: 16px;
}
</style>
