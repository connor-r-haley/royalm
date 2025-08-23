"""
Cost Management System for WWIII Simulator
Helps control API usage and costs while maintaining functionality
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

class CostManager:
    def __init__(self, daily_budget: float = 5.0, monthly_budget: float = 100.0):
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.usage_file = "cost_usage.json"
        
        # Load existing usage data
        self.usage_data = self._load_usage_data()
        
    def _load_usage_data(self) -> Dict[str, Any]:
        """Load usage data from file."""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "daily": {},
            "monthly": {},
            "total_spent": 0.0
        }
    
    def _save_usage_data(self):
        """Save usage data to file."""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save usage data: {e}")
    
    def can_make_request(self, estimated_cost: float = 0.01) -> bool:
        """Check if we can make a request within budget."""
        today = datetime.now().strftime("%Y-%m-%d")
        this_month = datetime.now().strftime("%Y-%m")
        
        # Get current usage
        daily_spent = self.usage_data["daily"].get(today, 0.0)
        monthly_spent = self.usage_data["monthly"].get(this_month, 0.0)
        
        # Check budgets
        if daily_spent + estimated_cost > self.daily_budget:
            return False
        
        if monthly_spent + estimated_cost > self.monthly_budget:
            return False
        
        return True
    
    def record_usage(self, cost: float):
        """Record API usage cost."""
        today = datetime.now().strftime("%Y-%m-%d")
        this_month = datetime.now().strftime("%Y-%m")
        
        # Update daily usage
        if today not in self.usage_data["daily"]:
            self.usage_data["daily"][today] = 0.0
        self.usage_data["daily"][today] += cost
        
        # Update monthly usage
        if this_month not in self.usage_data["monthly"]:
            self.usage_data["monthly"][this_month] = 0.0
        self.usage_data["monthly"][this_month] += cost
        
        # Update total
        self.usage_data["total_spent"] += cost
        
        # Save data
        self._save_usage_data()
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get current usage summary."""
        today = datetime.now().strftime("%Y-%m-%d")
        this_month = datetime.now().strftime("%Y-%m")
        
        daily_spent = self.usage_data["daily"].get(today, 0.0)
        monthly_spent = self.usage_data["monthly"].get(this_month, 0.0)
        
        return {
            "today": {
                "spent": daily_spent,
                "budget": self.daily_budget,
                "remaining": self.daily_budget - daily_spent,
                "percentage": (daily_spent / self.daily_budget) * 100
            },
            "this_month": {
                "spent": monthly_spent,
                "budget": self.monthly_budget,
                "remaining": self.monthly_budget - monthly_spent,
                "percentage": (monthly_spent / self.monthly_budget) * 100
            },
            "total_spent": self.usage_data["total_spent"],
            "recommendations": self._get_recommendations(daily_spent, monthly_spent)
        }
    
    def _get_recommendations(self, daily_spent: float, monthly_spent: float) -> list:
        """Get cost-saving recommendations."""
        recommendations = []
        
        if daily_spent > self.daily_budget * 0.8:
            recommendations.append("Daily budget nearly reached - consider reducing API calls")
        
        if monthly_spent > self.monthly_budget * 0.8:
            recommendations.append("Monthly budget nearly reached - review usage patterns")
        
        if daily_spent > self.daily_budget * 0.5:
            recommendations.append("High daily usage - enable more aggressive caching")
        
        if not recommendations:
            recommendations.append("Usage is within healthy limits")
        
        return recommendations

# Global cost manager instance
cost_manager = CostManager() 