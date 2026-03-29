from flask import Flask, render_template, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from typing import Optional
import requests
from datetime import datetime
import yfinance as yf  # type: ignore
from tech_patterns import TechnicalAnalyzer, PatternDetector
from opportunity_radar import OpportunityRadar, CompanyMetrics

app = Flask(__name__)

# Match ml.sql (adjust password if needed)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@127.0.0.1:3306/ml"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Companies(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.String(255), primary_key=True)  # ticker
    company_logo = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    chart_link = db.Column(db.String(255))
    about_company = db.Column(db.Text)
    website = db.Column(db.String(255))
    nse_profile = db.Column(db.String(255))
    bse_profile = db.Column(db.String(255))
    face_value = db.Column(db.Integer)
    book_value = db.Column(db.Integer)
    roce_percentage = db.Column(db.Numeric(12, 2))
    roe_percentage = db.Column(db.Numeric(12, 2))


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.String(255), db.ForeignKey("companies.id"), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # "pattern", "opportunity_score", "trend_change"
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON, nullable=True)  # Additional data (patterns found, score value, etc.)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship("Companies", backref="alerts")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/companies")
def all_companies():
    companies = Companies.query.order_by(Companies.id).all()

    company_cards = []
    for c in companies:
        roe = float(c.roe_percentage or 0)
        roce = float(c.roce_percentage or 0)

        is_exclusive = roe >= 20 and roce >= 20

        company_cards.append(
            {
                "id": c.id,
                "name": c.company_name or c.id,
                "roe": f"{roe:.1f}%" if c.roe_percentage is not None else "N/A",
                "roce": f"{roce:.1f}%" if c.roce_percentage is not None else "N/A",
                "is_exclusive": is_exclusive,
                "logo": c.company_logo,
            }
        )

    return render_template("all_companies.html", company_cards=company_cards)


def fetch_company_from_api(company_id: str):
    """Fetch full data for a company from SignalX API."""
    api_url = (
        "https://signalx.in/server/api/company.php"
        f"?id={company_id}&api_key=ghfkffu6378382826hhdjgk"
    )
    try:
        resp = requests.get(api_url, timeout=10)
        if resp.status_code != 200:
            return None
        return resp.json()
    except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError):
        return None


