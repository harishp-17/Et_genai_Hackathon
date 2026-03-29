"""
Quick-start test script for SignalX AI Challenge Features
Tests pattern detection and opportunity scoring
"""

import yfinance as yf  # type: ignore
import pandas as pd
from typing import cast
from tech_patterns import PatternDetector, TechnicalAnalyzer
from opportunity_radar import OpportunityRadar, CompanyMetrics


def test_pattern_detection():
    """Test chart pattern detection"""
    print("\n" + "="*70)
    print("TEST 1: CHART PATTERN DETECTION")
    print("="*70)
    
    # Download sample data
    ticker = 'RELIANCE.NS'
    print(f"\nDownloading historical data for {ticker}...")
    df = yf.download(ticker, period='1y', progress=False)
    
    if df is None:
        print(f"Failed to download data for {ticker}")
        return None
    
    if df.empty:
        print(f"Failed to download data for {ticker}")
        return None
    
    print(f"Downloaded {len(df)} trading days")
    
    # Detect patterns
    detector = PatternDetector()
    results = detector.detect_all_patterns(df)  # type: ignore
    
    print(f"\nTrend: {results['trend']}")
    print(f"Patterns Detected: {len(results['patterns'])}")
    
    if results['patterns']:
        print("\nDetailed Patterns:")
        for i, pattern in enumerate(results['patterns'], 1):
            print(f"\n  {i}. {pattern['pattern_type']}")
            print(f"     Signal: {pattern['signal']}")
            print(f"     Confidence: {pattern['confidence']*100:.1f}%")
            print(f"     Description: {pattern['description']}")
    else:
        print("\nNo specific patterns detected in recent data")
    
    return df


def test_technical_analysis(df):
    """Test technical indicator calculation"""
    print("\n" + "="*70)
    print("TEST 2: TECHNICAL ANALYSIS & INDICATORS")
    print("="*70)
    
    # Add indicators
    df = TechnicalAnalyzer.add_indicators(df)
    
    # Generate signals
    signals = TechnicalAnalyzer.generate_signal(df)
    
    print("\nLatest Technical Signals:")
    print(f"  Timestamp: {signals['timestamp']}")
    print(f"  RSI(14): {signals['rsi']['value']} - {signals['rsi']['signal']}")
    print(f"  Trend: {signals['trend']}")
    print(f"  MACD: {signals['macd']}")
    print(f"  Price Position: {signals['price_position']}")
    
    # Show last 5 days
    print("\nLast 5 Days Technical Data:")
    print(df[['Close', 'EMA_20', 'EMA_50', 'RSI_14']].tail(5).to_string())


