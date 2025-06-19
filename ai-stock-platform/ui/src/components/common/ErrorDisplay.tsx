/**
 * Error Display Component
 * Created: 2025-06-19 03:06:29
 * Author: daparthi001
 */
import React, { useEffect } from 'react';
import { useError } from '../../contexts/ErrorContext';

const ErrorDisplay: React.FC = () => {
  const { error, clearError } = useError();
  
  // Auto-dismiss the error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        clearError();
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);
  
  if (!error) {
    return null;
  }
  
  return (
    <div className="global-error-alert">
      <div className="alert alert-danger alert-dismissible fade show" role="alert">
        <strong>Error:</strong> {error.message}
        <button 
          type="button" 
          className="btn-close" 
          aria-label="Close"
          onClick={clearError}
        ></button>
      </div>
    </div>
  );
};

export default ErrorDisplay;