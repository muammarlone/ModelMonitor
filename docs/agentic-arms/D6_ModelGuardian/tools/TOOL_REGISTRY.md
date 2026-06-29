# TOOL_REGISTRY.md
## Persona D6 — The Model Guardian | Complete Tool Registry

**Version:** 1.0.0  
**Status:** Production-ready  
**Date:** 2026-06-28  
**Owner:** D6 The Model Guardian  
**Parent:** `AGENTIC_ARMS_OVERVIEW.md`

---

## 1. Tool Registry Overview

All tools for D6 arms are registered in this document. Each tool has a unique ID, owner arm, execution mode, and full input/output contract.

---

## 2. Tool Definitions

### T-01: drift_calculator

| Field | Value |
|-------|-------|
| **Tool ID** | `T-01` |
| **Name** | `drift_calculator` |
| **Description** | Core statistical engine for computing drift metrics (PSI, KS, Wasserstein, Chi-Square) between reference and current distributions |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-01` (Drift Detector) |
| **Input** | `DriftCalcRequest`: `{reference_data: DataFrame, current_data: DataFrame, features: array[string], test_suite: array[enum]}` |
| **Output** | `DriftCalcResponse`: `{psi: float, ks_statistic: float, ks_p_value: float, wasserstein: float, chi2: float, chi2_p_value: float, per_feature: object}` |
| **Execution Mode** | Python/CPU, batch processing, up to 4GB memory |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 300s default, 600s max |
| **Error Handling** | `on_error: return nulls with status "error"` + `log_to_p2` + `alert_d5` |
| **Example** | `POST /v1/tools/drift_calculator` with `{reference_data_uri: "s3://baseline.csv", current_data_uri: "s3://current.csv", features: ["credit_score", "income"]}` |

### T-02: statistical_tester

| Field | Value |
|-------|-------|
| **Tool ID** | `T-02` |
| **Name** | `statistical_tester` |
| **Description** | Orchestrates statistical test selection and execution, choosing appropriate tests based on data type (continuous vs categorical), sample size, and distribution |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-01` (Drift Detector) |
| **Input** | `StatTestRequest`: `{data_type: enum[continuous, categorical], samples: int, distribution: string, test_candidates: array[enum], alpha: float}` |
| **Output** | `StatTestResponse`: `{selected_test: string, test_result: object, p_value: float, significance: bool, recommendation: string}` |
| **Execution Mode** | Python/CPU, lightweight (< 100MB memory) |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 60s default, 120s max |
| **Error Handling** | `on_error: fallback to chi-square for categorical, ks for continuous` |
| **Example** | `POST /v1/tools/statistical_tester` with `{data_type: "continuous", samples: 12000, test_candidates: ["ks", "wasserstein"], alpha: 0.05}` |

### T-03: bias_metric_computer

