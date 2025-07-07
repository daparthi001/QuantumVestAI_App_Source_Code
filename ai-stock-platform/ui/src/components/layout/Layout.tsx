/**
 * Quantum Layout Component - World-Class Financial AI Platform
 * Features floating sidebar, glass morphism, and quantum animations
 */
import React, { useState, useEffect } from 'react';
import { Navbar, Nav, Container, Offcanvas, Button } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../providers/ThemeProvider';
import { ROUTES } from '../../config/constants';
import { motion, AnimatePresence } from 'framer-motion';

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
    { path: ROUTES.DASHBOARD, label: 'Dashboard', icon: '🎯', description: 'Overview & Analytics' },
    { path: ROUTES.STOCKS, label: 'Stocks', icon: '📈', description: 'Market Analysis' },
    { path: ROUTES.WATCHLIST, label: 'Watchlist', icon: '👁️', description: 'Track Favorites' },
    { path: ROUTES.PORTFOLIO, label: 'Portfolio', icon: '💼', description: 'Your Investments' },
    { path: ROUTES.ANALYTICS, label: 'Analytics', icon: '📊', description: 'Deep Insights' },
    { path: ROUTES.BACKTEST, label: 'Backtest', icon: '🔄', description: 'Strategy Testing' },
    { path: ROUTES.NEWS, label: 'News', icon: '📰', description: 'Market News' },
    { path: ROUTES.ALERTS, label: 'Alerts', icon: '🔔', description: 'Notifications' },
    { path: ROUTES.AI_ASSISTANT, label: 'AI Assistant', icon: '🤖', description: 'Quantum AI' },
    { path: ROUTES.TRADING, label: 'Trading', icon: '⚡', description: 'Live Trading' },
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
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="quantum-bg min-vh-100">
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
            
            <Navbar.Brand as={Link} to={ROUTES.DASHBOARD} className="fw-bold d-flex align-items-center">
              <motion.div
                className="me-2"
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                ⚛️
              </motion.div>
              <span className="quantum-text-gradient">QuantumVestAI</span>
            </Navbar.Brand>

            <Nav className="ms-auto d-flex align-items-center">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  variant="outline-secondary"
                  size="sm"
                  className="me-3 quantum-btn-outline"
                  onClick={toggleTheme}
                >
                  {theme === 'dark' ? '☀️' : '🌙'}
                </Button>
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
          className="quantum-sidebar d-none d-lg-block"
          variants={sidebarVariants}
          animate={sidebarCollapsed ? 'collapsed' : 'expanded'}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          initial={{ x: -280, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
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
                      >
                        <span className="quantum-sidebar-icon">{item.icon}</span>
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

        {/* Enhanced Mobile Sidebar */}
        <Offcanvas
          show={showSidebar}
          onHide={() => setShowSidebar(false)}
          placement="start"
          className="quantum-mobile-sidebar"
        >
          <Offcanvas.Header closeButton className="quantum-card-header">
            <Offcanvas.Title className="quantum-text-gradient">
              ⚛️ QuantumVestAI
            </Offcanvas.Title>
          </Offcanvas.Header>
          <Offcanvas.Body className="quantum-card-body">
            <Nav className="flex-column">
              {navigationItems.map((item, index) => (
                <motion.div
                  key={item.path}
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Nav.Link
                    as={Link}
                    to={item.path}
                    className={`quantum-nav-item ${
                      location.pathname === item.path ? 'active' : ''
                    }`}
                    onClick={() => setShowSidebar(false)}
                  >
                    <span className="me-3">{item.icon}</span>
                    <div>
                      <div className="fw-semibold">{item.label}</div>
                      <small className="text-muted">{item.description}</small>
                    </div>
                  </Nav.Link>
                </motion.div>
              ))}
            </Nav>
          </Offcanvas.Body>
        </Offcanvas>

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

      {/* Quantum Particles Background Effect */}
      <div className="quantum-particles">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="quantum-particle"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              opacity: 0
            }}
            animate={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              opacity: [0, 0.5, 0]
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{
              position: 'fixed',
              width: '2px',
              height: '2px',
              background: `rgba(74, 144, 226, ${Math.random() * 0.5})`,
              borderRadius: '50%',
              pointerEvents: 'none',
              zIndex: 1
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default Layout;