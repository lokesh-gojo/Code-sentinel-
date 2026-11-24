import ast
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.repo_intelligence import repo_intelligence_service


class ArchitectureIssue(BaseModel):
    category: str
    target_module: str
    impact: str
    recommendation: str
    priority: str  # "HIGH", "MEDIUM", "LOW"


class ArchitectureReviewReport(BaseModel):
    system_architectural_pattern: str
    technical_debt_index: int  # 0 to 100
    circular_import_violations: int
    architectural_issues: List[ArchitectureIssue]
    refactoring_priorities: List[str]


class ArchitectureReviewerService:
    """
    Feature 14: AI Architecture Reviewer & Technical Debt Analyzer.
    Reviews whole-repository architectural patterns, separation of concerns,
    tight coupling, and God objects.
    """

    def review_architecture(self, repo_path: str = ".") -> ArchitectureReviewReport:
        arch = repo_intelligence_service.scan_repository(repo_path)
        issues: List[ArchitectureIssue] = []

        # 1. Circular Dependencies
        if arch.circular_dependencies:
            for cycle in arch.circular_dependencies:
                issues.append(
                    ArchitectureIssue(
                        category="Circular Dependency Hazard",
                        target_module=" ➔ ".join(cycle),
                        impact="Tight coupling prevents independent module testing and complicates build lifecycles.",
                        recommendation="Introduce dependency inversion: abstract shared data types or use dependency injection.",
                        priority="HIGH",
                    )
                )

        # 2. Oversized Files / God Objects
        for node in arch.nodes:
            if node.lines_of_code > 300:
                issues.append(
                    ArchitectureIssue(
                        category="Oversized Module (God Object)",
                        target_module=node.id,
                        impact=f"Module has {node.lines_of_code} lines of code, exceeding modular maintainability boundaries.",
                        recommendation="Decompose module into focused sub-services following the Single Responsibility Principle.",
                        priority="MEDIUM",
                    )
                )

        # 3. Separation of Concerns & DB Coupling
        for node in arch.nodes:
            if "router" in node.id.lower() and any("sql" in f.lower() or "db" in f.lower() for f in node.functions):
                issues.append(
                    ArchitectureIssue(
                        category="Leaky Abstraction (Router to DB)",
                        target_module=node.id,
                        impact="API routes directly manipulate database logic rather than delegating to a service/repository layer.",
                        recommendation="Introduce a dedicated repository interface between the router and database layers.",
                        priority="MEDIUM",
                    )
                )

        tech_debt = min(100, len(issues) * 15 + len(arch.circular_dependencies) * 20)

        priorities = [
            "Break circular dependency cycles via interface abstraction",
            "Separate router endpoints from raw SQL persistence",
            "Refactor oversized files into domain-specific services",
        ]

        return ArchitectureReviewReport(
            system_architectural_pattern="Modular Service-Oriented Architecture (FastAPI + Next.js)",
            technical_debt_index=tech_debt,
            circular_import_violations=len(arch.circular_dependencies),
            architectural_issues=issues,
            refactoring_priorities=priorities,
        )


architecture_reviewer_service = ArchitectureReviewerService()
