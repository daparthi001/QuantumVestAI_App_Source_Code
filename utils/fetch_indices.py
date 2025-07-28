import os
import sys
from datetime import datetime

# Ensure we can import the API package
ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.services.market_overview_service import MarketOverviewService


def main():
    overview = MarketOverviewService.get_market_overview()
    date = overview.get("date")
    print(f"Market overview for {date}")
    for idx in overview.get("indices", []):
        name = idx.get("name")
        value = idx.get("value")
        change = idx.get("change_percent")
        icon = "📈" if change >= 0 else "📉"
        print(f"{name}: {icon} ${value:.2f} ({change:+.2f}%)")


if __name__ == "__main__":
    main()
