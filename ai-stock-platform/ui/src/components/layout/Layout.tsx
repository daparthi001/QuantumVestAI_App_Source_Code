/**
 * Main Layout Component
 * Provides the application shell with navigation and sidebar
 */
import React, { useState } from 'react';
import { Navbar, Nav, Container, Offcanvas, Button } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../providers/ThemeProvider';
import { ROUTES } from '../../config/constants';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [showSidebar, setShowSidebar] = useState(false);
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate(ROUTES.LOGIN);
  };

  const navigationItems = [
    { path: ROUTES.DASHBOARD, label: 'Dashboard', icon: '📊' },
    { path: ROUTES.STOCKS, label: 'Stocks', icon: '📈' },
    { path: ROUTES.WATCHLIST, label: 'Watchlist', icon: '👁' },
    { path: ROUTES.PORTFOLIO, label: 'Portfolio', icon: '💼' },
    { path: ROUTES.ANALYTICS, label: 'Analytics', icon: '📋' },
    { path: ROUTES.BACKTEST, label: 'Backtest', icon: '🔄' },
    { path: ROUTES.NEWS, label: 'News', icon: '📰' },
    { path: ROUTES.ALERTS, label: 'Alerts', icon: '🔔' },
  ];

  return (
    <>
      {/* Top Navigation */}
      <Navbar bg={theme === 'dark' ? 'dark' : 'light'} variant={theme} expand="lg" className="shadow-sm">
        <Container fluid>
          <Button
            variant="outline-secondary"
            className="me-3 d-lg-none"
            onClick={() => setShowSidebar(true)}
          >
            ☰
          </Button>
          
          <Navbar.Brand as={Link} to={ROUTES.DASHBOARD} className="fw-bold">
            QuantumVestAI
          </Navbar.Brand>

          <Nav className="ms-auto">
            <Button
              variant="outline-secondary"
              size="sm"
              className="me-2"
              onClick={toggleTheme}
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </Button>
            
            <Nav.Link as={Link} to={ROUTES.PROFILE}>
              {user?.full_name || user?.username || 'User'}
            </Nav.Link>
            
            <Button variant="outline-danger" size="sm" onClick={handleLogout}>
              Logout
            </Button>
          </Nav>
        </Container>
      </Navbar>

      <div className="d-flex">
        {/* Desktop Sidebar */}
        <div className="d-none d-lg-block bg-light border-end" style={{ width: '250px', minHeight: 'calc(100vh - 56px)' }}>
          <div className="p-3">
            <Nav className="flex-column">
              {navigationItems.map((item) => (
                <Nav.Link
                  key={item.path}
                  as={Link}
                  to={item.path}
                  className={`py-2 px-3 rounded mb-1 ${
                    location.pathname === item.path ? 'bg-primary text-white' : ''
                  }`}
                >
                  <span className="me-2">{item.icon}</span>
                  {item.label}
                </Nav.Link>
              ))}
            </Nav>
          </div>
        </div>

        {/* Mobile Sidebar */}
        <Offcanvas
          show={showSidebar}
          onHide={() => setShowSidebar(false)}
          placement="start"
        >
          <Offcanvas.Header closeButton>
            <Offcanvas.Title>QuantumVestAI</Offcanvas.Title>
          </Offcanvas.Header>
          <Offcanvas.Body>
            <Nav className="flex-column">
              {navigationItems.map((item) => (
                <Nav.Link
                  key={item.path}
                  as={Link}
                  to={item.path}
                  className={`py-2 px-3 rounded mb-1 ${
                    location.pathname === item.path ? 'bg-primary text-white' : ''
                  }`}
                  onClick={() => setShowSidebar(false)}
                >
                  <span className="me-2">{item.icon}</span>
                  {item.label}
                </Nav.Link>
              ))}
            </Nav>
          </Offcanvas.Body>
        </Offcanvas>

        {/* Main Content */}
        <div className="flex-grow-1">
          <Container fluid className="p-4">
            {children}
          </Container>
        </div>
      </div>
    </>
  );
};

export default Layout;