@app.route("/company/<company_id>")
def company_detail(company_id):
    # Get base company info from MySQL (for list & safety)
    base_company = Companies.query.filter_by(id=company_id).first()
    if not base_company:
        abort(404)

    # Fetch full details from external API
    payload = fetch_company_from_api(company_id)
    
    # Use API data if available, otherwise use database only
    if payload and "company" in payload and "data" in payload:
        api_company = payload["company"]
        api_data = payload["data"]
    else:
        # Fallback: use empty dicts so we can still render with DB data
        api_company = {}
        api_data = {}

    # Merge DB company + API company (API overrides when present)
    @dataclass
    class CompanyObj:
        id: str
        company_logo: Optional[str] = None
        company_name: Optional[str] = None
        about_company: Optional[str] = None
        website: Optional[str] = None
        nse_profile: Optional[str] = None
        bse_profile: Optional[str] = None
        face_value: Optional[int] = None
        book_value: Optional[int] = None
        roce_percentage: Optional[float] = None
        roe_percentage: Optional[float] = None
        chart_link: Optional[str] = None

    company = CompanyObj(id=company_id)
    company.company_logo = api_company.get("company_logo") or base_company.company_logo
    company.company_name = api_company.get("company_name") or base_company.company_name
    company.about_company = api_company.get("about_company") or base_company.about_company
    company.website = api_company.get("website") or base_company.website
    company.nse_profile = api_company.get("nse_profile") or base_company.nse_profile
    company.bse_profile = api_company.get("bse_profile") or base_company.bse_profile
    company.face_value = api_company.get("face_value") or base_company.face_value
    company.book_value = api_company.get("book_value") or base_company.book_value
    company.roce_percentage = api_company.get("roce_percentage") or base_company.roce_percentage
    company.roe_percentage = api_company.get("roe_percentage") or base_company.roe_percentage

    # TradingView chart always from NSE symbol
    base_tv = "https://in.tradingview.com/chart/?symbol=NSE:"
    company.chart_link = base_tv + company_id

    # Metrics – use first analysis entry if present
    analysis_list = api_data.get("analysis", [])
    if analysis_list:
        a0 = analysis_list[0]
        metrics = {
            "roe": a0.get("roe", "N/A"),
            "sales_cagr": a0.get("compounded_sales_growth", "N/A"),
            "profit_cagr": a0.get("compounded_profit_growth", "N/A"),
        }
    else:
        metrics = {"roe": "N/A", "sales_cagr": "N/A", "profit_cagr": "N/A"}

    # Pros & cons
    pros_list = []
    cons_list = []
    for pc in api_data.get("prosandcons", []):
        if pc.get("pros") and pc["pros"] != "NULL":
            pros_list.append(pc["pros"])
        if pc.get("cons") and pc["cons"] != "NULL":
            cons_list.append(pc["cons"])

    balancesheet = api_data.get("balancesheet", [])
    profitandloss = api_data.get("profitandloss", [])
    cashflow = api_data.get("cashflow", [])
    documents = api_data.get("documents", [])

    # Exclusive rule from ROE & ROCE
    try:
        roe_val = float(company.roe_percentage or 0)
    except ValueError:
        roe_val = 0.0
    try:
        roce_val = float(company.roce_percentage or 0)
    except ValueError:
        roce_val = 0.0
    is_exclusive = roe_val >= 20 and roce_val >= 20

    # AUTO-ANALYZE: Run chart analysis and create alerts in background
    try:
        analyze_company_chart(company_id, company.company_name or company_id)
    except Exception as e:
        print(f"⚠️ Auto-analysis skipped for {company_id}: {str(e)}")

    return render_template(
        "company_detail.html",
        company_id=company_id,
        company=company,
        metrics=metrics,
        pros_list=pros_list,
        cons_list=cons_list,
        balancesheet=balancesheet,
        profitandloss=profitandloss,
        cashflow=cashflow,
        documents=documents,
        is_exclusive=is_exclusive,
    )


# ============ ALERTS & DASHBOARD ===========

@app.route("/dashboard")
def dashboard():
    """Display alerts and investment opportunities dashboard"""
    # Get unread alerts (most recent first)
    unread_alerts = Alert.query.filter_by(is_read=False).order_by(Alert.created_at.desc()).all()
    
    # Get all recent alerts (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_alerts = Alert.query.filter(Alert.created_at >= thirty_days_ago).order_by(Alert.created_at.desc()).all()
    
    # Count alerts by type
    alert_stats = {
        "pattern": len([a for a in recent_alerts if a.alert_type == "pattern"]),
        "opportunity_score": len([a for a in recent_alerts if a.alert_type == "opportunity_score"]),
        "trend_change": len([a for a in recent_alerts if a.alert_type == "trend_change"]),
    }
    
    return render_template(
        "dashboard.html",
        unread_alerts=unread_alerts[:10],  # Show latest 10 unread
        recent_alerts=recent_alerts[:20],  # Show latest 20 recent
        alert_stats=alert_stats,
    )


