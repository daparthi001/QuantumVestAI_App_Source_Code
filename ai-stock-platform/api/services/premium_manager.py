"""
Premium Feature Management System
Created: 2025-01-09
Author: AI Assistant for QuantumVestAI
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("api.premium")

class SubscriptionTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class FeatureType(Enum):
    AI_PREDICTIONS = "ai_predictions"
    REAL_TIME_ALERTS = "real_time_alerts"
    ADVANCED_ANALYTICS = "advanced_analytics"
    PREMIUM_CONTENT = "premium_content"
    API_ACCESS = "api_access"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    RISK_ANALYSIS = "risk_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CUSTOM_REPORTS = "custom_reports"
    PRIORITY_SUPPORT = "priority_support"

@dataclass
class Feature:
    """Individual feature definition"""
    name: str
    feature_type: FeatureType
    description: str
    required_tier: SubscriptionTier
    usage_limits: Dict[str, int]  # e.g., {"daily_requests": 100}
    enabled: bool = True

@dataclass
class SubscriptionPlan:
    """Subscription plan definition"""
    id: str
    name: str
    tier: SubscriptionTier
    price_monthly: float
    price_yearly: float
    features: List[str]  # Feature IDs
    limits: Dict[str, int]
    description: str
    popular: bool = False

@dataclass
class UserSubscription:
    """User's subscription details"""
    user_id: str
    plan_id: str
    tier: SubscriptionTier
    start_date: datetime
    end_date: datetime
    auto_renew: bool
    payment_method: str
    status: str  # active, expired, cancelled, suspended
    usage_stats: Dict[str, int]

