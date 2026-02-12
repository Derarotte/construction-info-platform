<template>
  <el-card shadow="never">
    <template #header>AI 辅助中心</template>
    <el-alert
      title="当前为本地演示模式，二期可接入 FastAPI + 大模型服务。"
      type="info"
      :closable="false"
      show-icon
    />
    <el-row :gutter="16" class="cards">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="ai-title">周报自动生成</div>
          <p class="ai-desc">汇总进度、质量、隐患数据后生成项目周报草稿。</p>
          <el-button type="primary" link>生成示例</el-button>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="ai-title">日志摘要</div>
          <p class="ai-desc">将班组日志压缩成可审阅摘要并提取重点事件。</p>
          <el-button type="primary" link>查看模板</el-button>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="ai-title">风险异常提示</div>
          <p class="ai-desc">对延期、质量超阈值、隐患滞留进行预警排序。</p>
          <el-button type="primary" link>预警规则</el-button>
        </el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<style scoped>
.cards {
  margin-top: 16px;
}

.ai-title {
  font-size: 16px;
  font-weight: 600;
  color: #102a43;
}

.ai-desc {
  min-height: 42px;
  color: #627d98;
}
</style>
