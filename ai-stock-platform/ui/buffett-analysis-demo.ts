/**
 * Warren Buffett Analysis Demo
 * Created: 2025-01-09
 * Author: AI Assistant
 */
import { 
  calculateBuffettMetrics, 
  type FundamentalData 
} from './src/utils/buffettCalculations.js';

// Demo data for Apple Inc. (AAPL)
const appleData: FundamentalData = {
  marketCap: 2500000000000, // $2.5T
  freeCashFlow: 92000000000, // $92B
  revenue: 365000000000, // $365B
  netIncome: 94000000000, // $94B
  totalDebt: 120000000000, // $120B
  totalEquity: 180000000000, // $180B
  returnOnEquity: 0.25, // 25%
  eps: 3.75,
  bookValue: 45.67,
  dividendYield: 0.015, // 1.5%
  currentPrice: 150.00,
  historicalGrowthRate: 0.12, // 12% growth
  operatingMargin: 0.30 // 30%
};

// Demo data for a lower quality stock
const poorQualityData: FundamentalData = {
  marketCap: 50000000000, // $50B
  freeCashFlow: 2000000000, // $2B
  revenue: 25000000000, // $25B
  netIncome: 1000000000, // $1B
  totalDebt: 40000000000, // $40B (high debt)
  totalEquity: 15000000000, // $15B
  returnOnEquity: 0.05, // 5% (low)
  eps: 1.20,
  bookValue: 18.50,
  dividendYield: 0.00, // No dividend
  currentPrice: 60.00,
  historicalGrowthRate: 0.02, // 2% growth (low)
  operatingMargin: 0.08 // 8% (low)
};

console.log("=".repeat(80));
console.log("WARREN BUFFETT STOCK ANALYSIS DEMONSTRATION");
console.log("=".repeat(80));

// Analyze Apple (High Quality Stock)
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

// Analyze Poor Quality Stock
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

// Explain Warren Buffett's Key Principles
console.log("\n\n🎯 WARREN BUFFETT'S INVESTMENT PRINCIPLES");
console.log("=".repeat(60));

const principles = [
  {
    title: "💎 Value Investing",
    description: "Buy businesses trading below their intrinsic value. Focus on the business, not the stock price."
  },
  {
    title: "🛡️ Margin of Safety", 
    description: "Only invest when you can buy at a significant discount to intrinsic value (typically 20-30%)."
  },
  {
    title: "📈 Quality Business",
    description: "Look for businesses with consistent earnings growth, high return on equity, and competitive advantages."
  },
  {
    title: "💰 Cash Flow Focus",
    description: "Prioritize businesses that generate strong and growing free cash flows."
  },
  {
    title: "🏰 Economic Moats",
    description: "Invest in companies with sustainable competitive advantages that protect their market position."
  },
  {
    title: "⏰ Long-term Perspective",
    description: "Hold quality businesses for years or decades, not months or weeks."
  }
];

principles.forEach(principle => {
  console.log(`\n${principle.title}`);
  console.log(`${principle.description}`);
});

// Show calculation methodology
console.log("\n\n🔬 CALCULATION METHODOLOGY");
console.log("=".repeat(60));

console.log(`
📊 Quality Score Components:
• Earnings Growth (25%): Based on historical growth rate
• Return on Equity (25%): Measures management effectiveness  
• Debt Management (20%): Lower debt-to-equity is better
• Competitive Advantage (15%): Based on operating margins
• Management Effectiveness (15%): Combined ROE and margin analysis

💰 Intrinsic Value Calculation:
• Uses Discounted Cash Flow (DCF) model
• Projects free cash flow for 10 years
• Applies 10% discount rate (Buffett's typical rate)
• Includes terminal value with 3% perpetual growth
• Accounts for risk through conservative assumptions

🛡️ Investment Recommendation Logic:
• BUY: Margin of safety >20% AND Quality score >70%
• MODERATE BUY: Margin of safety >10% AND Quality score >60%  
• HOLD: Margin of safety >0% AND Quality score >50%
• SELL: Negative margin of safety OR poor quality metrics
`);

console.log("\n" + "=".repeat(80));
console.log("END OF WARREN BUFFETT ANALYSIS DEMONSTRATION");
console.log("=".repeat(80));