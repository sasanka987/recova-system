import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  IconButton,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  LinearProgress,
  Alert
} from '@mui/material';
import {
  CloudUpload,
  Refresh,
  CheckCircle,
  Error,
  PlayArrow,
  Visibility
} from '@mui/icons-material';
import { importService } from '../../services/import';

const ImportList = () => {
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadDialog, setUploadDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadForm, setUploadForm] = useState({
    bank_name: '',
    operation_type: 'CREDIT_CARD',
    import_period: ''
  });
  const [alert, setAlert] = useState({ show: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    setLoading(true);
    try {
      const response = await importService.getBatches();
      setBatches(response.data);
    } catch (error) {
      showAlert('Failed to fetch import batches', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !uploadForm.bank_name || !uploadForm.import_period) {
      showAlert('Please fill all required fields', 'error');
      return;
    }

    try {
      const response = await importService.uploadFile(
        selectedFile,
        uploadForm.bank_name,
        uploadForm.operation_type,
        uploadForm.import_period
      );

      showAlert('File uploaded successfully', 'success');
      setUploadDialog(false);
      resetUploadForm();
      fetchBatches();

      // Auto-validate after upload
      if (response.data.batch_id) {
        handleValidate(response.data.batch_id);
      }
    } catch (error) {
      showAlert('Upload failed: ' + (error.response?.data?.detail || 'Unknown error'), 'error');
    }
  };

  const handleValidate = async (batchId) => {
    try {
      await importService.validateBatch(batchId);
      showAlert('Validation started', 'info');
      // Poll for status updates
      setTimeout(() => fetchBatches(), 2000);
    } catch (error) {
      showAlert('Validation failed', 'error');
    }
  };

  const handleProcess = async (batchId) => {
    try {
      await importService.processBatch(batchId);
      showAlert('Processing started', 'info');
      // Poll for status updates
      setTimeout(() => fetchBatches(), 2000);
    } catch (error) {
      showAlert('Processing failed', 'error');
    }
  };

  const resetUploadForm = () => {
    setSelectedFile(null);
    setUploadForm({
      bank_name: '',
      operation_type: 'CREDIT_CARD',
      import_period: ''
    });
  };

  const showAlert = (message, severity) => {
    setAlert({ show: true, message, severity });
    setTimeout(() => setAlert({ show: false, message: '', severity: 'success' }), 5000);
  };

  const getStatusChip = (status) => {
    const config = {
      UPLOADED: { color: 'default', icon: <CloudUpload /> },
      VALIDATING: { color: 'info', icon: <Refresh /> },
      VALIDATED: { color: 'primary', icon: <CheckCircle /> },
      IMPORTING: { color: 'warning', icon: <Refresh /> },
      COMPLETED: { color: 'success', icon: <CheckCircle /> },
      FAILED: { color: 'error', icon: <Error /> }
    };

    const { color, icon } = config[status] || { color: 'default', icon: null };

    return (
      <Chip
        label={status}
        color={color}
        size="small"
        icon={icon}
      />
    );
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Import Management</Typography>
        <Button
          variant="contained"
          startIcon={<CloudUpload />}
          onClick={() => setUploadDialog(true)}
        >
          Upload New Import
        </Button>
      </Box>

      {alert.show && (
        <Alert severity={alert.severity} sx={{ mb: 2 }}>
          {alert.message}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Batch Name</TableCell>
              <TableCell>Bank</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Period</TableCell>
              <TableCell>Total Records</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {batches.map((batch) => (
              <TableRow key={batch.id}>
                <TableCell>{batch.batch_name}</TableCell>
                <TableCell>{batch.bank_name}</TableCell>
                <TableCell>{batch.operation_type}</TableCell>
                <TableCell>{batch.import_period}</TableCell>
                <TableCell>{batch.total_records}</TableCell>
                <TableCell>{getStatusChip(batch.status)}</TableCell>
                <TableCell>
                  {batch.status === 'UPLOADED' && (
                    <IconButton
                      size="small"
                      onClick={() => handleValidate(batch.id)}
                      title="Validate"
                    >
                      <PlayArrow />
                    </IconButton>
                  )}
                  {batch.status === 'VALIDATED' && (
                    <IconButton
                      size="small"
                      onClick={() => handleProcess(batch.id)}
                      title="Process"
                    >
                      <PlayArrow />
                    </IconButton>
                  )}
                  <IconButton size="small" title="View Details">
                    <Visibility />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Upload Dialog */}
      <Dialog open={uploadDialog} onClose={() => setUploadDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Import File</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Bank Name"
            value={uploadForm.bank_name}
            onChange={(e) => setUploadForm({ ...uploadForm, bank_name: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            select
            label="Operation Type"
            value={uploadForm.operation_type}
            onChange={(e) => setUploadForm({ ...uploadForm, operation_type: e.target.value })}
            margin="normal"
            required
          >
            <MenuItem value="CREDIT_CARD">Credit Card</MenuItem>
            <MenuItem value="LOAN">Loan</MenuItem>
            <MenuItem value="LEASING">Leasing</MenuItem>
            <MenuItem value="PAYMENT">Payment</MenuItem>
          </TextField>
          <TextField
            fullWidth
            label="Import Period"
            placeholder="e.g., August 2025"
            value={uploadForm.import_period}
            onChange={(e) => setUploadForm({ ...uploadForm, import_period: e.target.value })}
            margin="normal"
            required
          />
          <Button
            variant="outlined"
            component="label"
            fullWidth
            sx={{ mt: 2 }}
          >
            {selectedFile ? selectedFile.name : 'Select Excel File'}
            <input
              type="file"
              hidden
              accept=".xlsx,.xls"
              onChange={(e) => setSelectedFile(e.target.files[0])}
            />
          </Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialog(false)}>Cancel</Button>
          <Button onClick={handleUpload} variant="contained">
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ImportList;