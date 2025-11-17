"""
Template messages for different risk scenarios.
Used by generate_preprocessed_analysis.py to create realistic concern messages
and intervention recommendations without calling AI APIs.
"""

# Concern messages by risk level
CONCERNS = {
    "low_risk": [
        "Customer is healthy and engaged with no significant concerns",
        "All metrics are stable with positive engagement trends",
        "Strong usage patterns indicate high satisfaction",
        "Consistent activity levels show continued product value",
        "Customer relationship is stable with good communication",
    ],
    "medium_risk_feature_decline": [
        "Feature usage has decreased by 25-40%, potentially indicating reduced value perception",
        "Declining feature adoption suggests unmet needs or workflow changes",
        "Customer is using fewer platform capabilities compared to previous months",
        "Reduced feature engagement may signal changing requirements",
    ],
    "medium_risk_response_time": [
        "Email response time has increased significantly, indicating potential disengagement",
        "Slower responses may signal reduced priority or satisfaction issues",
        "Communication delays suggest declining attention to our platform",
        "Response time trending upward - may indicate competing priorities",
    ],
    "medium_risk_login_decline": [
        "Login frequency has decreased moderately over the past 60 days",
        "Platform access is declining which may indicate reduced dependency",
        "User engagement showing downward trend in recent weeks",
        "Reduced login activity suggests possible workflow changes",
    ],
    "high_risk_login_decline": [
        "Significant drop in login frequency indicates serious disengagement",
        "Reduced platform access suggests declining interest or perceived value",
        "Sharp decrease in user activity over the past 30-60 days",
        "Login metrics show concerning downward trend requiring immediate attention",
    ],
    "high_risk_multiple_signals": [
        "Multiple decay signals suggest compounding dissatisfaction issues",
        "Combination of declining metrics indicates high churn risk",
        "Several negative trends converging - urgent review needed",
        "Customer showing multiple warning signs across different metrics",
    ],
    "high_risk_payment": [
        "Payment delays combined with usage decline indicate financial or value concerns",
        "Late payments suggest budget pressures or questioning of ROI",
        "Payment issues correlating with reduced engagement - possible churn signal",
    ],
    "critical_risk": [
        "Severe disengagement across all metrics requires immediate intervention",
        "Customer showing strong indicators of imminent churn within 30 days",
        "Multiple critical signals suggest urgent retention action needed",
        "Extreme decline in all engagement metrics - emergency escalation required",
        "Customer relationship at critical risk - immediate executive involvement needed",
    ],
}

# Intervention recommendations by risk level
INTERVENTIONS = {
    "low_risk": [
        "Continue regular quarterly business reviews and success metrics monitoring",
        "Share relevant case studies and new feature announcements proactively",
        "Maintain current cadence of check-ins and value demonstrations",
        "Schedule annual strategic planning session to align on future roadmap",
    ],
    "medium_risk_feature": [
        "Schedule product training session to maximize feature utilization",
        "Offer targeted training on underutilized premium features",
        "Conduct feature adoption workshop with hands-on guidance",
        "Share use cases from similar customers achieving better outcomes",
    ],
    "medium_risk_engagement": [
        "Schedule proactive check-in within 2 weeks to understand changing needs",
        "Conduct product feedback session to identify gaps or friction points",
        "Reach out to key stakeholders to assess satisfaction and address concerns",
        "Book 30-minute success review to realign on goals and value metrics",
    ],
    "high_risk_immediate": [
        "Immediate CSM outreach (within 48 hours) to identify pain points",
        "Executive sponsor engagement to rebuild relationship at leadership level",
        "Schedule emergency meeting with key stakeholders this week",
        "Fast-track any pending support issues or feature requests",
    ],
    "high_risk_retention": [
        "Offer limited-time discount or additional services to demonstrate commitment",
        "Create custom success plan addressing specific concerns and goals",
        "Provide dedicated onboarding specialist for 30-day re-engagement program",
        "Consider contract flexibility or pilot program for new features",
    ],
    "critical_risk_emergency": [
        "URGENT: Executive escalation to C-level within 24 hours",
        "Immediate intervention: CEO or VP outreach with special retention offer",
        "Emergency response: Fast-track all outstanding issues and requests",
        "Critical: Offer significant account credit and dedicated support team",
    ],
    "critical_risk_executive": [
        "Schedule emergency executive meeting within 48 hours",
        "Deploy senior leadership for relationship recovery effort",
        "Offer executive sponsor program with monthly C-level touchpoints",
        "Consider bringing in founder/CEO for personal outreach",
    ],
}

