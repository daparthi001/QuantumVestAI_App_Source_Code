# QuantumVestAI Platform

QuantumVestAI is an advanced financial analytics and investment platform that combines machine learning, sentiment analysis, and traditional financial metrics to provide trading insights.

## Architecture Overview

QuantumVestAI is built on a cloud-native architecture, leveraging AWS services and Kubernetes for deployment. The system combines machine learning models, Twitter sentiment analysis, and financial market data to provide comprehensive stock market insights.

```
                                  ┌───────────────────────────────────────────────────────────────┐
                                  │                 AWS Cloud Infrastructure                      │
                                  └───────────────────────────────────────────────────────────────┘
                                                             │
                        ┌─────────────────────────────────────────────────────────────┐
                        ▼                                                             ▼
           ┌───────────────────────────────┐                          ┌──────────────────────────┐
           │        Terraform Layer        │                          │   Route 53 DNS Service   │
           └───────────────────────────────┘                          └──────────────────────────┘
                        │                                                           │
                        ▼                                                           │
┌───────────────────────────────────────────────────────────────────────────┐       │
│                             EKS Cluster                                   │       │
│ ┌─────────────────────────────────────────────────────────────────────┐  │       │
│ │                                                                     │  │       │
│ │  ┌────────────────────┐  ┌────────────────────┐  ┌───────────────┐  │  │       │
│ │  │  Dev Namespace     │  │  Staging Namespace │  │ Prod Namespace│  │  │       │
│ │  │                    │  │                    │  │               │  │  │       │
│ │  │  ┌──────────────┐  │  │  ┌──────────────┐  │  │ ┌───────────┐ │  │  │       │
│ │  │  │API Deployment│  │  │  │API Deployment│  │  │ │API Deploy.│ │  │  │       │
│ │  │  └──────────────┘  │  │  └──────────────┘  │  │ └───────────┘ │  │  │       │
│ │  │         │         │  │         │          │  │       │       │  │  │       │
│ │  │  ┌──────────────┐  │  │  ┌──────────────┐  │  │ ┌───────────┐ │  │  │       │
│ │  │  │UI Deployment │  │  │  │UI Deployment │  │  │ │UI Deploy. │ │  │  │       │
│ │  │  └──────────────┘  │  │  └──────────────┘  │  │ └───────────┘ │  │  │       │
│ │  │         │         │  │         │          │  │       │       │  │  │       │
│ │  │  ┌──────────────┐  │  │  ┌──────────────┐  │  │ ┌───────────┐ │  │  │       │
│ │  │  │  ML Retrain  │  │  │  │  ML Retrain  │  │  │ │ML Retrain │ │  │  │       │
│ │  │  │   CronJob    │  │  │  │   CronJob    │  │  │ │  CronJob  │ │  │  │       │
│ │  │  └──────────────┘  │  │  └──────────────┘  │  │ └───────────┘ │  │  │       │
│ │  │                    │  │                    │  │               │  │  │       │
│ │  └────────────────────┘  └────────────────────┘  └───────────────┘  │  │       │
│ │                                                                     │  │       │
│ │                     Kubernetes Ingress Controller                    │  │       │
│ └─────────────────────────────────────────────────────────────────────┘  │       │
└───────────────────────────────────────────────────────────────────────────┘       │
                        │                                                           │
                        ├───────────────────┐                                       │
                        │                   │                                       │
            ┌───────────▼───────────┐   ┌───▼───────────────┐                       │
            │    RDS Database       │   │    ECR Registry   │◄─────────┐            │
            │  (PostgreSQL Cluster) │   │                   │          │            │
            └───────────────────────┘   └───────────────────┘          │            │
                        │                        ▲                     │            │
                        ▼                        │                     │            │
            ┌───────────────────────┐    ┌───────┴────────┐    ┌──────▼────────┐   │
            │  S3 Bucket (Models)   │    │  GitHub Actions│    │ S3 (UI Static) │   │
            └───────────────────────┘    │     CI/CD      │    └───────────────┘   │
                        │                └────────────────┘            │           │
                        └───────────────────────┬──────────────────────┘           │
                                                │                                  │
                                                ▼                                  ▼
                                   ┌───────────────────────────┐    ┌───────────────────────┐
                                   │  External Data Sources    │    │  User Web Browsers    │
                                   │  - Market Data APIs       │    └───────────────────────┘
                                   │  - Twitter API            │
                                   │  - Financial News         │
                                   └───────────────────────────┘
```

