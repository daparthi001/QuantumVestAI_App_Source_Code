-- Reference data for QuantumVestAI

-- Forecast models reference data
INSERT INTO forecast_models (name, description, is_active, parameters) VALUES
('LSTM', 'Long Short-Term Memory neural network model', true, '{"layers": 2, "units": 50, "dropout": 0.2, "epochs": 100}'),
('XGBoost', 'Gradient boosting decision tree model', true, '{"max_depth": 5, "learning_rate": 0.1, "n_estimators": 200}'),
('Prophet', 'Facebook Prophet forecasting model', true, '{"changepoint_prior_scale": 0.05, "seasonality_mode": "multiplicative"}'),
('ARIMA', 'Auto-Regressive Integrated Moving Average', true, '{"p": 5, "d": 1, "q": 0}'),
('Ensemble', 'Ensemble of multiple forecasting models', true, '{"models": ["LSTM", "XGBoost", "Prophet"], "weights": [0.4, 0.4, 0.2]}')
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    parameters = EXCLUDED.parameters;

-- Market sectors reference data
INSERT INTO market_sectors (code, name, description) VALUES
('TECH', 'Technology', 'Companies focused on technology hardware, software, and services'),
('FIN', 'Financial Services', 'Banks, insurance companies, and investment firms'),
('HEALTH', 'Healthcare', 'Medical device companies, pharmaceutical firms, and healthcare providers'),
('ENERGY', 'Energy', 'Oil, gas, renewable energy companies'),
('CONS', 'Consumer Goods', 'Companies that provide goods directly to consumers'),
('INDUS', 'Industrial', 'Manufacturing, aerospace, defense, and transportation companies'),
('UTIL', 'Utilities', 'Electric, water, and gas providers'),
('REIT', 'Real Estate', 'Real estate investment trusts and property management firms'),
('COMM', 'Communication', 'Telecommunication, media, and entertainment companies'),
('MAT', 'Materials', 'Chemical, mining, and construction materials companies')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

-- System configurations
INSERT INTO system_config (key, value, description) VALUES
('api_rate_limits', 
 '{"free": 100, "basic": 1000, "premium": 10000, "enterprise": null}',
 'API rate limits per user role per day'),
('forecast_limits', 
 '{"free": 5, "basic": 20, "premium": 100, "enterprise": null}',
 'Number of forecasts a user can generate per day'),
('whitepaper_upload_limits', 
 '{"free": 2, "basic": 10, "premium": 50, "enterprise": null}',
 'Number of whitepapers a user can upload per day'),
('supported_file_formats', 
 '["pdf", "docx", "txt"]',
 'Supported file formats for whitepaper uploads')
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;