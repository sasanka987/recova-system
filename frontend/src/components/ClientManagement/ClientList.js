// components/ClientManagement/ClientList.js
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
  Alert,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Add,
  Edit,
  Visibility,
  Business,
  TrendingUp,
  People
} from '@mui/icons-material';

const ClientList = () => {
  const [clients, setClients] = useState([]);
  const [clientsWithStats, setClientsWithStats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', severity: 'success' });

  const [newClient, setNewClient] = useState({
    client_code: '',
    client_name: '',
    client_type: 'BANK',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    website: '',
    is_active: true
  });

  useEffect(() => {
    fetchClients();
    fetchClientsWithStats();
  }, []);

  const fetchClients = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/clients/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setClients(data);
      }
    } catch (error) {
      showAlert('Failed to fetch clients', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchClientsWithStats = async () => {
    try {
      const response = await fetch('/api/v1/clients/with-stats', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setClientsWithStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch client statistics:', error);
    }
  };

  const handleCreateClient = async () => {
    try {
      const response = await fetch('/api/v1/clients/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newClient)
      });

      if (response.ok) {
        showAlert('Client created successfully', 'success');
        setShowCreateDialog(false);
        resetForm();
        fetchClients();
        fetchClientsWithStats();
      } else {
        const error = await response.json();
        showAlert(error.detail || 'Failed to create client', 'error');
      }
    } catch (error) {
      showAlert('Network error occurred', 'error');
    }
  };

  const handleEditClient = async () => {
    try {
      const response = await fetch(`/api/v1/clients/${selectedClient.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(selectedClient)
      });

      if (response.ok) {
        showAlert('Client updated successfully', 'success');
        setShowEditDialog(false);
        setSelectedClient(null);
        fetchClients();
        fetchClientsWithStats();
      } else {
        const error = await response.json();
        showAlert(error.detail || 'Failed to update client', 'error');
      }
    } catch (error) {
      showAlert('Network error occurred', 'error');
    }
  };

  const resetForm = () => {
    setNewClient({
      client_code: '',
      client_name: '',
      client_type: 'BANK',
      contact_person: '',
      contact_email: '',
      contact_phone: '',
      address: '',
      website: '',
      is_active: true
    });
  };

  const showAlert = (message, severity) => {
    setAlert({ show: true, message, severity });
    setTimeout(() => setAlert({ show: false, message: '', severity: 'success' }), 5000);
  };

  const getClientTypeColor = (type) => {
    const colors = {
      'BANK': 'primary',
      'NBFI': 'secondary',
      'LEASING': 'info',
      'FINANCE': 'warning',
      'OTHER': 'default'
    };
    return colors[type] || 'default';
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Client Management</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setShowCreateDialog(true)}
        >
          Add New Client
        </Button>
      </Box>

      {alert.show && (
        <Alert severity={alert.severity} sx={{ mb: 2 }}>
          {alert.message}
        </Alert>
      )}

      {/* Client Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {clientsWithStats.slice(0, 4).map((client) => (
          <Grid item xs={12} sm={6} md={3} key={client.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="h6">
                      {client.client_code}
                    </Typography>
                    <Typography variant="h6" component="div">
                      {client.client_name}
                    </Typography>
                    <Typography variant="body2">
                      {client.customer_count} customers
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      LKR {client.total_outstanding?.toLocaleString() || '0'}
                    </Typography>
                  </Box>
                  <Box sx={{ color: 'primary.main' }}>
                    <Business fontSize="large" />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Clients Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Client Code</TableCell>
              <TableCell>Client Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Contact Person</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {clients.map((client) => (
              <TableRow key={client.id}>
                <TableCell>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    {client.client_code}
                  </Typography>
                </TableCell>
                <TableCell>{client.client_name}</TableCell>
                <TableCell>
                  <Chip
                    label={client.client_type}
                    color={getClientTypeColor(client.client_type)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{client.contact_person || '-'}</TableCell>
                <TableCell>{client.contact_email || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={client.is_active ? 'Active' : 'Inactive'}
                    color={client.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => {
                      setSelectedClient(client);
                      setShowEditDialog(true);
                    }}
                    title="Edit Client"
                  >
                    <Edit />
                  </IconButton>
                  <IconButton size="small" title="View Details">
                    <Visibility />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create Client Dialog */}
      <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Client</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Client Code"
                value={newClient.client_code}
                onChange={(e) => setNewClient({ ...newClient, client_code: e.target.value.toUpperCase() })}
                placeholder="e.g., SEYLAN, COMBANK"
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Client Type"
                value={newClient.client_type}
                onChange={(e) => setNewClient({ ...newClient, client_type: e.target.value })}
                required
              >
                <MenuItem value="BANK">Bank</MenuItem>
                <MenuItem value="NBFI">NBFI</MenuItem>
                {/*<MenuItem value="LEASING">Leasing Company</MenuItem>*/}
                {/*<MenuItem value="FINANCE">Finance Company</MenuItem>*/}
                <MenuItem value="OTHER">Other</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Client Name"
                value={newClient.client_name}
                onChange={(e) => setNewClient({ ...newClient, client_name: e.target.value })}
                placeholder="e.g., Seylan Bank PLC"
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Person"
                value={newClient.contact_person}
                onChange={(e) => setNewClient({ ...newClient, contact_person: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Email"
                type="email"
                value={newClient.contact_email}
                onChange={(e) => setNewClient({ ...newClient, contact_email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Phone"
                value={newClient.contact_phone}
                onChange={(e) => setNewClient({ ...newClient, contact_phone: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Website"
                value={newClient.website}
                onChange={(e) => setNewClient({ ...newClient, website: e.target.value })}
                placeholder="https://www.example.com"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                multiline
                rows={3}
                value={newClient.address}
                onChange={(e) => setNewClient({ ...newClient, address: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateClient} variant="contained">
            Create Client
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Client Dialog */}
      <Dialog open={showEditDialog} onClose={() => setShowEditDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Client</DialogTitle>
        <DialogContent>
          {selectedClient && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Client Code"
                  value={selectedClient.client_code}
                  onChange={(e) => setSelectedClient({ ...selectedClient, client_code: e.target.value.toUpperCase() })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Client Type"
                  value={selectedClient.client_type}
                  onChange={(e) => setSelectedClient({ ...selectedClient, client_type: e.target.value })}
                  required
                >
                  <MenuItem value="BANK">Bank</MenuItem>
                  <MenuItem value="NBFI">NBFI</MenuItem>
                  <MenuItem value="LEASING">Leasing Company</MenuItem>
                  <MenuItem value="FINANCE">Finance Company</MenuItem>
                  <MenuItem value="OTHER">Other</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Client Name"
                  value={selectedClient.client_name}
                  onChange={(e) => setSelectedClient({ ...selectedClient, client_name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Contact Person"
                  value={selectedClient.contact_person || ''}
                  onChange={(e) => setSelectedClient({ ...selectedClient, contact_person: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Contact Email"
                  type="email"
                  value={selectedClient.contact_email || ''}
                  onChange={(e) => setSelectedClient({ ...selectedClient, contact_email: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Contact Phone"
                  value={selectedClient.contact_phone || ''}
                  onChange={(e) => setSelectedClient({ ...selectedClient, contact_phone: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Website"
                  value={selectedClient.website || ''}
                  onChange={(e) => setSelectedClient({ ...selectedClient, website: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Address"
                  multiline
                  rows={3}
                  value={selectedClient.address || ''}
                  onChange={(e) => setSelectedClient({ ...selectedClient, address: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Status"
                  value={selectedClient.is_active}
                  onChange={(e) => setSelectedClient({ ...selectedClient, is_active: e.target.value === 'true' })}
                >
                  <MenuItem value={true}>Active</MenuItem>
                  <MenuItem value={false}>Inactive</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEditDialog(false)}>Cancel</Button>
          <Button onClick={handleEditClient} variant="contained">
            Update Client
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ClientList;

// components/ImportManagement/ImportUpload.js - UPDATED VERSION
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  MenuItem,
  Button,
  Alert,
  Grid,
  LinearProgress,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { CloudUpload, Description, CheckCircle } from '@mui/icons-material';

const ImportUpload = ({ onUploadComplete }) => {
  const [clients, setClients] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadForm, setUploadForm] = useState({
    client_id: '',
    operation_type: 'CREDIT_CARD',
    import_period: ''
  });
  const [uploading, setUploading] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', severity: 'success' });
  const [activeStep, setActiveStep] = useState(0);

  const steps = ['Select Client & Type', 'Upload File', 'Process Import'];

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await fetch('/api/v1/clients/?active_only=true', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setClients(data);
      }
    } catch (error) {
      showAlert('Failed to fetch clients', 'error');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !uploadForm.client_id || !uploadForm.import_period) {
      showAlert('Please fill all required fields and select a file', 'error');
      return;
    }

    setUploading(true);
    setActiveStep(1);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('client_id', uploadForm.client_id);
    formData.append('operation_type', uploadForm.operation_type);
    formData.append('import_period', uploadForm.import_period);

    try {
      const response = await fetch('/api/v1/imports/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setActiveStep(2);
        showAlert('File uploaded successfully! Starting validation...', 'success');

        // Auto-start validation
        setTimeout(async () => {
          try {
            await fetch(`/api/v1/imports/validate/${result.batch_id}`, {
              method: 'POST',
              headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            showAlert('Import process completed successfully!', 'success');
            if (onUploadComplete) {
              onUploadComplete(result.batch_id);
            }
          } catch (error) {
            showAlert('Validation failed', 'error');
          }
        }, 2000);

        resetForm();
      } else {
        const error = await response.json();
        showAlert(error.detail || 'Upload failed', 'error');
      }
    } catch (error) {
      showAlert('Network error occurred', 'error');
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setUploadForm({
      client_id: '',
      operation_type: 'CREDIT_CARD',
      import_period: ''
    });
    setActiveStep(0);
  };

  const showAlert = (message, severity) => {
    setAlert({ show: true, message, severity });
    setTimeout(() => setAlert({ show: false, message: '', severity: 'success' }), 5000);
  };

  const downloadTemplate = async () => {
    try {
      const response = await fetch(`/api/v1/templates/${uploadForm.operation_type.toLowerCase()}/download`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `RECOVA_${uploadForm.operation_type}_Template.xlsx`;
        a.click();
        window.URL.revokeObjectURL(url);
        showAlert('Template downloaded successfully', 'success');
      }
    } catch (error) {
      showAlert('Failed to download template', 'error');
    }
  };

  const selectedClient = clients.find(c => c.id === parseInt(uploadForm.client_id));

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Import Data
      </Typography>

      {alert.show && (
        <Alert severity={alert.severity} sx={{ mb: 2 }}>
          {alert.message}
        </Alert>
      )}

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Paper sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Client Selection */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Select Client"
              value={uploadForm.client_id}
              onChange={(e) => setUploadForm({ ...uploadForm, client_id: e.target.value })}
              required
              disabled={uploading}
            >
              <MenuItem value="">Choose a client...</MenuItem>
              {clients.map((client) => (
                <MenuItem key={client.id} value={client.id}>
                  {client.client_code} - {client.client_name}
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          {/* Operation Type */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Operation Type"
              value={uploadForm.operation_type}
              onChange={(e) => setUploadForm({ ...uploadForm, operation_type: e.target.value })}
              required
              disabled={uploading}
            >
              <MenuItem value="CREDIT_CARD">Credit Card</MenuItem>
              <MenuItem value="LOAN">Loan</MenuItem>
              <MenuItem value="LEASING">Leasing</MenuItem>
              <MenuItem value="PAYMENT">Payment</MenuItem>
            </TextField>
          </Grid>

          {/* Import Period */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Import Period"
              placeholder="e.g., August 2025"
              value={uploadForm.import_period}
              onChange={(e) => setUploadForm({ ...uploadForm, import_period: e.target.value })}
              required
              disabled={uploading}
            />
          </Grid>

          {/* Template Download */}
          <Grid item xs={12} sm={6}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Description />}
              onClick={downloadTemplate}
              disabled={!uploadForm.operation_type || uploading}
              sx={{ height: '56px' }}
            >
              Download Template
            </Button>
          </Grid>

          {/* File Upload */}
          <Grid item xs={12}>
            <Box
              sx={{
                border: '2px dashed #ccc',
                borderRadius: 2,
                p: 3,
                textAlign: 'center',
                cursor: 'pointer',
                '&:hover': { borderColor: 'primary.main' }
              }}
              onClick={() => document.getElementById('file-upload').click()}
            >
              <input
                id="file-upload"
                type="file"
                accept=".xlsx,.xls"
                style={{ display: 'none' }}
                onChange={(e) => setSelectedFile(e.target.files[0])}
                disabled={uploading}
              />

              {selectedFile ? (
                <Box>
                  <CheckCircle color="success" sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="h6">{selectedFile.name}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="h6">
                    Click to select Excel file
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Supported formats: .xlsx, .xls
                  </Typography>
                </Box>
              )}
            </Box>
          </Grid>

          {/* Selected Client Info */}
          {selectedClient && (
            <Grid item xs={12}>
              <Alert severity="info">
                <Typography variant="subtitle2">
                  Selected Client: {selectedClient.client_code} - {selectedClient.client_name}
                </Typography>
                <Typography variant="body2">
                  Type: {selectedClient.client_type} | Operation: {uploadForm.operation_type}
                </Typography>
              </Alert>
            </Grid>
          )}

          {/* Upload Progress */}
          {uploading && (
            <Grid item xs={12}>
              <LinearProgress sx={{ mb: 2 }} />
              <Typography variant="body2" color="textSecondary" align="center">
                Processing import... Please wait.
              </Typography>
            </Grid>
          )}

          {/* Upload Button */}
          <Grid item xs={12}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handleUpload}
              disabled={!selectedFile || !uploadForm.client_id || !uploadForm.import_period || uploading}
              startIcon={<CloudUpload />}
            >
              {uploading ? 'Processing...' : 'Upload and Process'}
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default ImportUpload;

// Updated App.js to include client filter in customer management
// Add this to your existing customer management section:

const CustomerManagementWithClientFilter = () => {
  const [selectedClientId, setSelectedClientId] = useState('');
  const [clients, setClients] = useState([]);

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await fetch('/api/v1/clients/?active_only=true', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setClients(data);
      }
    } catch (error) {
      console.error('Failed to fetch clients:', error);
    }
  };

  // Update your existing customer fetch function to include client_id
  const fetchCustomersWithClient = async () => {
    const params = new URLSearchParams();
    if (customerFilters.search) params.append('search', customerFilters.search);
    if (selectedClientId) params.append('client_id', selectedClientId); // NEW CLIENT FILTER
    if (customerFilters.zone) params.append('zone', customerFilters.zone);
    // ... other filters

    const response = await fetch(`/api/v1/customers?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      const data = await response.json();
      setCustomers(data.customers || data); // Handle new response format
    }
  };

  // Add client filter to your existing filter section:
  return (
    <div className="filter-section">
      <h3>Search & Filter</h3>
      <div className="filter-grid">
        {/* NEW: Client Filter */}
        <select
          value={selectedClientId}
          onChange={(e) => {
            setSelectedClientId(e.target.value);
            // Auto-refresh customers when client changes
            setTimeout(fetchCustomersWithClient, 100);
          }}
        >
          <option value="">All Clients</option>
          {clients.map(client => (
            <option key={client.id} value={client.id}>
              {client.client_code} - {client.client_name}
            </option>
          ))}
        </select>

        {/* Existing filters... */}
        <input
          type="text"
          placeholder="Search by name, NIC, or contract..."
          value={customerFilters.search}
          onChange={(e) => setCustomerFilters({...customerFilters, search: e.target.value})}
        />
        {/* ... rest of existing filters */}
      </div>
    </div>
  );
};