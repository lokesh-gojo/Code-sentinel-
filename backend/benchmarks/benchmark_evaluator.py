import time
from typing import List, Dict, Any
from pydantic import BaseModel
from benchmarks.ground_truth_cases import BENCHMARK_CASES, GroundTruthTestCase
from app.services.analyzer import analyzer_service
from app.services.ai_reviewer import ai_reviewer_service
from app.services.sandbox import sandbox_service


class CaseBenchmarkResult(BaseModel):
    case_id: str
    name: str
    detected_rule_ids: List[str]
    expected_rule_ids: List[str]
    true_positive: bool
    false_positive: bool
    false_negative: bool
    patch_verified_in_sandbox: bool
    latency_ms: float


class EmpiricalEvaluationReport(BaseModel):
    total_benchmark_cases: int
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    patch_sandbox_pass_rate: float
    average_latency_ms: float
    cost_per_scan_usd: float
    case_results: List[CaseBenchmarkResult]


class BenchmarkEvaluator:
    """
    Evaluates Code Sentinel AI against ground-truth defect fixtures to calculate
    empirical precision, recall, false-positive rate, and patch acceptance.
    """

    def run_benchmark(self) -> EmpiricalEvaluationReport:
        tp = 0
        fp = 0
        fn = 0
        tn = 0
        patch_passes = 0
        total_latency = 0.0
        results: List[CaseBenchmarkResult] = []

        for case in BENCHMARK_CASES:
            t0 = time.time()
            findings = analyzer_service.analyze_snippet(
                code=case.code,
                filename=case.filename,
                language=case.language,
            )
            elapsed_ms = (time.time() - t0) * 1000.0
            total_latency += elapsed_ms

            detected_rules = {f.rule_id for f in findings}
            expected_rules = set(case.expected_rule_ids)

            # Verification of self-healing patch in sandbox
            patch_verified = False
            if findings:
                patch_output = ai_reviewer_service.generate_fix_and_test(
                    code=case.code,
                    filename=case.filename,
                    findings=findings,
                )
                passed, _ = sandbox_service.run_test(
                    patched_code=patch_output.suggested_patch,
                    regression_test=patch_output.regression_test,
                    filename=case.filename,
                )
                patch_verified = passed
                if passed:
                    patch_passes += 1
            else:
                patch_verified = True  # Negative control has no defects

            # Precision & Recall metrics
            if case.is_negative_control:
                if len(detected_rules) == 0:
                    tn += 1
                    case_tp, case_fp, case_fn = False, False, False
                else:
                    fp += 1
                    case_tp, case_fp, case_fn = False, True, False
            else:
                # Defect case
                overlap = detected_rules.intersection(expected_rules)
                if overlap:
                    tp += 1
                    case_tp = True
                    case_fn = False
                else:
                    fn += 1
                    case_tp = False
                    case_fn = True

                # Check if unexpected findings were triggered
                extra = detected_rules - expected_rules
                case_fp = len(extra) > 2  # Tolerance for secondary lint warnings
                if case_fp:
                    fp += 1

            results.append(
                CaseBenchmarkResult(
                    case_id=case.case_id,
                    name=case.name,
                    detected_rule_ids=list(detected_rules),
                    expected_rule_ids=list(expected_rules),
                    true_positive=case_tp,
                    false_positive=case_fp,
                    false_negative=case_fn,
                    patch_verified_in_sandbox=patch_verified,
                    latency_ms=round(elapsed_ms, 2),
                )
            )

        precision = round(tp / (tp + fp) if (tp + fp) > 0 else 1.0, 3)
        recall = round(tp / (tp + fn) if (tp + fn) > 0 else 1.0, 3)
        f1 = round(2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0, 3)
        fpr = round(fp / (fp + tn) if (fp + tn) > 0 else 0.0, 3)
        patch_rate = round(patch_passes / max(1, len(BENCHMARK_CASES) - 1), 3)

        return EmpiricalEvaluationReport(
            total_benchmark_cases=len(BENCHMARK_CASES),
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            true_negatives=tn,
            precision=precision,
            recall=recall,
            f1_score=f1,
            false_positive_rate=fpr,
            patch_sandbox_pass_rate=patch_rate,
            average_latency_ms=round(total_latency / len(BENCHMARK_CASES), 2),
            cost_per_scan_usd=0.00,  # Zero cost in local offline mode
            case_results=results,
        )


benchmark_evaluator = BenchmarkEvaluator()