class PremiumFeatureManager:
    """Manages premium features and subscriptions"""
    
    def __init__(self):
        self.features = self._initialize_features()
        self.plans = self._initialize_plans()
        self.user_subscriptions = {}  # In real app, this would be from database
        
    def _initialize_features(self) -> Dict[str, Feature]:
        """Initialize all available features"""
        features = {}
        
        # AI Predictions
        features["basic_predictions"] = Feature(
            name="Basic AI Predictions",
            feature_type=FeatureType.AI_PREDICTIONS,
            description="AI-powered stock price predictions with basic models",
            required_tier=SubscriptionTier.FREE,
            usage_limits={"daily_predictions": 5, "stocks_tracked": 10}
        )
        
        features["advanced_predictions"] = Feature(
            name="Advanced AI Predictions",
            feature_type=FeatureType.AI_PREDICTIONS,
            description="Multi-model ensemble predictions with confidence intervals",
            required_tier=SubscriptionTier.PREMIUM,
            usage_limits={"daily_predictions": 100, "stocks_tracked": 500}
        )
        
        features["enterprise_predictions"] = Feature(
            name="Enterprise AI Predictions",
            feature_type=FeatureType.AI_PREDICTIONS,
            description="Custom AI models with real-time training and unlimited predictions",
            required_tier=SubscriptionTier.ENTERPRISE,
            usage_limits={"daily_predictions": -1, "stocks_tracked": -1}  # -1 = unlimited
        )
        
        # Real-time Alerts
        features["basic_alerts"] = Feature(
            name="Basic Price Alerts",
            feature_type=FeatureType.REAL_TIME_ALERTS,
            description="Email alerts for price thresholds",
            required_tier=SubscriptionTier.FREE,
            usage_limits={"active_alerts": 3, "alert_frequency": 60}  # 60 minutes minimum
        )
        
        features["premium_alerts"] = Feature(
            name="Premium Real-time Alerts",
            feature_type=FeatureType.REAL_TIME_ALERTS,
            description="Multi-channel alerts (email, SMS, push) with advanced conditions",
            required_tier=SubscriptionTier.PREMIUM,
            usage_limits={"active_alerts": 50, "alert_frequency": 1}  # 1 minute minimum
        )
        
        # Analytics
        features["basic_analytics"] = Feature(
            name="Basic Analytics",
            feature_type=FeatureType.ADVANCED_ANALYTICS,
            description="Standard charts and performance metrics",
            required_tier=SubscriptionTier.FREE,
            usage_limits={"dashboard_refresh": 60, "historical_data_months": 12}
        )
        
        features["advanced_analytics"] = Feature(
            name="Advanced Analytics",
            feature_type=FeatureType.ADVANCED_ANALYTICS,
            description="Interactive charts, custom indicators, and backtesting",
            required_tier=SubscriptionTier.BASIC,
            usage_limits={"dashboard_refresh": 5, "historical_data_months": 60}
        )
        
        features["enterprise_analytics"] = Feature(
            name="Enterprise Analytics",
            feature_type=FeatureType.ADVANCED_ANALYTICS,
            description="Real-time data feeds, custom dashboards, and API access",
            required_tier=SubscriptionTier.ENTERPRISE,
            usage_limits={"dashboard_refresh": 1, "historical_data_months": -1}
        )
        
        # Premium Content
        features["premium_content"] = Feature(
            name="Premium Educational Content",
            feature_type=FeatureType.PREMIUM_CONTENT,
            description="Exclusive guides, case studies, and expert analysis",
            required_tier=SubscriptionTier.PREMIUM,
            usage_limits={"monthly_downloads": 20}
        )
        
        # API Access
        features["api_access"] = Feature(
            name="API Access",
            feature_type=FeatureType.API_ACCESS,
            description="RESTful API for integrating QuantumVestAI into your applications",
            required_tier=SubscriptionTier.BASIC,
            usage_limits={"daily_api_calls": 1000}
        )
        
        features["enterprise_api"] = Feature(
            name="Enterprise API",
            feature_type=FeatureType.API_ACCESS,
            description="High-volume API access with WebSocket streaming",
            required_tier=SubscriptionTier.ENTERPRISE,
            usage_limits={"daily_api_calls": 100000}
        )
        
        # Portfolio Optimization
        features["portfolio_optimization"] = Feature(
            name="AI Portfolio Optimization",
            feature_type=FeatureType.PORTFOLIO_OPTIMIZATION,
            description="Modern portfolio theory with AI-enhanced optimization",
            required_tier=SubscriptionTier.PREMIUM,
            usage_limits={"monthly_optimizations": 10}
        )
        
        # Risk Analysis
        features["risk_analysis"] = Feature(
            name="Advanced Risk Analysis",
            feature_type=FeatureType.RISK_ANALYSIS,
            description="VaR, stress testing, and scenario analysis",
            required_tier=SubscriptionTier.PREMIUM,
            usage_limits={"risk_reports": 5}
        )
        
        # Sentiment Analysis
        features["sentiment_analysis"] = Feature(
            name="Multi-Source Sentiment Analysis",
            feature_type=FeatureType.SENTIMENT_ANALYSIS,
            description="Social media, news, and expert sentiment tracking",
            required_tier=SubscriptionTier.BASIC,
            usage_limits={"sentiment_queries": 50}
        )
        
        # Custom Reports
        features["custom_reports"] = Feature(
            name="Custom Reports",
            feature_type=FeatureType.CUSTOM_REPORTS,
            description="Personalized investment reports and market analysis",
            required_tier=SubscriptionTier.PREMIUM,
            usage_limits={"monthly_reports": 4}
        )
        
        # Priority Support
        features["priority_support"] = Feature(
            name="Priority Support",
            feature_type=FeatureType.PRIORITY_SUPPORT,
            description="24/7 priority customer support with dedicated account manager",
            required_tier=SubscriptionTier.ENTERPRISE,
            usage_limits={}
        )
        
        return features
    
    def _initialize_plans(self) -> Dict[str, SubscriptionPlan]:
        """Initialize subscription plans"""
        plans = {}
        
        plans["free"] = SubscriptionPlan(
            id="free",
            name="Free",
            tier=SubscriptionTier.FREE,
            price_monthly=0.0,
            price_yearly=0.0,
            features=[
                "basic_predictions",
                "basic_alerts",
                "basic_analytics"
            ],
            limits={
                "daily_predictions": 5,
                "active_alerts": 3,
                "stocks_tracked": 10,
                "dashboard_refresh": 60
            },
            description="Perfect for getting started with AI-powered investing"
        )
        
        plans["basic"] = SubscriptionPlan(
            id="basic",
            name="Basic",
            tier=SubscriptionTier.BASIC,
            price_monthly=19.99,
            price_yearly=199.99,
            features=[
                "basic_predictions",
                "basic_alerts",
                "advanced_analytics",
                "sentiment_analysis",
                "api_access"
            ],
            limits={
                "daily_predictions": 25,
                "active_alerts": 10,
                "stocks_tracked": 50,
                "dashboard_refresh": 5,
                "daily_api_calls": 1000,
                "sentiment_queries": 50
            },
            description="Enhanced features for serious individual investors",
            popular=True
        )
        
        plans["premium"] = SubscriptionPlan(
            id="premium",
            name="Premium",
            tier=SubscriptionTier.PREMIUM,
            price_monthly=49.99,
            price_yearly=499.99,
            features=[
                "advanced_predictions",
                "premium_alerts",
                "advanced_analytics",
                "premium_content",
                "portfolio_optimization",
                "risk_analysis",
                "sentiment_analysis",
                "custom_reports",
                "api_access"
            ],
            limits={
                "daily_predictions": 100,
                "active_alerts": 50,
                "stocks_tracked": 500,
                "dashboard_refresh": 5,
                "daily_api_calls": 5000,
                "monthly_optimizations": 10,
                "risk_reports": 5,
                "monthly_reports": 4,
                "monthly_downloads": 20,
                "sentiment_queries": 200
            },
            description="Professional-grade tools for advanced investors and advisors"
        )
        
        plans["enterprise"] = SubscriptionPlan(
            id="enterprise",
            name="Enterprise",
            tier=SubscriptionTier.ENTERPRISE,
            price_monthly=199.99,
            price_yearly=1999.99,
            features=[
                "enterprise_predictions",
                "premium_alerts",
                "enterprise_analytics",
                "premium_content",
                "portfolio_optimization",
                "risk_analysis",
                "sentiment_analysis",
                "custom_reports",
                "enterprise_api",
                "priority_support"
            ],
            limits={
                "daily_predictions": -1,  # unlimited
                "active_alerts": -1,
                "stocks_tracked": -1,
                "dashboard_refresh": 1,
                "daily_api_calls": 100000,
                "monthly_optimizations": -1,
                "risk_reports": -1,
                "monthly_reports": -1,
                "monthly_downloads": -1,
                "sentiment_queries": -1
            },
            description="Unlimited access for institutions and professional traders"
        )
        
        return plans
    
    def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """Get user's current subscription"""
        return self.user_subscriptions.get(user_id)
    
    def get_user_tier(self, user_id: str) -> SubscriptionTier:
        """Get user's subscription tier"""
        subscription = self.get_user_subscription(user_id)
        if subscription and subscription.status == "active":
            return subscription.tier
        return SubscriptionTier.FREE
    
    def has_feature_access(self, user_id: str, feature_id: str) -> bool:
        """Check if user has access to a specific feature"""
        user_tier = self.get_user_tier(user_id)
        feature = self.features.get(feature_id)
        
        if not feature or not feature.enabled:
            return False
        
        # Check tier hierarchy
        tier_hierarchy = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.BASIC: 1,
            SubscriptionTier.PREMIUM: 2,
            SubscriptionTier.ENTERPRISE: 3
        }
        
        return tier_hierarchy[user_tier] >= tier_hierarchy[feature.required_tier]
    
    def check_usage_limit(self, user_id: str, feature_id: str, usage_type: str) -> Dict[str, Any]:
        """Check if user has exceeded usage limits for a feature"""
        feature = self.features.get(feature_id)
        subscription = self.get_user_subscription(user_id)
        
        if not feature:
            return {"allowed": False, "reason": "Feature not found"}
        
        if not self.has_feature_access(user_id, feature_id):
            return {"allowed": False, "reason": "Feature not available in current plan"}
        
        # Get usage limits
        if subscription:
            plan = self.plans.get(subscription.plan_id)
            limit = plan.limits.get(usage_type, feature.usage_limits.get(usage_type, 0))
        else:
            limit = feature.usage_limits.get(usage_type, 0)
        
        # -1 means unlimited
        if limit == -1:
            return {"allowed": True, "remaining": -1}
        
        # Get current usage
        current_usage = 0
        if subscription and usage_type in subscription.usage_stats:
            current_usage = subscription.usage_stats[usage_type]
        
        remaining = max(0, limit - current_usage)
        allowed = remaining > 0
        
        return {
            "allowed": allowed,
            "remaining": remaining,
            "limit": limit,
            "current_usage": current_usage
        }
    
    def increment_usage(self, user_id: str, usage_type: str, amount: int = 1):
        """Increment usage counter for a user"""
        subscription = self.get_user_subscription(user_id)
        if subscription:
            if usage_type not in subscription.usage_stats:
                subscription.usage_stats[usage_type] = 0
            subscription.usage_stats[usage_type] += amount
    
    def reset_usage_stats(self, user_id: str, period: str = "monthly"):
        """Reset usage statistics for a user (called by scheduler)"""
        subscription = self.get_user_subscription(user_id)
        if subscription:
            # Reset based on period
            if period == "daily":
                daily_counters = ["daily_predictions", "daily_api_calls"]
                for counter in daily_counters:
                    subscription.usage_stats[counter] = 0
            elif period == "monthly":
                monthly_counters = ["monthly_optimizations", "monthly_reports", "monthly_downloads"]
                for counter in monthly_counters:
                    subscription.usage_stats[counter] = 0
    
    def get_plan_features(self, plan_id: str) -> List[Feature]:
        """Get all features included in a plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            return []
        
        return [self.features[feature_id] for feature_id in plan.features if feature_id in self.features]
    
    def compare_plans(self, plan_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple subscription plans"""
        comparison = {
            "plans": [],
            "features": {}
        }
        
        all_features = set()
        plan_data = {}
        
        # Collect plan data and all features
        for plan_id in plan_ids:
            plan = self.plans.get(plan_id)
            if plan:
                plan_data[plan_id] = plan
                all_features.update(plan.features)
        
        # Create comparison structure
        comparison["plans"] = [
            {
                "id": plan.id,
                "name": plan.name,
                "price_monthly": plan.price_monthly,
                "price_yearly": plan.price_yearly,
                "description": plan.description,
                "popular": plan.popular
            }
            for plan in plan_data.values()
        ]
        
        # Feature comparison
        for feature_id in all_features:
            feature = self.features.get(feature_id)
            if feature:
                comparison["features"][feature_id] = {
                    "name": feature.name,
                    "description": feature.description,
                    "availability": {
                        plan_id: feature_id in plan.features
                        for plan_id, plan in plan_data.items()
                    }
                }
        
        return comparison
    
    def upgrade_user(self, user_id: str, new_plan_id: str, payment_method: str) -> Dict[str, Any]:
        """Upgrade user to a new plan"""
        new_plan = self.plans.get(new_plan_id)
        if not new_plan:
            return {"success": False, "error": "Invalid plan"}
        
        current_subscription = self.get_user_subscription(user_id)
        
        # Create new subscription
        new_subscription = UserSubscription(
            user_id=user_id,
            plan_id=new_plan_id,
            tier=new_plan.tier,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),  # Monthly by default
            auto_renew=True,
            payment_method=payment_method,
            status="active",
            usage_stats={}
        )
        
        # Preserve usage stats if upgrading
        if current_subscription:
            new_subscription.usage_stats = current_subscription.usage_stats.copy()
        
        self.user_subscriptions[user_id] = new_subscription
        
        return {
            "success": True,
            "subscription": new_subscription,
            "message": f"Successfully upgraded to {new_plan.name} plan"
        }
    
    def cancel_subscription(self, user_id: str) -> Dict[str, Any]:
        """Cancel user subscription"""
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return {"success": False, "error": "No active subscription"}
        
        subscription.status = "cancelled"
        subscription.auto_renew = False
        
        return {
            "success": True,
            "message": "Subscription cancelled successfully",
            "access_until": subscription.end_date
        }
    
    def get_usage_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get user's usage analytics"""
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return {"error": "No subscription found"}
        
        plan = self.plans.get(subscription.plan_id)
        if not plan:
            return {"error": "Invalid plan"}
        
        analytics = {
            "plan": {
                "name": plan.name,
                "tier": plan.tier.value
            },
            "usage": {},
            "limits": plan.limits,
            "recommendations": []
        }
        
        # Calculate usage percentages
        for usage_type, current_usage in subscription.usage_stats.items():
            limit = plan.limits.get(usage_type, 0)
            if limit > 0:
                percentage = (current_usage / limit) * 100
                analytics["usage"][usage_type] = {
                    "current": current_usage,
                    "limit": limit,
                    "percentage": round(percentage, 1),
                    "remaining": limit - current_usage
                }
                
                # Add recommendations
                if percentage > 80:
                    analytics["recommendations"].append({
                        "type": "usage_warning",
                        "message": f"You've used {percentage:.1f}% of your {usage_type} limit",
                        "action": "Consider upgrading your plan"
                    })
            elif limit == -1:
                analytics["usage"][usage_type] = {
                    "current": current_usage,
                    "limit": "unlimited",
                    "percentage": 0,
                    "remaining": "unlimited"
                }
        
        return analytics
    
    def get_feature_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get feature recommendations for user"""
        user_tier = self.get_user_tier(user_id)
        subscription = self.get_user_subscription(user_id)
        
        recommendations = []
        
        # Recommend higher tier features
        if user_tier != SubscriptionTier.ENTERPRISE:
            higher_tier_features = [
                feature for feature in self.features.values()
                if feature.required_tier.value > user_tier.value
            ]
            
            for feature in higher_tier_features[:3]:  # Top 3 recommendations
                recommendations.append({
                    "type": "feature_upgrade",
                    "feature_name": feature.name,
                    "description": feature.description,
                    "required_tier": feature.required_tier.value,
                    "benefit": "Enhanced capabilities and higher limits"
                })
        
        # Recommend based on usage patterns
        if subscription:
            high_usage_features = [
                usage_type for usage_type, current in subscription.usage_stats.items()
                if current > 0
            ]
            
            if len(high_usage_features) > 3:
                recommendations.append({
                    "type": "usage_optimization",
                    "message": "You're actively using multiple features",
                    "suggestion": "Consider upgrading for better limits and additional features"
                })
        
        return recommendations
    
    def get_all_plans(self) -> List[SubscriptionPlan]:
        """Get all available subscription plans"""
        return list(self.plans.values())
    
    def get_plan_pricing(self, plan_id: str, billing_cycle: str = "monthly") -> Dict[str, Any]:
        """Get pricing information for a plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}
        
        if billing_cycle == "monthly":
            price = plan.price_monthly
            savings = 0
        else:  # yearly
            price = plan.price_yearly
            monthly_equivalent = plan.price_monthly * 12
            savings = monthly_equivalent - price
        
        return {
            "plan_id": plan_id,
            "plan_name": plan.name,
            "billing_cycle": billing_cycle,
            "price": price,
            "savings": savings if billing_cycle == "yearly" else 0,
            "savings_percentage": round((savings / (price + savings)) * 100, 1) if savings > 0 else 0
        }

# Global premium feature manager instance
premium_manager = PremiumFeatureManager()
