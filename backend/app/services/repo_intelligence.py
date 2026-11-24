import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import networkx as nx
from pydantic import BaseModel, Field


class DependencyNode(BaseModel):
    id: str
    label: str
    type: str  # "file", "module", "service", "route"
    language: str
    lines_of_code: int = 0
    functions: List[str] = []
    classes: List[str] = []


class DependencyEdge(BaseModel):
    source: str
    target: str
    relation: str  # "imports", "calls"


class RepositoryArchitectureReport(BaseModel):
    total_files: int
    languages_detected: Dict[str, int]
    frameworks_detected: List[str]
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]
    circular_dependencies: List[List[str]]
    unused_functions: List[str]
    duplicated_blocks_count: int
    architecture_summary: str


class RepositoryIntelligenceEngine:
    """
    Parses whole repository structures, discovers dependencies using NetworkX,
    detects circular imports, unused functions, and architecture layout.
    """

    EXCLUDED_DIRS = {
        ".git", "node_modules", ".venv", "venv", "__pycache__",
        ".next", "dist", "build", ".pytest_cache"
    }

    def scan_repository(self, root_path: str) -> RepositoryArchitectureReport:
        root = Path(root_path)
        if not root.exists() or not root.is_dir():
            return self._empty_report()

        graph = nx.DiGraph()
        nodes_dict: Dict[str, DependencyNode] = {}
        defined_functions: Dict[str, str] = {}  # func_name -> file_rel_path
        called_functions: Set[str] = set()
        language_counts: Dict[str, int] = {}
        all_code_blocks: Dict[str, int] = {}
        frameworks: Set[str] = set()

        # Step 1: Collect all source files
        for current_root, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]
            for file in files:
                file_path = Path(current_root) / file
                rel_path = file_path.relative_to(root).as_posix()
                ext = file_path.suffix.lower()

                lang = "unknown"
                if ext == ".py":
                    lang = "python"
                elif ext in (".js", ".jsx"):
                    lang = "javascript"
                elif ext in (".ts", ".tsx"):
                    lang = "typescript"
                elif ext in (".sql", ".json", ".md"):
                    continue
                else:
                    continue

                language_counts[lang] = language_counts.get(lang, 0) + 1

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                lines_count = len(content.splitlines())
                functions: List[str] = []
                classes: List[str] = []
                imports: List[str] = []

                # Framework detection
                if "fastapi" in content.lower():
                    frameworks.add("FastAPI")
                if "next" in content.lower() or "react" in content.lower():
                    frameworks.add("Next.js / React")
                if "supabase" in content.lower() or "postgres" in content.lower():
                    frameworks.add("Supabase PostgreSQL")
                if "langgraph" in content.lower():
                    frameworks.add("LangGraph Multi-Agent")
                if "tailwind" in content.lower():
                    frameworks.add("Tailwind CSS")

                # Parse Python AST
                if lang == "python":
                    try:
                        tree = ast.parse(content, filename=rel_path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                functions.append(node.name)
                                defined_functions[node.name] = rel_path
                            elif isinstance(node, ast.ClassDef):
                                classes.append(node.name)
                            elif isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports.append(alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    imports.append(node.module)
                            elif isinstance(node, ast.Call):
                                if isinstance(node.func, ast.Name):
                                    called_functions.add(node.func.id)
                    except Exception:
                        pass
                else:
                    # Regex-based extraction for JS/TS
                    found_fns = re.findall(r"(?:function\s+([a-zA-Z0-9_]+)|const\s+([a-zA-Z0-9_]+)\s*=\s*(?:\([^)]*\)|async\s*\([^)]*\))\s*=>)", content)
                    for fn_tuple in found_fns:
                        fn = fn_tuple[0] or fn_tuple[1]
                        if fn:
                            functions.append(fn)
                            defined_functions[fn] = rel_path
                    # Imports
                    import_matches = re.findall(r"from\s+['\"]([^'\"]+)['\"]", content)
                    imports.extend(import_matches)

                # Store Node
                dep_node = DependencyNode(
                    id=rel_path,
                    label=Path(rel_path).name,
                    type="route" if "router" in rel_path or "app/" in rel_path else "service" if "service" in rel_path else "file",
                    language=lang,
                    lines_of_code=lines_count,
                    functions=functions,
                    classes=classes,
                )
                nodes_dict[rel_path] = dep_node
                graph.add_node(rel_path)

                # Store Edges for local imports
                for imp in imports:
                    normalized_imp = imp.replace(".", "/").strip("/")
                    for candidate_rel in nodes_dict.keys():
                        if normalized_imp in candidate_rel:
                            graph.add_edge(rel_path, candidate_rel)

        # Step 2: Compute Circular Dependencies
        circular: List[List[str]] = []
        try:
            for cycle in nx.simple_cycles(graph):
                if len(cycle) > 1:
                    circular.append(cycle)
        except Exception:
            pass

        # Step 3: Compute Unused Functions
        unused_fns = [
            f"{fn} ({file})"
            for fn, file in defined_functions.items()
            if fn not in called_functions
            and not fn.startswith(("_", "test_", "handle", "get_", "scan_", "main"))
        ]

        # Step 4: Construct edges list
        edges_list: List[DependencyEdge] = [
            DependencyEdge(source=u, target=v, relation="imports")
            for u, v in graph.edges()
        ]

        summary_text = (
            f"Repository contains {len(nodes_dict)} tracked source files across {len(language_counts)} languages. "
            f"Detected frameworks: {', '.join(sorted(frameworks)) if frameworks else 'Standard Multi-tier'}. "
            f"Discovered {len(circular)} circular import cycles and {len(unused_fns)} potentially unreferenced functions."
        )

        return RepositoryArchitectureReport(
            total_files=len(nodes_dict),
            languages_detected=language_counts,
            frameworks_detected=list(frameworks),
            nodes=list(nodes_dict.values()),
            edges=edges_list,
            circular_dependencies=circular[:5],
            unused_functions=unused_fns[:10],
            duplicated_blocks_count=0,
            architecture_summary=summary_text,
        )

    def _empty_report(self) -> RepositoryArchitectureReport:
        return RepositoryArchitectureReport(
            total_files=0,
            languages_detected={},
            frameworks_detected=[],
            nodes=[],
            edges=[],
            circular_dependencies=[],
            unused_functions=[],
            duplicated_blocks_count=0,
            architecture_summary="Empty or non-existent repository path provided.",
        )


repo_intelligence_service = RepositoryIntelligenceEngine()
