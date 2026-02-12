# 施工信息化一体化平台（Web + Desktop）

一期 MVP 已完成可运行骨架，技术栈为 Electron + Vue3 + TypeScript。

## 本地运行

```bash
npm install
npm run dev
```

启动后会同时打开 Vite 页面与 Electron 桌面窗口。

## 打包

```bash
npm run build:win
```

产物输出在 `release/`。

## 一期模块范围

- 项目与组织管理（项目、标段、工区）
- 质量管理（问题上报、整改闭环）
- 资料管理（上传、分类、版本）
- GIS 工点展示（当前为占位，二期接入真实地图服务）
- 基础看板（延期率、闭环率、隐患处理时长）
- AI 辅助入口（周报、日志摘要、风险提示）

## 后续迭代建议

1. 接入 FastAPI + PostgreSQL/PostGIS + Redis 后端。
2. 将当前页面示例数据替换为完整 CRUD 与审批流程。
3. 接入对象存储与分片上传，完善资料中心。
4. 接入地图服务与空间查询。
5. 接入大模型服务，形成可运营的 AI 助理能力。
