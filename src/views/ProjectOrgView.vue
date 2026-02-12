<template>
  <el-card shadow="never">
    <template #header>项目与组织管理</template>
    <el-row :gutter="16">
      <el-col :span="10">
        <el-form label-width="90px">
          <el-form-item label="项目名称">
            <el-input v-model="form.projectName" placeholder="请输入项目名称" />
          </el-form-item>
          <el-form-item label="标段编号">
            <el-input v-model="form.sectionCode" placeholder="例如 A1" />
          </el-form-item>
          <el-form-item label="工区名称">
            <el-input v-model="form.workArea" placeholder="请输入工区名称" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary">新增</el-button>
            <el-button>重置</el-button>
          </el-form-item>
        </el-form>
      </el-col>
      <el-col :span="14">
        <el-table :data="rows" stripe>
          <el-table-column prop="projectName" label="项目" />
          <el-table-column prop="sectionCode" label="标段" width="100" />
          <el-table-column prop="workArea" label="工区" />
          <el-table-column prop="manager" label="负责人" width="120" />
        </el-table>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  projectName: '',
  sectionCode: '',
  workArea: '',
})

const rows = [
  { projectName: '江北快速路项目', sectionCode: 'A1', workArea: '北段工区', manager: '赵工' },
  { projectName: '城南隧道项目', sectionCode: 'B2', workArea: '隧道西工区', manager: '李工' },
]
</script>
