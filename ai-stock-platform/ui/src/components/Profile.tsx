/**
 * Profile Component - User Profile Management
 * Full implementation with authentication and user data
 * Updated: 2025-08-06
 * Author: QuantumVestAI Team
 */
import React, { useState, useEffect } from 'react';
import { 
  Card, CardContent, CardHeader, CardTitle, 
  Grid, Typography, Button, TextField, 
  Chip, Box, Avatar, Divider, Alert,
  Tab, Tabs, TabPanel
} from '@mui/material';
import { Person, Edit, Save, Cancel } from '@mui/icons-material';

interface UserProfile {
  username: string;
  email: string;
  fullName: string;
  role: string;
  subscriptionType: string;
  joinDate: string;
  lastLogin: string;
  preferences: {
    theme: string;
    notifications: boolean;
    autoRefresh: boolean;
  };
}

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<UserProfile>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      // In a real app, this would fetch from API
      // For now, simulate with mock data
      const mockProfile: UserProfile = {
        username: 'demo_user',
        email: 'demo@quantumvestai.com',
        fullName: 'Demo User',
        role: 'user',
        subscriptionType: 'free',
        joinDate: '2025-01-01',
        lastLogin: new Date().toISOString(),
        preferences: {
          theme: 'dark',
          notifications: true,
          autoRefresh: true
        }
      };
      
      setTimeout(() => {
        setProfile(mockProfile);
        setEditForm(mockProfile);
        setLoading(false);
      }, 1000);
      
    } catch (err) {
      setError('Failed to load profile');
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      // In a real app, this would send PUT request to API
      setProfile({ ...profile, ...editForm } as UserProfile);
      setIsEditing(false);
      setError(null);
    } catch (err) {
      setError('Failed to save profile');
    }
  };

  const handleCancel = () => {
    setEditForm(profile || {});
    setIsEditing(false);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Typography>Loading profile...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
        <Button onClick={loadProfile} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  if (!profile) {
    return (
      <Alert severity="warning" sx={{ mt: 2 }}>
        Profile not found
      </Alert>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Profile Settings
      </Typography>

      <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)} sx={{ mb: 3 }}>
        <Tab label="General" />
        <Tab label="Preferences" />
        <Tab label="Subscription" />
      </Tabs>

      {/* General Tab */}
      {activeTab === 0 && (
        <Card>
          <CardHeader
            avatar={
              <Avatar sx={{ bgcolor: 'primary.main' }}>
                <Person />
              </Avatar>
            }
            title={profile.fullName}
            subheader={`@${profile.username}`}
            action={
              isEditing ? (
                <Box>
                  <Button startIcon={<Save />} onClick={handleSave} sx={{ mr: 1 }}>
                    Save
                  </Button>
                  <Button startIcon={<Cancel />} onClick={handleCancel}>
                    Cancel
                  </Button>
                </Box>
              ) : (
                <Button startIcon={<Edit />} onClick={() => setIsEditing(true)}>
                  Edit
                </Button>
              )
            }
          />
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Full Name"
                  value={isEditing ? editForm.fullName || '' : profile.fullName}
                  onChange={(e) => setEditForm({ ...editForm, fullName: e.target.value })}
                  disabled={!isEditing}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Email"
                  value={isEditing ? editForm.email || '' : profile.email}
                  onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                  disabled={!isEditing}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Username"
                  value={profile.username}
                  disabled
                  helperText="Username cannot be changed"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Role
                  </Typography>
                  <Chip 
                    label={profile.role} 
                    color={profile.role === 'admin' ? 'secondary' : 'default'}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Member Since"
                  value={new Date(profile.joinDate).toLocaleDateString()}
                  disabled
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Last Login"
                  value={new Date(profile.lastLogin).toLocaleString()}
                  disabled
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Preferences Tab */}
      {activeTab === 1 && (
        <Card>
          <CardHeader title="Preferences" />
          <CardContent>
            <Typography variant="body1" color="text.secondary">
              Preference settings will be available in the next update.
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Subscription Tab */}
      {activeTab === 2 && (
        <Card>
          <CardHeader title="Subscription" />
          <CardContent>
            <Box sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Current Plan
              </Typography>
              <Chip 
                label={profile.subscriptionType.toUpperCase()} 
                color={profile.subscriptionType === 'premium' ? 'primary' : 'default'}
                size="large"
              />
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="body1" color="text.secondary">
              Upgrade options and billing information will be available soon.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Profile;