## Core Components

### 1. Infrastructure

- **AWS Cloud**: Primary hosting environment
- **Terraform**: Infrastructure as code for AWS resources
- **EKS (Elastic Kubernetes Service)**: Container orchestration
- **RDS**: PostgreSQL database cluster
- **ECR**: Docker image repository
- **S3**: Storage for ML models and static assets
- **Route 53**: DNS and domain management

### 2. Application Layers

#### Backend (API)
- **FastAPI Framework**: High-performance Python API
- **SQLAlchemy**: ORM for database interaction
- **JWT Authentication**: Secure user authentication
- **ML Integration**: Real-time and batch predictions
- **Twitter Sentiment Analysis**: Social media insights

#### Frontend (UI)
- **React**: Component-based UI library
- **Material-UI**: Design system components
- **Redux**: State management
- **Chart.js**: Data visualization
- **Responsive Design**: Mobile and desktop support

### 3. Machine Learning Pipeline

- **Data Collection**: Financial market data ingestion
- **Feature Engineering**: Transform raw data for ML models
- **Model Training**: LSTM and other algorithms for price prediction
- **Model Evaluation**: Accuracy, precision and recall metrics
- **Automated Retraining**: Scheduled model updates

### 4. Social Media Integration

- **Twitter API**: Real-time tweet collection
- **NLP Processing**: Extract sentiment from financial tweets
- **Sentiment Analysis**: Positive/negative market sentiment
- **Trend Detection**: Identify trending stocks on social media
- **Background Processing**: Efficient data handling

### 5. Deployment and DevOps

- **GitHub Actions**: CI/CD automation
- **Docker**: Container-based deployment
- **Kubernetes**: Orchestration and scaling
- **Multi-Environment**: Development, staging, and production
- **Infrastructure as Code**: Terraform automation

## Getting Started

### Prerequisites

- AWS Account with appropriate permissions
- GitHub account
- Docker installed locally
- kubectl configured for Kubernetes access
- Terraform installed

### Local Development Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/quantumvestai.git
cd quantumvestai
```

2. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration values
```

3. Start local development environment:

```bash
docker-compose up -d
```

4. Access the application:
   - API: http://localhost:8000
   - UI: http://localhost:3000

### Deployment

Deploy to AWS with Terraform and GitHub Actions:

1. Configure GitHub repository secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `JWT_SECRET`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `ADMIN_EMAIL`
   - `ALPHA_VANTAGE_API_KEY`
   - `TWITTER_CONSUMER_KEY`
   - `TWITTER_CONSUMER_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_SECRET`

2. Initiate deployment with GitHub Actions:
   - Navigate to Actions tab in GitHub
   - Select "Deploy QuantumVestAI" workflow
   - Run workflow with desired environment (dev, staging, prod)

## Environment Configuration

QuantumVestAI supports three deployment environments:

### Development (Dev)
- Purpose: Development and testing
- Features: All features enabled, sample data available
- Data: Non-sensitive test data

### Staging
- Purpose: Pre-production testing
- Features: All features enabled, limited sample data
- Data: Representative of production but not sensitive

### Production
- Purpose: Live application
- Features: All features enabled, no sample data
- Data: Real production data

## Key Features

- **Stock Analysis Dashboard**: Comprehensive view of stock performance
- **Portfolio Management**: Track investments and performance
- **Machine Learning Predictions**: AI-powered price forecasts
- **Social Sentiment Analysis**: Twitter trends and sentiment
- **User Authentication**: Secure account management
- **Responsive Design**: Mobile and desktop support

## API Documentation

API documentation is available at `/api/docs` when the application is running. This provides an interactive Swagger UI for exploring and testing API endpoints.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Project Lead - [Your Name](mailto:your.email@example.com)

Project Repository: [https://github.com/yourusername/quantumvestai](https://github.com/yourusername/quantumvestai)