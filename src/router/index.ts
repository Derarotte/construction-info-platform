import { createRouter, createWebHashHistory } from 'vue-router'
import PlatformLayout from '../views/PlatformLayout.vue'
import DashboardView from '../views/DashboardView.vue'
import ProjectOrgView from '../views/ProjectOrgView.vue'
import QualityView from '../views/QualityView.vue'
import DocumentView from '../views/DocumentView.vue'
import GisView from '../views/GisView.vue'
import AiAssistView from '../views/AiAssistView.vue'
import PlanningCostView from '../views/PlanningCostView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      component: PlatformLayout,
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', component: DashboardView, meta: { title: '运营看板' } },
        { path: 'project-org', component: ProjectOrgView, meta: { title: '项目与组织' } },
        { path: 'quality', component: QualityView, meta: { title: '质量管理' } },
        { path: 'planning-cost', component: PlanningCostView, meta: { title: '工期与造价' } },
        { path: 'documents', component: DocumentView, meta: { title: '资料管理' } },
        { path: 'gis', component: GisView, meta: { title: 'GIS 工点地图' } },
        { path: 'ai-assist', component: AiAssistView, meta: { title: 'AI 辅助中心' } },
      ],
    },
  ],
})

export default router
