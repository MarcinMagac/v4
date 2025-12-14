import json
import csv
import os

# --- KONFIGURACJA VIP ---
TOP_CRYPTO = {
    "BTC/USD", "ETH/USD", "USDT/USD", "BNB/USD", "SOL/USD", "XRP/USD", "USDC/USD", "ADA/USD", "AVAX/USD", "DOGE/USD",
    "DOT/USD", "TRX/USD", "LINK/USD", "MATIC/USD", "WBTC/USD", "SHIB/USD", "LTC/USD", "DAI/USD", "UNI/USD"
}

TOP_STOCKS_GLOBAL = {
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK.B", "LLY", "V", "UNH", "XOM", "JPM"
}

TOP_STOCKS_PL = {
    "ALE", "ACP", "CCC", "CDR", "CPS", "DNP", "JSW", "KGH", "LPP", "MBK", "OPL", "PEO", "PGE", "PKN", "PKO", "PZU",
    "SPL"
}


def main():
    print("--- ROZPOCZYNAM GENEROWANIE LISTY ---")

    try:
        with open('cryptocurrencies.json', 'r', encoding='utf-8') as f:
            crypto_data = json.load(f).get('data', [])
    except:
        crypto_data = []

    try:
        with open('stocks.json', 'r', encoding='utf-8') as f:
            stocks_data = json.load(f).get('data', [])
    except:
        stocks_data = []

    final_list = []

    # KRYPTO
    for item in crypto_data:
        sym = item.get('symbol', '')
        if sym.endswith('/USD'):
            prio = 1 if sym in TOP_CRYPTO else 0
            final_list.append(
                {'symbol': sym, 'name': item.get('currency_base', ''), 'type': 'crypto', 'currency': 'USD',
                 'exchange': 'CRYPTO', 'priority': prio})

    # AKCJE
    for item in stocks_data:
        sym = item.get('symbol', '')
        curr = item.get('currency', '')
        country = item.get('country', '')

        # USA
        if curr == 'USD' and country == 'United States':
            prio = 1 if sym in TOP_STOCKS_GLOBAL else 0
            final_list.append(
                {'symbol': sym, 'name': item.get('name', sym), 'type': 'stock', 'currency': curr, 'exchange': 'NYSE',
                 'priority': prio})

        # PL
        if curr == 'PLN' or country == 'Poland':
            prio = 1 if sym in TOP_STOCKS_PL else 0
            final_list.append(
                {'symbol': sym, 'name': item.get('name', sym), 'type': 'stock', 'currency': curr, 'exchange': 'GPW',
                 'priority': prio})

    # Sortowanie i przycięcie
    final_list.sort(key=lambda x: (-x['priority'], x['symbol']))
    final_vip_list = final_list[:300]

    # Zapis
    headers = ['symbol', 'name', 'type', 'currency', 'exchange']
    with open('selected_assets.csv', 'w', newline='', encoding='utf-8') as f:
        # !!! TU BYŁ BŁĄD - TERAZ JEST POPRAWKA !!!
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(final_vip_list)

    print(f"SUKCES! Utworzono plik: selected_assets.csv ({len(final_vip_list)} pozycji).")


if __name__ == "__main__":
    main()