| Field | Value |
|-------|-------|
| **Tool ID** | `T-03` |
| **Name** | `bias_metric_computer` |
| **Description** | Computes fairness metrics (demographic parity, equalized odds, equal opportunity, calibration, disparate impact ratio) with bootstrap confidence intervals |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-02` (Bias Auditor) |
| **Input** | `BiasMetricRequest`: `{predictions: array, ground_truth: array, protected_attribute: array, groups: array, metric_suite: array[enum], confidence_level: float, bootstrap_iterations: int}` |
| **Output** | `BiasMetricResponse`: `{metrics: object, confidence_intervals: object, per_group: object, overall_status: enum[pass, marginal, fail]}` |
| **Execution Mode** | Python/CPU, memory scales with group count |
| **Auth** | JWT RS256, role `d6-audit` |
| **Timeout** | 600s default, 1800s max |
| **Error Handling** | `on_error: return single-metric result with error flag` + `alert_g1` |
| **Example** | `POST /v1/tools/bias_metric_computer` with `{predictions: [0,1,1...], ground_truth: [0,1,0...], protected_attribute: ["M","F","M"...], groups: ["M","F"], metric_suite: ["demographic_parity","equalized_odds"]}` |

### T-04: fairness_auditor

| Field | Value |
|-------|-------|
| **Tool ID** | `T-04` |
| **Name** | `fairness_auditor` |
| **Description** | Maps computed fairness metrics to regulatory compliance frameworks (EU AI Act, NYC 144, EEOC, Fair Lending) and generates compliance verdicts |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-02` (Bias Auditor) |
| **Input** | `FairnessAuditRequest`: `{metric_results: object, frameworks: array[enum], model_type: enum[high_risk, limited_risk, minimal_risk]}` |
| **Output** | `FairnessAuditResponse`: `{compliance_mapping: object, verdicts: object, gaps: array, recommendations: array}` |
| **Execution Mode** | Python/CPU, rules engine (< 50MB memory) |
| **Auth** | JWT RS256, role `d6-audit` |
| **Timeout** | 30s default, 60s max |
| **Error Handling** | `on_error: return "compliance status unknown"` + `alert_g1` |
| **Example** | `POST /v1/tools/fairness_auditor` with `{metric_results: {demographic_parity_diff: 0.14}, frameworks: ["EU_AI_ACT", "NYC_144"], model_type: "high_risk"}` |

### T-05: performance_tracker

| Field | Value |
|-------|-------|
| **Tool ID** | `T-05` |
| **Name** | `performance_tracker` |
| **Description** | Computes model performance metrics (accuracy, precision, recall, F1, AUC, log-loss, calibration) from prediction and ground truth streams |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-03` (Performance Monitor) |
| **Input** | `PerformanceTrackRequest`: `{predictions: array, ground_truth: array, prediction_type: enum[binary, multiclass, regression], metric_suite: array[enum], window: string}` |
| **Output** | `PerformanceTrackResponse`: `{metrics: object, health_score: float, status: enum[healthy, degraded, critical], trend: enum[improving, stable, declining]}` |
| **Execution Mode** | Python/CPU, streaming capable |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 60s default, 120s max |
| **Error Handling** | `on_error: return cached metrics from last window` |
| **Example** | `POST /v1/tools/performance_tracker` with `{predictions: [...], ground_truth: [...], prediction_type: "binary", metric_suite: ["accuracy","precision","recall","f1","auc"]}` |

### T-06: sla_monitor

| Field | Value |
|-------|-------|
| **Tool ID** | `T-06` |
| **Name** | `sla_monitor` |
| **Description** | Tracks SLA compliance for model serving infrastructure (latency, availability, error rate, throughput) against defined targets |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-03` (Performance Monitor) |
| **Input** | `SLAMonitorRequest`: `{model_id: UUID, sla_targets: object, metrics_window: enum[1h, 24h, 7d], datasource: string}` |
| **Output** | `SLAMonitorResponse`: `{sla_compliance: object, breach_count: int, breach_details: array, status: enum[pass, marginal, fail]}` |
| **Execution Mode** | FastAPI/DB, query TimescaleDB/Prometheus |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 15s default, 30s max |
| **Error Handling** | `on_error: return "sla data unavailable"` + `alert_d5` |
| **Example** | `GET /v1/tools/sla_monitor?model_id=uuid&window=24h` |

### T-07: shap_explainer

