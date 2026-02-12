<template>
  <el-row :gutter="16">
    <el-col :span="8">
      <el-card shadow="hover">
        <div class="metric-title">延期率</div>
        <div class="metric-value">12.4%</div>
        <div class="metric-desc">本月较上月下降 1.8%</div>
      </el-card>
    </el-col>
    <el-col :span="8">
      <el-card shadow="hover">
        <div class="metric-title">问题闭环率</div>
        <div class="metric-value">87.6%</div>
        <div class="metric-desc">待整改 23 条</div>
      </el-card>
    </el-col>
    <el-col :span="8">
      <el-card shadow="hover">
        <div class="metric-title">隐患处理时长</div>
        <div class="metric-value">2.3 天</div>
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

<script setup lang="ts">
const tableData = [
  { project: '江北快速路项目', section: 'A1', progress: '68%', qualityIssue: 6, status: '正常' },
  { project: '城南隧道项目', section: 'B2', progress: '52%', qualityIssue: 11, status: '关注' },
  { project: '临港桥梁项目', section: 'C3', progress: '74%', qualityIssue: 4, status: '正常' },
]
</script>

<style scoped>
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
