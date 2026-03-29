"""
Setup script to initialize the alerts table and demonstrate alert generation
Run this script once to create the database schema
"""

from typing import Optional, List
from app import app, db, Alert, Companies
import yfinance as yf  # type: ignore
from tech_patterns import PatternDetector, TechnicalAnalyzer
from opportunity_radar import OpportunityRadar, CompanyMetrics

def init_alerts_database():
    """Create the alerts table in the database"""
    with app.app_context():
        db.create_all()
        print("✅ Alerts table created successfully!")


def analyze_and_create_alerts(ticker: str):
    """
    Analyze a stock and create alerts for patterns and opportunities
    This can be run periodically (e.g., daily) to scan all stocks
    """
    with app.app_context():
        # Get company from database
        company = Companies.query.filter_by(id=ticker).first()
        if not company:
            print(f"❌ Company {ticker} not found in database")
            return
        
        print(f"\n📊 Analyzing {ticker}...")
        
        # Download historical data
        df = yf.download(ticker, period='1y', progress=False)
        
        if df is None or df.empty:
            print(f"❌ Failed to download data for {ticker}")
            return
        
        # --- PATTERN DETECTION ---
        try:
            detector = PatternDetector()
            patterns_result = detector.detect_all_patterns(df)
            
            if patterns_result.get('patterns'):
                message = f"Found {len(patterns_result['patterns'])} bullish patterns!"
                from app import create_alert
                create_alert(
                    company_id=ticker,
                    alert_type="pattern",
                    message=message,
                    details={
                        "patterns": [
                            {
                                "pattern_type": p["pattern_type"],
                                "signal": p["signal"],
                                "confidence": p["confidence"],
                            }
                            for p in patterns_result["patterns"]
                        ],
                        "trend": patterns_result["trend"],
                    }
                )
                print(f"  ✅ Pattern Alert Created: {message}")
        except Exception as e:
            print(f"  ⚠️ Pattern detection failed: {e}")
        
        # --- OPPORTUNITY SCORING ---
        try:
            radar = OpportunityRadar()
            
            # Prepare metrics from company data and recent data
            metrics = CompanyMetrics(
                company_id=ticker,
                company_name=company.company_name or ticker,
                pe_ratio=15.0,  # You'll get these from your API
                pb_ratio=2.5,
                dividend_yield=2.0,
                sales_cagr_5y=12.0,
                profit_cagr_5y=15.0,
                roe=22.0,
                roce=20.0,
                debt_to_equity=0.5,
                current_ratio=2.0,
                profit_margin=15.0,
                market_cap=50000,
                rsi_14=55,
                trend="uptrend",
            )
            
            score_result = radar.calculate_opportunity_score(metrics)
            score = score_result.overall_score
            
            if score >= 70:  # High opportunity
                message = f"High opportunity score: {score:.0f}/100 - {score_result.recommendation.value}"
                from app import create_alert
                create_alert(
                    company_id=ticker,
                    alert_type="opportunity_score",
                    message=message,
                    details={
                        "score": score,
                        "recommendation": score_result.recommendation.value,
                        "strengths": score_result.key_strengths,
                        "weaknesses": score_result.key_weaknesses,
                        "thesis": score_result.investment_thesis,
                    }
                )
                print(f"  ✅ Opportunity Alert Created: {message}")
        except Exception as e:
            print(f"  ⚠️ Opportunity scoring failed: {e}")
        
        # --- TREND ANALYSIS ---
        try:
            df_with_indicators = TechnicalAnalyzer.add_indicators(df)
            signals = TechnicalAnalyzer.generate_signal(df_with_indicators)
            
            current_trend = signals.get('trend', 'Neutral')
            if current_trend in ['Strong Bullish', 'Bullish']:
                message = f"Strong bullish trend detected ({current_trend})"
                from app import create_alert
                create_alert(
                    company_id=ticker,
                    alert_type="trend_change",
                    message=message,
                    details={
                        "trend": current_trend,
                        "rsi": signals.get('rsi', {}).get('value'),
                        "price_position": signals.get('price_position'),
                    }
                )
                print(f"  ✅ Trend Alert Created: {message}")
        except Exception as e:
            print(f"  ⚠️ Trend analysis failed: {e}")


def bulk_analyze_portfolio(tickers: Optional[list] = None):
    """Analyze multiple stocks and create alerts"""
    with app.app_context():
        if tickers is None:
            # Get all tickers from database
            companies = Companies.query.all()
            tickers = [c.id for c in companies]
        
        print(f"\n📈 Analyzing {len(tickers)} stocks for opportunities...\n")
        
        for ticker in tickers:
            try:
                analyze_and_create_alerts(ticker)
            except Exception as e:
                print(f"  ❌ Error analyzing {ticker}: {e}")
        
        print(f"\n✅ Analysis complete!")


if __name__ == "__main__":
    import sys
    
    # Initialize database
    print("🔧 Initializing alerts database...")
    init_alerts_database()
    
    # Example: Analyze a few specific stocks
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
        print(f"\nAnalyzing {ticker}...")
        analyze_and_create_alerts(ticker)
    else:
        # Analyze all companies in database
        print("\nRunning bulk analysis on all companies...")
        bulk_analyze_portfolio()