| Field | Value |
|-------|-------|
| **Tool ID** | `T-07` |
| **Name** | `shap_explainer` |
| **Description** | Computes SHAP (SHapley Additive exPlanations) values for model predictions using TreeSHAP, KernelSHAP, or DeepSHAP |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-04` (Explainability Analyzer), `ARM-02` (Bias Auditor — proxy detection) |
| **Input** | `SHAPRequest`: `{model_uri: string, data: DataFrame, background_data: DataFrame, explainer_type: enum[tree, kernel, deep], output_type: enum[waterfall, summary, beeswarm]}` |
| **Output** | `SHAPResponse`: `{shap_values: array, feature_importance: array, plots: array[string], base_value: float, computation_time_ms: int}` |
| **Execution Mode** | Python/CPU (GPU optional for DeepSHAP), up to 2GB memory |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 300s default, 600s max |
| **Error Handling** | `on_error: return feature_importance from surrogate model` |
| **Example** | `POST /v1/tools/shap_explainer` with `{model_uri: "s3://model.pkl", data: [...], explainer_type: "tree", output_type: "summary"}` |

### T-08: lime_explainer

| Field | Value |
|-------|-------|
| **Tool ID** | `T-08` |
| **Name** | `lime_explainer` |
| **Description** | Generates LIME (Local Interpretable Model-agnostic Explanations) for individual predictions, supporting tabular, text, and image data |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-04` (Explainability Analyzer) |
| **Input** | `LIMERequest`: `{model: object, instance: object, data_type: enum[tabular, text, image], num_features: int, num_samples: int}` |
| **Output** | `LIMEResponse`: `{explanation: object, feature_weights: array, local_model_score: float, plot_uri: string}` |
| **Execution Mode** | Python/CPU, lightweight |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 120s default, 300s max |
| **Error Handling** | `on_error: return empty explanation with error flag` |
| **Example** | `POST /v1/tools/lime_explainer` with `{model: "model_ref", instance: {credit_score: 580, income: 42000}, data_type: "tabular", num_features: 5}` |

### T-09: counterfactual_generator

| Field | Value |
|-------|-------|
| **Tool ID** | `T-09` |
| **Name** | `counterfactual_generator` |
| **Description** | Generates counterfactual explanations showing minimal changes required to flip a prediction, using DiCE or nearest-neighbor methods |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-04` (Explainability Analyzer) |
| **Input** | `CounterfactualRequest`: `{model: object, instance: object, desired_outcome: enum[0,1], method: enum[dice, nearest, genetic], constraints: object, max_changes: int}` |
| **Output** | `CounterfactualResponse`: `{counterfactuals: array, feasibility_scores: array, distances: array, feature_changes: array}` |
| **Execution Mode** | Python/CPU, up to 1GB memory |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 300s default, 600s max |
| **Error Handling** | `on_error: return empty counterfactuals with "not feasible" flag` |
| **Example** | `POST /v1/tools/counterfactual_generator` with `{model: "model_ref", instance: {...}, desired_outcome: 1, method: "dice", max_changes: 3}` |

### T-10: adversarial_tester

| Field | Value |
|-------|-------|
| **Tool ID** | `T-10` |
| **Name** | `adversarial_tester` |
| **Description** | Tests model robustness against adversarial attacks (FGSM, PGD, Carlini-Wagner, boundary) and generates vulnerability scores |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-05` (Adversarial Tester) |
| **Input** | `AdversarialTestRequest`: `{model_uri: string, test_data: DataFrame, attack_methods: array[enum], epsilon: float, max_iterations: int}` |
| **Output** | `AdversarialTestResponse`: `{robustness_score: float, per_attack: object, adversarial_examples: array, perturbation_analysis: object}` |
| **Execution Mode** | Python/CPU (GPU recommended for neural networks), up to 4GB memory |
| **Auth** | JWT RS256, role `d6-audit` |
| **Timeout** | 600s default, 1200s max |
| **Error Handling** | `on_error: return partial results with attack methods that succeeded` |
| **Example** | `POST /v1/tools/adversarial_tester` with `{model_uri: "s3://model.pkl", test_data: [...], attack_methods: ["fgsm", "pgd"], epsilon: 0.3}` |

### T-11: retrain_trigger

