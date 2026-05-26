import api from './index'

export const importCsv = () => api.post('/import/csv')
export const importCsvUpload = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/import/csv/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const getImportStatus = () => api.get('/import/status')
export const enrichAll = () => api.post('/import/enrich')
export const getEnrichStatus = () => api.get('/import/enrich/status')
