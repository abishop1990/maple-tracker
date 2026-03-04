"""
Water Intake Anomaly Detection for Cats
Detects unusual water intake patterns indicating potential health issues
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta


class WaterIntakeAnalyzer:
    """Analyzes cat water intake for health anomalies"""
    
    # Normal cat water intake: 40-60 mL/kg/day
    NORMAL_MIN_ML_PER_KG = 40
    NORMAL_MAX_ML_PER_KG = 60
    
    # Concerning thresholds
    HIGH_INTAKE_THRESHOLD = 80  # mL/kg/day = possible diabetes/hyperthyroidism
    LOW_INTAKE_THRESHOLD = 30   # mL/kg/day = possible dehydration
    
    def __init__(self, cat_weight_kg: float):
        self.cat_weight_kg = cat_weight_kg
        self.normal_daily_min = cat_weight_kg * self.NORMAL_MIN_ML_PER_KG
        self.normal_daily_max = cat_weight_kg * self.NORMAL_MAX_ML_PER_KG
    
    def analyze_daily_intake(self, water_ml: float) -> Dict[str, Any]:
        """Analyze single day's water intake"""
        per_kg = water_ml / self.cat_weight_kg if self.cat_weight_kg > 0 else 0
        
        alert = None
        severity = None
        
        if per_kg > self.HIGH_INTAKE_THRESHOLD:
            alert = f"High water intake: {water_ml:.0f}mL ({per_kg:.1f}mL/kg)"
            severity = "HIGH"
            recommendation = "Contact vet immediately. May indicate diabetes or hyperthyroidism."
        elif water_ml > self.normal_daily_max * 1.3:
            alert = f"Elevated water intake: {water_ml:.0f}mL"
            severity = "MEDIUM"
            recommendation = "Monitor closely. Watch for other symptoms."
        elif per_kg < self.LOW_INTAKE_THRESHOLD:
            alert = f"Low water intake: {water_ml:.0f}mL ({per_kg:.1f}mL/kg)"
            severity = "MEDIUM"
            recommendation = "Ensure fresh water available. Monitor for dehydration."
        elif water_ml < self.normal_daily_min * 0.7:
            alert = f"Significantly low intake: {water_ml:.0f}mL"
            severity = "HIGH"
            recommendation = "Contact vet. May indicate kidney issues or dehydration."
        
        return {
            "water_ml": water_ml,
            "per_kg": per_kg,
            "status": "normal" if not alert else "abnormal",
            "alert": alert,
            "severity": severity,
            "recommendation": recommendation,
            "normal_range": f"{self.normal_daily_min:.0f}-{self.normal_daily_max:.0f}mL"
        }
    
    def analyze_trend(self, daily_intakes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze water intake trend over time"""
        if len(daily_intakes) < 3:
            return {"status": "insufficient_data"}
        
        intakes = [d.get("water_ml", 0) for d in daily_intakes if d.get("water_ml")]
        
        if not intakes:
            return {"status": "no_data"}
        
        avg_intake = sum(intakes) / len(intakes)
        trend_alert = None
        trend_type = None
        
        # Check for increasing trend (last 7 days vs previous)
        if len(intakes) >= 14:
            recent_7 = intakes[-7:]
            previous_7 = intakes[-14:-7]
            
            recent_avg = sum(recent_7) / len(recent_7)
            previous_avg = sum(previous_7) / len(previous_7)
            
            increase_percent = ((recent_avg - previous_avg) / previous_avg) * 100
            
            if increase_percent > 25:
                trend_alert = f"Water intake up {increase_percent:.1f}% in last week"
                trend_type = "INCREASING"
            elif increase_percent < -25:
                trend_alert = f"Water intake down {increase_percent:.1f}% in last week"
                trend_type = "DECREASING"
        
        return {
            "status": "analyzed",
            "average_intake": avg_intake,
            "trend": trend_type,
            "trend_alert": trend_alert,
            "days_recorded": len(intakes)
        }
    
    def get_health_recommendations(self, daily_intake: float) -> List[str]:
        """Get vet-friendly health recommendations"""
        per_kg = daily_intake / self.cat_weight_kg
        recommendations = []
        
        if per_kg > 80:
            recommendations.extend([
                "Contact veterinarian immediately",
                "Screen for diabetes (elevated blood glucose)",
                "Screen for hyperthyroidism (TSH levels)",
                "Check kidney function (BUN, creatinine)",
            ])
        elif daily_intake > self.normal_daily_max * 1.3:
            recommendations.extend([
                "Monitor for increased drinking (polydipsia)",
                "Record water intake for vet visit",
                "Ensure fresh, clean water always available",
            ])
        elif per_kg < 30:
            recommendations.extend([
                "Contact veterinarian",
                "Check for kidney disease",
                "Assess for dehydration",
                "Ensure water bowl accessibility",
            ])
        elif daily_intake < self.normal_daily_min * 0.7:
            recommendations.extend([
                "Increase water availability",
                "Try water fountains (cats prefer moving water)",
                "Add water bowls in multiple locations",
            ])
        else:
            recommendations.append("Water intake appears normal. Continue monitoring.")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    analyzer = WaterIntakeAnalyzer(cat_weight_kg=4.5)
    
    # Test daily intakes
    test_intakes = [
        150, 160, 155,  # Normal
        200, 220,        # High
        100,             # Low
    ]
    
    for intake in test_intakes:
        result = analyzer.analyze_daily_intake(intake)
        print(f"{intake}mL: {result['status']} - {result.get('alert', 'Normal')}")