| Field | Value |
|-------|-------|
| **Tool ID** | `T-11` |
| **Name** | `retrain_trigger` |
| **Description** | Evaluates drift, performance, and bias signals to generate data-driven retrain recommendations with validation gates and cost estimates |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-06` (Retrain Recommender) |
| **Input** | `RetrainTriggerRequest`: `{model_id: UUID, drift_report: object, performance_report: object, bias_report: object, cost_constraints: object, business_priority: enum[low, medium, high]}` |
| **Output** | `RetrainTriggerResponse`: `{recommendation: enum[retrain, monitor, investigate], rationale: string, validation_gates: array, expected_improvements: object, cost_estimate: object, risk_score: float}` |
| **Execution Mode** | Python/CPU, rules engine + LLM rationale |
| **Auth** | JWT RS256, role `d6-admin` |
| **Timeout** | 60s default, 120s max |
| **Error Handling** | `on_error: return "manual review required"` + `alert_d3` |
| **Example** | `POST /v1/tools/retrain_trigger` with `{model_id: "uuid", drift_report: {psi: 0.34}, performance_report: {accuracy_drop: 0.07}, bias_report: {overall: "fail"}}` |

### T-12: model_lineage_tracker

| Field | Value |
|-------|-------|
| **Tool ID** | `T-12` |
| **Name** | `model_lineage_tracker` |
| **Description** | Tracks model lineage: training data, features, hyperparameters, metrics, artifacts, deployment history, and decision log for full traceability |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | All arms (cross-cutting) |
| **Input** | `LineageRequest`: `{model_id: UUID, version: string, query_type: enum[full, baseline, deployment, experiment]}` |
| **Output** | `LineageResponse`: `{model_id: UUID, lineage: object, experiments: array, deployments: array, artifacts: array, graph_uri: string}` |
| **Execution Mode** | FastAPI/DB (PostgreSQL JSONB + MLflow API) |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 15s default, 30s max |
| **Error Handling** | `on_error: return partial lineage with missing flags` |
| **Example** | `GET /v1/tools/model_lineage_tracker?model_id=uuid&version=2.3.1` |

### T-13: experiment_logger

| Field | Value |
|-------|-------|
| **Tool ID** | `T-13` |
| **Name** | `experiment_logger` |
| **Description** | Logs all D6 arm executions, metrics, and artifacts to MLflow with structured metadata for experiment tracking and reproducibility |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | All arms (cross-cutting) |
| **Input** | `ExperimentLogRequest`: `{run_id: UUID, arm_id: string, model_id: UUID, parameters: object, metrics: object, artifacts: array[string]}` |
| **Output** | `ExperimentLogResponse`: `{run_id: UUID, mlflow_uri: string, status: string, logged_metrics: array, logged_artifacts: array}` |
| **Execution Mode** | FastAPI/MLflow API |
| **Auth** | JWT RS256 + MLflow tracking token, role `d6-monitor` |
| **Timeout** | 30s default, 60s max |
| **Error Handling** | `on_error: log to local filesystem and retry async` |
| **Example** | `POST /v1/tools/experiment_logger` with `{run_id: "uuid", arm_id: "ARM-01", model_id: "uuid", metrics: {psi: 0.34}, artifacts: ["drift_report.json"]}` |

### T-14: version_comparator

| Field | Value |
|-------|-------|
| **Tool ID** | `T-14` |
| **Name** | `version_comparator` |
| **Description** | Compares model versions across metrics, features, hyperparameters, and performance to identify regression or improvement |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-03` (Performance Monitor), `ARM-06` (Retrain Recommender) |
| **Input** | `VersionCompareRequest`: `{model_id: UUID, baseline_version: string, current_version: string, comparison_dimensions: array[enum]}` |
| **Output** | `VersionCompareResponse`: `{comparison: object, regressions: array, improvements: array, unchanged: array, verdict: enum[better, worse, equivalent, mixed]}` |
| **Execution Mode** | FastAPI/DB (PostgreSQL + MLflow) |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 30s default, 60s max |
| **Error Handling** | `on_error: return "comparison incomplete"` |
| **Example** | `GET /v1/tools/version_comparator?model_id=uuid&baseline=2.3.0&current=2.3.1` |

