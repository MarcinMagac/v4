import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()


class DataClient:
    BASE_URL = "https://api.twelvedata.com"
    CSV_FILE = "selected_assets.csv"
    CACHE_TTL = 60

    def __init__(self):
        self.api_key = os.getenv("TWELVE_DATA_API_KEY")
        self.quota = {"limit": 800, "remaining": 800, "used": 0, "percent": 0}
        self._cache = {}
        self.available_assets = self._load_assets_from_csv()

    def _load_assets_from_csv(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        file_path = os.path.join(project_root, self.CSV_FILE)

        assets = []
        if not os.path.exists(file_path):
            print("Brak pliku CSV! Uruchom generate_assets.py")
            return []

        try:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                prefix = "💎" if row['type'] == 'crypto' else ("🇵🇱" if row.get('currency') == 'PLN' else "🇺🇸")
                assets.append({
                    "symbol": row['symbol'],
                    "label": f"{prefix} {row['name']} ({row['symbol']})",
                    "type": row['type']
                })
            return assets
        except Exception as e:
            print(f"Błąd CSV: {e}")
            return []

    def get_all_assets(self):
        return self.available_assets

    def fetch_series(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> pd.DataFrame:
        clean_symbol = symbol.upper()
        cache_key = f"{clean_symbol}_{interval}"
        current_time = time.time()

        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if current_time - timestamp < self.CACHE_TTL:
                return data
            else:
                print(f"[CACHE] Dane wygasły dla {clean_symbol}, odświeżam...")

        params = {"symbol": clean_symbol, "interval": interval, "outputsize": outputsize, "apikey": self.api_key,
                  "order": "ASC"}
        print(f"[API] Pobieranie: {clean_symbol}")

        try:
            response = requests.get(f"{self.BASE_URL}/time_series", params=params)
            data = response.json()

            if "values" not in data:
                print(f"[API ERROR] Response: {data}")
                raise Exception("Brak danych w API")

            df = pd.DataFrame(data["values"])

            # DIAGNOSTYKA: Sprawdźmy co przyszło
            # print(f"[DEBUG] Kolumny z API dla {clean_symbol}: {df.columns.tolist()}")

            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            cols_to_keep = ["open", "high", "low", "close", "volume"]

            for c in cols_to_keep:
                if c in df.columns:
                    df[c] = df[c].astype(float)

            if "volume" not in df.columns:
                print(f"[API WARNING] Brak wolumenu dla {clean_symbol} (To normalne dla Forex/Indeksów)")
                df["volume"] = 0.0

            final_df = df[cols_to_keep]

            self._cache[cache_key] = (final_df, current_time)

            return final_df
        except Exception as e:
            print(f"Błąd API: {e}")
            if cache_key in self._cache:
                print("[API] Używam starych danych z cache (Awaryjnie)")
                return self._cache[cache_key][0]
            raise e

    def get_quota(self):
        return self.quota


client = DataClient()