def test_opportunity_scoring():
    """Test opportunity radar scoring"""
    print("\n" + "="*70)
    print("TEST 3: OPPORTUNITY RADAR SCORING")
    print("="*70)
    
    # Create radar
    radar = OpportunityRadar(
        valuation_weight=0.25,
        growth_weight=0.25,
        profitability_weight=0.25,
        financial_health_weight=0.15,
        technical_weight=0.10
    )
    
    # Test with multiple sample companies
    companies = [
        CompanyMetrics(
            company_id='RELIANCE',
            company_name='Reliance Industries Limited',
            pe_ratio=20.5,
            pb_ratio=2.8,
            price_to_sales=2.5,
            sales_cagr_5y=9.2,
            profit_cagr_5y=11.8,
            roe=11.2,
            roce=9.1,
            profit_margin=8.3,
            debt_to_equity=0.35,
            current_ratio=1.42,
            rsi_14=58,
            trend='Uptrend',
            dividend_yield=2.0
        ),
        CompanyMetrics(
            company_id='TCS',
            company_name='Tata Consultancy Services',
            pe_ratio=24.3,
            pb_ratio=8.5,
            price_to_sales=6.2,
            sales_cagr_5y=7.8,
            profit_cagr_5y=8.5,
            roe=45.2,
            roce=38.5,
            profit_margin=21.5,
            debt_to_equity=0.05,
            current_ratio=2.15,
            rsi_14=62,
            trend='Uptrend',
            dividend_yield=1.8
        ),
        CompanyMetrics(
            company_id='INFY',
            company_name='Infosys Limited',
            pe_ratio=35.2,
            pb_ratio=12.1,
            price_to_sales=8.9,
            sales_cagr_5y=5.2,
            profit_cagr_5y=2.8,
            roe=28.0,
            roce=22.0,
            profit_margin=18.0,
            debt_to_equity=0.12,
            current_ratio=2.45,
            rsi_14=48,
            trend='Sideways',
            dividend_yield=1.5
        ),
        CompanyMetrics(
            company_id='HDFC',
            company_name='HDFC Bank Limited',
            pe_ratio=18.7,
            pb_ratio=2.2,
            price_to_sales=4.5,
            sales_cagr_5y=14.3,
            profit_cagr_5y=18.5,
            roe=15.8,
            roce=14.2,
            profit_margin=35.5,
            debt_to_equity=0.08,
            current_ratio=1.98,
            rsi_14=65,
            trend='Uptrend',
            dividend_yield=2.8
        ),
    ]
    
    # Score each company
    scores = []
    for company in companies:
        score = radar.calculate_opportunity_score(company)
        scores.append((company.company_name, score))
        
        print(f"\n{'-'*70}")
        print(f"Company: {company.company_name}")
        print(f"{'-'*70}")
        print(f"Overall Score: {score.overall_score}/100")
        print(f"Recommendation: {score.recommendation.value}")
        print(f"\nScore Breakdown:")
        print(f"  Valuation:         {score.valuation_score}/100")
        print(f"  Growth:            {score.growth_score}/100")
        print(f"  Profitability:     {score.profitability_score}/100")
        print(f"  Financial Health:  {score.financial_health_score}/100")
        print(f"  Technical:         {score.technical_score}/100")
        
        print(f"\nKey Strengths:")
        for strength in score.key_strengths:
            print(f"  ✓ {strength}")
        
        print(f"\nKey Weaknesses:")
        for weakness in score.key_weaknesses:
            print(f"  ✗ {weakness}")
        
        print(f"\nInvestment Thesis:")
        print(f"  {score.investment_thesis}")
    
    # Ranking
    print(f"\n{'='*70}")
    print("RANKING SUMMARY")
    print(f"{'='*70}")
    
    ranked = sorted(scores, key=lambda x: x[1].overall_score, reverse=True)
    for rank, (name, score) in enumerate(ranked, 1):
        print(f"{rank}. {name:<35} Score: {score.overall_score:>6}/100 | {score.recommendation.value}")
    
    return scores


def test_multi_ticker_analysis():
    """Test analysis across multiple Indian stocks"""
    print("\n" + "="*70)
    print("TEST 4: MULTI-TICKER PATTERN ANALYSIS")
    print("="*70)
    
    tickers = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS']
    detector = PatternDetector()
    
    print("\nAnalyzing patterns across key Indian stocks...\n")
    
    for ticker in tickers:
        try:
            # Download data
            df = yf.download(ticker, period='1y', progress=False)
            
            if df is None:
                print(f"Failed to download data for {ticker}")
                continue
            
            if df.empty:
                print(f"Failed to download data for {ticker}")
                continue
            
            # Detect patterns
            results = detector.detect_all_patterns(df)  # type: ignore
            
            # Get latest close
            latest_close = df['Close'].iloc[-1]
            
            print(f"{ticker:12} | Close: ₹{latest_close:>8.2f} | Trend: {results['trend']:<20} | Patterns: {len(results['patterns'])}")
            
            if results['patterns']:
                for pattern in results['patterns'][:2]:  # Show top 2
                    print(f"             ├─ {pattern['pattern_type']:<25} ({pattern['signal']})")
        
        except Exception as e:
            print(f"{ticker:12} | Error: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SignalX - AI for Indian Investor Challenge")
    print("Feature Test Suite")
    print("="*70)
    
    # Test 1: Pattern Detection
    df = test_pattern_detection()
    
    # Test 2: Technical Analysis
    test_technical_analysis(df)
    
    # Test 3: Opportunity Scoring
    test_opportunity_scoring()
    
    # Test 4: Multi-ticker Analysis
    test_multi_ticker_analysis()
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)
    print("\nNext Steps:")
    print("1. Run: python test_ai_features.py")
    print("2. Integrate patterns/scores into Flask endpoints")
    print("3. Add UI components to display results")
    print("4. Create scheduled jobs for real-time updates")
    print("="*70 + "\n")
