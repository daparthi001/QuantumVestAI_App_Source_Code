import React, { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  useMediaQuery,
  Box
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import InsightsIcon from '@mui/icons-material/Insights';
import SettingsIcon from '@mui/icons-material/Settings';
import PortfolioIcon from '@mui/icons-material/PieChart';
import MenuIcon from '@mui/icons-material/Menu';
import { useTheme } from '@mui/material/styles';

interface SidebarProps {
  /** Controls drawer visibility on mobile */
  open?: boolean;
  /** Callback when drawer should close on mobile */
  onClose?: () => void;
}

const drawerWidth = 240;
const collapsedWidth = 64;

const menuItems = [
  { label: 'Home', icon: <HomeIcon />, path: '/' },
  { label: 'Portfolio', icon: <PortfolioIcon />, path: '/portfolio' },
  { label: 'AI Insights', icon: <InsightsIcon />, path: '/ai' },
  { label: 'Settings', icon: <SettingsIcon />, path: '/settings' }
];

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [collapsed, setCollapsed] = useState(false);

  const handleToggleCollapse = () => setCollapsed(!collapsed);

  const drawerContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <IconButton
        onClick={handleToggleCollapse}
        sx={{ m: 1, alignSelf: collapsed ? 'center' : 'flex-end' }}
        aria-label="toggle sidebar"
      >
        <MenuIcon />
      </IconButton>
      <List sx={{ flexGrow: 1 }}>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.label}
            sx={{
              justifyContent: collapsed ? 'center' : 'flex-start',
              px: collapsed ? 0 : 2
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: collapsed ? 0 : 2,
                justifyContent: 'center'
              }}
            >
              {item.icon}
            </ListItemIcon>
            {!collapsed && <ListItemText primary={item.label} />}
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'permanent'}
      open={isMobile ? open : true}
      onClose={onClose}
      ModalProps={{ keepMounted: true }}
      sx={{
        width: collapsed ? collapsedWidth : drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: collapsed ? collapsedWidth : drawerWidth,
          boxSizing: 'border-box'
        }
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;
