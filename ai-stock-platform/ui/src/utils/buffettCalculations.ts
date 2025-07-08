/**
 * Warren Buffett Analysis Calculations
 * Created: 2025-01-09
 * Author: AI Assistant
 */

export interface BuffettMetrics {
  intrinsicValue: number;
  marginOfSafety: number;
  qualityScore: number;
  investmentRecommendation: 'BUY' | 'HOLD' | 'SELL';
  reasoning: string[];
}

export interface BusinessQualityMetrics {
  consistentEarningsGrowth: number; // Score 0-100
  highROE: number; // Score 0-100
  lowDebtToEquity: number; // Score 0-100
  competitiveAdvantage: number; // Score 0-100
  managementEffectiveness: number; // Score 0-100
}

export interface IntrinsicValueInputs {
  freeCashFlow: number;
  growthRate: number;
  discountRate: number;
  terminalGrowthRate: number;
  yearsToProject: number;
}

export interface FundamentalData {
  marketCap: number;
  freeCashFlow: number;
  revenue: number;
  netIncome: number;
  totalDebt: number;
  totalEquity: number;
  returnOnEquity: number;
  eps: number;
  bookValue: number;
  dividendYield: number;
  currentPrice: number;
  historicalGrowthRate: number;
  operatingMargin: number;
}

/**
 * Calculate intrinsic value using Discounted Cash Flow (DCF) model
 * This follows Warren Buffett's approach of valuing businesses based on future cash flows
 */
export function calculateIntrinsicValue(inputs: IntrinsicValueInputs): number {
  const { freeCashFlow, growthRate, discountRate, terminalGrowthRate, yearsToProject } = inputs;
  
  let totalValue = 0;
  
  // Calculate present value of projected cash flows
  for (let year = 1; year <= yearsToProject; year++) {
    const projectedCashFlow = freeCashFlow * Math.pow(1 + growthRate, year);
    const presentValue = projectedCashFlow / Math.pow(1 + discountRate, year);
    totalValue += presentValue;
  }
  
  // Calculate terminal value
  const finalYearCashFlow = freeCashFlow * Math.pow(1 + growthRate, yearsToProject);
  const terminalValue = (finalYearCashFlow * (1 + terminalGrowthRate)) / (discountRate - terminalGrowthRate);
  const presentTerminalValue = terminalValue / Math.pow(1 + discountRate, yearsToProject);
  
  totalValue += presentTerminalValue;
  
  return totalValue;
}

/**
 * Calculate margin of safety - the difference between intrinsic value and market price
 * Buffett typically looks for at least 20-30% margin of safety
 */
export function calculateMarginOfSafety(intrinsicValue: number, marketPrice: number): number {
  if (marketPrice <= 0) return 0;
  return ((intrinsicValue - marketPrice) / marketPrice) * 100;
}

/**
 * Assess business quality based on Buffett's criteria
 */
export function assessBusinessQuality(data: FundamentalData): BusinessQualityMetrics {
  // Consistent earnings growth (based on historical growth rate)
  const consistentEarningsGrowth = Math.min(100, Math.max(0, data.historicalGrowthRate * 1000));
  
  // High ROE (Buffett likes ROE > 15%)
  const highROE = Math.min(100, Math.max(0, (data.returnOnEquity / 0.15) * 100));
  
  // Low debt-to-equity (lower is better)
  const debtToEquity = data.totalDebt / data.totalEquity;
  const lowDebtToEquity = Math.min(100, Math.max(0, (1 - Math.min(1, debtToEquity)) * 100));
  
  // Competitive advantage (based on operating margin)
  const competitiveAdvantage = Math.min(100, Math.max(0, (data.operatingMargin / 0.15) * 100));
  
  // Management effectiveness (combination of ROE and operating margin)
  const managementEffectiveness = Math.min(100, Math.max(0, 
    ((data.returnOnEquity / 0.15) * 50) + ((data.operatingMargin / 0.15) * 50)
  ));
  
  return {
    consistentEarningsGrowth,
    highROE,
    lowDebtToEquity,
    competitiveAdvantage,
    managementEffectiveness
  };
}

