# SignalX AI Challenge - Quick Implementation Guide

## 🚀 IMMEDIATE ACTIONS (Today)

### Step 1: Install Dependencies
```bash
cd c:\Users\Harish\VS Code\Bluestock-module\MLFA
pip install yfinance pandas_ta plotly flask-cors
```

### Step 2: Test the New Features
```bash
python test_ai_features.py
```
This will:
- Download real stock data for Reliance, TCS, Infosys, HDFC
- Detect chart patterns (bullish engulfing, triangles, etc.)
- Calculate opportunity scores
- Display technical indicators

Expected output shows patterns found and opportunity rankings!

### Step 3: Quick Integration Test
```python
# Quick test in Python shell
from tech_patterns import PatternDetector, TechnicalAnalyzer
from opportunity_radar import OpportunityRadar, CompanyMetrics
import yfinance as yf

# Test pattern detection
ticker = 'RELIANCE.NS'
df = yf.download(ticker, period='1y', progress=False)
detector = PatternDetector()
patterns = detector.detect_all_patterns(df)
print(f"Patterns detected: {len(patterns['patterns'])}")
print(f"Trend: {patterns['trend']}")

# Test opportunity scoring
radar = OpportunityRadar()
metrics = CompanyMetrics(
    company_id='RELIANCE',
    company_name='Reliance',
    pe_ratio=20, roe=12, roce=9, 
    sales_cagr_5y=10, profit_cagr_5y=12
)
score = radar.calculate_opportunity_score(metrics)
print(f"Score: {score.overall_score} - {score.recommendation.value}")
```

---

## 📊 WEEK 1-2: DATABASE SETUP

### Create New Tables
Run in MySQL:
```sql
-- Stock price data (OHLCV)
CREATE TABLE stock_prices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id VARCHAR(255) NOT NULL,
    trading_date DATE NOT NULL,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date (company_id, trading_date),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE INDEX idx_company_date ON stock_prices(company_id, trading_date DESC);

-- Detected patterns
CREATE TABLE chart_patterns (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(100),
    signal VARCHAR(50),
    confidence FLOAT,
    detected_date DATE,
    pattern_start_date DATE,
    pattern_end_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE INDEX idx_company_patterns ON chart_patterns(company_id, created_at DESC);

-- Opportunity scores
CREATE TABLE opportunity_scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id VARCHAR(255) NOT NULL,
    overall_score FLOAT,
    valuation_score FLOAT,
    growth_score FLOAT,
    profitability_score FLOAT,
    financial_health_score FLOAT,
    technical_score FLOAT,
    recommendation VARCHAR(50),
    key_strengths JSON,
    key_weaknesses JSON,
    investment_thesis TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE INDEX idx_company_scores ON opportunity_scores(company_id, updated_at DESC);
```

### Create SQLAlchemy Models
Add to `models.py`:
```python
from datetime import datetime

class StockPrice(Base):
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(String(255), ForeignKey('companies.id'))
    trading_date = Column(Date)
    open_price = Column(Numeric(12, 4))
    high_price = Column(Numeric(12, 4))
    low_price = Column(Numeric(12, 4))
    close_price = Column(Numeric(12, 4))
    volume = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChartPattern(Base):
    __tablename__ = "chart_patterns"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(String(255), ForeignKey('companies.id'))
    pattern_type = Column(String(100))
    signal = Column(String(50))
    confidence = Column(Float)
    detected_date = Column(Date)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class OpportunityScore(Base):
    __tablename__ = "opportunity_scores"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(String(255), ForeignKey('companies.id'))
    overall_score = Column(Float)
    valuation_score = Column(Float)
    growth_score = Column(Float)
    profitability_score = Column(Float)
    financial_health_score = Column(Float)
    technical_score = Column(Float)
    recommendation = Column(String(50))
    key_strengths = Column(JSON)
    key_weaknesses = Column(JSON)
    investment_thesis = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 📡 WEEK 2-3: FLASK API ENDPOINTS

### Add to `app.py`:

```python
from flask import jsonify
from tech_patterns import PatternDetector, TechnicalAnalyzer
from opportunity_radar import OpportunityRadar, CompanyMetrics
import yfinance as yf
from datetime import datetime, timedelta

