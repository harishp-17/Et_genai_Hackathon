# SignalX - AI Investment Intelligence Platform 📊

## Project Summary
**SignalX** is an intelligent investment analysis platform for Indian stock market investors. It combines **Machine Learning**, **Technical Analysis**, and **Fundamental Analysis** to identify investment opportunities and provide actionable trading signals.

**Location**: `c:\Users\Harish\VS Code\Bluestock-module\MLFA`

---

## 🎯 Core Features

### 1. **Chart Pattern Intelligence** 📈
Detects technical chart patterns and generates trading signals
- **12+ Chart Patterns**: Bullish/Bearish Engulfing, Morning/Evening Star, Hammer, Head & Shoulders, Triangles, Breakouts
- **Technical Indicators**: RSI, MACD, Bollinger Bands, EMA (20, 50)
- **Signals**: BUY, SELL, HOLD with confidence levels
- **File**: `tech_patterns.py` (500+ lines)

### 2. **Opportunity Radar** 🎯
AI-powered investment opportunity scoring system
- **5-Component Analysis**:
  1. **Valuation Score** - P/E, P/B, Price-to-Sales ratios
  2. **Growth Score** - Sales CAGR, Profit CAGR
  3. **Profitability Score** - ROE, ROCE, Profit Margins
  4. **Financial Health Score** - Debt ratios, Current ratios
  5. **Technical Score** - RSI trends, momentum
- **Opportunity Scores**: 0-100 scale with STRONG BUY/BUY/HOLD/SELL recommendations
- **Auto-Generated Reports**: Investment thesis, strengths, weaknesses
- **File**: `opportunity_radar.py` (700+ lines)

### 3. **ML Engine** 🤖
Fundamental analysis engine
- **Pros & Cons Generation**: Auto-generates investment rationale
- **Company Metrics Analysis**: ROE, ROCE, CAGR, debt levels
- **Intelligent Scoring**: Rules-based analysis
- **File**: `ml_engine.py`

