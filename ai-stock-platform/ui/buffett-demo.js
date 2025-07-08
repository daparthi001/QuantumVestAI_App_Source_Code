/**
 * Warren Buffett Analysis Demo (JavaScript)
 * Created: 2025-01-09
 * Author: AI Assistant
 */

// Calculation functions
function calculateIntrinsicValue({ freeCashFlow, growthRate, discountRate, terminalGrowthRate, yearsToProject }) {
  if (freeCashFlow <= 0) return 0;
  
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

function calculateMarginOfSafety(intrinsicValue, marketPrice) {
  if (marketPrice <= 0) return 0;
  return ((intrinsicValue - marketPrice) / marketPrice) * 100;
}

function assessBusinessQuality(data) {
  const consistentEarningsGrowth = Math.min(100, Math.max(0, data.historicalGrowthRate * 1000));
  const highROE = Math.min(100, Math.max(0, (data.returnOnEquity / 0.15) * 100));
  const debtToEquity = data.totalDebt / data.totalEquity;
  const lowDebtToEquity = Math.min(100, Math.max(0, (1 - Math.min(1, debtToEquity)) * 100));
  const competitiveAdvantage = Math.min(100, Math.max(0, (data.operatingMargin / 0.15) * 100));
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

function calculateQualityScore(metrics) {
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

function generateInvestmentRecommendation(marginOfSafety, qualityScore, data) {
  const reasoning = [];
  
  if (marginOfSafety > 20 && qualityScore > 70) {
    reasoning.push(`Excellent margin of safety (${marginOfSafety.toFixed(1)}%)`);
    reasoning.push(`High quality business (score: ${qualityScore.toFixed(1)})`);
    if (data.returnOnEquity > 0.15) reasoning.push('Strong return on equity (>15%)');
    if (data.operatingMargin > 0.15) reasoning.push('Healthy operating margins');
    return { recommendation: 'BUY', reasoning };
  }
  
  if (marginOfSafety > 10 && qualityScore > 60) {
    reasoning.push(`Good margin of safety (${marginOfSafety.toFixed(1)}%)`);
    reasoning.push(`Decent quality business (score: ${qualityScore.toFixed(1)})`);
    return { recommendation: 'BUY', reasoning };
  }
  
  if (marginOfSafety > 0 && qualityScore > 50) {
    reasoning.push(`Positive margin of safety (${marginOfSafety.toFixed(1)}%)`);
    reasoning.push(`Average quality business (score: ${qualityScore.toFixed(1)})`);
    return { recommendation: 'HOLD', reasoning };
  }
  
  reasoning.push(`Negative margin of safety (${marginOfSafety.toFixed(1)}%)`);
  if (qualityScore < 50) reasoning.push(`Below average quality business (score: ${qualityScore.toFixed(1)})`);
  if (data.returnOnEquity < 0.10) reasoning.push('Low return on equity (<10%)');
  
  return { recommendation: 'SELL', reasoning };
}

function calculateBuffettMetrics(data) {
  const intrinsicValueInputs = {
    freeCashFlow: data.freeCashFlow,
    growthRate: Math.max(0.02, Math.min(0.15, data.historicalGrowthRate)),
    discountRate: 0.10,
    terminalGrowthRate: 0.03,
    yearsToProject: 10
  };
  
  const intrinsicValue = calculateIntrinsicValue(intrinsicValueInputs);
  const marginOfSafety = calculateMarginOfSafety(intrinsicValue, data.currentPrice);
  const businessQuality = assessBusinessQuality(data);
  const qualityScore = calculateQualityScore(businessQuality);
  const { recommendation, reasoning } = generateInvestmentRecommendation(marginOfSafety, qualityScore, data);
  
  return {
    intrinsicValue,
    marginOfSafety,
    qualityScore,
    investmentRecommendation: recommendation,
    reasoning
  };
}

// Demo data
const appleData = {
  marketCap: 2500000000000,
  freeCashFlow: 92000000000,
  revenue: 365000000000,
  netIncome: 94000000000,
  totalDebt: 120000000000,
  totalEquity: 180000000000,
  returnOnEquity: 0.25,
  eps: 3.75,
  bookValue: 45.67,
  dividendYield: 0.015,
  currentPrice: 150.00,
  historicalGrowthRate: 0.12,
  operatingMargin: 0.30
};

const poorQualityData = {
  marketCap: 50000000000,
  freeCashFlow: 2000000000,
  revenue: 25000000000,
  netIncome: 1000000000,
  totalDebt: 40000000000,
  totalEquity: 15000000000,
  returnOnEquity: 0.05,
  eps: 1.20,
  bookValue: 18.50,
  dividendYield: 0.00,
  currentPrice: 60.00,
  historicalGrowthRate: 0.02,
  operatingMargin: 0.08
};

// Run the demo
console.log("=".repeat(80));
console.log("WARREN BUFFETT STOCK ANALYSIS DEMONSTRATION");
console.log("=".repeat(80));

console.log("\n📊 ANALYSIS: Apple Inc. (AAPL) - High Quality Stock");
console.log("-".repeat(60));

const appleAnalysis = calculateBuffettMetrics(appleData);

console.log(`💰 Intrinsic Value: $${appleAnalysis.intrinsicValue.toFixed(2)}`);
console.log(`📈 Market Price: $${appleData.currentPrice.toFixed(2)}`);
console.log(`🛡️  Margin of Safety: ${appleAnalysis.marginOfSafety.toFixed(1)}%`);
console.log(`⭐ Quality Score: ${appleAnalysis.qualityScore.toFixed(1)}/100`);
console.log(`📋 Recommendation: ${appleAnalysis.investmentRecommendation}`);

console.log("\n🧠 Analysis Reasoning:");
appleAnalysis.reasoning.forEach((reason, index) => {
  console.log(`   ${index + 1}. ${reason}`);
});

console.log("\n\n📊 ANALYSIS: Poor Quality Corp (POOR) - Low Quality Stock");
console.log("-".repeat(60));

const poorAnalysis = calculateBuffettMetrics(poorQualityData);

console.log(`💰 Intrinsic Value: $${poorAnalysis.intrinsicValue.toFixed(2)}`);
console.log(`📈 Market Price: $${poorQualityData.currentPrice.toFixed(2)}`);
console.log(`🛡️  Margin of Safety: ${poorAnalysis.marginOfSafety.toFixed(1)}%`);
console.log(`⭐ Quality Score: ${poorAnalysis.qualityScore.toFixed(1)}/100`);
console.log(`📋 Recommendation: ${poorAnalysis.investmentRecommendation}`);

console.log("\n🧠 Analysis Reasoning:");
poorAnalysis.reasoning.forEach((reason, index) => {
  console.log(`   ${index + 1}. ${reason}`);
});

console.log("\n\n🎯 WARREN BUFFETT'S INVESTMENT PRINCIPLES");
console.log("=".repeat(60));

const principles = [
  "💎 Value Investing: Buy businesses trading below their intrinsic value.",
  "🛡️ Margin of Safety: Only invest with 20-30% discount to intrinsic value.",
  "📈 Quality Business: Look for consistent earnings growth and high ROE.",
  "💰 Cash Flow Focus: Prioritize strong and growing free cash flows.",
  "🏰 Economic Moats: Invest in companies with competitive advantages.",
  "⏰ Long-term Perspective: Hold quality businesses for years or decades."
];

principles.forEach(principle => console.log(`\n${principle}`));

console.log("\n\n🔬 CALCULATION METHODOLOGY");
console.log("=".repeat(60));
console.log(`
📊 Quality Score Components:
• Earnings Growth (25%): Based on historical growth rate
• Return on Equity (25%): Measures management effectiveness  
• Debt Management (20%): Lower debt-to-equity is better
• Competitive Advantage (15%): Based on operating margins
• Management Effectiveness (15%): Combined ROE and margin analysis

💰 Intrinsic Value: Uses DCF model with 10-year projections
🛡️ Investment Logic: BUY >20% margin + >70% quality, SELL if negative margin
`);

console.log("\n" + "=".repeat(80));
console.log("END OF WARREN BUFFETT ANALYSIS DEMONSTRATION");
console.log("=".repeat(80));