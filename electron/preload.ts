import { contextBridge } from 'electron'

contextBridge.exposeInMainWorld('platformInfo', {
  env: process.env.NODE_ENV ?? 'production',
  desktop: true,
})
