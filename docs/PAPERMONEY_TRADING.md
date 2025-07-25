# PaperMoney Paper Trading Setup

This guide explains how to connect QuantumVestAI's order management system to the TD Ameritrade **paperMoney** environment for risk‑free practice trading.

## 1. Create a TD Ameritrade Developer Account
- Register at [developer.tdameritrade.com](https://developer.tdameritrade.com/).
- Under **My Apps**, create a new application and note the _Consumer Key_.

## 2. Configure OAuth Redirect URI
- Set your application's redirect URI to `https://localhost` or a secure endpoint of your choosing.
- Save the configuration so paperMoney can redirect back after user authorization.

## 3. Obtain an Access Token
- Direct the user to the TD Ameritrade OAuth URL with your Consumer Key and redirect URI.
- After login, TD Ameritrade will redirect to the URI with an authorization code.
- Exchange this code for an access token using the token endpoint. The token grants access to paperMoney order APIs.

## 4. Use the paperMoney Endpoints
- All trading requests should include the access token in the `Authorization` header.
- Use the `/accounts/{accountId}/orders` endpoint for placing practice orders.
- Responses from paperMoney mimic live trading but do not execute real trades.

## 5. Integrate with OrderManagementService
- Use the provided `PaperMoneyExecutionService` (found in `services/paper_money_execution.py`) which implements the same interface as `TradingExecutionService`.
- Replace the dummy execution layer with this service when paper trading is enabled.

With these steps, QuantumVestAI can send simulated trades to the paperMoney environment, allowing users to test strategies without risking capital.
