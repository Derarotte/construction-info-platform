<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useProjectOrgStore } from '../stores/projectOrg'
import { usePlatformScopeStore } from '../stores/platformScope'

const projectOrgStore = useProjectOrgStore()
const scopeStore = usePlatformScopeStore()

const timelineItems = computed(() =>
  (scopeStore.selectedProject ? [scopeStore.selectedProject] : projectOrgStore.projects).flatMap((project) =>
    project.sections.flatMap((section) =>
      section.workAreas.map((area) => ({
        project: project.name,
        label: `${section.code} ${area.name}`,
        status: area.status,
      })),
    ),
  ),
)

onMounted(() => {
  projectOrgStore.load()
  scopeStore.load()
})
</script>

<template>
  <el-row :gutter="16">
    <el-col :span="16">
      <el-card shadow="never" class="map-card">
        <template #header>GIS 工点分层展示（MVP 占位）</template>
        <el-alert :title="scopeStore.scopeTitle" type="info" :closable="false" show-icon class="scope-alert" />
        <div class="map-placeholder">
          <el-icon size="26"><LocationInformation /></el-icon>
          <p>二期接入 Mapbox/ArcGIS/PostGIS 后替换为真实地图</p>
        </div>
      </el-card>
    </el-col>
    <el-col :span="8">
      <el-card shadow="never">
        <template #header>工点状态图例</template>
        <el-timeline>
          <el-timeline-item
            v-for="item in timelineItems"
            :key="`${item.project}-${item.label}`"
            :type="item.status === '正常' ? 'success' : item.status === '关注' ? 'warning' : 'danger'"
            :timestamp="item.project"
          >
            {{ item.label }}
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.map-card {
  min-height: 420px;
}

.scope-alert {
  margin-bottom: 12px;
}

.map-placeholder {
  height: 340px;
  display: grid;
  place-items: center;
  text-align: center;
  color: #486581;
  border: 1px dashed #bcccdc;
  border-radius: 10px;
  background: linear-gradient(135deg, #f0f4f8 0%, #e4ecf4 100%);
}
</style>
