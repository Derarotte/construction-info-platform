import type { TaskNode } from '../stores/planningCost'
import { getDataSourceMode, warnApiFallback } from './dataSource'

const STORAGE_KEY = 'cip_planning_cost_v1'

export interface PlanningCostRepository {
  loadTasks(): TaskNode[]
  saveTasks(tasks: TaskNode[]): void
}

class LocalPlanningCostRepository implements PlanningCostRepository {
  loadTasks() {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as TaskNode[]) : []
  }

  saveTasks(tasks: TaskNode[]) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks))
  }
}

export function createPlanningCostRepository(): PlanningCostRepository {
  const mode = getDataSourceMode()
  if (mode === 'api') {
    warnApiFallback('planning-cost')
  }
  return new LocalPlanningCostRepository()
}
