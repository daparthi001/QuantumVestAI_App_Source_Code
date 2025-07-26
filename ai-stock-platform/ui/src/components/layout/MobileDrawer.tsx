import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface DrawerItem {
  path: string;
  label: string;
  description?: string;
  modernIcon?: string;
  color?: string;
}

interface MobileDrawerProps {
  open: boolean;
  onClose: () => void;
  items: DrawerItem[];
}

const MobileDrawer: React.FC<MobileDrawerProps> = ({ open, onClose, items }) => {
  const location = useLocation();

  return (
    <>
      <div
        className={`fixed inset-0 bg-black/50 transition-opacity z-40 ${open ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
      />
      <div
        className={`fixed inset-y-0 left-0 w-64 bg-dark-bg-secondary overflow-y-auto shadow-quantum-md transform transition-transform z-50 ${open ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <span className="font-bold text-lg text-white">QuantumVestAI</span>
          <button className="text-white" onClick={onClose} aria-label="Close menu">
            ✕
          </button>
        </div>
        <nav className="p-4 space-y-2">
          {items.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-700 transition-colors ${location.pathname === item.path ? 'bg-gray-700' : ''}`}
              style={{ color: item.color || undefined }}
            >
              {item.modernIcon && <i className={`bi ${item.modernIcon}`} />}
              <span className="text-white">{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </>
  );
};

export default MobileDrawer;
