import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, Card, CardContent } from '@mui/material';
import { People, CloudUpload, AttachMoney, TrendingUp } from '@mui/icons-material';
import api from '../../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalCustomers: 0,
    pendingImports: 0,
    completedImports: 0,
    totalPayments: 0
  });

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      // Fetch actual stats from your API
      // For now, using placeholder data
      setStats({
        totalCustomers: 1250,
        pendingImports: 3,
        completedImports: 15,
        totalPayments: 458
      });
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    }
  };

  const StatCard = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Customers"
            value={stats.totalCustomers}
            icon={<People fontSize="large" />}
            color="#1976d2"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Imports"
            value={stats.pendingImports}
            icon={<CloudUpload fontSize="large" />}
            color="#ff9800"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed Imports"
            value={stats.completedImports}
            icon={<TrendingUp fontSize="large" />}
            color="#4caf50"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Payments"
            value={stats.totalPayments}
            icon={<AttachMoney fontSize="large" />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      {/* Recent Activity Section */}
      <Paper sx={{ mt: 4, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Activities
        </Typography>
        <Box>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
            • New import batch uploaded - Commercial Bank Credit Card
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
            • 45 payments processed successfully
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
            • Customer data updated for 150 accounts
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default Dashboard;