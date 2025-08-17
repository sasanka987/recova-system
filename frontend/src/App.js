import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000/api/v1';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [batches, setBatches] = useState([]);

  // Customer Management States
  const [customers, setCustomers] = useState([]);
  const [customerStats, setCustomerStats] = useState(null);
  const [customerFilters, setCustomerFilters] = useState({
    search: '',
    zone: '',
    region: '',
    branch: '',
    minArrears: '',
    maxArrears: ''
  });
  const [filterOptions, setFilterOptions] = useState({
    zones: [],
    regions: [],
    branches: []
  });
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [showCustomerDetail, setShowCustomerDetail] = useState(false);
  const [customerLoading, setCustomerLoading] = useState(false);

  // Client Management States
  const [clients, setClients] = useState([]);
  const [showCreateClientDialog, setShowCreateClientDialog] = useState(false);
  const [showEditClientDialog, setShowEditClientDialog] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [newClient, setNewClient] = useState({
    client_code: '',
    client_name: '',
    client_type: 'BANK',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    is_active: true
  });

  // Abbreviations Management States
  const [abbreviations, setAbbreviations] = useState([]);
  const [showCreateAbbreviationDialog, setShowCreateAbbreviationDialog] = useState(false);
  const [showEditAbbreviationDialog, setShowEditAbbreviationDialog] = useState(false);
  const [showDeleteAbbreviationDialog, setShowDeleteAbbreviationDialog] = useState(false);
  const [selectedAbbreviation, setSelectedAbbreviation] = useState(null);
  const [abbreviationToDelete, setAbbreviationToDelete] = useState(null);
  const [newAbbreviation, setNewAbbreviation] = useState({
    abbreviation: '',
    description: '',
    detailed_description: '',
    is_active: true
  });

  // Director role check helper - FIXED with proper null checks
  const isDirector = user && user.role && user.role.code === "DIRECTOR";

  // Debug function to check user role
  const debugUserRole = () => {
    console.log('User object:', user);
    console.log('User role:', user?.role);
    console.log('User role code:', user?.role?.code);
    console.log('Is Director:', isDirector);
  };

  useEffect(() => {
    if (token) {
      fetchUserProfile();
    }
  }, [token]);

  useEffect(() => {
    if (currentView === 'imports' && isLoggedIn) {
      fetchBatches();
      fetchClients();
    }
    if (currentView === 'clients' && isLoggedIn) {
      fetchClients();
    }
    if (currentView === 'abbreviations' && isLoggedIn) {
      fetchAbbreviations();
    }
    if (currentView === 'customers' && isLoggedIn) {
      fetchCustomers();
      fetchCustomerStats();
      fetchFilterOptions();
    }
  }, [currentView, isLoggedIn]);

  // Debug user role when it changes
  useEffect(() => {
    if (user) {
      debugUserRole();
    }
  }, [user]);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data);
        setIsLoggedIn(true);
        setCurrentView('dashboard');
      } else {
        console.error('Profile fetch failed:', response.status);
        if (response.status === 401) {
          handleLogout();
        }
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData();
    formData.append('username', loginForm.email);
    formData.append('password', loginForm.password);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        setMessage('Login successful!');

        const profileResponse = await fetch(`${API_URL}/auth/me`, {
          headers: { 'Authorization': `Bearer ${data.access_token}` }
        });

        if (profileResponse.ok) {
          const userData = await profileResponse.json();
          setUser(userData);
          setIsLoggedIn(true);
          setCurrentView('dashboard');
          setMessage('');
        } else {
          setIsLoggedIn(true);
          setCurrentView('dashboard');
          setMessage('');
        }
      } else {
        setMessage(data.detail || 'Login failed');
      }
    } catch (error) {
      setMessage('Network error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsLoggedIn(false);
    setCurrentView('login');
  };

  const fetchBatches = async () => {
    try {
      const response = await fetch(`${API_URL}/imports/batches`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setBatches(data);
      }
    } catch (error) {
      console.error('Error fetching batches:', error);
    }
  };

  const fetchClients = async () => {
    try {
      const response = await fetch(`${API_URL}/clients/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setClients(data);
      }
    } catch (error) {
      console.error('Error fetching clients:', error);
    }
  };

  const fetchAbbreviations = async () => {
    try {
      const response = await fetch(`${API_URL}/abbreviations/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAbbreviations(data);
      }
    } catch (error) {
      setMessage('Failed to fetch abbreviations');
    }
  };

  const uploadFile = async (file, clientId, operationType, period) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('client_id', clientId);
    formData.append('operation_type', operationType);
    formData.append('import_period', period);

    try {
      const response = await fetch(`${API_URL}/imports/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (response.ok) {
        setMessage('File uploaded successfully!');
        fetchBatches();
      } else {
        const error = await response.json();
        setMessage(error.detail || 'Upload failed');
      }
    } catch (error) {
      setMessage('Network error');
    }
  };

  // Customer Management Functions
  const fetchCustomers = async () => {
    setCustomerLoading(true);
    try {
      const params = new URLSearchParams();
      if (customerFilters.search) params.append('search', customerFilters.search);
      if (customerFilters.zone) params.append('zone', customerFilters.zone);
      if (customerFilters.region) params.append('region', customerFilters.region);
      if (customerFilters.branch) params.append('branch', customerFilters.branch);
      if (customerFilters.minArrears) params.append('min_arrears', customerFilters.minArrears);
      if (customerFilters.maxArrears) params.append('max_arrears', customerFilters.maxArrears);

      const response = await fetch(`${API_URL}/customers?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();

        if (Array.isArray(data)) {
          setCustomers(data);
        } else if (data.customers && Array.isArray(data.customers)) {
          setCustomers(data.customers);
        } else {
          console.error('Unexpected API response format:', data);
          setCustomers([]);
          setMessage('Unexpected data format received from server');
        }
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Error fetching customers:', error);
      setMessage('Failed to fetch customers');
      setCustomers([]);
    } finally {
      setCustomerLoading(false);
    }
  };

  const fetchCustomerStats = async () => {
    try {
      const response = await fetch(`${API_URL}/customers/statistics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setCustomerStats(data);
      }
    } catch (error) {
      console.error('Error fetching customer statistics:', error);
    }
  };

  const fetchFilterOptions = async () => {
    try {
      const response = await fetch(`${API_URL}/customers/filters`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setFilterOptions(data);
      }
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const fetchCustomerDetail = async (customerId) => {
    try {
      const response = await fetch(`${API_URL}/customers/${customerId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedCustomer(data);
        setShowCustomerDetail(true);
      }
    } catch (error) {
      console.error('Error fetching customer detail:', error);
      setMessage('Failed to fetch customer details');
    }
  };

  const exportCustomers = async () => {
    try {
      const params = new URLSearchParams();
      if (customerFilters.search) params.append('search', customerFilters.search);
      if (customerFilters.zone) params.append('zone', customerFilters.zone);
      if (customerFilters.region) params.append('region', customerFilters.region);

      const response = await fetch(`${API_URL}/customers/export/csv?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `customers_export_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        setMessage('Customers exported successfully!');
      }
    } catch (error) {
      console.error('Error exporting customers:', error);
      setMessage('Failed to export customers');
    }
  };

  // Client Management Functions
  const handleCreateClient = async () => {
    try {
      const response = await fetch(`${API_URL}/clients/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newClient)
      });

      if (response.ok) {
        setMessage('Client created successfully!');
        setShowCreateClientDialog(false);
        resetClientForm();
        fetchClients();
      } else {
        const error = await response.json();
        setMessage(error.detail || 'Failed to create client');
      }
    } catch (error) {
      setMessage('Network error occurred');
    }
  };

  const handleEditClient = async () => {
    try {
      const response = await fetch(`${API_URL}/clients/${selectedClient.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(selectedClient)
      });

      if (response.ok) {
        setMessage('Client updated successfully!');
        setShowEditClientDialog(false);
        setSelectedClient(null);
        fetchClients();
      } else {
        const error = await response.json();
        setMessage(error.detail || 'Failed to update client');
      }
    } catch (error) {
      setMessage('Network error occurred');
    }
  };

  const resetClientForm = () => {
    setNewClient({
      client_code: '',
      client_name: '',
      client_type: 'BANK',
      contact_person: '',
      contact_email: '',
      contact_phone: '',
      address: '',
      is_active: true
    });
  };

  // Abbreviations Management Functions
  const handleCreateAbbreviation = async () => {
    try {
      const response = await fetch(`${API_URL}/abbreviations/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newAbbreviation)
      });

      if (response.ok) {
        setMessage('Abbreviation created successfully!');
        setShowCreateAbbreviationDialog(false);
        resetAbbreviationForm();
        fetchAbbreviations();
      } else {
        const error = await response.json();
        setMessage(error.detail || 'Failed to create abbreviation');
      }
    } catch (error) {
      setMessage('Network error occurred');
    }
  };

  const handleEditAbbreviation = async () => {
    try {
      const response = await fetch(`${API_URL}/abbreviations/${selectedAbbreviation.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(selectedAbbreviation)
      });

      if (response.ok) {
        setMessage('Abbreviation updated successfully!');
        setShowEditAbbreviationDialog(false);
        setSelectedAbbreviation(null);
        fetchAbbreviations();
      } else {
        const error = await response.json();
        setMessage(error.detail || 'Failed to update abbreviation');
      }
    } catch (error) {
      setMessage('Network error occurred');
    }
  };

  const handleDeleteAbbreviation = async () => {
    try {
      const response = await fetch(`${API_URL}/abbreviations/${abbreviationToDelete.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        setMessage('Abbreviation deleted successfully!');
        setShowDeleteAbbreviationDialog(false);
        setAbbreviationToDelete(null);
        fetchAbbreviations();
      } else {
        const error = await response.json();
        if (error.detail && error.detail.includes('remarks')) {
          setMessage(`Warning: ${error.detail}`);
        } else {
          setMessage(error.detail || 'Failed to delete abbreviation');
        }
      }
    } catch (error) {
      setMessage('Network error occurred');
    }
  };

  const toggleAbbreviationStatus = async (abbreviation) => {
    try {
      const endpoint = abbreviation.is_active ? 'deactivate' : 'activate';
      const response = await fetch(`${API_URL}/abbreviations/${abbreviation.id}/${endpoint}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        setMessage(`Abbreviation ${abbreviation.is_active ? 'deactivated' : 'activated'} successfully!`);
        fetchAbbreviations();
      } else {
        setMessage('Failed to update abbreviation status');
      }
    } catch (error) {
      setMessage('Network error occurred');
    }
  };

  const resetAbbreviationForm = () => {
    setNewAbbreviation({
      abbreviation: '',
      description: '',
      detailed_description: '',
      is_active: true
    });
  };

  // Login View
  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-box">
          <h1>RECOVA</h1>
          <p>Recovery Redefined</p>
          {message && <div className="message">{message}</div>}
          <form onSubmit={handleLogin}>
            <input
              type="email"
              placeholder="Email"
              value={loginForm.email}
              onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={loginForm.password}
              onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Main App
  return (
    <div className="app">
      <header className="app-header">
        <h1>RECOVA</h1>
        <div className="user-info">
          <span>Welcome, {user?.first_name} {user?.last_name}</span>
          <span style={{fontSize: '0.8rem', marginLeft: '1rem', opacity: 0.8}}>
            Role: {user?.role?.name || 'Loading...'}
          </span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <div className="app-body">
        <nav className="sidebar">
          <ul>
            <li onClick={() => setCurrentView('dashboard')}>Dashboard</li>
            <li onClick={() => { setCurrentView('imports'); fetchBatches(); }}>Imports</li>
            <li onClick={() => setCurrentView('customers')}>Customers</li>
            <li onClick={() => setCurrentView('reports')}>Reports</li>
            <li onClick={() => setCurrentView('remarks')}>Remarks</li>
            {/* Always show Client Management - handle permission in content */}
            <li onClick={() => setCurrentView('clients')}>Client Management</li>
            {/* Always show Abbreviations - handle permission in content */}
            <li onClick={() => setCurrentView('abbreviations')}>Remark Abbreviations</li>
          </ul>
        </nav>

        <main className="main-content">
          {message && <div className="message">{message}</div>}

          {currentView === 'dashboard' && (
            <div>
              <h2>Dashboard</h2>
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Total Customers</h3>
                  <p>1,250</p>
                </div>
                <div className="stat-card">
                  <h3>Pending Imports</h3>
                  <p>3</p>
                </div>
                <div className="stat-card">
                  <h3>Completed Imports</h3>
                  <p>15</p>
                </div>
                <div className="stat-card">
                  <h3>Recent Payments</h3>
                  <p>45</p>
                </div>
              </div>

              {/* Debug Panel */}
              <div style={{marginTop: '2rem', padding: '1rem', background: '#f8f9fa', borderRadius: '8px'}}>
                <h4>Debug Information</h4>
                <p><strong>User Role:</strong> {user?.role?.name || 'Not loaded'}</p>
                <p><strong>Role Code:</strong> {user?.role?.code || 'Not loaded'}</p>
                <p><strong>Is Director:</strong> {isDirector ? 'Yes' : 'No'}</p>
                <p><strong>Current View:</strong> {currentView}</p>
              </div>
            </div>
          )}

          {currentView === 'imports' && (
            <div>
              <h2>Import Management</h2>
              <div className="upload-section">
                <h3>Upload New Import</h3>

                <select id="client-select" defaultValue="">
                  <option value="" disabled>Select Client...</option>
                  {clients.map(client => (
                    <option key={client.id} value={client.id}>
                      {client.client_code} - {client.client_name}
                    </option>
                  ))}
                </select>

                <input type="file" id="file-upload" accept=".xlsx,.xls" />

                <select id="operation-type">
                    <option value="CREDIT_CARD">Credit Card</option>
                    <option value="LOAN">Loan</option>
                    <option value="LEASING">Leasing</option>
                    <option value="PAYMENT">Payment</option>
                </select>

                <input type="text" id="import-period" placeholder="Import Period (e.g., August 2025)" />

                <button onClick={() => {
                    const file = document.getElementById('file-upload').files[0];
                    const clientId = document.getElementById('client-select').value;
                    const operationType = document.getElementById('operation-type').value;
                    const period = document.getElementById('import-period').value;
                    if (file && clientId && period) {
                      uploadFile(file, clientId, operationType, period);
                    } else {
                      setMessage('Please select client, file, and enter import period');
                    }
                  }}>Upload</button>
                </div>

              <table className="data-table">
                <thead>
                  <tr>
                    <th>Batch Name</th>
                    <th>Bank</th>
                    <th>Type</th>
                    <th>Period</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {batches.map(batch => (
                    <tr key={batch.id}>
                      <td>{batch.batch_name}</td>
                      <td>{batch.bank_name}</td>
                      <td>{batch.operation_type}</td>
                      <td>{batch.import_period}</td>
                      <td>
                        <span className={`status-badge status-${batch.status.toLowerCase()}`}>
                          {batch.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {currentView === 'customers' && (
            <div>
              <div className="header-section">
                <h2>Customer Management</h2>
                <button onClick={exportCustomers} className="export-btn">
                  Export to CSV
                </button>
              </div>

              {customerStats && (
                <div className="stats-grid">
                  <div className="stat-card">
                    <h3>Total Customers</h3>
                    <p>{customerStats.total_customers}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Current (0 days)</h3>
                    <p>{customerStats.arrears_breakdown.current}</p>
                  </div>
                  <div className="stat-card">
                    <h3>1-30 Days Arrears</h3>
                    <p className="warning">{customerStats.arrears_breakdown['1_30_days']}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Over 90 Days</h3>
                    <p className="danger">{customerStats.arrears_breakdown.over_90_days}</p>
                  </div>
                </div>
              )}

              <div className="filter-section">
                <h3>Search & Filter</h3>
                <div className="filter-grid">
                  <input
                    type="text"
                    placeholder="Search by name, NIC, or contract..."
                    value={customerFilters.search}
                    onChange={(e) => setCustomerFilters({...customerFilters, search: e.target.value})}
                    onKeyPress={(e) => e.key === 'Enter' && fetchCustomers()}
                  />

                  <select
                    value={customerFilters.zone}
                    onChange={(e) => setCustomerFilters({...customerFilters, zone: e.target.value})}
                  >
                    <option value="">All Zones</option>
                    {filterOptions.zones.map(zone => (
                      <option key={zone} value={zone}>{zone}</option>
                    ))}
                  </select>

                  <select
                    value={customerFilters.region}
                    onChange={(e) => setCustomerFilters({...customerFilters, region: e.target.value})}
                  >
                    <option value="">All Regions</option>
                    {filterOptions.regions.map(region => (
                      <option key={region} value={region}>{region}</option>
                    ))}
                  </select>

                  <select
                    value={customerFilters.branch}
                    onChange={(e) => setCustomerFilters({...customerFilters, branch: e.target.value})}
                  >
                    <option value="">All Branches</option>
                    {filterOptions.branches.map(branch => (
                      <option key={branch} value={branch}>{branch}</option>
                    ))}
                  </select>

                  <input
                    type="number"
                    placeholder="Min arrears days"
                    value={customerFilters.minArrears}
                    onChange={(e) => setCustomerFilters({...customerFilters, minArrears: e.target.value})}
                  />

                  <input
                    type="number"
                    placeholder="Max arrears days"
                    value={customerFilters.maxArrears}
                    onChange={(e) => setCustomerFilters({...customerFilters, maxArrears: e.target.value})}
                  />

                  <button onClick={fetchCustomers} className="search-btn">
                    Search
                  </button>

                  <button
                    onClick={() => {
                      setCustomerFilters({
                        search: '',
                        zone: '',
                        region: '',
                        branch: '',
                        minArrears: '',
                        maxArrears: ''
                      });
                      fetchCustomers();
                    }}
                    className="clear-btn"
                  >
                    Clear Filters
                  </button>
                </div>
              </div>

              <div className="table-container">
                {customerLoading ? (
                  <div className="loading">Loading customers...</div>
                ) : (
                  <table className="data-table">
                    <thead>
                      <tr>
                          <th>ID</th>
                          <th>Client Name</th>
                          <th>NIC</th>
                          <th>Contract Number</th>
                          <th>Zone</th>
                          <th>Region</th>
                          <th>Branch</th>
                          <th>Days in Arrears</th>
                          <th>Amount (LKR)</th>
                          <th>Contact</th>
                          <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                        {Array.isArray(customers) && customers.length > 0 ? (
                          customers.map(customer => (
                            <tr key={customer.id}>
                              <td>{customer.id}</td>
                              <td>{customer.client_name}</td>
                              <td>{customer.nic}</td>
                              <td>{customer.contract_number}</td>
                              <td>{customer.zone || '-'}</td>
                              <td>{customer.region || '-'}</td>
                              <td>{customer.branch_name || '-'}</td>
                              <td>
                                <span className={`arrears-badge ${
                                  customer.days_in_arrears === 0 ? 'current' :
                                  customer.days_in_arrears <= 30 ? 'warning' :
                                  customer.days_in_arrears <= 90 ? 'danger' : 'critical'
                                }`}>
                                  {customer.days_in_arrears || 0} days
                                </span>
                              </td>
                              <td>{customer.granted_amount ? customer.granted_amount.toLocaleString() : '-'}</td>
                              <td>{customer.customer_contact_number_1 || '-'}</td>
                              <td>
                                <button
                                  onClick={() => fetchCustomerDetail(customer.id)}
                                  className="view-btn"
                                >
                                  View
                                </button>
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="11" style={{textAlign: 'center', padding: '2rem'}}>
                              {customerLoading ? 'Loading...' : 'No customers found'}
                            </td>
                          </tr>
                        )}
                      </tbody>
                  </table>
                )}
              </div>

              {showCustomerDetail && selectedCustomer && (
                <div className="modal">
                  <div className="modal-content large">
                    <div className="modal-header">
                      <h3>Customer Details</h3>
                      <button
                        onClick={() => setShowCustomerDetail(false)}
                        className="close-btn"
                      >
                        ×
                      </button>
                    </div>

                    <div className="customer-detail">
                      <div className="detail-section">
                        <h4>Personal Information</h4>
                        <div className="detail-grid">
                          <div><strong>Name:</strong> {selectedCustomer.client_name}</div>
                          <div><strong>NIC:</strong> {selectedCustomer.nic}</div>
                          <div><strong>Contract:</strong> {selectedCustomer.contract_number}</div>
                          <div><strong>Address:</strong> {selectedCustomer.home_address || 'N/A'}</div>
                        </div>
                      </div>

                      <div className="detail-section">
                        <h4>Contact Information</h4>
                        <div className="detail-grid">
                          <div><strong>Primary:</strong> {selectedCustomer.customer_contact_number_1 || 'N/A'}</div>
                          <div><strong>Secondary:</strong> {selectedCustomer.customer_contact_number_2 || 'N/A'}</div>
                          <div><strong>Tertiary:</strong> {selectedCustomer.customer_contact_number_3 || 'N/A'}</div>
                        </div>
                      </div>

                      <div className="detail-section">
                        <h4>Employment Information</h4>
                        <div className="detail-grid">
                          <div><strong>Workplace:</strong> {selectedCustomer.work_place_name || 'N/A'}</div>
                          <div><strong>Designation:</strong> {selectedCustomer.designation || 'N/A'}</div>
                          <div><strong>Work Address:</strong> {selectedCustomer.work_place_address || 'N/A'}</div>
                          <div><strong>Work Contact:</strong> {selectedCustomer.work_place_contact_number_1 || 'N/A'}</div>
                        </div>
                      </div>

                      <div className="detail-section">
                        <h4>Financial Information</h4>
                        <div className="detail-grid">
                          <div><strong>Granted Amount:</strong> LKR {selectedCustomer.granted_amount?.toLocaleString() || 'N/A'}</div>
                          <div><strong>Days in Arrears:</strong> {selectedCustomer.days_in_arrears} days</div>
                          <div><strong>Last Payment:</strong> {selectedCustomer.last_payment_date || 'N/A'}</div>
                          <div><strong>Last Amount:</strong> LKR {selectedCustomer.last_payment_amount?.toLocaleString() || 'N/A'}</div>
                        </div>
                      </div>

                      {selectedCustomer.guarantor_1_name && (
                        <div className="detail-section">
                          <h4>Guarantor 1</h4>
                          <div className="detail-grid">
                            <div><strong>Name:</strong> {selectedCustomer.guarantor_1_name}</div>
                            <div><strong>NIC:</strong> {selectedCustomer.guarantor_1_nic || 'N/A'}</div>
                            <div><strong>Contact:</strong> {selectedCustomer.guarantor_1_contact_number_1 || 'N/A'}</div>
                            <div><strong>Address:</strong> {selectedCustomer.guarantor_1_address || 'N/A'}</div>
                          </div>
                        </div>
                      )}

                      {selectedCustomer.guarantor_2_name && (
                        <div className="detail-section">
                          <h4>Guarantor 2</h4>
                          <div className="detail-grid">
                            <div><strong>Name:</strong> {selectedCustomer.guarantor_2_name}</div>
                            <div><strong>NIC:</strong> {selectedCustomer.guarantor_2_nic || 'N/A'}</div>
                            <div><strong>Contact:</strong> {selectedCustomer.guarantor_2_contact_number_1 || 'N/A'}</div>
                            <div><strong>Address:</strong> {selectedCustomer.guarantor_2_address || 'N/A'}</div>
                          </div>
                        </div>
                      )}

                      <div className="detail-section">
                        <h4>Location & Branch</h4>
                        <div className="detail-grid">
                          <div><strong>Zone:</strong> {selectedCustomer.zone || 'N/A'}</div>
                          <div><strong>Region:</strong> {selectedCustomer.region || 'N/A'}</div>
                          <div><strong>Branch:</strong> {selectedCustomer.branch_name || 'N/A'}</div>
                          <div><strong>District:</strong> {selectedCustomer.district_name || 'N/A'}</div>
                          <div><strong>Postal Town:</strong> {selectedCustomer.postal_town || 'N/A'}</div>
                        </div>
                      </div>

                      {selectedCustomer.details && (
                        <div className="detail-section">
                          <h4>Additional Details</h4>
                          <p>{selectedCustomer.details}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {currentView === 'clients' && (
            <div>
              {!isDirector ? (
                <div style={{textAlign: 'center', padding: '3rem'}}>
                  <h2>Access Restricted</h2>
                  <p style={{color: '#666', fontSize: '1.1rem', marginBottom: '1rem'}}>
                    🔒 Client Management is only available to Directors
                  </p>
                  <p style={{color: '#888'}}>
                    Your current role: <strong>{user?.role?.name || 'Unknown'}</strong>
                  </p>
                  <p style={{color: '#888', fontSize: '0.9rem'}}>
                    Please contact your system administrator if you need access to this feature.
                  </p>
                </div>
              ) : (
                <div>
                  <div className="header-section">
                    <h2>Client Management</h2>
                    <button onClick={() => setShowCreateClientDialog(true)} className="export-btn">
                      Add New Client
                    </button>
                  </div>

                  <div className="table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Client Code</th>
                          <th>Client Name</th>
                          <th>Type</th>
                          <th>Contact Person</th>
                          <th>Email</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {clients.length === 0 ? (
                          <tr>
                            <td colSpan="7" style={{textAlign: 'center', padding: '2rem'}}>
                              No clients found
                            </td>
                          </tr>
                        ) : (
                          clients.map((client) => (
                            <tr key={client.id}>
                              <td style={{fontWeight: 'bold', color: '#667eea'}}>{client.client_code}</td>
                              <td>{client.client_name}</td>
                              <td>
                                <span className={`badge ${client.client_type === 'BANK' ? 'badge-primary' : 'badge-secondary'}`}>
                                  {client.client_type}
                                </span>
                              </td>
                              <td>{client.contact_person || '-'}</td>
                              <td>{client.contact_email || '-'}</td>
                              <td>
                                <span className={`badge ${client.is_active ? 'badge-success' : 'badge-inactive'}`}>
                                  {client.is_active ? 'Active' : 'Inactive'}
                                </span>
                              </td>
                              <td>
                                <button
                                  onClick={() => {
                                    setSelectedClient(client);
                                    setShowEditClientDialog(true);
                                  }}
                                  className="view-btn"
                                  style={{marginRight: '0.5rem'}}
                                >
                                  Edit
                                </button>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Create Client Modal */}
                  {showCreateClientDialog && (
                    <div className="modal">
                      <div className="modal-content">
                        <div className="modal-header">
                          <h3>Add New Client</h3>
                          <button onClick={() => setShowCreateClientDialog(false)} className="close-btn">×</button>
                        </div>
                        <div style={{padding: '1.5rem'}}>
                          <div className="form-grid">
                            <div>
                              <label>Client Code *</label>
                              <input
                                type="text"
                                value={newClient.client_code}
                                onChange={(e) => setNewClient({ ...newClient, client_code: e.target.value.toUpperCase() })}
                                placeholder="e.g., SEYLAN"
                                required
                              />
                            </div>
                            <div>
                              <label>Client Type *</label>
                              <select
                                value={newClient.client_type}
                                onChange={(e) => setNewClient({ ...newClient, client_type: e.target.value })}
                                required
                              >
                                <option value="BANK">Bank</option>
                                <option value="NBFI">NBFI</option>
                                <option value="OTHER">Other</option>
                              </select>
                            </div>
                            <div className="full-width">
                              <label>Client Name *</label>
                              <input
                                type="text"
                                value={newClient.client_name}
                                onChange={(e) => setNewClient({ ...newClient, client_name: e.target.value })}
                                placeholder="e.g., Seylan Bank PLC"
                                required
                              />
                            </div>
                            <div>
                              <label>Contact Person</label>
                              <input
                                type="text"
                                value={newClient.contact_person}
                                onChange={(e) => setNewClient({ ...newClient, contact_person: e.target.value })}
                                placeholder="Contact person name"
                              />
                            </div>
                            <div>
                              <label>Contact Email</label>
                              <input
                                type="email"
                                value={newClient.contact_email}
                                onChange={(e) => setNewClient({ ...newClient, contact_email: e.target.value })}
                                placeholder="email@example.com"
                              />
                            </div>
                            <div>
                              <label>Contact Phone</label>
                              <input
                                type="tel"
                                value={newClient.contact_phone}
                                onChange={(e) => setNewClient({ ...newClient, contact_phone: e.target.value })}
                                placeholder="+94 71 234 5678"
                              />
                            </div>
                            <div className="full-width">
                              <label>Address</label>
                              <textarea
                                value={newClient.address}
                                onChange={(e) => setNewClient({ ...newClient, address: e.target.value })}
                                placeholder="Full address"
                                rows="3"
                              />
                            </div>
                          </div>
                          <div style={{marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'flex-end'}}>
                            <button onClick={() => setShowCreateClientDialog(false)} className="clear-btn">
                              Cancel
                            </button>
                            <button
                              onClick={handleCreateClient}
                              className="search-btn"
                              disabled={!newClient.client_code || !newClient.client_name}
                            >
                              Create Client
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Edit Client Modal */}
                  {showEditClientDialog && selectedClient && (
                    <div className="modal">
                      <div className="modal-content">
                        <div className="modal-header">
                          <h3>Edit Client</h3>
                          <button onClick={() => setShowEditClientDialog(false)} className="close-btn">×</button>
                        </div>
                        <div style={{padding: '1.5rem'}}>
                          <div className="form-grid">
                            <div>
                              <label>Client Code *</label>
                              <input
                                type="text"
                                value={selectedClient.client_code}
                                onChange={(e) => setSelectedClient({ ...selectedClient, client_code: e.target.value.toUpperCase() })}
                                required
                              />
                            </div>
                            <div>
                              <label>Client Type *</label>
                              <select
                                value={selectedClient.client_type}
                                onChange={(e) => setSelectedClient({ ...selectedClient, client_type: e.target.value })}
                                required
                              >
                                <option value="BANK">Bank</option>
                                <option value="NBFI">NBFI</option>
                                <option value="OTHER">Other</option>
                              </select>
                            </div>
                            <div className="full-width">
                              <label>Client Name *</label>
                              <input
                                type="text"
                                value={selectedClient.client_name}
                                onChange={(e) => setSelectedClient({ ...selectedClient, client_name: e.target.value })}
                                required
                              />
                            </div>
                            <div>
                              <label>Contact Person</label>
                              <input
                                type="text"
                                value={selectedClient.contact_person || ''}
                                onChange={(e) => setSelectedClient({ ...selectedClient, contact_person: e.target.value })}
                              />
                            </div>
                            <div>
                              <label>Contact Email</label>
                              <input
                                type="email"
                                value={selectedClient.contact_email || ''}
                                onChange={(e) => setSelectedClient({ ...selectedClient, contact_email: e.target.value })}
                              />
                            </div>
                            <div>
                              <label>Contact Phone</label>
                              <input
                                type="tel"
                                value={selectedClient.contact_phone || ''}
                                onChange={(e) => setSelectedClient({ ...selectedClient, contact_phone: e.target.value })}
                              />
                            </div>
                            <div className="full-width">
                              <label>Address</label>
                              <textarea
                                value={selectedClient.address || ''}
                                onChange={(e) => setSelectedClient({ ...selectedClient, address: e.target.value })}
                                rows="3"
                              />
                            </div>
                            <div className="full-width">
                              <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                                <input
                                  type="checkbox"
                                  checked={selectedClient.is_active}
                                  onChange={(e) => setSelectedClient({ ...selectedClient, is_active: e.target.checked })}
                                />
                                Active
                              </label>
                            </div>
                          </div>
                          <div style={{marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'flex-end'}}>
                            <button onClick={() => setShowEditClientDialog(false)} className="clear-btn">
                              Cancel
                            </button>
                            <button onClick={handleEditClient} className="search-btn">
                              Update Client
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {currentView === 'abbreviations' && (
            <div>
              {!isDirector ? (
                <div style={{textAlign: 'center', padding: '3rem'}}>
                  <h2>Access Restricted</h2>
                  <p style={{color: '#666', fontSize: '1.1rem', marginBottom: '1rem'}}>
                    🔒 Remark Abbreviations Management is only available to Directors
                  </p>
                  <p style={{color: '#888'}}>
                    Your current role: <strong>{user?.role?.name || 'Unknown'}</strong>
                  </p>
                  <p style={{color: '#888', fontSize: '0.9rem'}}>
                    Please contact your system administrator if you need access to this feature.
                  </p>
                </div>
              ) : (
                <div>
                  <div className="header-section">
                    <h2>Remark Abbreviations Management</h2>
                    <p style={{color: '#666', fontSize: '0.9rem', margin: '0.5rem 0'}}>
                      🔐 Directors Only - Manage remark abbreviations for the collection team
                    </p>
                    <button
                      onClick={() => setShowCreateAbbreviationDialog(true)}
                      className="export-btn"
                    >
                      ➕ Add New Abbreviation
                    </button>
                  </div>

                  <div className="table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Abbreviation</th>
                          <th>Description</th>
                          <th>Detailed Description</th>
                          <th>Type</th>
                          <th>Usage Count</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {abbreviations.length === 0 ? (
                          <tr>
                            <td colSpan="7" style={{textAlign: 'center', padding: '2rem'}}>
                              No abbreviations found
                            </td>
                          </tr>
                        ) : (
                          abbreviations.map((abbr) => (
                            <tr key={abbr.id}>
                              <td>
                                <span className="abbreviation-code">
                                  {abbr.abbreviation}
                                </span>
                              </td>
                              <td className="description-cell">{abbr.description}</td>
                              <td style={{maxWidth: '200px', fontSize: '0.9rem', color: '#666'}}>
                                {abbr.detailed_description ? (
                                  abbr.detailed_description.length > 50
                                    ? abbr.detailed_description.substring(0, 50) + '...'
                                    : abbr.detailed_description
                                ) : '-'}
                              </td>
                              <td>
                                <span className={`badge ${abbr.is_system_default ? 'badge-system' : 'badge-custom'}`}>
                                  {abbr.is_system_default ? '🛠️ System' : '🔧 Custom'}
                                </span>
                              </td>
                              <td className="usage-cell">
                                <span className={`badge ${abbr.usage_count === 0 ? 'badge-unused' : 'badge-used'}`}>
                                  {abbr.usage_count}
                                </span>
                              </td>
                              <td>
                                <span
                                  className={`badge clickable ${abbr.is_active ? 'badge-success' : 'badge-inactive'}`}
                                  onClick={() => toggleAbbreviationStatus(abbr)}
                                  title={`Click to ${abbr.is_active ? 'deactivate' : 'activate'}`}
                                  style={{cursor: 'pointer'}}
                                >
                                  {abbr.is_active ? '✅ Active' : '❌ Inactive'}
                                </span>
                              </td>
                              <td>
                                <div style={{display: 'flex', gap: '0.5rem'}}>
                                  <button
                                    onClick={() => {
                                      setSelectedAbbreviation({...abbr});
                                      setShowEditAbbreviationDialog(true);
                                    }}
                                    className="view-btn"
                                    title="Edit Abbreviation"
                                    style={{fontSize: '0.8rem', padding: '0.3rem 0.6rem'}}
                                  >
                                    ✏️
                                  </button>
                                  <button
                                    onClick={() => {
                                      setAbbreviationToDelete(abbr);
                                      setShowDeleteAbbreviationDialog(true);
                                    }}
                                    className="view-btn"
                                    title="Delete Abbreviation"
                                    disabled={abbr.is_system_default}
                                    style={{
                                      fontSize: '0.8rem',
                                      padding: '0.3rem 0.6rem',
                                      backgroundColor: abbr.is_system_default ? '#ccc' : '#dc3545',
                                      cursor: abbr.is_system_default ? 'not-allowed' : 'pointer'
                                    }}
                                  >
                                    🗑️
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Create Abbreviation Modal */}
                  {showCreateAbbreviationDialog && (
                    <div className="modal">
                      <div className="modal-content">
                        <div className="modal-header">
                          <h3>Add New Abbreviation</h3>
                          <button
                            onClick={() => setShowCreateAbbreviationDialog(false)}
                            className="close-btn"
                          >
                            ×
                          </button>
                        </div>
                        <div style={{padding: '1.5rem'}}>
                          <div style={{display: 'grid', gap: '1rem'}}>
                            <div>
                              <label>Abbreviation * (Max 10 characters)</label>
                              <input
                                type="text"
                                value={newAbbreviation.abbreviation}
                                onChange={(e) => setNewAbbreviation({
                                  ...newAbbreviation,
                                  abbreviation: e.target.value.toUpperCase()
                                })}
                                placeholder="e.g., LMG, PTP, RNR"
                                maxLength="10"
                                required
                              />
                              <div className="form-helper">
                                Use short codes like LMG (Left Message), PTP (Promise to Pay)
                              </div>
                            </div>
                            <div>
                              <label>Description *</label>
                              <input
                                type="text"
                                value={newAbbreviation.description}
                                onChange={(e) => setNewAbbreviation({
                                  ...newAbbreviation,
                                  description: e.target.value
                                })}
                                placeholder="e.g., Left Message"
                                required
                              />
                            </div>
                            <div>
                              <label>Detailed Description</label>
                              <textarea
                                value={newAbbreviation.detailed_description}
                                onChange={(e) => setNewAbbreviation({
                                  ...newAbbreviation,
                                  detailed_description: e.target.value
                                })}
                                placeholder="Detailed explanation of when to use this abbreviation..."
                                rows="4"
                              />
                            </div>
                            <div>
                              <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                                <input
                                  type="checkbox"
                                  checked={newAbbreviation.is_active}
                                  onChange={(e) => setNewAbbreviation({
                                    ...newAbbreviation,
                                    is_active: e.target.checked
                                  })}
                                />
                                Active (available for use)
                              </label>
                            </div>
                          </div>
                          <div style={{marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'flex-end'}}>
                            <button
                              onClick={() => setShowCreateAbbreviationDialog(false)}
                              className="clear-btn"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={handleCreateAbbreviation}
                              className="search-btn"
                              disabled={!newAbbreviation.abbreviation || !newAbbreviation.description}
                            >
                              Create Abbreviation
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Edit Abbreviation Modal */}
                  {showEditAbbreviationDialog && selectedAbbreviation && (
                    <div className="modal">
                      <div className="modal-content">
                        <div className="modal-header">
                          <h3>Edit Abbreviation</h3>
                          <button
                            onClick={() => setShowEditAbbreviationDialog(false)}
                            className="close-btn"
                          >
                            ×
                          </button>
                        </div>
                        <div style={{padding: '1.5rem'}}>
                          <div style={{display: 'grid', gap: '1rem'}}>
                            <div>
                              <label>Abbreviation *</label>
                              <input
                                type="text"
                                value={selectedAbbreviation.abbreviation}
                                onChange={(e) => setSelectedAbbreviation({
                                  ...selectedAbbreviation,
                                  abbreviation: e.target.value.toUpperCase()
                                })}
                                maxLength="10"
                                required
                                disabled={selectedAbbreviation.is_system_default}
                              />
                              {selectedAbbreviation.is_system_default && (
                                <div className="form-helper" style={{color: '#dc3545'}}>
                                  ⚠️ System defaults cannot be modified
                                </div>
                              )}
                            </div>
                            <div>
                              <label>Description *</label>
                              <input
                                type="text"
                                value={selectedAbbreviation.description}
                                onChange={(e) => setSelectedAbbreviation({
                                  ...selectedAbbreviation,
                                  description: e.target.value
                                })}
                                required
                                disabled={selectedAbbreviation.is_system_default}
                              />
                            </div>
                            <div>
                              <label>Detailed Description</label>
                              <textarea
                                value={selectedAbbreviation.detailed_description || ''}
                                onChange={(e) => setSelectedAbbreviation({
                                  ...selectedAbbreviation,
                                  detailed_description: e.target.value
                                })}
                                rows="4"
                                disabled={selectedAbbreviation.is_system_default}
                              />
                            </div>
                            <div>
                              <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                                <input
                                  type="checkbox"
                                  checked={selectedAbbreviation.is_active}
                                  onChange={(e) => setSelectedAbbreviation({
                                    ...selectedAbbreviation,
                                    is_active: e.target.checked
                                  })}
                                />
                                Active (available for use)
                              </label>
                            </div>
                            {selectedAbbreviation.usage_count > 0 && (
                              <div className="usage-warning">
                                ⚠️ This abbreviation is used in {selectedAbbreviation.usage_count} remarks
                              </div>
                            )}
                          </div>
                          <div style={{marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'flex-end'}}>
                            <button
                              onClick={() => setShowEditAbbreviationDialog(false)}
                              className="clear-btn"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={handleEditAbbreviation}
                              className="search-btn"
                            >
                              Update Abbreviation
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Delete Confirmation Modal */}
                  {showDeleteAbbreviationDialog && abbreviationToDelete && (
                    <div className="modal">
                      <div className="modal-content">
                        <div className="modal-header danger">
                          <h3>⚠️ Confirm Delete</h3>
                          <button
                            onClick={() => setShowDeleteAbbreviationDialog(false)}
                            className="close-btn"
                          >
                            ×
                          </button>
                        </div>
                        <div style={{padding: '1.5rem'}}>
                          <p>
                            Are you sure you want to delete abbreviation <strong>{abbreviationToDelete.abbreviation}</strong>?
                          </p>
                          <p style={{color: '#856404', fontSize: '0.9rem', fontStyle: 'italic'}}>
                            This action cannot be undone. If this abbreviation is used in remarks, you will be warned.
                          </p>
                          {abbreviationToDelete.usage_count > 0 && (
                            <div style={{
                              background: '#f8d7da',
                              color: '#721c24',
                              padding: '1rem',
                              borderRadius: '8px',
                              borderLeft: '4px solid #dc3545'
                            }}>
                              ⚠️ This abbreviation is currently used in {abbreviationToDelete.usage_count} remarks
                            </div>
                          )}
                        </div>
                        <div style={{padding: '0 1.5rem 1.5rem', display: 'flex', gap: '1rem', justifyContent: 'flex-end'}}>
                          <button
                            onClick={() => setShowDeleteAbbreviationDialog(false)}
                            className="clear-btn"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={handleDeleteAbbreviation}
                            className="view-btn"
                            style={{backgroundColor: '#dc3545'}}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {currentView === 'reports' && (
            <div>
              <h2>Reports</h2>
              <p>Reporting features coming soon...</p>
            </div>
          )}

          {currentView === 'remarks' && (
            <div>
              <h2>Remarks</h2>
              <p>Remarks management features coming soon...</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;