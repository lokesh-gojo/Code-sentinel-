from typing import List, Dict, Any
from pydantic import BaseModel
from app.models.schemas import Finding


class QualityScoreReport(BaseModel):
    overall: int
    code_quality: int
    security: int
    performance: int
    test_coverage: int
    maintainability: int
    assessment: str


class QualityScorerService:
    """
    Transparent, configurable 0–100 quality score calculation engine.
    Calibrated deterministically from findings and code structure.
    """

    def calculate_score(
        self,
        findings: List[Finding],
        total_lines: int = 100,
        has_tests: bool = True
    ) -> QualityScoreReport:
        # Base scores
        code_quality = 100
        security = 100
        performance = 100
        test_coverage = 88 if has_tests else 35
        maintainability = 92

        # Deductions
        for f in findings:
            if f.category in ("Security Vulnerability", "Vulnerable Dependency"):
                if f.severity == "high":
                    security -= 25
                elif f.severity == "medium":
                    security -= 12
                else:
                    security -= 5
            elif f.category in ("Potential Runtime Bug", "Syntax Bug"):
                if f.severity == "high":
                    code_quality -= 20
                else:
                    code_quality -= 10
            elif f.category in ("Performance Bottleneck",):
                performance -= 18
            else:
                code_quality -= 4
                maintainability -= 3

        # Clamp scores between 10 and 100
        code_quality = max(10, min(100, code_quality))
        security = max(10, min(100, security))
        performance = max(10, min(100, performance))
        maintainability = max(10, min(100, maintainability))

        # Weighted Overall Score
        overall = int(
            code_quality * 0.25 +
            security * 0.35 +
            performance * 0.15 +
            test_coverage * 0.15 +
            maintainability * 0.10
        )

        assessment = "Excellent" if overall >= 85 else "Good" if overall >= 70 else "Action Required" if overall >= 50 else "Critical Defect Risk"

        return QualityScoreReport(
            overall=overall,
            code_quality=code_quality,
            security=security,
            performance=performance,
            test_coverage=test_coverage,
            maintainability=maintainability,
            assessment=assessment,
        )


quality_scorer_service = QualityScorerService()
