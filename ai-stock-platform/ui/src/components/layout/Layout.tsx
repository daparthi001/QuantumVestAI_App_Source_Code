/**
 * Quantum Layout Component - World-Class Financial AI Platform
 * Features floating sidebar, glass morphism, and quantum animations
 */
import React, { useState, useEffect } from 'react';
import { Navbar, Nav, Container, Button, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../providers/ThemeProvider';
import { ROUTES } from '../../config/constants';
import { motion, AnimatePresence } from 'framer-motion';
import MobileDrawer from './MobileDrawer';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [showSidebar, setShowSidebar] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate(ROUTES.LOGIN);
  };

  const navigationItems = [
    { 
      path: ROUTES.DASHBOARD, 
      label: 'Dashboard', 
      icon: '📊', 
      modernIcon: 'bi-speedometer2',
      description: 'Overview & Analytics',
      color: '#4facfe'
    },
    { 
      path: ROUTES.STOCKS, 
      label: 'Stocks', 
      icon: '📈', 
      modernIcon: 'bi-graph-up-arrow',
      description: 'Market Analysis',
      color: '#43e97b'
    },
    { 
      path: ROUTES.STOCK_FLOW, 
      label: 'Stock Flow', 
      icon: '🌊', 
      modernIcon: 'bi-diagram-3',
      description: 'Flow Visualization',
      color: '#06b6d4'
    },
    { 
      path: ROUTES.WATCHLIST, 
      label: 'Watchlist', 
      icon: '👁️', 
      modernIcon: 'bi-eye',
      description: 'Track Favorites',
      color: '#f093fb'
    },
    { 
      path: ROUTES.PORTFOLIO, 
      label: 'Portfolio', 
      icon: '💼', 
      modernIcon: 'bi-briefcase',
      description: 'Your Investments',
      color: '#667eea'
    },
    { 
      path: ROUTES.ANALYTICS, 
      label: 'Analytics', 
      icon: '📊', 
      modernIcon: 'bi-bar-chart',
      description: 'Deep Insights',
      color: '#00d4ff'
    },
    { 
      path: ROUTES.BACKTEST, 
      label: 'Backtest', 
      icon: '🔄', 
      modernIcon: 'bi-arrow-repeat',
      description: 'Strategy Testing',
      color: '#8b5cf6'
    },
    { 
      path: ROUTES.NEWS, 
      label: 'News', 
      icon: '📰', 
      modernIcon: 'bi-newspaper',
      description: 'Market News',
      color: '#fa709a'
    },
    { 
      path: ROUTES.ALERTS, 
      label: 'Alerts', 
      icon: '🔔', 
      modernIcon: 'bi-bell',
      description: 'Notifications',
      color: '#fee140'
    },
    { 
      path: ROUTES.AI_ASSISTANT, 
      label: 'AI Assistant', 
      icon: '🤖', 
      modernIcon: 'bi-robot',
      description: 'Quantum AI',
      color: '#06ffa5'
    },
    { 
      path: ROUTES.TRADING, 
      label: 'Trading', 
      icon: '⚡', 
      modernIcon: 'bi-lightning',
      description: 'Live Trading',
      color: '#ffd700'
    },
  ];

  const sidebarVariants = {
    expanded: { width: '280px' },
    collapsed: { width: '70px' }
  };

  const contentVariants = {
    expanded: { marginLeft: '280px' },
    collapsed: { marginLeft: '70px' }
  };

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 992) {
        setSidebarCollapsed(false);
        setShowSidebar(false);
      }
    };

    window.addEventListener('resize', handleResize);
    // Call once to set initial state
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="quantum-bg min-vh-100" style={{ paddingTop: '76px' }}>
      {/* Enhanced Top Navigation */}
      <motion.div
        className="quantum-nav"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <Navbar expand="lg" className="px-4 py-3">
          <Container fluid>
            <Button
              variant="outline-secondary"
              className="me-3 d-lg-none quantum-btn-outline"
              onClick={() => setShowSidebar(true)}
            >
              <motion.div
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                ☰
              </motion.div>
            </Button>
            
            <Navbar.Brand
              as={Link}
              to={ROUTES.DASHBOARD}
              className="fw-bold d-flex align-items-center me-lg-4"
            >
              <motion.div
                className="me-2"
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                ⚛️
              </motion.div>
              <span className="quantum-text-gradient">QuantumVestAI</span>
            </Navbar.Brand>

            <Nav className="ms-auto d-flex align-items-center gap-1">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <OverlayTrigger placement="bottom" overlay={<Tooltip id="theme-tip">Toggle theme</Tooltip>}>
                  <Button
                    variant="outline-secondary"
                    size="sm"
                    className="me-3 quantum-btn-outline"
                    onClick={toggleTheme}
                    aria-label="Toggle theme"
                  >
                    {theme === 'dark' ? '☀️' : '🌙'}
                  </Button>
                </OverlayTrigger>
              </motion.div>
              
              <Nav.Link as={Link} to={ROUTES.PROFILE} className="text-white me-3">
                <motion.div whileHover={{ scale: 1.05 }}>
                  {user?.full_name || user?.username || 'User'}
                </motion.div>
              </Nav.Link>
              
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button variant="outline-danger" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </motion.div>
            </Nav>
          </Container>
        </Navbar>
      </motion.div>

      <div className="d-flex">
        {/* Enhanced Desktop Sidebar */}
        <motion.div
          className="quantum-sidebar d-lg-none"
          variants={sidebarVariants}
          initial={{ x: -280, opacity: 0 }}
          animate={sidebarCollapsed ? 'collapsed' : 'expanded'}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          <div className="p-3">
            {/* Sidebar Toggle */}
            <motion.button
              className="quantum-btn quantum-btn-outline w-100 mb-4"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <motion.span
                animate={{ rotate: sidebarCollapsed ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                {sidebarCollapsed ? '→' : '←'}
              </motion.span>
              {!sidebarCollapsed && <span className="ms-2">Collapse</span>}
            </motion.button>

            {/* Navigation Items */}
            <Nav className="flex-column">
              <AnimatePresence>
                {navigationItems.map((item, index) => (
                  <motion.div
                    key={item.path}
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <motion.div
                      whileHover={{ scale: 1.02, x: 5 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Nav.Link
                        as={Link}
                        to={item.path}
                        className={`quantum-sidebar-item ${
                          location.pathname === item.path ? 'active' : ''
                        }`}
                        style={{
                          '--item-color': item.color
                        } as React.CSSProperties}
                      >
                        <motion.div 
                          className="quantum-sidebar-icon"
                          whileHover={{ rotate: 360, scale: 1.2 }}
                          transition={{ duration: 0.5 }}
                        >
                          <i className={`bi ${item.modernIcon}`} style={{ color: item.color }}></i>
                          {sidebarCollapsed && (
                            <motion.div
                              className="quantum-tooltip quantum-tooltip-right"
                              initial={{ opacity: 0, scale: 0.8 }}
                              whileHover={{ opacity: 1, scale: 1 }}
                              data-tooltip={item.label}
                            />
                          )}
                        </motion.div>
                        <AnimatePresence>
                          {!sidebarCollapsed && (
                            <motion.div
                              className="quantum-sidebar-text"
                              initial={{ opacity: 0, width: 0 }}
                              animate={{ opacity: 1, width: 'auto' }}
                              exit={{ opacity: 0, width: 0 }}
                              transition={{ duration: 0.2 }}
                            >
                              <div>
                                <div className="fw-semibold">{item.label}</div>
                                <small className="text-muted">{item.description}</small>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </Nav.Link>
                    </motion.div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </Nav>

            {/* User Info Section */}
            {!sidebarCollapsed && (
              <motion.div
                className="mt-auto pt-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                <div className="quantum-card p-3 text-center">
                  <motion.div
                    className="quantum-pulse"
                    whileHover={{ scale: 1.1 }}
                  >
                    <div className="h5 mb-1">Welcome back!</div>
                    <small className="text-muted">{user?.full_name || 'Quantum Trader'}</small>
                  </motion.div>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Mobile Drawer */}
        <MobileDrawer
          open={showSidebar}
          onClose={() => setShowSidebar(false)}
          items={navigationItems}
        />

        {/* Enhanced Main Content */}
        <motion.div
          className="flex-grow-1"
          variants={contentVariants}
          animate={sidebarCollapsed ? 'collapsed' : 'expanded'}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          style={{ minHeight: 'calc(100vh - 76px)' }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Container fluid className="p-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.3 }}
              >
                {children}
              </motion.div>
            </Container>
          </motion.div>
        </motion.div>
      </div>

      {/* Quantum Particles Background Effect - Optimized */}
      <div className="quantum-particles">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="quantum-particle"
            initial={{
              x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1920),
              y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1080),
              opacity: 0
            }}
            animate={{
              x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1920),
              y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1080),
              opacity: [0, 0.3, 0]
            }}
            transition={{
              duration: Math.random() * 15 + 15,
              repeat: Infinity,
              ease: "linear",
              repeatDelay: Math.random() * 5
            }}
            style={{
              position: 'fixed',
              width: '1px',
              height: '1px',
              background: `rgba(74, 144, 226, ${Math.random() * 0.3})`,
              borderRadius: '50%',
              pointerEvents: 'none',
              zIndex: 1,
              willChange: 'transform, opacity'
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default Layout;