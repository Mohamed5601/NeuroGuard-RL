import pandas as pd
import numpy as np
import pandas_ta as ta
import ccxt
import time

class DataProcessor:
    def __init__(self, exchange_id='binance'):
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
    def download_data(self, symbol, timeframe, limit=30000, since=None):
        print(f"⬇️ Downloading {symbol} ({timeframe}) - Target: {limit} candles...")
        all_ohlcv = []
        # Start from Jan 1, 2020 if no date provided
        current_since = since if since else 1577836800000 
        
        while len(all_ohlcv) < limit:
            try:
                remaining = limit - len(all_ohlcv)
                fetch_limit = 1000 if remaining > 1000 else remaining
                
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=current_since, limit=fetch_limit)
                if not ohlcv: break
                
                all_ohlcv.extend(ohlcv)
                current_since = ohlcv[-1][0] + 1
                
                print(f"   Fetched {len(all_ohlcv)} / {limit} candles...", end='\r')
                time.sleep(0.5) 
                
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def _add_indicators(self, df):
        if df.empty: return df
        df = df.copy()
        
        # Capitalize for pandas_ta
        df.columns = [c.capitalize() for c in df.columns] 

        # Indicators
        df['log_ret'] = np.log(df['Close'] / df['Close'].shift(1))
        df['rsi'] = ta.rsi(df['Close'], length=14) / 100.0
        
        macd_df = ta.macd(df['Close'])
        if macd_df is not None:
            df['macd'] = macd_df.iloc[:, 0] / df['Close']

        df['atr'] = ta.atr(df['High'], df['Low'], df['Close'], length=14) / df['Close']

        bbands = ta.bbands(df['Close'], length=20, std=2)
        if bbands is not None:
            lower = bbands.iloc[:, 0]
            upper = bbands.iloc[:, 1]
            df['bb_pos'] = (df['Close'] - lower) / (upper - lower)
            df['bb_width'] = (upper - lower) / df['Close'] 
        
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        # Return to lowercase for the Environment
        df.columns = [c.lower() for c in df.columns]

        return df

    def prepare_multitimeframe_data(self, symbol, base_timeframe='5m', start_limit=30000):
        print("--- Processing Data Pipeline ---")
        df = self.download_data(symbol, base_timeframe, limit=start_limit)
        df = self._add_indicators(df)
        
        original_len = len(df)
        df.dropna(inplace=True)
        print(f"\n🧹 Cleaned Data: {original_len} -> {len(df)} rows")
        
        return df