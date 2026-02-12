<template>
  <el-card shadow="never">
    <template #header>质量问题上报与整改闭环</template>
    <el-table :data="issues" stripe>
      <el-table-column prop="code" label="问题编号" width="140" />
      <el-table-column prop="title" label="问题描述" min-width="220" />
      <el-table-column prop="level" label="等级" width="100">
        <template #default="{ row }">
          <el-tag :type="row.level === '高' ? 'danger' : 'warning'">{{ row.level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="owner" label="责任人" width="100" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.status === '已闭环' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="deadline" label="整改期限" width="140" />
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
const issues = [
  {
    code: 'Q-2026-001',
    title: '支护结构喷射厚度不足',
    level: '高',
    owner: '王工',
    status: '整改中',
    deadline: '2026-02-18',
  },
  {
    code: 'Q-2026-002',
    title: '钢筋绑扎间距偏差',
    level: '中',
    owner: '陈工',
    status: '已闭环',
    deadline: '2026-02-15',
  },
]
</script>