# Decay signal definitions
DECAY_SIGNALS = {
    "login_decline_moderate": "login_frequency_decline_moderate",
    "login_decline_severe": "login_frequency_decline_severe",
    "feature_decline": "feature_usage_decrease",
    "feature_decline_severe": "feature_usage_severe_decrease",
    "response_time_increase": "email_response_time_increase",
    "response_time_severe": "email_response_time_severe_increase",
    "payment_delay": "payment_delays",
    "payment_delay_severe": "payment_delays_severe",
    "negative_sentiment": "negative_support_sentiment",
    "ticket_increase": "increased_support_tickets",
    "engagement_drop": "overall_engagement_decline",
    "critical_inactivity": "critical_inactivity_detected",
}

def get_concern_for_signals(risk_level: str, signals: list) -> str:
    """
    Get appropriate concern message based on risk level and decay signals.
    
    Args:
        risk_level: "low", "medium", "high", or "critical"
        signals: List of decay signal strings
        
    Returns:
        Human-readable concern message
    """
    import random
    
    if risk_level == "low":
        return random.choice(CONCERNS["low_risk"])
    
    if risk_level == "medium":
        if any("feature" in s for s in signals):
            return random.choice(CONCERNS["medium_risk_feature_decline"])
        elif any("response" in s for s in signals):
            return random.choice(CONCERNS["medium_risk_response_time"])
        elif any("login" in s for s in signals):
            return random.choice(CONCERNS["medium_risk_login_decline"])
        else:
            return random.choice(CONCERNS["medium_risk_feature_decline"])
    
    if risk_level == "high":
        if len(signals) >= 3:
            return random.choice(CONCERNS["high_risk_multiple_signals"])
        elif any("login" in s for s in signals):
            return random.choice(CONCERNS["high_risk_login_decline"])
        elif any("payment" in s for s in signals):
            return random.choice(CONCERNS["high_risk_payment"])
        else:
            return random.choice(CONCERNS["high_risk_multiple_signals"])
    
    if risk_level == "critical":
        return random.choice(CONCERNS["critical_risk"])
    
    return "Customer requires attention"

def get_intervention_for_risk(risk_level: str, signals: list) -> str:
    """
    Get appropriate intervention recommendation based on risk level and signals.
    
    Args:
        risk_level: "low", "medium", "high", or "critical"
        signals: List of decay signal strings
        
    Returns:
        Recommended intervention action
    """
    import random
    
    if risk_level == "low":
        return random.choice(INTERVENTIONS["low_risk"])
    
    if risk_level == "medium":
        if any("feature" in s for s in signals):
            return random.choice(INTERVENTIONS["medium_risk_feature"])
        else:
            return random.choice(INTERVENTIONS["medium_risk_engagement"])
    
    if risk_level == "high":
        if random.random() < 0.5:
            return random.choice(INTERVENTIONS["high_risk_immediate"])
        else:
            return random.choice(INTERVENTIONS["high_risk_retention"])
    
    if risk_level == "critical":
        if random.random() < 0.5:
            return random.choice(INTERVENTIONS["critical_risk_emergency"])
        else:
            return random.choice(INTERVENTIONS["critical_risk_executive"])
    
    return "Schedule check-in to assess customer health"
