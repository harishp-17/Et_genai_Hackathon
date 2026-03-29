"""
Opportunity Radar - Intelligent Investment Opportunity Scoring System
Combines fundamental, technical, and quantitative analysis to identify 
undervalued companies with growth potential.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RecommendationType(Enum):
    """Investment recommendation types"""
    STRONG_BUY = "STRONG BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG SELL"


@dataclass
class CompanyMetrics:
    """Container for company metrics"""
    company_id: str
    company_name: str
    
    # Valuation Metrics
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    price_to_sales: Optional[float] = None
    
    # Growth Metrics
    sales_cagr_3y: Optional[float] = None
    sales_cagr_5y: Optional[float] = None
    profit_cagr_3y: Optional[float] = None
    profit_cagr_5y: Optional[float] = None
    
    # Profitability Metrics
    roe: Optional[float] = None
    roce: Optional[float] = None
    profit_margin: Optional[float] = None
    
    # Financial Health
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    
    # Technical Metrics
    rsi_14: Optional[float] = None
    trend: Optional[str] = None  # 'uptrend', 'downtrend', 'sideways'
    
    # Market Metrics
    market_cap: Optional[float] = None
    dividend_yield: Optional[float] = None


@dataclass
class OpportunityScore:
    """Results of opportunity scoring"""
    overall_score: float
    valuation_score: float
    growth_score: float
    profitability_score: float
    financial_health_score: float
    technical_score: float
    recommendation: RecommendationType
    key_strengths: List[str]
    key_weaknesses: List[str]
    investment_thesis: str


class OpportunityRadar:
    """Main opportunity scoring engine"""
    
    def __init__(self, 
                 valuation_weight: float = 0.20,
                 growth_weight: float = 0.25,
                 profitability_weight: float = 0.25,
                 financial_health_weight: float = 0.15,
                 technical_weight: float = 0.15):
        """
        Initialize with custom weights
        Total must sum to 1.0
        """
        self.valuation_weight = valuation_weight
        self.growth_weight = growth_weight
        self.profitability_weight = profitability_weight
        self.financial_health_weight = financial_health_weight
        self.technical_weight = technical_weight
        
        # Verify weights sum to 1.0
        total = (valuation_weight + growth_weight + profitability_weight + 
                financial_health_weight + technical_weight)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def calculate_opportunity_score(self, metrics: CompanyMetrics) -> OpportunityScore:
        """
        Calculate comprehensive opportunity score for a company
        
        Args:
            metrics: CompanyMetrics object with all available data
        
        Returns:
            OpportunityScore with detailed analysis
        """
        
        # Calculate component scores
        valuation = self._score_valuation(metrics)
        growth = self._score_growth(metrics)
        profitability = self._score_profitability(metrics)
        financial_health = self._score_financial_health(metrics)
        technical = self._score_technical(metrics)
        
        # Weighted overall score
        overall = (
            valuation * self.valuation_weight +
            growth * self.growth_weight +
            profitability * self.profitability_weight +
            financial_health * self.financial_health_weight +
            technical * self.technical_weight
        )
        
        # Generate insights
        strengths = self._identify_strengths(metrics)
        weaknesses = self._identify_weaknesses(metrics)
        thesis = self._generate_investment_thesis(metrics, overall)
        recommendation = self._get_recommendation(overall)
        
        return OpportunityScore(
            overall_score=round(overall, 2),
            valuation_score=round(valuation, 2),
            growth_score=round(growth, 2),
            profitability_score=round(profitability, 2),
            financial_health_score=round(financial_health, 2),
            technical_score=round(technical, 2),
            recommendation=recommendation,
            key_strengths=strengths,
            key_weaknesses=weaknesses,
            investment_thesis=thesis
        )
    
    # ========== SCORING COMPONENTS ==========
    
    def _score_valuation(self, metrics: CompanyMetrics) -> float:
        """
        Score based on valuation metrics (P/E, P/B, Price/Sales)
        Lower valuations = Higher scores
        Range: 0-100
        """
        scores = []
        
        # P/E Ratio Scoring
        if metrics.pe_ratio:
            # Good P/E: < 20, Excellent: < 15
            if metrics.pe_ratio < 15:
                scores.append(100)
            elif metrics.pe_ratio < 20:
                scores.append(100 - (metrics.pe_ratio - 15) * 5)  # Gradual decrease
            elif metrics.pe_ratio < 30:
                scores.append(75 - (metrics.pe_ratio - 20) * 2.5)
            else:
                scores.append(max(0, 50 - (metrics.pe_ratio - 30)))
        
        # P/B Ratio Scoring
        if metrics.pb_ratio:
            # Good P/B: < 2, Excellent: < 1.5
            if metrics.pb_ratio < 1.5:
                scores.append(100)
            elif metrics.pb_ratio < 2.5:
                scores.append(100 - (metrics.pb_ratio - 1.5) * 20)
            elif metrics.pb_ratio < 4:
                scores.append(80 - (metrics.pb_ratio - 2.5) * 16)
            else:
                scores.append(max(0, 60 - (metrics.pb_ratio - 4)))
        
        # Price/Sales Ratio
        if metrics.price_to_sales:
            if metrics.price_to_sales < 1:
                scores.append(100)
            elif metrics.price_to_sales < 2:
                scores.append(100 - (metrics.price_to_sales - 1) * 50)
            else:
                scores.append(max(0, 50 - (metrics.price_to_sales - 2) * 25))
        
        return sum(scores) / len(scores) if scores else 50
    
    def _score_growth(self, metrics: CompanyMetrics) -> float:
        """
        Score based on growth metrics (CAGR)
        Range: 0-100
        """
        scores = []
        
        # Sales CAGR (prefer longer period)
        sales_cagr = metrics.sales_cagr_5y or metrics.sales_cagr_3y
        if sales_cagr:
            # Excellent: > 20%, Good: > 12%, Satisfactory: > 8%
            if sales_cagr > 20:
                scores.append(100)
            elif sales_cagr > 15:
                scores.append(90)
            elif sales_cagr > 12:
                scores.append(80)
            elif sales_cagr > 8:
                scores.append(60)
            elif sales_cagr > 5:
                scores.append(40)
            else:
                scores.append(max(0, sales_cagr * 5))
        
        # Profit CAGR (prefer longer period)
        profit_cagr = metrics.profit_cagr_5y or metrics.profit_cagr_3y
        if profit_cagr:
            # Excellent: > 25%, Good: > 15%, Satisfactory: > 10%
            if profit_cagr > 25:
                scores.append(100)
            elif profit_cagr > 20:
                scores.append(95)
            elif profit_cagr > 15:
                scores.append(85)
            elif profit_cagr > 10:
                scores.append(70)
            elif profit_cagr > 5:
                scores.append(50)
            else:
                scores.append(max(0, profit_cagr * 5))
        
        return sum(scores) / len(scores) if scores else 50
    
    def _score_profitability(self, metrics: CompanyMetrics) -> float:
        """
        Score based on return metrics (ROE, ROCE)
        Range: 0-100
        """
        scores = []
        
        # ROE Scoring
        if metrics.roe:
            # Excellent: > 20%, Good: > 15%, Satisfactory: > 10%
            if metrics.roe > 25:
                scores.append(100)
            elif metrics.roe > 20:
                scores.append(90)
            elif metrics.roe > 15:
                scores.append(75)
            elif metrics.roe > 10:
                scores.append(60)
            elif metrics.roe > 5:
                scores.append(40)
            else:
                scores.append(max(0, metrics.roe * 6))
        
        # ROCE Scoring
        if metrics.roce:
            # Excellent: > 20%, Good: > 15%, Satisfactory: > 12%
            if metrics.roce > 25:
                scores.append(100)
            elif metrics.roce > 20:
                scores.append(90)
            elif metrics.roce > 15:
                scores.append(75)
            elif metrics.roce > 12:
                scores.append(65)
            elif metrics.roce > 10:
                scores.append(50)
            else:
                scores.append(max(0, metrics.roce * 4))
        
        # Profit Margin
        if metrics.profit_margin:
            if metrics.profit_margin > 15:
                scores.append(100)
            elif metrics.profit_margin > 10:
                scores.append(80)
            elif metrics.profit_margin > 5:
                scores.append(60)
            else:
                scores.append(40)
        
        return sum(scores) / len(scores) if scores else 50
    
    def _score_financial_health(self, metrics: CompanyMetrics) -> float:
        """
        Score based on balance sheet strength
        Range: 0-100
        """
        scores = []
        
        # Debt-to-Equity Scoring
        if metrics.debt_to_equity is not None:
            if metrics.debt_to_equity == 0:
                scores.append(100)  # Debt-free
            elif metrics.debt_to_equity < 0.5:
                scores.append(90)   # Very healthy
            elif metrics.debt_to_equity < 1.0:
                scores.append(75)   # Healthy
            elif metrics.debt_to_equity < 2.0:
                scores.append(60)   # Acceptable
            else:
                scores.append(40)   # Leveraged
        
        # Current Ratio Scoring
        if metrics.current_ratio:
            if metrics.current_ratio > 2.0:
                scores.append(100)  # Excellent liquidity
            elif metrics.current_ratio > 1.5:
                scores.append(80)   # Good liquidity
            elif metrics.current_ratio > 1.0:
                scores.append(60)   # Acceptable
            else:
                scores.append(30)   # Liquidity concerns
        
        # Dividend Yield (bonus indicator)
        if metrics.dividend_yield and metrics.dividend_yield > 2:
            scores.append(75)  # Good dividend payer
        
        return sum(scores) / len(scores) if scores else 50
    
    def _score_technical(self, metrics: CompanyMetrics) -> float:
        """
        Score based on technical indicators
        Range: 0-100
        """
        scores = []
        
        # RSI Scoring
        if metrics.rsi_14 is not None:
            if metrics.rsi_14 > 70:
                scores.append(40)   # Overbought
            elif metrics.rsi_14 > 60:
                scores.append(60)   # Strong
            elif metrics.rsi_14 >= 40:
                scores.append(80)   # Healthy
            elif metrics.rsi_14 >= 30:
                scores.append(70)   # Oversold but recovering
            elif metrics.rsi_14 < 30:
                scores.append(50)   # Oversold
        
        # Trend Scoring
        if metrics.trend:
            if metrics.trend == 'uptrend':
                scores.append(85)
            elif metrics.trend == 'Strong Uptrend':
                scores.append(95)
            elif metrics.trend == 'Strong Downtrend':
                scores.append(20)
            elif metrics.trend == 'downtrend':
                scores.append(30)
            else:  # sideways
                scores.append(50)
        
        return sum(scores) / len(scores) if scores else 50
    
    # ========== INSIGHTS & ANALYSIS ==========
    
    def _identify_strengths(self, metrics: CompanyMetrics) -> List[str]:
        """Identify positive qualities of the company"""
        strengths = []
        
        if metrics.pe_ratio and metrics.pe_ratio < 15:
            strengths.append("Undervalued on P/E basis")
        if metrics.pb_ratio and metrics.pb_ratio < 1.5:
            strengths.append("Strong book value")
        if metrics.sales_cagr_5y and metrics.sales_cagr_5y > 15:
            strengths.append("Consistent 5-year sales growth")
        if metrics.profit_cagr_3y and metrics.profit_cagr_3y > 20:
            strengths.append("Strong profit CAGR")
        if metrics.roe and metrics.roe > 20:
            strengths.append("Excellent return on equity")
        if metrics.roce and metrics.roce > 20:
            strengths.append("Strong capital efficiency")
        if metrics.debt_to_equity and metrics.debt_to_equity < 0.5:
            strengths.append("Conservative debt levels")
        if metrics.dividend_yield and metrics.dividend_yield > 2:
            strengths.append("Good dividend payout")
        if metrics.trend and 'uptrend' in metrics.trend.lower():
            strengths.append("Positive price momentum")
        
        return strengths[:5]  # Top 5 strengths
    
    def _identify_weaknesses(self, metrics: CompanyMetrics) -> List[str]:
        """Identify concerns about the company"""
        weaknesses = []
        
        if metrics.pe_ratio and metrics.pe_ratio > 30:
            weaknesses.append("High valuation multiple")
        if metrics.pb_ratio and metrics.pb_ratio > 4:
            weaknesses.append("Expensive on book value")
        if metrics.sales_cagr_3y and metrics.sales_cagr_3y < 5:
            weaknesses.append("Weak sales growth")
        if metrics.profit_cagr_3y and metrics.profit_cagr_3y < 5:
            weaknesses.append("Sluggish profit growth")
        if metrics.roe and metrics.roe < 10:
            weaknesses.append("Low return on equity")
        if metrics.roce and metrics.roce < 10:
            weaknesses.append("Poor capital efficiency")
        if metrics.debt_to_equity and metrics.debt_to_equity > 2:
            weaknesses.append("High leverage risk")
        if metrics.current_ratio and metrics.current_ratio < 1:
            weaknesses.append("Liquidity concerns")
        if metrics.trend and 'downtrend' in metrics.trend.lower():
            weaknesses.append("Negative price momentum")
        
        return weaknesses[:5]  # Top 5 weaknesses
    
    def _generate_investment_thesis(self, metrics: CompanyMetrics, score: float) -> str:
        """Generate investment thesis narrative"""
        if score >= 75:
            return (f"{metrics.company_name} is a compelling opportunity with strong fundamentals "
                   "and favorable valuation. The company demonstrates consistent growth, "
                   "excellent profitability, and solid financial health.")
        elif score >= 60:
            return (f"{metrics.company_name} presents a reasonable investment opportunity with "
                   "decent growth prospects and acceptable valuation. The company has "
                   "demonstrated stable financial performance.")
        elif score >= 40:
            return (f"{metrics.company_name} shows mixed characteristics. While some metrics "
                   "are attractive, there are areas of concern that warrant careful analysis "
                   "before investment consideration.")
        elif score >= 25:
            return (f"{metrics.company_name} has several concerning factors that suggest "
                   "limited upside potential. Investors should carefully consider risks "
                   "before investing.")
        else:
            return (f"{metrics.company_name} exhibits significant challenges including weak "
                   "growth, poor profitability, or unfavorable valuation. Caution is advised.")
    
    def _get_recommendation(self, score: float) -> RecommendationType:
        """Convert score to recommendation"""
        if score >= 80:
            return RecommendationType.STRONG_BUY
        elif score >= 65:
            return RecommendationType.BUY
        elif score >= 40:
            return RecommendationType.HOLD
        elif score >= 25:
            return RecommendationType.SELL
        else:
            return RecommendationType.STRONG_SELL


class RadarComparator:
    """Compare multiple companies on the radar"""
    
    @staticmethod
    def rank_companies(scores: List[OpportunityScore]) -> List[Tuple[float, int]]:
        """Rank companies by opportunity score"""
        rankings = [(score.overall_score, idx) for idx, score in enumerate(scores)]
        rankings.sort(reverse=True)
        return rankings
    
    @staticmethod
    def identify_top_opportunities(scores: List[OpportunityScore], top_n: int = 5) -> List[OpportunityScore]:
        """Get top N opportunities"""
        strong_opportunities = [s for s in scores 
                               if s.overall_score >= 70]
        return sorted(strong_opportunities, 
                     key=lambda x: x.overall_score, 
                     reverse=True)[:top_n]
    
    @staticmethod
    def find_sector_leaders(scores: Dict[str, List[OpportunityScore]]) -> Dict[str, OpportunityScore]:
        """Find best opportunity in each sector"""
        sector_leaders = {}
        for sector, sector_scores in scores.items():
            best = max(sector_scores, key=lambda x: x.overall_score)
            sector_leaders[sector] = best
        return sector_leaders


if __name__ == "__main__":
    # Example usage
    radar = OpportunityRadar()
    
    # Sample company metrics
    reliance = CompanyMetrics(
        company_id='RELIANCE',
        company_name='Reliance Industries',
        pe_ratio=22.5,
        pb_ratio=3.2,
        price_to_sales=3.1,
        sales_cagr_5y=8.3,
        profit_cagr_5y=12.1,
        roe=11.5,
        roce=9.2,
        profit_margin=8.5,
        debt_to_equity=0.32,
        current_ratio=1.45,
        rsi_14=58,
        trend='Uptrend',
        dividend_yield=2.1
    )
    
    # Calculate score
    score = radar.calculate_opportunity_score(reliance)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"Opportunity Radar Analysis: {reliance.company_name}")
    print(f"{'='*60}")
    print(f"Overall Score: {score.overall_score}/100")
    print(f"Recommendation: {score.recommendation.value}")
    print(f"\nComponent Scores:")
    print(f"  Valuation:         {score.valuation_score}/100")
    print(f"  Growth:            {score.growth_score}/100")
    print(f"  Profitability:     {score.profitability_score}/100")
    print(f"  Financial Health:  {score.financial_health_score}/100")
    print(f"  Technical:         {score.technical_score}/100")
    print(f"\nStrengths:")
    for s in score.key_strengths:
        print(f"  ✓ {s}")
    print(f"\nWeaknesses:")
    for w in score.key_weaknesses:
        print(f"  ✗ {w}")
    print(f"\nInvestment Thesis:")
    print(f"  {score.investment_thesis}")
    print(f"\n{'='*60}")
