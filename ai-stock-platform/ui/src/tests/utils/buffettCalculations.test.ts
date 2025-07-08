/**
 * Warren Buffett Calculations Tests
 * Created: 2025-01-09
 * Author: AI Assistant
 */
import { describe, it, expect } from 'vitest';
import {
  calculateIntrinsicValue,
  calculateMarginOfSafety,
  assessBusinessQuality,
  calculateQualityScore,
  generateInvestmentRecommendation,
  calculateBuffettMetrics,
  type FundamentalData,
  type IntrinsicValueInputs,
  type BusinessQualityMetrics
} from '../../utils/buffettCalculations';

describe('Buffett Calculations', () => {
  describe('calculateIntrinsicValue', () => {
    it('should calculate intrinsic value using DCF model', () => {
      const inputs: IntrinsicValueInputs = {
        freeCashFlow: 1000000000, // $1B
        growthRate: 0.10, // 10%
        discountRate: 0.10, // 10%
        terminalGrowthRate: 0.03, // 3%
        yearsToProject: 10
      };

      const result = calculateIntrinsicValue(inputs);
      expect(result).toBeGreaterThan(0);
      expect(result).toBeGreaterThan(inputs.freeCashFlow);
    });

    it('should return 0 for zero cash flow', () => {
      const inputs: IntrinsicValueInputs = {
        freeCashFlow: 0,
        growthRate: 0.10,
        discountRate: 0.10,
        terminalGrowthRate: 0.03,
        yearsToProject: 10
      };

      const result = calculateIntrinsicValue(inputs);
      expect(result).toBe(0);
    });
  });

  describe('calculateMarginOfSafety', () => {
    it('should calculate positive margin of safety when undervalued', () => {
      const intrinsicValue = 100;
      const marketPrice = 80;
      const result = calculateMarginOfSafety(intrinsicValue, marketPrice);
      expect(result).toBe(25); // (100-80)/80 * 100 = 25%
    });

    it('should calculate negative margin of safety when overvalued', () => {
      const intrinsicValue = 80;
      const marketPrice = 100;
      const result = calculateMarginOfSafety(intrinsicValue, marketPrice);
      expect(result).toBe(-20); // (80-100)/100 * 100 = -20%
    });

    it('should return 0 for zero market price', () => {
      const result = calculateMarginOfSafety(100, 0);
      expect(result).toBe(0);
    });
  });

  describe('assessBusinessQuality', () => {
    it('should assess high quality business correctly', () => {
      const data: FundamentalData = {
        marketCap: 1000000000,
        freeCashFlow: 100000000,
        revenue: 500000000,
        netIncome: 75000000,
        totalDebt: 50000000,
        totalEquity: 200000000,
        returnOnEquity: 0.20, // 20%
        eps: 5.0,
        bookValue: 40.0,
        dividendYield: 0.02,
        currentPrice: 50.0,
        historicalGrowthRate: 0.12, // 12%
        operatingMargin: 0.18 // 18%
      };

      const result = assessBusinessQuality(data);
      expect(result.highROE).toBeGreaterThan(80); // Should score high for 20% ROE
      expect(result.competitiveAdvantage).toBeGreaterThan(80); // Should score high for 18% margin
      expect(result.consistentEarningsGrowth).toBeGreaterThan(80); // Should score high for 12% growth
    });

    it('should assess low quality business correctly', () => {
      const data: FundamentalData = {
        marketCap: 1000000000,
        freeCashFlow: 10000000,
        revenue: 500000000,
        netIncome: 5000000,
        totalDebt: 300000000,
        totalEquity: 100000000,
        returnOnEquity: 0.05, // 5%
        eps: 1.0,
        bookValue: 20.0,
        dividendYield: 0.0,
        currentPrice: 30.0,
        historicalGrowthRate: 0.02, // 2%
        operatingMargin: 0.05 // 5%
      };

      const result = assessBusinessQuality(data);
      expect(result.highROE).toBeLessThan(50); // Should score low for 5% ROE
      expect(result.competitiveAdvantage).toBeLessThan(50); // Should score low for 5% margin
      expect(result.lowDebtToEquity).toBeLessThan(50); // Should score low for high debt
    });
  });

  describe('calculateQualityScore', () => {
    it('should calculate quality score correctly', () => {
      const metrics: BusinessQualityMetrics = {
        consistentEarningsGrowth: 80,
        highROE: 90,
        lowDebtToEquity: 70,
        competitiveAdvantage: 85,
        managementEffectiveness: 75
      };

      const result = calculateQualityScore(metrics);
      expect(result).toBeGreaterThan(70);
      expect(result).toBeLessThan(100);
    });
  });

  describe('generateInvestmentRecommendation', () => {
    it('should recommend BUY for high margin of safety and quality', () => {
      const { recommendation, reasoning } = generateInvestmentRecommendation(
        25, // 25% margin of safety
        85, // 85% quality score
        {
          marketCap: 1000000000,
          freeCashFlow: 100000000,
          revenue: 500000000,
          netIncome: 75000000,
          totalDebt: 50000000,
          totalEquity: 200000000,
          returnOnEquity: 0.20,
          eps: 5.0,
          bookValue: 40.0,
          dividendYield: 0.02,
          currentPrice: 50.0,
          historicalGrowthRate: 0.12,
          operatingMargin: 0.18
        }
      );

      expect(recommendation).toBe('BUY');
      expect(reasoning).toContain('Excellent margin of safety (25.0%)');
      expect(reasoning).toContain('High quality business (score: 85.0)');
    });

    it('should recommend SELL for negative margin of safety', () => {
      const { recommendation, reasoning } = generateInvestmentRecommendation(
        -20, // -20% margin of safety
        40, // 40% quality score
        {
          marketCap: 1000000000,
          freeCashFlow: 50000000,
          revenue: 500000000,
          netIncome: 25000000,
          totalDebt: 300000000,
          totalEquity: 100000000,
          returnOnEquity: 0.05,
          eps: 2.0,
          bookValue: 20.0,
          dividendYield: 0.0,
          currentPrice: 60.0,
          historicalGrowthRate: 0.02,
          operatingMargin: 0.05
        }
      );

      expect(recommendation).toBe('SELL');
      expect(reasoning).toContain('Negative margin of safety (-20.0%)');
    });

    it('should recommend HOLD for moderate conditions', () => {
      const { recommendation, reasoning } = generateInvestmentRecommendation(
        5, // 5% margin of safety
        60, // 60% quality score
        {
          marketCap: 1000000000,
          freeCashFlow: 75000000,
          revenue: 500000000,
          netIncome: 50000000,
          totalDebt: 150000000,
          totalEquity: 200000000,
          returnOnEquity: 0.12,
          eps: 3.0,
          bookValue: 30.0,
          dividendYield: 0.01,
          currentPrice: 40.0,
          historicalGrowthRate: 0.08,
          operatingMargin: 0.12
        }
      );

      expect(recommendation).toBe('HOLD');
      expect(reasoning).toContain('Positive margin of safety (5.0%)');
    });
  });

  describe('calculateBuffettMetrics', () => {
    it('should calculate comprehensive Buffett metrics', () => {
      const data: FundamentalData = {
        marketCap: 1000000000,
        freeCashFlow: 100000000,
        revenue: 500000000,
        netIncome: 75000000,
        totalDebt: 50000000,
        totalEquity: 200000000,
        returnOnEquity: 0.20,
        eps: 5.0,
        bookValue: 40.0,
        dividendYield: 0.02,
        currentPrice: 50.0,
        historicalGrowthRate: 0.12,
        operatingMargin: 0.18
      };

      const result = calculateBuffettMetrics(data);
      expect(result.intrinsicValue).toBeGreaterThan(0);
      expect(result.qualityScore).toBeGreaterThan(0);
      expect(result.qualityScore).toBeLessThanOrEqual(100);
      expect(['BUY', 'HOLD', 'SELL']).toContain(result.investmentRecommendation);
      expect(result.reasoning).toBeInstanceOf(Array);
      expect(result.reasoning.length).toBeGreaterThan(0);
    });
  });
});