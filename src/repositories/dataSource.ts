export type DataSourceMode = 'local' | 'api'

export function getDataSourceMode(): DataSourceMode {
  const mode = (import.meta.env.VITE_DATA_SOURCE ?? 'local').toString().toLowerCase()
  return mode === 'api' ? 'api' : 'local'
}

export function warnApiFallback(domain: string) {
  console.warn(`[repository:${domain}] API mode is not connected yet, fallback to local storage.`)
}
