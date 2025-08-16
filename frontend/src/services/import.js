import api from './api';

export const importService = {
  uploadFile: async (file, bankName, operationType, importPeriod) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('bank_name', bankName);
    formData.append('operation_type', operationType);
    formData.append('import_period', importPeriod);

    return await api.post('/imports/upload', formData);
  },

  validateBatch: async (batchId) => {
    return await api.post(`/imports/validate/${batchId}`);
  },

  processBatch: async (batchId) => {
    return await api.post(`/imports/process/${batchId}`);
  },

  getBatches: async () => {
    return await api.get('/imports/batches');
  },

  getBatchStatus: async (batchId) => {
    return await api.get(`/imports/status/${batchId}`);
  },

  getBatchErrors: async (batchId) => {
    return await api.get(`/imports/batch/${batchId}/errors`);
  },

  downloadTemplate: async (operationType) => {
    const response = await api.get(`/templates/${operationType}/download`, {
      responseType: 'blob'
    });
    return response.data;
  }
};