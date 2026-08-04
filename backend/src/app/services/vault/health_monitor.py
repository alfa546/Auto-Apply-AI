"""
Key Health Monitor - Tracks health status of API keys and triggers alerts
"""
import time
import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from src.app.services.vault.key_manager import APIKeyInfo

logger = logging.getLogger(__name__)


class KeyHealthMonitor:
    """
    Monitors health of API keys and provides health status reports.
    """
    
    def __init__(self):
        self._alert_handlers = []
        self._health_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_alert_handler(self, handler):
        """Register a callback for health alerts"""
        self._alert_handlers.append(handler)
    
    def check_key_health(self, key_info: APIKeyInfo) -> Dict[str, Any]:
        """
        Perform health check on a single API key.
        
        Args:
            key_info: API key to check
            
        Returns:
            Health status dictionary
        """
        health = {
            "key_id": key_info.key_id,
            "service": key_info.service,
            "status": "healthy",
            "checks": {},
            "issues": [],
            "recommendations": []
        }
        
        # Check 1: Is key active?
        if not key_info.is_active:
            health["checks"]["is_active"] = "fail"
            health["status"] = "inactive"
            health["issues"].append("Key is inactive")
            return health
        else:
            health["checks"]["is_active"] = "pass"
        
        # Check 2: Is key available?
        is_available = key_info.is_available()
        health["checks"]["is_available"] = "pass" if is_available else "fail"
        if not is_available:
            health["status"] = "unavailable"
            health["issues"].append("Key is currently unavailable")
        
        # Check 3: Error rate
        total_uses = key_info.daily_usage + key_info.monthly_usage
        if total_uses > 10:
            error_rate = key_info.error_count / total_uses
            health["checks"]["error_rate"] = "pass" if error_rate < 0.1 else "fail"
            if error_rate >= 0.3:
                health["issues"].append(f"High error rate: {error_rate:.1%}")
                health["recommendations"].append("Consider rotating this key")
        
        # Check 4: Usage limits
        if key_info.daily_limit and key_info.daily_usage >= key_info.daily_limit * 0.9:
            health["checks"]["daily_limit"] = "warning"
            health["issues"].append(f"Approaching daily limit: {key_info.daily_usage}/{key_info.daily_limit}")
            health["recommendations"].append("Prepare to switch to next available key")
        else:
            health["checks"]["daily_limit"] = "pass"
        
        if key_info.monthly_limit and key_info.monthly_usage >= key_info.monthly_limit * 0.9:
            health["checks"]["monthly_limit"] = "warning"
            health["issues"].append(f"Approaching monthly limit: {key_info.monthly_usage}/{key_info.monthly_limit}")
        else:
            health["checks"]["monthly_limit"] = "pass"
        
        # Check 5: Cooldown status
        if key_info.cooldown_until:
            health["checks"]["cooldown"] = "warning"
            remaining = (key_info.cooldown_until - datetime.utcnow()).total_seconds() / 60
            health["issues"].append(f"Key in cooldown for {remaining:.0f} more minutes")
        else:
            health["checks"]["cooldown"] = "pass"
        
        # Overall status
        if health["status"] == "healthy" and health["issues"]:
            health["status"] = "warning"
        
        # Store in history
        self._record_health_check(key_info.service, key_info.key_id, health)
        
        return health
    
    def _record_health_check(self, service: str, key_id: str, health: Dict[str, Any]):
        """Record health check in history"""
        key = f"{service}:{key_id}"
        if key not in self._health_history:
            self._health_history[key] = []
        
        self._health_history[key].append({
            "timestamp": datetime.utcnow().isoformat(),
            "status": health["status"],
            "issues": health["issues"]
        })
        
        # Keep only last 100 checks
        self._health_history[key] = self._health_history[key][-100:]
    
    def get_service_health(self, key_manager) -> Dict[str, Any]:
        """
        Get overall health status for a service.
        
        Args:
            key_manager: KeyManager instance with registered keys
            
        Returns:
            Service health report
        """
        all_keys = []
        for service, keys in key_manager._key_registry.items():
            for key in keys:
                health = self.check_key_health(key)
                all_keys.append(health)
        
        # Calculate summary
        total_keys = len(all_keys)
        healthy_keys = sum(1 for k in all_keys if k["status"] == "healthy")
        warning_keys = sum(1 for k in all_keys if k["status"] == "warning")
        unhealthy_keys = sum(1 for k in all_keys if k["status"] in ["unavailable", "inactive"])
        
        return {
            "total_keys": total_keys,
            "healthy": healthy_keys,
            "warning": warning_keys,
            "unhealthy": unhealthy_keys,
            "health_percentage": (healthy_keys / total_keys * 100) if total_keys > 0 else 0,
            "keys": all_keys,
            "recommendations": self._generate_recommendations(all_keys)
        }
    
    def _generate_recommendations(self, health_checks: List[Dict[str, Any]]) -> List[str]:
        """Generate system-wide recommendations"""
        recommendations = []
        
        unhealthy = [k for k in health_checks if k["status"] in ["unavailable", "inactive"]]
        warning = [k for k in health_checks if k["status"] == "warning"]
        
        if len(unhealthy) > 0:
            recommendations.append(f"⚠️ {len(unhealthy)} keys are unavailable. Consider adding more keys or fixing issues.")
        
        if len(warning) > 0:
            recommendations.append(f"⚡ {len(warning)} keys need attention. Review usage limits and errors.")
        
        # Check if any service has no available keys
        services_with_issues = {}
        for check in health_checks:
            svc = check["service"]
            if svc not in services_with_issues:
                services_with_issues[svc] = {"total": 0, "available": 0}
            services_with_issues[svc]["total"] += 1
            if check["status"] == "healthy":
                services_with_issues[svc]["available"] += 1
        
        for svc, stats in services_with_issues.items():
            if stats["available"] == 0:
                recommendations.append(f"🔴 CRITICAL: Service '{svc}' has no available keys!")
        
        return recommendations
    
    def get_health_history(self, service: Optional[str] = None, key_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get health check history.
        
        Args:
            service: Optional service filter
            key_id: Optional key ID filter
            
        Returns:
            Health history
        """
        if service and key_id:
            key = f"{service}:{key_id}"
            return {key: self._health_history.get(key, [])}
        
        if service:
            return {
                k: v for k, v in self._health_history.items()
                if k.startswith(f"{service}:")
            }
        
        return dict(self._health_history)
    
    def simulate_health_check(self, key_info: APIKeyInfo) -> Dict[str, Any]:
        """
        Simulate a health check for testing purposes.
        
        Args:
            key_info: API key to simulate check for
            
        Returns:
            Simulated health status
        """
        # Simulate random health status
        rand = random.random()
        
        if not key_info.is_active:
            status = "inactive"
        elif rand < 0.7:
            status = "healthy"
        elif rand < 0.9:
            status = "warning"
        else:
            status = "unavailable"
        
        return {
            "key_id": key_info.key_id,
            "service": key_info.service,
            "status": status,
            "simulated": True
        }


# Global health monitor instance
key_health_monitor = KeyHealthMonitor()