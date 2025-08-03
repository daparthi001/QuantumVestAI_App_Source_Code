import React, { useState } from 'react';
import { Box } from '@mui/material';
import Header from '../Header';
import Sidebar from '../Sidebar';

interface AppLayoutProps {
  children: React.ReactNode;
}

/**
 * Global application layout with header, sidebar and main content area.
 * The sidebar collapses on mobile and can be toggled via the header menu button.
 */
const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Header onMenuClick={handleDrawerToggle} />
      <Sidebar open={mobileOpen} onClose={handleDrawerToggle} />
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        {children}
      </Box>
    </Box>
  );
};

export default AppLayout;
