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

  useEffect(() => {
    if (token) {
      fetchUserProfile();
    }
  }, [token]);

  useEffect(() => {
    if (currentView === 'customers' && isLoggedIn) {
      fetchCustomers();
      fetchCustomerStats();
      fetchFilterOptions();
    }
  }, [currentView]);

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

        // Fetch user profile immediately
        const profileResponse = await fetch(`${API_URL}/auth/me`, {
          headers: { 'Authorization': `Bearer ${data.access_token}` }
        });

        if (profileResponse.ok) {
          const userData = await profileResponse.json();
          setUser(userData);
          setIsLoggedIn(true);
          setCurrentView('dashboard');
          setMessage(''); // Clear the success message
        } else {
          // If profile fetch fails, still set logged in
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

  const uploadFile = async (file, bankName, operationType, period) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('bank_name', bankName);
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
        setMessage('Upload failed');
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
        setCustomers(data);
      }
    } catch (error) {
      console.error('Error fetching customers:', error);
      setMessage('Failed to fetch customers');
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
            </div>
          )}

          {currentView === 'imports' && (
            <div>
              <h2>Import Management</h2>
              <div className="upload-section">
                <h3>Upload New Import</h3>
                <input type="file" id="file-upload" accept=".xlsx,.xls" />
                <input type="text" id="bank-name" placeholder="Bank Name" />
                <select id="operation-type">
                  <option value="CREDIT_CARD">Credit Card</option>
                  <option value="LOAN">Loan</option>
                  <option value="LEASING">Leasing</option>
                  <option value="PAYMENT">Payment</option>
                </select>
                <input type="text" id="import-period" placeholder="Import Period (e.g., August 2025)" />
                <button onClick={() => {
                  const file = document.getElementById('file-upload').files[0];
                  const bankName = document.getElementById('bank-name').value;
                  const operationType = document.getElementById('operation-type').value;
                  const period = document.getElementById('import-period').value;
                  if (file && bankName && period) {
                    uploadFile(file, bankName, operationType, period);
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

              {/* Statistics Cards */}
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

              {/* Filters Section */}
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

              {/* Customer Table */}
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
                      {customers.map(customer => (
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
                              {customer.days_in_arrears} days
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
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              {/* Customer Detail Modal */}
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

          {currentView === 'reports' && (
            <div>
              <h2>Reports</h2>
              <p>Reporting features coming soon...</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;