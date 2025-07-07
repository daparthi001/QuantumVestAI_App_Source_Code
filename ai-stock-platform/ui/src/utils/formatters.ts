/**
 * Utility functions for formatting financial data
 */

/**
 * Format price with currency symbol
 */
export const formatPrice = (price: number, currency: string = "$"): string => {
  if (typeof price !== "number" || isNaN(price)) {
    return `${currency}0.00`;
  }
  
  return `${currency}${price.toFixed(2)}`;
};

/**
 * Format currency values
 */
export const formatCurrency = (value: number, currency: string = "$"): string => {
  if (typeof value !== "number" || isNaN(value)) {
    return `${currency}0.00`;
  }
  
  return `${currency}${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

/**
 * Format numbers with proper thousands separators
 */
export const formatNumber = (value: number, decimals: number = 0): string => {
  if (typeof value !== "number" || isNaN(value)) {
    return "0";
  }
  
  return value.toLocaleString('en-US', { 
    minimumFractionDigits: decimals, 
    maximumFractionDigits: decimals 
  });
};

/**
 * Format price change with percentage
 */
export const formatChange = (change: number, changePercent?: number): string => {
  if (typeof change !== "number" || isNaN(change)) {
    return "0.00 (0.00%)";
  }
  
  const sign = change >= 0 ? "+" : "";
  const changeStr = `${sign}${change.toFixed(2)}`;
  
  if (changePercent !== undefined && !isNaN(changePercent)) {
    const percentStr = `${sign}${changePercent.toFixed(2)}%`;
    return `${changeStr} (${percentStr})`;
  }
  
  return changeStr;
};

/**
 * Format large numbers (e.g., market cap)
 */
export const formatLargeNumber = (value: number): string => {
  if (typeof value !== "number" || isNaN(value)) {
    return "0";
  }
  
  if (value >= 1e12) {
    return `${(value / 1e12).toFixed(2)}T`;
  } else if (value >= 1e9) {
    return `${(value / 1e9).toFixed(2)}B`;
  } else if (value >= 1e6) {
    return `${(value / 1e6).toFixed(2)}M`;
  } else if (value >= 1e3) {
    return `${(value / 1e3).toFixed(2)}K`;
  }
  
  return value.toString();
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number): string => {
  if (typeof value !== "number" || isNaN(value)) {
    return "0.00%";
  }
  
  return `${value.toFixed(2)}%`;
};

/**
 * Format volume
 */
export const formatVolume = (volume: number): string => {
  return formatLargeNumber(volume);
};

/**
 * Format date to readable string
 */
export const formatDate = (date: string | Date): string => {
  if (!date) {
    return "N/A";
  }
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return "Invalid Date";
  }
  
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Format date and time to readable string
 */
export const formatDateTime = (date: string | Date): string => {
  if (!date) {
    return "N/A";
  }
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return "Invalid Date";
  }
  
  return dateObj.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Format duration in milliseconds to readable format
 */
export const formatDuration = (milliseconds: number): string => {
  if (typeof milliseconds !== "number" || isNaN(milliseconds)) {
    return "0ms";
  }
  
  if (milliseconds < 1000) {
    return `${milliseconds.toFixed(0)}ms`;
  }
  
  const seconds = milliseconds / 1000;
  if (seconds < 60) {
    return `${seconds.toFixed(2)}s`;
  }
  
  const minutes = seconds / 60;
  if (minutes < 60) {
    return `${minutes.toFixed(2)}m`;
  }
  
  const hours = minutes / 60;
  return `${hours.toFixed(2)}h`;
};

