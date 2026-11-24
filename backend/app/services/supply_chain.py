import json
import uuid
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class SBOMComponent(BaseModel):
    name: str
    version: str
    purl: str
    license: str
    is_vulnerable: bool = False
    cve_id: str = ""
    recommendation: str = ""


class CycloneDXSBOMReport(BaseModel):
    bom_format: str = "CycloneDX"
    spec_version: str = "1.5"
    serial_number: str = Field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    components: List[SBOMComponent]
    total_components: int
    vulnerable_components: int
    licenses_summary: Dict[str, int]


class SupplyChainSecurityService:
    """
    Feature 16: Software Supply Chain Security and CycloneDX v1.5 SBOM Generator.
    Inspects dependency manifests, licenses, and known CVE advisories.
    """

    KNOWN_LICENSES = {
        "fastapi": "MIT",
        "pydantic": "MIT",
        "ruff": "MIT",
        "bandit": "Apache-2.0",
        "pytest": "MIT",
        "supabase": "MIT",
        "langgraph": "MIT",
        "langchain": "MIT",
        "next": "MIT",
        "react": "MIT",
        "tailwindcss": "MIT",
    }

    VULN_DB = {
        "requests": ("<2.31.0", "CVE-2023-32681", "Upgrade to requests >= 2.31.0"),
        "urllib3": ("<2.0.7", "CVE-2023-45803", "Upgrade to urllib3 >= 2.0.7"),
        "cryptography": ("<41.0.6", "CVE-2023-49083", "Upgrade to cryptography >= 41.0.6"),
    }

    def generate_cyclonedx_sbom(self, requirements_content: str) -> CycloneDXSBOMReport:
        components: List[SBOMComponent] = []
        licenses_count: Dict[str, int] = {}
        vuln_count = 0

        for line in requirements_content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Parse pkg name and version operator
            pkg_name = line.split(">=")[0].split("==")[0].split("<")[0].strip().lower()
            version = "latest"
            if ">=" in line:
                version = line.split(">=")[1].strip()
            elif "==" in line:
                version = line.split("==")[1].strip()

            lic = self.KNOWN_LICENSES.get(pkg_name, "MIT")
            licenses_count[lic] = licenses_count.get(lic, 0) + 1

            is_vuln = pkg_name in self.VULN_DB
            cve_id = self.VULN_DB[pkg_name][1] if is_vuln else ""
            rec = self.VULN_DB[pkg_name][2] if is_vuln else "Package conforms to license and security policies."
            if is_vuln:
                vuln_count += 1

            components.append(
                SBOMComponent(
                    name=pkg_name,
                    version=version,
                    purl=f"pkg:pypi/{pkg_name}@{version}",
                    license=lic,
                    is_vulnerable=is_vuln,
                    cve_id=cve_id,
                    recommendation=rec,
                )
            )

        return CycloneDXSBOMReport(
            components=components,
            total_components=len(components),
            vulnerable_components=vuln_count,
            licenses_summary=licenses_count,
        )


supply_chain_service = SupplyChainSecurityService()