# ========== STOCK DATA ENDPOINTS ==========

@app.route("/api/stock-data/<company_id>")
def get_stock_data(company_id):
    """Fetch and cache historical OHLCV data"""
    try:
        ticker = f"{company_id}.NS"
        
        # Try to get from cache first
        existing = db.session.query(StockPrice).filter_by(company_id=company_id).all()
        
        if not existing or len(existing) < 250:  # If less than 1 year
            # Download 2 years of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)
            
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            # Save to database
            for date, row in df.iterrows():
                price = StockPrice(
                    company_id=company_id,
                    trading_date=date.date(),
                    open_price=float(row['Open']),
                    high_price=float(row['High']),
                    low_price=float(row['Low']),
                    close_price=float(row['Close']),
                    volume=int(row['Volume'])
                )
                db.session.add(price)
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'company_id': company_id,
            'data_points': len(existing)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ========== PATTERN DETECTION ENDPOINTS ==========

@app.route("/api/patterns/<company_id>")
def get_patterns(company_id):
    """Detect chart patterns for a company"""
    try:
        ticker = f"{company_id}.NS"
        
        # Get last 250 days of data
        df = yf.download(ticker, period='1y', progress=False)
        
        if df is None or len(df) == 0:
            return jsonify({'error': f'No data for {ticker}'}), 404
        
        # Detect patterns
        detector = PatternDetector()
        results = detector.detect_all_patterns(df)
        
        # Save to database
        for pattern in results['patterns']:
            existing = db.session.query(ChartPattern).filter_by(
                company_id=company_id,
                pattern_type=pattern['pattern_type'],
                detected_date=datetime.now().date()
            ).first()
            
            if not existing:
                p = ChartPattern(
                    company_id=company_id,
                    pattern_type=pattern['pattern_type'],
                    signal=pattern['signal'],
                    confidence=pattern['confidence'],
                    detected_date=datetime.now().date(),
                    description=pattern['description']
                )
                db.session.add(p)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'company_id': company_id,
            'trend': results['trend'],
            'patterns_detected': len(results['patterns']),
            'patterns': results['patterns']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ========== OPPORTUNITY RADAR ENDPOINTS ==========

