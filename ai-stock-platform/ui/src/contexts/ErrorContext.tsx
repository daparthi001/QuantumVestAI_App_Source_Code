/**
 * Global Error Context
 * Created: 2025-06-19 03:06:29
 * Author: daparthi001
 */
import React, { createContext, useContext, useState, useCallback } from 'react';

interface ErrorContextType {
  error: Error | null;
  setError: (error: Error | null) => void;
  clearError: () => void;
  showErrorMessage: (message: string) => void;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

export const ErrorProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [error, setErrorState] = useState<Error | null>(null);

  const setError = useCallback((error: Error | null) => {
    setErrorState(error);
  }, []);

  const clearError = useCallback(() => {
    setErrorState(null);
  }, []);

  const showErrorMessage = useCallback((message: string) => {
    setErrorState(new Error(message));
  }, []);

  return (
    <ErrorContext.Provider value={{ error, setError, clearError, showErrorMessage }}>
      {children}
    </ErrorContext.Provider>
  );
};

export const useError = (): ErrorContextType => {
  const context = useContext(ErrorContext);
  if (context === undefined) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
};