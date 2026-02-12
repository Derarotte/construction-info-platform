/// <reference types="vite/client" />

interface PlatformInfo {
  env: string
  desktop: boolean
}

interface Window {
  platformInfo?: PlatformInfo
}