/**
 * Calculate overall quality score (0-100)
 */
export function calculateQualityScore(metrics: BusinessQualityMetrics): number {
  const weights = {
    consistentEarningsGrowth: 0.25,
    highROE: 0.25,
    lowDebtToEquity: 0.2,
    competitiveAdvantage: 0.15,
    managementEffectiveness: 0.15
  };
  
  return (
    metrics.consistentEarningsGrowth * weights.consistentEarningsGrowth +
    metrics.highROE * weights.highROE +
    metrics.lowDebtToEquity * weights.lowDebtToEquity +
    metrics.competitiveAdvantage * weights.competitiveAdvantage +
    metrics.managementEffectiveness * weights.managementEffectiveness
  );
}

/**
 * Generate investment recommendation based on Buffett's criteria
 */
export function generateInvestmentRecommendation(
  marginOfSafety: number,
  qualityScore: number,
  data: FundamentalData
): { recommendation: 'BUY' | 'HOLD' | 'SELL'; reasoning: string[] } {
  const reasoning: string[] = [];
  
  // Buffett's criteria for a strong buy
  if (marginOfSafety > 20 && qualityScore > 70) {
    reasoning.push(`Excellent margin of safety (${marginOfSafety.toFixed(1)}%)`);
    reasoning.push(`High quality business (score: ${qualityScore.toFixed(1)})`);
    if (data.returnOnEquity > 0.15) {
      reasoning.push('Strong return on equity (>15%)');
    }
    if (data.operatingMargin > 0.15) {
      reasoning.push('Healthy operating margins');
    }
    return { recommendation: 'BUY', reasoning };
  }
  
  // Moderate buy conditions
  if (marginOfSafety > 10 && qualityScore > 60) {
    reasoning.push(`Good margin of safety (${marginOfSafety.toFixed(1)}%)`);
    reasoning.push(`Decent quality business (score: ${qualityScore.toFixed(1)})`);
    return { recommendation: 'BUY', reasoning };
  }
  
  // Hold conditions
  if (marginOfSafety > 0 && qualityScore > 50) {
    reasoning.push(`Positive margin of safety (${marginOfSafety.toFixed(1)}%)`);
    reasoning.push(`Average quality business (score: ${qualityScore.toFixed(1)})`);
    return { recommendation: 'HOLD', reasoning };
  }
  
  // Sell conditions
  reasoning.push(`Negative margin of safety (${marginOfSafety.toFixed(1)}%)`);
  if (qualityScore < 50) {
    reasoning.push(`Below average quality business (score: ${qualityScore.toFixed(1)})`);
  }
  if (data.returnOnEquity < 0.10) {
    reasoning.push('Low return on equity (<10%)');
  }
  
  return { recommendation: 'SELL', reasoning };
}

/**
 * Main function to calculate all Buffett metrics
 */
export function calculateBuffettMetrics(data: FundamentalData): BuffettMetrics {
  // Calculate intrinsic value
  const intrinsicValueInputs: IntrinsicValueInputs = {
    freeCashFlow: data.freeCashFlow,
    growthRate: Math.max(0.02, Math.min(0.15, data.historicalGrowthRate)), // Cap between 2% and 15%
    discountRate: 0.10, // Buffett's typical discount rate
    terminalGrowthRate: 0.03, // Long-term GDP growth
    yearsToProject: 10
  };
  
  const intrinsicValue = calculateIntrinsicValue(intrinsicValueInputs);
  const marginOfSafety = calculateMarginOfSafety(intrinsicValue, data.currentPrice);
  
  // Assess business quality
  const businessQuality = assessBusinessQuality(data);
  const qualityScore = calculateQualityScore(businessQuality);
  
  // Generate recommendation
  const { recommendation, reasoning } = generateInvestmentRecommendation(
    marginOfSafety,
    qualityScore,
    data
  );
  
  return {
    intrinsicValue,
    marginOfSafety,
    qualityScore,
    investmentRecommendation: recommendation,
    reasoning
  };
}