### T-15: dataset_profiler

| Field | Value |
|-------|-------|
| **Tool ID** | `T-15` |
| **Name** | `dataset_profiler` |
| **Description** | Profiles datasets for quality, distribution, missing values, duplicates, and data leakage before drift or bias analysis |
| **Owner** | D6 The Model Guardian |
| **Arm Binding** | `ARM-01` (Drift Detector), `ARM-04` (Explainability Analyzer) |
| **Input** | `DatasetProfileRequest`: `{dataset_uri: string, dataset_type: enum[tabular, text, image], checks: array[enum]}` |
| **Output** | `DatasetProfileResponse`: `{quality_score: float, row_count: int, missing_pct: float, duplicate_pct: float, distribution_summary: object, warnings: array, recommendations: array}` |
| **Execution Mode** | Python/CPU, pandas-based |
| **Auth** | JWT RS256, role `d6-monitor` |
| **Timeout** | 120s default, 300s max |
| **Error Handling** | `on_error: return partial profile with available checks` |
| **Example** | `POST /v1/tools/dataset_profiler` with `{dataset_uri: "s3://data.csv", dataset_type: "tabular", checks: ["missing", "duplicates", "distribution", "leakage"]}` |

---

## 3. Tool-to-Arm Mapping Matrix

| Tool | ARM-01 | ARM-02 | ARM-03 | ARM-04 | ARM-05 | ARM-06 | Execution |
|------|--------|--------|--------|--------|--------|--------|-----------|
| T-01 drift_calculator | ✅ Core | ❌ | ❌ | ❌ | ❌ | ❌ | Python/CPU |
| T-02 statistical_tester | ✅ Core | ❌ | ❌ | ❌ | ❌ | ❌ | Python/CPU |
| T-03 bias_metric_computer | ❌ | ✅ Core | ❌ | ❌ | ❌ | ❌ | Python/CPU |
| T-04 fairness_auditor | ❌ | ✅ Core | ❌ | ❌ | ❌ | ❌ | Python/CPU |
| T-05 performance_tracker | ❌ | ❌ | ✅ Core | ❌ | ❌ | ❌ | Python/CPU |
| T-06 sla_monitor | ❌ | ❌ | ✅ Core | ❌ | ❌ | ❌ | FastAPI/DB |
| T-07 shap_explainer | ❌ | ✅ Aux | ❌ | ✅ Core | ❌ | ❌ | Python/CPU+GPU |
| T-08 lime_explainer | ❌ | ❌ | ❌ | ✅ Core | ❌ | ❌ | Python/CPU |
| T-09 counterfactual_generator | ❌ | ❌ | ❌ | ✅ Core | ❌ | ❌ | Python/CPU |
| T-10 adversarial_tester | ❌ | ❌ | ❌ | ❌ | ✅ Core | ❌ | Python/CPU+GPU |
| T-11 retrain_trigger | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Core | Python/CPU+LLM |
| T-12 model_lineage_tracker | ✅ Aux | ✅ Aux | ✅ Aux | ✅ Aux | ✅ Aux | ✅ Aux | FastAPI/DB |
| T-13 experiment_logger | ✅ Aux | ✅ Aux | ✅ Aux | ✅ Aux | ✅ Aux | ✅ Aux | FastAPI/MLflow |
| T-14 version_comparator | ❌ | ❌ | ✅ Aux | ❌ | ❌ | ✅ Aux | FastAPI/DB |
| T-15 dataset_profiler | ✅ Core | ❌ | ❌ | ✅ Aux | ❌ | ❌ | Python/CPU |

---

**Document Owner:** GAI-OBSERVE Advisory Architecture Team  
**Next Review:** 2026-07-28  
**Classification:** Internal — Tool Registry