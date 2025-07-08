/**
 * Enhanced Notification Provider
 * Provides notification context and toast management with improved UX
 */
import React, { createContext, useContext, useState, useCallback } from 'react';
import { toast, ToastContainer, ToastOptions, Id } from 'react-toastify';

interface NotificationState {
  activeNotifications: Map<string, Id>;
  queue: Array<{ message: string; type: string; options?: ToastOptions }>;
}

interface NotificationContextType {
  showSuccess: (message: string, options?: ToastOptions) => Id;
  showError: (message: string, options?: ToastOptions) => Id;
  showWarning: (message: string, options?: ToastOptions) => Id;
  showInfo: (message: string, options?: ToastOptions) => Id;
  showLoading: (message: string, options?: ToastOptions) => Id;
  updateToast: (toastId: Id, message: string, type?: 'success' | 'error' | 'warning' | 'info') => void;
  dismissToast: (toastId: Id) => void;
  dismissAll: () => void;
  getActiveCount: () => number;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [state, setState] = useState<NotificationState>({
    activeNotifications: new Map(),
    queue: []
  });

  const defaultOptions: ToastOptions = {
    position: 'top-right',
    autoClose: 5000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    onClose: () => {
      // Update active notifications count when a toast closes
      setState(prev => ({
        ...prev,
        activeNotifications: new Map([...prev.activeNotifications].filter(([_, id]) => id !== undefined))
      }));
    }
  };

  const showSuccess = useCallback((message: string, options?: ToastOptions) => {
    const id = toast.success(message, { ...defaultOptions, ...options });
    setState(prev => ({
      ...prev,
      activeNotifications: new Map(prev.activeNotifications.set('success', id))
    }));
    return id;
  }, []);

  const showError = useCallback((message: string, options?: ToastOptions) => {
    const id = toast.error(message, { 
      ...defaultOptions, 
      autoClose: 8000, // Longer duration for errors
      ...options 
    });
    setState(prev => ({
      ...prev,
      activeNotifications: new Map(prev.activeNotifications.set('error', id))
    }));
    return id;
  }, []);

  const showWarning = useCallback((message: string, options?: ToastOptions) => {
    const id = toast.warning(message, { 
      ...defaultOptions, 
      autoClose: 6000, // Slightly longer for warnings
      ...options 
    });
    setState(prev => ({
      ...prev,
      activeNotifications: new Map(prev.activeNotifications.set('warning', id))
    }));
    return id;
  }, []);

  const showInfo = useCallback((message: string, options?: ToastOptions) => {
    const id = toast.info(message, { ...defaultOptions, ...options });
    setState(prev => ({
      ...prev,
      activeNotifications: new Map(prev.activeNotifications.set('info', id))
    }));
    return id;
  }, []);

  const showLoading = useCallback((message: string, options?: ToastOptions) => {
    const id = toast.loading(message, { 
      ...defaultOptions, 
      autoClose: false, // Loading toasts don't auto-close
      ...options 
    });
    setState(prev => ({
      ...prev,
      activeNotifications: new Map(prev.activeNotifications.set('loading', id))
    }));
    return id;
  }, []);

  const updateToast = useCallback((toastId: Id, message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    toast.update(toastId, {
      render: message,
      type: type,
      autoClose: 5000,
      isLoading: false
    });
  }, []);

  const dismissToast = useCallback((toastId: Id) => {
    toast.dismiss(toastId);
  }, []);

  const dismissAll = useCallback(() => {
    toast.dismiss();
    setState(prev => ({
      ...prev,
      activeNotifications: new Map()
    }));
  }, []);

  const getActiveCount = useCallback(() => {
    return state.activeNotifications.size;
  }, [state.activeNotifications.size]);

  const value: NotificationContextType = {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showLoading,
    updateToast,
    dismissToast,
    dismissAll,
    getActiveCount,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={true}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
        style={{ 
          zIndex: 9999,
          fontSize: '0.9rem'
        }}
        toastStyle={{
          borderRadius: '12px',
          backdropFilter: 'blur(10px)',
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}
      />
    </NotificationContext.Provider>
  );
};