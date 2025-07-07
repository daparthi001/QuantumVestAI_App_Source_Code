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
 * Format price change with percentage
 */
export const formatChange = (change: number, changePercent: number): string => {
  if (typeof change !== "number" || isNaN(change)) {
    return "0.00 (0.00%)";
  }
  
  const sign = change >= 0 ? "+" : "";
  const changeStr = `${sign}${change.toFixed(2)}`;
  const percentStr = `${sign}${changePercent.toFixed(2)}%`;
  
  return `${changeStr} (${percentStr})`;
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