@app.route("/api/alerts")
def get_alerts():
    """API endpoint to fetch alerts (JSON)"""
    # Query parameters
    unread_only = request.args.get("unread_only", "true").lower() == "true"
    limit = int(request.args.get("limit", 20))
    
    query = Alert.query
    if unread_only:
        query = query.filter_by(is_read=False)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    return jsonify([
        {
            "id": a.id,
            "company_id": a.company_id,
            "company_name": a.company.company_name or a.company_id,
            "alert_type": a.alert_type,
            "message": a.message,
            "details": a.details,
            "is_read": a.is_read,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ])


@app.route("/api/alerts/<int:alert_id>/read", methods=["POST"])
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404
    
    alert.is_read = True
    db.session.commit()
    return jsonify({"status": "success"})


@app.route("/api/alerts/clear-all", methods=["POST"])
def clear_all_alerts():
    """Mark all alerts as read"""
    Alert.query.update({"is_read": True})
    db.session.commit()
    return jsonify({"status": "success"})


def create_alert(company_id: str, alert_type: str, message: str, details: Optional[dict] = None) -> Alert:
    """Create an investment alert"""
    alert = Alert(  # type: ignore[call-arg]
        company_id=company_id,  # type: ignore[assignment]
        alert_type=alert_type,  # type: ignore[assignment]
        message=message,  # type: ignore[assignment]
        details=details if details is not None else {},  # type: ignore[assignment]
        is_read=False,  # type: ignore[assignment]
    )
    db.session.add(alert)
    db.session.commit()
    return alert


def analyze_company_chart(ticker: str, company_name: str) -> dict:
    """
    Automatically analyze company chart and create alerts
    Called when viewing company page
    Returns analysis results
    """
    try:
        # Download price data with NSE format
        ticker_with_ns = f"{ticker}.NS"
        df = yf.download(ticker_with_ns, period="1y", progress=False)  # type: ignore
        
        if df is None or df.empty:
            return {"status": "no_data"}
        
        # Run technical analysis for patterns
        analyzer = TechnicalAnalyzer()
        df_with_indicators = analyzer.add_indicators(df)
        
        if df_with_indicators is None or df_with_indicators.empty:
            return {"status": "analysis_failed"}
        
        # Detect chart patterns
        detector = PatternDetector()
        patterns_result = detector.detect_all_patterns(df_with_indicators)
        patterns = patterns_result.get('patterns', []) if isinstance(patterns_result, dict) else patterns_result
        
        # Create pattern alerts if found
        if patterns:
            for pattern in patterns:
                create_alert(
                    company_id=ticker,
                    alert_type="pattern",
                    message=f"📈 {pattern['pattern_type']} detected ({pattern['signal']})",
                    details={
                        "patterns": [pattern],
                        "confidence": pattern.get("confidence", 0)
                    }
                )
        
        # Calculate opportunity score
        try:
            metrics = CompanyMetrics(
                company_id=ticker,
                company_name=company_name,
                pe_ratio=20.0,  # Default
                pb_ratio=2.5,   # Default
                price_to_sales=1.5,  # Default
                sales_cagr_3y=10.0,  # Default
                sales_cagr_5y=9.5,   # Default
                profit_cagr_3y=8.0,  # Default
                profit_cagr_5y=7.5,  # Default
                roe=12.0,  # Default
                roce=10.0,  # Default
                profit_margin=15.0,  # Default
                debt_to_equity=0.5,  # Default
                current_ratio=1.5,  # Default
                rsi_14=50.0,  # Default
                trend="neutral",  # Default
                market_cap=100000000000.0,  # Default
                dividend_yield=2.5  # Default
            )
            
            radar = OpportunityRadar()
            score = radar.calculate_opportunity_score(metrics)
            
            # Create opportunity score alert if score is high
            if score.overall_score >= 70:
                create_alert(
                    company_id=ticker,
                    alert_type="opportunity_score",
                    message=f"⭐ High Opportunity Score: {score.overall_score:.0f}/100 - {score.recommendation}",
                    details={
                        "score": int(score.overall_score),
                        "recommendation": score.recommendation,
                        "key_strengths": score.key_strengths,
                        "key_weaknesses": score.key_weaknesses
                    }
                )
        except Exception:
            pass  # Opportunity scoring failed, continue
        
        return {
            "status": "success",
            "patterns_found": len(patterns),
            "alerts_created": True
        }
        
    except Exception as e:
        print(f"❌ Chart analysis failed for {ticker}: {str(e)}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    app.run(debug=True)