### 4. **Alerts System** 🔔
Real-time notifications for:
- New chart patterns detected
- Opportunity scores changing
- Trend reversals
- Database table: `alerts`

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│           SignalX Web Application                   │
├─────────────────────────────────────────────────────┤
│
│  Frontend Layer (HTML/CSS/JavaScript)
│  ├── Dashboard (index.html)
│  ├── Company Listing (all_companies.html)
│  ├── Company Detail (company_detail.html)
│  └── Base Template (base.html)
│
├─────────────────────────────────────────────────────┤
│
│  Backend Layer (Flask REST API)
│  ├── app.py - Main application & routes
│  ├── api_client.py - External API integration
│  └── API Endpoints:
│      ├── GET / - Home page
│      ├── GET /companies - All companies listing
│      ├── GET /company/<id> - Company details
│      └── /api/* - Data endpoints
│
├─────────────────────────────────────────────────────┤
│
│  ML/Analytics Layer
│  ├── tech_patterns.py - Pattern detection
│  ├── opportunity_radar.py - Opportunity scoring
│  ├── ml_engine.py - Pros/cons generation
│  └── test_ai_features.py - Testing suite
│
├─────────────────────────────────────────────────────┤
│
│  Data Layer (MySQL Database)
│  ├── companies - Company master data
│  ├── opportunities - Opportunity scores
│  ├── alerts - User notifications
│  └── stock_prices - OHLCV historical data
│
└─────────────────────────────────────────────────────┘
```

---

## 💾 Database (MySQL)

**Database Name**: `ml`  
**Host**: `127.0.0.1:3306`  
**User**: `root` (no password)

### Tables:

#### 1. **companies** - Master company data
```sql
CREATE TABLE companies (
    id VARCHAR(255) PRIMARY KEY,           -- Ticker symbol
    company_name VARCHAR(255),             -- Full name
    company_logo VARCHAR(255),
    about_company TEXT,
    website VARCHAR(255),
    roe_percentage NUMERIC(12,2),          -- Return on Equity
    roce_percentage NUMERIC(12,2),         -- Return on Capital Employed
    face_value INT,
    book_value INT,
    nse_profile VARCHAR(255),              -- NSE link
    bse_profile VARCHAR(255)               -- BSE link
);
```

#### 2. **alerts** - Notifications table
```sql
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id VARCHAR(255) FK,
    alert_type VARCHAR(50),                -- "pattern", "opportunity_score", "trend_change"
    message TEXT,
    details JSON,                          -- Additional metadata
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. **prosandcons** - Company analysis
```sql
CREATE TABLE prosandcons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id VARCHAR(255),
    pros VARCHAR(255),                     -- Investment strengths
    cons VARCHAR(255)                      -- Investment weaknesses
);
```

### Planned Tables (for full feature implementation):

```sql
-- Stock price data (OHLCV)
CREATE TABLE stock_prices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id VARCHAR(255) FK,
    trading_date DATE,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date (company_id, trading_date)
);

-- Detected chart patterns
CREATE TABLE chart_patterns (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id VARCHAR(255) FK,
    pattern_type VARCHAR(100),
    signal VARCHAR(50),
    confidence FLOAT,
    detected_date DATE,
    pattern_start_date DATE,
    pattern_end_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Opportunity scores
CREATE TABLE opportunity_scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id VARCHAR(255) FK,
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📦 Tech Stack

### Backend
- **Framework**: Flask (Python web framework)
- **ORM**: SQLAlchemy (database abstraction)
- **Database**: MySQL
- **API**: RESTful endpoints

### Frontend
- **HTML/CSS/JavaScript**: Bootstrap templates
- **Templating**: Jinja2

### Data & Analytics
- **yfinance**: Download historical stock data (Yahoo Finance)
- **pandas_ta**: Technical analysis indicators
- **NumPy/Pandas**: Data manipulation
- **plotly**: Chart visualization

### Libraries
```
yfinance          - Stock data fetching
pandas            - Data manipulation
pandas_ta         - Technical analysis
numpy             - Numerical computing
flask             - Web framework
flask-sqlalchemy  - ORM integration
sqlalchemy        - Database ORM
pymysql           - MySQL driver
flask-cors        - Cross-origin support
plotly            - Charting
requests          - HTTP client
```

---

## 📁 Directory Structure & File Descriptions

### Core Application Files

#### **app.py** - Main Flask Application (👈 Currently editing)
- Defines Flask application and routes
- Database models: `Companies`, `Alert`
- Routes:
  - `GET /` - Home page (index.html)
  - `GET /companies` - Company list (all_companies.html)
  - `GET /company/<id>` - Company detail (company_detail.html)
- Integrates with AI modules
- Connects to MySQL database

#### **config.py** - Configuration
```python
COMPANY_EXCEL_PATH = "companies.xlsx"
COMPANY_ID_COLUMN = "company_id"
BASE_URL = "https://signalx.in/server/api/company.php"
API_KEY = "ghfkffu6378382826hhdjgk"
TEST_LIMIT = None  # Set to limit test runs
```

#### **db_config.py** - Database Configuration
```python
HOST = "127.0.0.1"
PORT = 3306
USER = "root"
PASSWORD = ""
DB_NAME = "ml"
```

Provides `get_engine()` function for SQLAlchemy connections.

#### **models.py** - SQLAlchemy Models
- `ProsAndCons` model for database mapping
- Used by `run_ml_to_db.py`

### AI/ML Modules

#### **tech_patterns.py** - Pattern Detection Engine (500+ lines)
**Purpose**: Detects technical chart patterns and generates trading signals

**Main Classes**:

1. **`PatternDetector`**
   - `detect_all_patterns(df)` - Run all pattern detection
   - Candlestick patterns:
     - `_bullish_engulfing()` - Bullish trend reversal
     - `_bearish_engulfing()` - Bearish trend reversal
     - `_morning_star()` - Bottom reversal
     - `_evening_star()` - Top reversal
     - `_hammer()` - Bottom doji indicator
     - `_hanging_man()` - Top doji indicator
   - Chart patterns (10+ bars):
     - `_detect_triangle()` - Continuation pattern
     - `_detect_head_and_shoulders()` - Reversal pattern
     - `_detect_double_bottom()` - Support bounce
     - `_detect_double_top()` - Resistance rejection
   - Trend patterns:
     - `_detect_breakout()` - Price breaks key levels
     - `_detect_pullback()` - Temporary reversal
   - `_determine_trend()` - Uptrend/Downtrend/Sideways

2. **`TechnicalAnalyzer`**
   - `add_indicators(df)` - Calculate: RSI, MACD, Bollinger Bands, EMA
   - `generate_signal(df)` - Generate BUY/SELL/HOLD signals
   - Analyzes momentum, trend, volatility

**Returns**: Pattern results with confidence, signal type, description

**Example Output**:
```
{
  'patterns': [
    {
      'pattern_type': 'Bullish Engulfing',
      'signal': 'BUY',
      'confidence': 0.85,
      'description': 'Strong bullish reversal signal'
    }
  ],
  'trend': 'Uptrend'
}
```

#### **opportunity_radar.py** - Opportunity Scoring (700+ lines)
**Purpose**: AI-powered investment opportunity scoring

**Main Classes**:

1. **`OpportunityRadar`**
   ```python
   radar = OpportunityRadar(
       valuation_weight=0.20,
       growth_weight=0.25,
       profitability_weight=0.25,
       financial_health_weight=0.15,
       technical_weight=0.15
   )
   ```
   - `calculate_opportunity_score(metrics)` - Generate opportunity analysis
   - Weights components (must sum to 1.0)

2. **`CompanyMetrics`** (dataclass)
   ```python
   CompanyMetrics(
       company_id='RELIANCE',
       company_name='Reliance Industries',
       # Valuation
       pe_ratio=20.5,
       pb_ratio=2.8,
       price_to_sales=2.5,
       # Growth
       sales_cagr_5y=12.5,
       profit_cagr_5y=15.2,
       # Profitability
       roe=11.2,
       roce=9.5,
       profit_margin=8.5,
       # Financial Health
       debt_to_equity=0.8,
       current_ratio=1.5,
       # Technical
       rsi_14=55,
       trend='uptrend'
   )
   ```

3. **`OpportunityScore`** (dataclass - Results)
   ```python
   OpportunityScore(
       overall_score=78.5,                  # 0-100
       valuation_score=72.0,
       growth_score=85.0,
       profitability_score=80.0,
       financial_health_score=75.0,
       technical_score=82.0,
       recommendation=RecommendationType.BUY,
       key_strengths=['Strong ROE', 'Growing revenue'],
       key_weaknesses=['High debt', 'Market volatility'],
       investment_thesis='Company shows strong growth...'
   )
   ```

4. **`RecommendationType`** (Enum)
   - `STRONG_BUY`
   - `BUY`
   - `HOLD`
   - `SELL`
   - `STRONG_SELL`

#### **ml_engine.py** - ML Analysis Engine (500+ lines)
**Purpose**: Generate pros and cons for companies

**Main Function**:
```python
generate_pros_cons(company_id, metrics) -> (pros_list, cons_list)

# metrics contains:
{
    'sales_cagr_3y': '12%',
    'sales_cagr_5y': '10%',
    'profit_cagr_3y': '15%',
    'profit_cagr_5y': '12%',
    'roe_3y': '11%',
    'roe_5y': '10%',
    'dividend_payout': '25%',
    'debt_ratio': '0.5'
}
```

**Returns**:
```python
pros = [
    "Company has good return on equity (ROE) track record: 3 Years ROE 11%.",
    "Company has delivered good profit growth of 15%.",
    "Company maintains healthy dividend payout of 25%."
]

cons = [
    "Sales growth is slowing down.",
    "Company has increased debt levels.",
    "Profit margins are declining."
]
```

### Utility Files

#### **api_client.py** - External API Integration
**Purpose**: Fetch company data from SignalX API

**Functions**:
- `load_company_ids(path, column, limit)` - Load from Excel
- `fetch_company_data(company_id)` - Call SignalX API
- `main()` - Command-line testing

**Configuration** (from config.py):
```
BASE_URL: https://signalx.in/server/api/company.php
API_KEY: ghfkffu6378382826hhdjgk
```

#### **run_ml_to_db.py** - ETL Pipeline
**Purpose**: Process company data and save pros/cons to database

**Workflow**:
1. Load company data from Excel
2. Generate pros/cons using ml_engine.py
3. Insert results into `prosandcons` table

#### **setup_alerts.py** - Alert Configuration
**Purpose**: Configure and manage alert rules

#### **test_ai_features.py** - Testing Suite (400+ lines)
**Purpose**: Test and demonstrate all AI features

**Test Functions**:
1. `test_pattern_detection()` - Chart pattern detection
2. `test_technical_analysis()` - Technical indicators
3. `test_opportunity_scoring()` - Opportunity scoring
4. Integration testing with real stock data

**Run Tests**:
```bash
python test_ai_features.py
```

**Test Data**: Reliance, TCS, Infosys, HDFC (NSE tickers)

### Frontend Templates (HTML)

Located in `templates/` folder:

#### **base.html** - Base Template
- Navigation bar
- Layout structure
- Reusable components
- CSS styling (Bootstrap)

#### **index.html** - Dashboard/Home
- Company overview
- Key metrics display
- Quick links to features

#### **all_companies.html** - Companies Listing
- Sortable company list
- Filters (ROE, ROCE)
- "Exclusive Companies" badge (ROE ≥ 20%, ROCE ≥ 20%)
- Company cards with logos

#### **company_detail.html** - Company Detail Page
- Full company profile
- Financial metrics
- Technical chart
- Pros & Cons analysis
- Opportunity score breakdown
- Recent alerts

### Configuration & Documentation Files

#### **ml.sql** - Database Schema
Creates MySQL database and tables (run on setup)

#### **companies.xlsx** - Company Master Data
Excel file with company IDs and metadata
- Columns: `company_id`, `company_name`, etc.

#### **QUICKSTART.md** - Quick Implementation Guide
30-minute setup guide with code examples

#### **IMPLEMENTATION_GUIDE.md** - Detailed Implementation
Week-by-week implementation roadmap

#### **AI_CHALLENGE_ANALYSIS.md** - Strategic Analysis
2000+ lines of strategic planning and gap analysis

#### **DELIVERABLES.md** - Feature Overview  
Complete deliverables checklist

---

## 🔄 How It Works - Data Flow

### 1. **Company Data Ingestion**
```
companies.xlsx → api_client.py (fetch from SignalX API) → database
```

### 2. **Pattern Detection Workflow**
```
Stock Ticker (e.g., 'RELIANCE.NS')
    ↓
yfinance.download() → Get 1 year historical OHLCV data
    ↓
PatternDetector.detect_all_patterns() → Scan 12+ patterns
    ↓
TechnicalAnalyzer.add_indicators() → Calculate RSI, MACD, EMA, Bollinger Bands
    ↓
TechnicalAnalyzer.generate_signal() → Create BUY/SELL/HOLD signals
    ↓
Results displayed in UI / stored in database
```

### 3. **Opportunity Scoring Workflow**
```
Company Financial Data (P/E, ROE, ROCE, CAGR, Debt ratios, etc.)
    ↓
CompanyMetrics object creation
    ↓
OpportunityRadar.calculate_opportunity_score()
    │
    ├─→ _score_valuation(metrics) → 0-100
    ├─→ _score_growth(metrics) → 0-100
    ├─→ _score_profitability(metrics) → 0-100
    ├─→ _score_financial_health(metrics) → 0-100
    └─→ _score_technical(metrics) → 0-100
    ↓
Weighted Average: (val×0.20) + (growth×0.25) + ... = overall_score (0-100)
    ↓
Generate Recommendation: STRONG_BUY / BUY / HOLD / SELL / STRONG_SELL
    ↓
Extract key_strengths, key_weaknesses, investment_thesis
    ↓
OpportunityScore object returned with full analysis
```

### 4. **ML Analysis Workflow**
```
Company Metrics (CAGR, ROE, ROE, Debt levels, etc.)
    ↓
ml_engine.generate_pros_cons(company_id, metrics)
    │
    ├─→ Parse percentage strings ("3 Years: 56%" → 56.0)
    ├─→ Check against thresholds:
    │   ├─ ROE > 10% → "Good ROE track record"
    │   ├─ Profit CAGR > 10% → "Good profit growth"
    │   ├─ Sales CAGR < 8% → "Sales growth slowing"
    │   └─ Debt ratio < 10% → "Low debt"
    └─→ Generate up to 3 pros and 3 cons
    ↓
List of strings: ["Pro 1", "Pro 2", ...] and ["Con 1", "Con 2", ...]
    ↓
Store in database → Display in UI
```

### 5. **Alert Generation**
```
Pattern Detection → New pattern found?
    ↓ YES
Create Alert entry: type="pattern", message="Bullish Engulfing found"
    ↓
Store in `alerts` table
    ↓
Display notification in UI (is_read = FALSE)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL Server running on localhost:3306
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
cd c:\Users\Harish\VS Code\Bluestock-module\MLFA
pip install yfinance pandas pandas_ta plotly flask flask-sqlalchemy flask-cors pymysql requests openpyxl
```

### Step 2: Setup Database
```bash
# Create database (run in MySQL client)
mysql -u root < ml.sql

# Or manually create:
CREATE DATABASE ml;
USE ml;
-- Then run table creation scripts
```

### Step 3: Run Tests
```bash
# Test all AI features
python test_ai_features.py
```

**Expected Output**:
```
======================================================================
TEST 1: CHART PATTERN DETECTION
======================================================================
Downloaded 252 trading days
Trend: Strong Uptrend
Patterns Detected: 3
Detailed Patterns:
  1. Bullish Engulfing
     Signal: BUY
     Confidence: 0.85%
     Description: Strong bullish reversal signal

======================================================================
TEST 2: TECHNICAL ANALYSIS & INDICATORS
======================================================================
Latest Technical Signals:
  RSI(14): 58 - Neutral
  Trend: Uptrend
  MACD: Bullish
  Price Position: Near 20-day EMA

======================================================================
TEST 3: OPPORTUNITY SCORING
======================================================================
Company: Reliance Industries
Overall Score: 78 / 100 → BUY
  Valuation: 72
  Growth: 85
  Profitability: 80
  Financial Health: 75
  Technical: 82
Key Strengths:
  - Strong revenue growth
  - Good ROE
```

### Step 4: Run Web Application
```bash
# Start Flask server
python app.py

# Open browser: http://localhost:5000
```

---

## 📊 API Endpoints

### Frontend Routes (Return HTML)
```
GET  /                    → Dashboard (index.html)
GET  /companies           → Company listing (all_companies.html)
GET  /company/<id>        → Company detail (company_detail.html)
```

### Data API Endpoints (Return JSON)
(To be implemented for full feature set)

```
GET  /api/company/<id>/patterns       → Chart patterns
GET  /api/company/<id>/opportunity   → Opportunity score
GET  /api/company/<id>/pros-cons      → Analysis
GET  /api/alerts                      → Notifications
POST /api/alerts/<id>/read            → Mark alert as read
GET  /api/companies/top-opportunities → Ranked companies
GET  /api/technical/<ticker>          → Technical indicators
```

### External API Integration
```
SignalX API:
  Base URL: https://signalx.in/server/api/company.php
  Query Params: ?id=RELIANCE&api_key=ghfkffu6378382826hhdjgk
  Returns: Company metrics JSON
```

---

## 🎯 Key Configuration Parameters

### Pattern Detection Thresholds (tech_patterns.py)
```python
# Confidence levels (0-1)
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_THRESHOLD = 0.01

# EMA periods
EMA_SHORT = 20
EMA_MEDIUM = 50
EMA_LONG = 200
```

### Opportunity Scoring Weights (opportunity_radar.py)
```python
valuation_weight = 0.20        # 20%
growth_weight = 0.25           # 25%
profitability_weight = 0.25    # 25%
financial_health_weight = 0.15 # 15%
technical_weight = 0.15        # 15%
Total = 100%
```

### ML Engine Thresholds (ml_engine.py)
```python
SALES_POOR_THRESHOLD = 8.0     # < 8% sales growth = con
ROE_LOW_THRESHOLD = 8.0        # < 8% ROE = con
HIGH_VALUE_THRESHOLD = 10.0    # > 10% = pro
```

---

## 🔐 Security Considerations

- **API Key**: Store in environment variables (not in config.py)
- **Database**: Use strong passwords in production
- **Frontend**: Validate user inputs
- **CORS**: Configure for allowed domains
- **SSL/TLS**: Use HTTPS in production

---

## 📈 Performance Optimization

### Caching Strategy
- Cache pattern detection results (1 hour)
- Cache opportunity scores (daily)
- Cache company list (hourly)

### Database Optimization
- Add indexes on frequently queried columns
- Use connection pool (already configured)
- Batch processing for bulk data

### Frontend Optimization
- Lazy load company data
- Paginate company listings
- Compress chart data

---

## 🧪 Testing Checklist

- [ ] Pattern detection with real stock data
- [ ] Opportunity scoring calculations
- [ ] Database connectivity and queries
- [ ] API endpoint responses
- [ ] Alert generation and notification
- [ ] Frontend page rendering
- [ ] Company filter functionality
- [ ] Cross-browser compatibility (Firefox, Chrome, Edge)

---

## 📝 Common Use Cases

### 1. **Find Investment Opportunity**
```python
# User visits dashboard → Sees top opportunity companies
# Clicks on company → Views:
# - Opportunity score (0-100)
# - Investment recommendation (BUY/HOLD/SELL)
# - Key strengths & weaknesses
# - Technical chart with patterns
# - Recent trading signals
```

### 2. **Analyze Chart Pattern**
```python
# User searches for ticker (e.g., RELIANCE.NS)
# System downloads 1 year of historical data
# Detects patterns: Bullish Engulfing (3-bar pattern)
# Shows: Date, confidence level, signal (BUY/SELL)
# Displays: RSI, MACD, trend analysis
```

### 3. **Set Alert for Company**
```python
# User sets alert: "Notify me if Opportunity Score > 80"
# System creates alert rule
# Periodically checks scores
# Creates alert entry when triggered
# User sees notification badge
```

### 4. **Compare Multiple Companies**
```python
# User views all_companies.html
# Sees ranked list by ROE, ROCE, Opportunity Score
# Filters by metrics (ROE ≥ 20%, ROCE ≥ 20%)
# Compares technical indicators side-by-side
```

---

## 🐛 Debugging & Troubleshooting

### Database Connection Issues
```python
# Test connection
python -c "from db_config import get_engine; engine = get_engine(); print(engine.execute('SELECT 1'))"
```

### Pattern Detection Not Working
- Check yfinance connectivity: `python -c "import yfinance as yf; yf.download('RELIANCE.NS', period='1y')"`
- Verify pandas_ta installation: `python -c "import pandas_ta; print(pandas_ta.__version__)"`

### Opportunity Score Low
- Check all metrics are provided
- Verify metric values are in expected ranges
- Review weighting configuration

### Web Server Won't Start
- Check port 5000 is not in use
- Verify Flask installed: `pip show flask`
- Check database URI in app.py

---

## 🔄 Development Workflow

### Making Changes
1. Create feature branch
2. Update relevant module(s)
3. Add test cases in test_ai_features.py
4. Update documentation (this file)
5. Test locally
6. Commit with clear message

### Adding New Feature
1. Add business logic in appropriate module
2. Update database schema if needed (ml.sql)
3. Add API endpoint in app.py
4. Add frontend template in templates/
5. Add test cases
6. Update documentation

---

## 📚 Reference & Resources

### External Libraries Documentation
- **yfinance**: `https://pypi.org/project/yfinance/`
- **pandas_ta**: `https://github.com/twopirllc/pandas-ta`
- **Flask**: `https://flask.palletsprojects.com/`
- **SQLAlchemy**: `https://www.sqlalchemy.org/`

### Stock Market Concepts
- **Technical Analysis**: RSI, MACD, Bollinger Bands explained
- **Fundamental Analysis**: P/E, ROE, ROCE, CAGR ratios
- **Chart Patterns**: Bullish Engulfing, Head & Shoulders, Triangles

### File Structure Summary
```
MLFA/
├── Core Application
│   ├── app.py                    # Flask application & routes
│   ├── config.py                 # Configuration
│   └── db_config.py              # Database setup
├── AI/ML Modules  
│   ├── tech_patterns.py          # Pattern detection (500+ lines)
│   ├── opportunity_radar.py      # Opportunity scoring (700+ lines)
│   ├── ml_engine.py              # Pros/cons generation
│   └── models.py                 # SQLAlchemy models
├── Utilities
│   ├── api_client.py             # External API client
│   ├── run_ml_to_db.py           # ETL pipeline
│   ├── setup_alerts.py           # Alert configuration
│   └── test_ai_features.py       # Test suite (400+ lines)
├── Frontend
│   └── templates/
│       ├── base.html             # Base template
│       ├── index.html            # Dashboard
│       ├── all_companies.html    # Company listing
│       └── company_detail.html   # Company detail
├── Data
│   ├── ml.sql                    # Database schema
│   └── companies.xlsx            # Master data
└── Documentation
    ├── PROJECT_OVERVIEW.md        # This file
    ├── QUICKSTART.md              # Quick start guide
    ├── IMPLEMENTATION_GUIDE.md    # Detailed implementation
    ├── AI_CHALLENGE_ANALYSIS.md   # Strategic analysis
    └── DELIVERABLES.md            # Feature overview
```

---

**Last Updated**: March 29, 2026  
**Project Status**: Active Development  
**Version**: 1.0 (Alpha)
