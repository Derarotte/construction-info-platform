<template>
  <el-row :gutter="16">
    <el-col :span="16">
      <el-card shadow="never" class="map-card">
        <template #header>GIS 工点分层展示（MVP 占位）</template>
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
          <el-timeline-item type="success" timestamp="正常推进">江北 A1 基础施工</el-timeline-item>
          <el-timeline-item type="warning" timestamp="风险关注">城南 B2 进度偏慢</el-timeline-item>
          <el-timeline-item type="danger" timestamp="异常处理">临港 C3 质量复检中</el-timeline-item>
        </el-timeline>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.map-card {
  min-height: 420px;
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