@app.route("/api/opportunity-score/<company_id>")
def get_opportunity_score(company_id):
    """Calculate opportunity score for a company"""
    try:
        # Fetch company fundamentals from API or DB
        base_company = Companies.query.filter_by(id=company_id).first()
        if not base_company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get API data for full metrics
        payload = fetch_company_from_api(company_id)
        if not payload:
            return jsonify({'error': 'Could not fetch company data'}), 404
        
        api_company = payload['company']
        api_data = payload['data']
        
        # Extract metrics from API
        metrics = map_api_to_metrics(api_data)
        
        # Get technical data
        ticker = f"{company_id}.NS"
        df = yf.download(ticker, period='1y', progress=False)
        df = TechnicalAnalyzer.add_indicators(df)
        
        # Determine trend
        detector = PatternDetector()
        trend = detector._determine_trend(df)
        
        # Build CompanyMetrics
        company_metrics = CompanyMetrics(
            company_id=company_id,
            company_name=base_company.company_name,
            pe_ratio=float(api_company.get('pe_ratio', 20)) if api_company.get('pe_ratio') else None,
            pb_ratio=float(api_company.get('pb_ratio', 2)) if api_company.get('pb_ratio') else None,
            sales_cagr_5y=float(metrics.get('sales_cagr_5y', 0)) if metrics.get('sales_cagr_5y') else None,
            profit_cagr_5y=float(metrics.get('profit_cagr_5y', 0)) if metrics.get('profit_cagr_5y') else None,
            roe=base_company.roe_percentage,
            roce=base_company.roce_percentage,
            debt_to_equity=float(api_company.get('debt_to_equity', 0.5)) if api_company.get('debt_to_equity') else None,
            rsi_14=float(df['RSI_14'].iloc[-1]) if 'RSI_14' in df.columns else None,
            trend=trend,
            dividend_yield=float(api_company.get('dividend_yield', 2)) if api_company.get('dividend_yield') else None
        )
        
        # Calculate score
        radar = OpportunityRadar()
        score = radar.calculate_opportunity_score(company_metrics)
        
        # Save to database
        existing = db.session.query(OpportunityScore).filter_by(company_id=company_id).first()
        
        if existing:
            db.session.delete(existing)
        
        opp_score = OpportunityScore(
            company_id=company_id,
            overall_score=score.overall_score,
            valuation_score=score.valuation_score,
            growth_score=score.growth_score,
            profitability_score=score.profitability_score,
            financial_health_score=score.financial_health_score,
            technical_score=score.technical_score,
            recommendation=score.recommendation.value,
            key_strengths=score.key_strengths,
            key_weaknesses=score.key_weaknesses,
            investment_thesis=score.investment_thesis
        )
        
        db.session.add(opp_score)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'company_id': company_id,
            'company_name': base_company.company_name,
            'overall_score': score.overall_score,
            'recommendation': score.recommendation.value,
            'scores': {
                'valuation': score.valuation_score,
                'growth': score.growth_score,
                'profitability': score.profitability_score,
                'financial_health': score.financial_health_score,
                'technical': score.technical_score
            },
            'strengths': score.key_strengths,
            'weaknesses': score.key_weaknesses,
            'thesis': score.investment_thesis
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ========== RANKING ENDPOINTS ==========

