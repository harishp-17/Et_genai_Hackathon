"""
Technical Analysis & Chart Pattern Detection Engine
Detects candlestick patterns, chart formations, and trend indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PatternDetector:
    """Detects chart patterns and candlestick formations"""
    
    def __init__(self):
        self.patterns_found = []
    
    def detect_all_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Run all pattern detection algorithms on price data
        
        Args:
            df: DataFrame with OHLCV columns (Open, High, Low, Close, Volume)
        
        Returns:
            Dictionary of detected patterns with metadata
        """
        if df is None or len(df) < 3:
            return {'status': 'insufficient_data', 'patterns': []}
        
        results = {
            'patterns': [],
            'signals': {},
            'trend': None
        }
        
        # Candlestick patterns (need 2-5 bars)
        bullish_engulfing = self._bullish_engulfing(df)
        if bullish_engulfing:
            results['patterns'].append(bullish_engulfing)
        
        bearish_engulfing = self._bearish_engulfing(df)
        if bearish_engulfing:
            results['patterns'].append(bearish_engulfing)
        
        morning_star = self._morning_star(df)
        if morning_star:
            results['patterns'].append(morning_star)
        
        evening_star = self._evening_star(df)
        if evening_star:
            results['patterns'].append(evening_star)
        
        hammer = self._hammer(df)
        if hammer:
            results['patterns'].append(hammer)
        
        hanging_man = self._hanging_man(df)
        if hanging_man:
            results['patterns'].append(hanging_man)
        
        # Chart patterns (need 10+ bars)
        if len(df) >= 10:
            triangle = self._detect_triangle(df)
            if triangle:
                results['patterns'].append(triangle)
            
            head_shoulders = self._detect_head_and_shoulders(df)
            if head_shoulders:
                results['patterns'].append(head_shoulders)
            
            double_bottom = self._detect_double_bottom(df)
            if double_bottom:
                results['patterns'].append(double_bottom)
            
            double_top = self._detect_double_top(df)
            if double_top:
                results['patterns'].append(double_top)
        
        # Trend-based patterns
        breakout = self._detect_breakout(df)
        if breakout:
            results['patterns'].append(breakout)
        
        pullback = self._detect_pullback(df)
        if pullback:
            results['patterns'].append(pullback)
        
        # Overall trend
        results['trend'] = self._determine_trend(df)
        
        return results
    
    # ========== CANDLESTICK PATTERNS ==========
    
    def _bullish_engulfing(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Bullish Engulfing Pattern
        - Previous bar: bearish (close < open)
        - Current bar: bullish (close > open)  
        - Current body completely engulfs previous body
        """
        if len(df) < 2:
            return None
        
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        
        is_prev_bearish = prev['Close'] < prev['Open']
        is_curr_bullish = curr['Close'] > curr['Open']
        engulfs = (curr['Open'] <= prev['Close'] and 
                   curr['Close'] >= prev['Open'])
        
        if is_prev_bearish and is_curr_bullish and engulfs:
            return {
                'pattern_type': 'Bullish Engulfing',
                'signal': 'BUY',
                'confidence': 0.78,
                'date': str(df.index[-1]),
                'description': 'Strong reversal pattern indicating bullish momentum'
            }
        return None
    
    def _bearish_engulfing(self, df: pd.DataFrame) -> Optional[Dict]:
        """Bearish Engulfing - reverse of bullish"""
        if len(df) < 2:
            return None
        
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        
        is_prev_bullish = prev['Close'] > prev['Open']
        is_curr_bearish = curr['Close'] < curr['Open']
        engulfs = (curr['Close'] <= prev['Open'] and 
                   curr['Open'] >= prev['Close'])
        
        if is_prev_bullish and is_curr_bearish and engulfs:
            return {
                'pattern_type': 'Bearish Engulfing',
                'signal': 'SELL',
                'confidence': 0.78,
                'date': str(df.index[-1]),
                'description': 'Strong reversal pattern indicating bearish momentum'
            }
        return None
    
    def _morning_star(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Morning Star - 3 candle reversal at bottom
        1. Long bearish candle
        2. Small body candle (gap down)
        3. Long bullish candle that closes into previous white candle
        """
        if len(df) < 3:
            return None
        
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        
        is_c1_bearish = c1['Close'] < c1['Open']
        is_c2_small = abs(c2['Close'] - c2['Open']) < (c1['Close'] - c1['Open']) * 0.5
        is_c3_bullish = c3['Close'] > c3['Open']
        
        if is_c1_bearish and is_c2_small and is_c3_bullish:
            return {
                'pattern_type': 'Morning Star',
                'signal': 'BUY',
                'confidence': 0.72,
                'date': str(df.index[-1]),
                'description': 'Bullish reversal pattern at market bottom'
            }
        return None
    
    def _evening_star(self, df: pd.DataFrame) -> Optional[Dict]:
        """Evening Star - opposite of morning star (bearish)"""
        if len(df) < 3:
            return None
        
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        
        is_c1_bullish = c1['Close'] > c1['Open']
        is_c2_small = abs(c2['Close'] - c2['Open']) < (c1['Close'] - c1['Open']) * 0.5
        is_c3_bearish = c3['Close'] < c3['Open']
        
        if is_c1_bullish and is_c2_small and is_c3_bearish:
            return {
                'pattern_type': 'Evening Star',
                'signal': 'SELL',
                'confidence': 0.72,
                'date': str(df.index[-1]),
                'description': 'Bearish reversal pattern at market top'
            }
        return None
    
    def _hammer(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Hammer Pattern - bullish reversal
        - Small body at top
        - Long lower wick
        - Appears after downtrend
        """
        if len(df) < 2:
            return None
        
        curr = df.iloc[-1]
        body = abs(curr['Close'] - curr['Open'])
        lower_wick = min(curr['Open'], curr['Close']) - curr['Low']
        
        if lower_wick > body * 2 and (curr['Close'] > curr['Open']):
            return {
                'pattern_type': 'Hammer',
                'signal': 'BUY',
                'confidence': 0.65,
                'date': str(df.index[-1]),
                'description': 'Bullish reversal with strong support'
            }
        return None
    
    def _hanging_man(self, df: pd.DataFrame) -> Optional[Dict]:
        """Hanging Man - bearish reversal (reverse of hammer)"""
        if len(df) < 2:
            return None
        
        curr = df.iloc[-1]
        body = abs(curr['Close'] - curr['Open'])
        lower_wick = min(curr['Open'], curr['Close']) - curr['Low']
        
        if lower_wick > body * 2 and (curr['Close'] < curr['Open']):
            return {
                'pattern_type': 'Hanging Man',
                'signal': 'SELL',
                'confidence': 0.65,
                'date': str(df.index[-1]),
                'description': 'Bearish reversal signal'
            }
        return None
    
    # ========== CHART PATTERNS ==========
    
    def _detect_triangle(self, df: pd.DataFrame, window: int = 20) -> Optional[Dict]:
        """
        Detect triangle consolidation pattern
        - Range decreases over time
        - Convergence of highs and lows
        """
        if len(df) < window:
            return None
        
        recent = df.tail(window)
        high_vals = recent['High'].to_numpy(dtype=float, na_value=0.0)
        low_vals = recent['Low'].to_numpy(dtype=float, na_value=0.0)
        
        # Calculate ranges for two halves
        mid = len(recent) // 2
        first_half_range = float(np.max(high_vals[:mid])) - float(np.min(low_vals[:mid]))
        second_half_range = float(np.max(high_vals[mid:])) - float(np.min(low_vals[mid:]))
        
        # Check if range is decreasing (converging)
        if first_half_range > 0 and second_half_range < first_half_range * 0.7:
            return {
                'pattern_type': 'Triangle',
                'signal': 'BREAKOUT_PENDING',
                'confidence': 0.68,
                'date': str(df.index[-1]),
                'description': 'Consolidation with breakout potential'
            }
        return None
    
    def _detect_head_and_shoulders(self, df: pd.DataFrame, window: int = 30) -> Optional[Dict]:
        """
        Detect Head and Shoulders pattern
        - Three peaks with middle peak (head) being highest
        - Two shoulder peaks on sides are lower
        - Indicates trend reversal
        """
        if len(df) < window:
            return None
        
        recent = df.tail(window)
        highs = recent['High'].values
        
        # Find local maxima
        local_maxima = []
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                local_maxima.append((i, highs[i]))
        
        # Look for H&S pattern (3 peaks with middle highest)
        if len(local_maxima) >= 3:
            idx1, h1 = local_maxima[-3]
            idx2, h2 = local_maxima[-2]
            idx3, h3 = local_maxima[-1]
            
            # Head higher than both shoulders
            if h2 > h1 and h2 > h3:
                return {
                    'pattern_type': 'Head and Shoulders',
                    'signal': 'SELL',
                    'confidence': 0.72,
                    'date': str(df.index[-1]),
                    'description': 'Bearish reversal pattern at resistance'
                }
        return None
    
    def _detect_double_bottom(self, df: pd.DataFrame, window: int = 30) -> Optional[Dict]:
        """Detect double bottom - two lows at similar level"""
        if len(df) < window:
            return None
        
        recent = df.tail(window)
        lows = recent['Low'].values
        
        # Find local minima
        local_minima = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                local_minima.append((i, lows[i]))
        
        # Check for two similar lows
        if len(local_minima) >= 2:
            idx1, low1 = local_minima[-2]
            idx2, low2 = local_minima[-1]
            
            # Lows are within 5% of each other
            if abs(low1 - low2) / min(low1, low2) < 0.05:
                return {
                    'pattern_type': 'Double Bottom',
                    'signal': 'BUY',
                    'confidence': 0.70,
                    'date': str(df.index[-1]),
                    'description': 'Bullish reversal at support level'
                }
        return None
    
    def _detect_double_top(self, df: pd.DataFrame, window: int = 30) -> Optional[Dict]:
        """Detect double top - two highs at similar level"""
        if len(df) < window:
            return None
        
        recent = df.tail(window)
        highs = recent['High'].values
        
        local_maxima = []
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                local_maxima.append((i, highs[i]))
        
        if len(local_maxima) >= 2:
            idx1, high1 = local_maxima[-2]
            idx2, high2 = local_maxima[-1]
            
            if abs(high1 - high2) / min(high1, high2) < 0.05:
                return {
                    'pattern_type': 'Double Top',
                    'signal': 'SELL',
                    'confidence': 0.70,
                    'date': str(df.index[-1]),
                    'description': 'Bearish reversal at resistance level'
                }
        return None
    
    # ========== TREND-BASED PATTERNS ==========
    
    def _detect_breakout(self, df: pd.DataFrame, window: int = 20) -> Optional[Dict]:
        """
        Detect breakout - price breaks above resistance/support
        """
        if len(df) < window:
            return None
        
        recent = df.tail(window)
        resistance = recent['High'].iloc[:-1].max()
        support = recent['Low'].iloc[:-1].min()
        current_close = recent['Close'].iloc[-1]
        current_high = recent['High'].iloc[-1]
        
        volume = recent['Volume']
        avg_volume = volume.iloc[:-1].mean()
        current_volume = volume.iloc[-1]
        
        # Breakout above resistance with volume
        if current_high > resistance and current_volume > avg_volume * 1.5:
            return {
                'pattern_type': 'Breakout',
                'signal': 'BUY',
                'confidence': 0.70,
                'date': str(df.index[-1]),
                'description': 'Price breaks above resistance with strong volume'
            }
        
        # Breakdown below support
        if current_close < support and current_volume > avg_volume * 1.5:
            return {
                'pattern_type': 'Breakdown',
                'signal': 'SELL',
                'confidence': 0.70,
                'date': str(df.index[-1]),
                'description': 'Price breaks below support with strong volume'
            }
        
        return None
    
    def _detect_pullback(self, df: pd.DataFrame, window: int = 20) -> Optional[Dict]:
        """
        Detect pullback - price retraces to support during uptrend
        Buying opportunity signal
        """
        if len(df) < window:
            return None
        
        recent = df.tail(window)
        
        # Check if in uptrend
        ema_20 = recent['Close'].ewm(span=20).mean()
        is_uptrend = ema_20.iloc[-1] > ema_20.iloc[-5]
        
        # Check if pullback to EMA
        support = ema_20.iloc[-1]
        current_close = recent['Close'].iloc[-1]
        
        if is_uptrend and current_close < support * 1.02 and current_close > support * 0.98:
            return {
                'pattern_type': 'Pullback',
                'signal': 'BUY',
                'confidence': 0.65,
                'date': str(df.index[-1]),
                'description': 'Price pullback to trend support - buy opportunity'
            }
        
        return None
    
    def _determine_trend(self, df: pd.DataFrame) -> str:
        """Determine overall trend: uptrend, downtrend, or sideways"""
        if len(df) < 20:
            return 'insufficient_data'
        
        recent = df.tail(20)
        ema_20 = recent['Close'].ewm(span=20).mean()
        ema_50 = recent['Close'].ewm(span=50).mean() if len(df) >= 50 else ema_20
        
        close = recent['Close'].iloc[-1]
        
        if close > ema_20.iloc[-1] > ema_50.iloc[-1]:
            return 'Strong Uptrend'
        elif close > ema_20.iloc[-1]:
            return 'Uptrend'
        elif close < ema_20.iloc[-1] < ema_50.iloc[-1]:
            return 'Strong Downtrend'
        elif close < ema_20.iloc[-1]:
            return 'Downtrend'
        else:
            return 'Sideways'


class TechnicalAnalyzer:
    """Calculate technical indicators for trading signals"""
    
    @staticmethod
    def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add common technical indicators to dataframe"""
        df = df.copy()
        
        # Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_20'] = df['Close'].ewm(span=20).mean()
        df['EMA_50'] = df['Close'].ewm(span=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Momentum
        df['RSI_14'] = TechnicalAnalyzer._calculate_rsi(df['Close'], 14)
        df['MACD'], df['MACD_Signal'] = TechnicalAnalyzer._calculate_macd(df['Close'])
        
        # Volatility
        df['ATR_14'] = TechnicalAnalyzer._calculate_atr(df, 14)
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = TechnicalAnalyzer._calculate_bollinger(df['Close'])
        
        return df
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        
        return macd_line, signal_line
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range"""
        df = df.copy()
        df['tr'] = np.maximum(
            df['High'] - df['Low'],
            np.maximum(
                abs(df['High'] - df['Close'].shift()),
                abs(df['Low'] - df['Close'].shift())
            )
        )
        atr = df['tr'].rolling(window=period).mean()
        return atr
    
    @staticmethod
    def _calculate_bollinger(prices: pd.Series, period: int = 20, num_std: float = 2):
        """Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        
        return upper, sma, lower
    
    @staticmethod
    def generate_signal(df: pd.DataFrame) -> Dict:
        """Generate trading signal from technical indicators"""
        if len(df) < 1:
            return {'status': 'insufficient_data'}
        
        latest = df.iloc[-1]
        
        signals = {
            'timestamp': str(df.index[-1]),
            'rsi': {
                'value': round(latest['RSI_14'], 2) if 'RSI_14' in df.columns else None,
                'signal': 'Overbought' if latest.get('RSI_14', 50) > 70 else 'Oversold' if latest.get('RSI_14', 50) < 30 else 'Neutral'
            },
            'trend': 'Uptrend' if latest['EMA_20'] > latest['EMA_50'] else 'Downtrend',
            'macd': 'Bullish' if latest.get('MACD', 0) > latest.get('MACD_Signal', 0) else 'Bearish',
            'price_position': 'Above Upper BB' if latest['Close'] > latest['BB_Upper'] else 'Below Lower BB' if latest['Close'] < latest['BB_Lower'] else 'Within Bands'
        }
        
        return signals


if __name__ == "__main__":
    # Test with sample data
    import yfinance as yf  # type: ignore
    
    ticker = 'RELIANCE.NS'
    df = yf.download(ticker, period='1y', progress=False)
    
    if df is None:
        print(f"Failed to download data for {ticker}")
        exit(1)
    
    if df.empty:
        print(f"Failed to download data for {ticker}")
        exit(1)
    
    detector = PatternDetector()
    patterns_result = detector.detect_all_patterns(df)  # type: ignore
    
    print(f"\n{'='*60}")
    print(f"Pattern Detection for {ticker}")
    print(f"{'='*60}")
    print(f"Trend: {patterns_result['trend']}")
    print(f"Patterns Found: {len(patterns_result['patterns'])}")
    
    for i, pattern in enumerate(patterns_result['patterns'], 1):
        print(f"\n{i}. {pattern['pattern_type']} (Signal: {pattern['signal']})")
        print(f"   Confidence: {pattern['confidence']*100:.1f}%")
        print(f"   {pattern['description']}")
    
    # Add indicators and generate signals
    df = TechnicalAnalyzer.add_indicators(df)  # type: ignore
    signals = TechnicalAnalyzer.generate_signal(df)
    
    print(f"\n{'='*60}")
    print("Technical Signals")
    print(f"{'='*60}")
    print(f"RSI: {signals['rsi']['value']} ({signals['rsi']['signal']})")
    print(f"Trend: {signals['trend']}")
    print(f"MACD: {signals['macd']}")
    print(f"Price Position: {signals['price_position']}")
