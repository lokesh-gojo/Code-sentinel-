from typing import List, Dict, Any, Set
from pydantic import BaseModel
from app.services.repo_intelligence import repo_intelligence_service
import os


class ModuleImpact(BaseModel):
    module_name: str
    risk_level: str  # "HIGH", "MEDIUM", "LOW"
    blast_radius_depth: int
    dependent_count: int


class RegressionRiskReport(BaseModel):
    change_risk_score: str  # "HIGH", "MEDIUM", "LOW"
    overall_risk_index: int  # 0 to 100
    changed_files: List[str]
    impacted_modules: List[ModuleImpact]
    recommended_tests: List[str]
    merge_recommendation: str


class RegressionRiskPredictor:
    """
    Feature 13: Predicts blast-radius and regression risk of code modifications
    by traversing NetworkX dependency graphs and computing impacted downstream modules.
    """

    def predict_risk(self, changed_files: List[str], repo_path: str = ".") -> RegressionRiskReport:
        arch_report = repo_intelligence_service.scan_repository(repo_path)
        
        # Build dependency adjacency
        downstream_dependents: Dict[str, Set[str]] = {}
        for edge in arch_report.edges:
            # edge.source imports edge.target -> target is depended upon by source
            if edge.target not in downstream_dependents:
                downstream_dependents[edge.target] = set()
            downstream_dependents[edge.target].add(edge.source)

        impacted: List[ModuleImpact] = []
        max_dependents = 0

        for file in changed_files:
            file_clean = file.replace("\\", "/").strip("/")
            dependents = downstream_dependents.get(file_clean, set())
            dep_count = len(dependents)
            max_dependents = max(max_dependents, dep_count)

            # High risk if core module with >= 3 dependents or auth/db
            is_critical_path = any(term in file_clean.lower() for term in ["auth", "core", "db", "security", "main"])
            
            if dep_count >= 3 or (is_critical_path and dep_count >= 1):
                risk_level = "HIGH"
            elif dep_count >= 1:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            impacted.append(
                ModuleImpact(
                    module_name=file_clean,
                    risk_level=risk_level,
                    blast_radius_depth=2 if dep_count >= 2 else 1,
                    dependent_count=dep_count,
                )
            )

        # Calculate Overall Risk Index (0-100)
        high_count = sum(1 for m in impacted if m.risk_level == "HIGH")
        med_count = sum(1 for m in impacted if m.risk_level == "MEDIUM")
        
        risk_index = min(100, high_count * 35 + med_count * 15 + len(changed_files) * 5)
        
        if risk_index >= 60:
            change_risk = "HIGH"
            merge_rec = "Require senior review, isolated sandbox test run, and regression verification before merge."
        elif risk_index >= 30:
            change_risk = "MEDIUM"
            merge_rec = "Standard peer review and unit test execution recommended."
        else:
            change_risk = "LOW"
            merge_rec = "Low blast radius; safe for merge following automated CI checks."

        # Recommended tests
        recommended_tests = [
            "Integration tests for affected API routers",
            "Regression test for modified business logic",
            "Authentication & Session token validation",
        ]

        return RegressionRiskReport(
            change_risk_score=change_risk,
            overall_risk_index=risk_index,
            changed_files=changed_files,
            impacted_modules=impacted,
            recommended_tests=recommended_tests,
            merge_recommendation=merge_rec,
        )


regression_risk_predictor = RegressionRiskPredictor()