@app.route("/api/top-opportunities")
def get_top_opportunities():
    """Get top opportunity radar scores"""
    try:
        scores = db.session.query(OpportunityScore).order_by(
            OpportunityScore.overall_score.desc()
        ).limit(10).all()
        
        return jsonify({
            'status': 'success',
            'count': len(scores),
            'opportunities': [{
                'company_id': s.company_id,
                'overall_score': s.overall_score,
                'recommendation': s.recommendation,
                'thesis': s.investment_thesis
            } for s in scores]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

---

## 🎨 WEEK 3-4: FRONTEND ENHANCEMENTS

Add to `company_detail.html`:

```html
<!-- Opportunity Score Card -->
<div class="row mt-5">
  <div class="col-lg-4">
    <div class="card">
      <div class="card-header bg-success text-white">
        <h5>🎯 Opportunity Radar Score</h5>
      </div>
      <div class="card-body text-center">
        <h2 id="oppScore">--</h2>
        <p class="h6" id="recommendation"></p>
        <div class="mt-3" id="scoreBreakdown"></div>
      </div>
    </div>
  </div>
  
  <div class="col-lg-8">
    <div class="card">
      <div class="card-header bg-info text-white">
        <h5>📈 Chart Pattern Intelligence</h5>
      </div>
      <div class="card-body">
        <canvas id="priceChart"></canvas>
        <div id="patternsList" class="mt-3"></div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<script>
// Load opportunity score
const companyId = "{{ company.id }}";

fetch(`/api/opportunity-score/${companyId}`)
  .then(r => r.json())
  .then(data => {
    if (data.status === 'success') {
      document.getElementById('oppScore').innerText = data.overall_score;
      document.getElementById('recommendation').innerHTML = 
        `<strong>${data.recommendation}</strong>`;
      
      const breakdown = `
        <div class="row text-center">
          <div class="col-6"><small>Valuation</small><br><strong>${data.scores.valuation}</strong></div>
          <div class="col-6"><small>Growth</small><br><strong>${data.scores.growth}</strong></div>
          <div class="col-6"><small>Profitability</small><br><strong>${data.scores.profitability}</strong></div>
          <div class="col-6"><small>Tech</small><br><strong>${data.scores.technical}</strong></div>
        </div>
      `;
      document.getElementById('scoreBreakdown').innerHTML = breakdown;
    }
  });

// Load patterns
fetch(`/api/patterns/${companyId}`)
  .then(r => r.json())
  .then(data => {
    if (data.patterns_detected > 0) {
      let html = `<strong>Trend:</strong> ${data.trend}<br><br>`;
      data.patterns.forEach((p, i) => {
        html += `<p><strong>${p.pattern_type}</strong> - Signal: ${p.signal} (${(p.confidence*100).toFixed(0)}%)</p>`;
      });
      document.getElementById('patternsList').innerHTML = html;
    } else {
      document.getElementById('patternsList').innerHTML = '<em>No specific patterns detected</em>';
    }
  });
</script>
```

---

## 🔄 WEEK 4-5: BACKGROUND JOBS

Create `scheduled_tasks.py`:
```python
from celery import Celery
from app import app, db
from models import Companies
from api_client import fetch_company_data
import yfinance as yf

celery = Celery(app.name, broker='redis://localhost:6379')

@celery.task
def update_all_patterns():
    """Daily task to update patterns for all companies"""
    companies = db.session.query(Companies).all()
    
    for company in companies:
        try:
            ticker = f"{company.id}.NS"
            df = yf.download(ticker, period='1y', progress=False)
            # Run pattern detection...
        except:
            pass

@celery.task
def update_all_scores():
    """Daily task to update opportunity scores"""
    companies = db.session.query(Companies).all()
    
    for company in companies:
        try:
            # Fetch data and calculate score...
        except:
            pass

# Schedule in a separate worker:
# celery -A scheduled_tasks worker --beat
```

---

## ⏱️ TESTING CHECKLIST

- [ ] Run `python test_ai_features.py` - passes without errors
- [ ] Database tables created successfully
- [ ] `/api/stock-data/RELIANCE` returns data
- [ ] `/api/patterns/RELIANCE` returns patterns
- [ ] `/api/opportunity-score/RELIANCE` returns score
- [ ] `/api/top-opportunities` returns ranking
- [ ] UI displays opportunity scores
- [ ] UI displays detected patterns
- [ ] UI displays technical indicators

---

## 🎯 CHALLENGE SUBMISSION CHECKLIST

✅ **Opportunity Radar**
- [ ] Intelligent scoring system implemented
- [ ] Combines fundamental + technical metrics
- [ ] Real-time opportunity identification
- [ ] Ranking system for opportunities
- [ ] Alert mechanism for high-score companies

✅ **Chart Pattern Intelligence**
- [ ] 12+ pattern types detected
- [ ] Technical indicators calculated
- [ ] Confidence levels for signals
- [ ] Trend analysis included
- [ ] Visualization on charts

✅ **Integration**
- [ ] Real market data (yfinance/NSE)
- [ ] Database persistence
- [ ] REST API endpoints
- [ ] Frontend visualization
- [ ] Responsive UI

---

## 📞 TROUBLESHOOTING

**Issue**: ModuleNotFoundError for tech_patterns
- **Fix**: `pip install -r requirements.txt` (create one if needed)

**Issue**: No yfinance data
- **Fix**: Check internet connection, try different ticker format

**Issue**: MySQL connection errors
- **Fix**: Verify credentials in `db_config.py`, ensure MySQL is running

**Issue**: Performance slow with large datasets
- **Fix**: Add database indexes, use pagination, cache results in Redis

---

## 📚 DOCUMENTATION

Detailed documentation available in:
- `AI_CHALLENGE_ANALYSIS.md` - Complete strategic planning
- `tech_patterns.py` - Pattern detection code + docstrings
- `opportunity_radar.py` - Scoring algorithm + docstrings
- `test_ai_features.py` - Working examples

---

**Created**: March 25, 2026  
**Project**: SignalX - AI for the Indian Investor Challenge  
**Status**: Ready for Implementation
