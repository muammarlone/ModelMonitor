# ARM_02_D6_Bias_Auditor.md
## Persona D6 — The Model Guardian | Primary Arm 2: Bias Auditor

**Arm ID:** `ARM-02`  
**Name:** `bias_auditor`  
**Type:** Primary  
**Status:** Production-ready  
**Version:** 1.0.0  
**Owner:** D6 The Model Guardian  
**Parent:** `AGENTIC_ARMS_OVERVIEW.md`

---

## 1. Purpose

The Bias Auditor arm audits ML models for **fairness across protected attributes** with statistical confidence intervals and regulatory compliance mapping. It detects disparate impact, demographic parity violations, and proxy discrimination.

---

## 2. Protected Attributes & Regulatory Mapping

| Protected Attribute | EU AI Act | NYC 144 | EEOC | Fair Lending | Applicable |
|---------------------|-----------|---------|------|-------------|------------|
| **Gender / Sex** | Article 10 (High-risk) | Required | Title VII | ECOA | All |
| **Race / Ethnicity** | Article 10 (High-risk) | Required | Title VII | ECOA | All |
| **Age** | Article 10 (High-risk) | Required | ADEA | ECOA | All |
| **Disability** | Article 10 (High-risk) | Optional | ADA | ECOA | All |
| **Religion** | Article 10 | Optional | Title VII | ECOA | Healthcare, Hiring |
| **National Origin** | Article 10 | Optional | Title VII | ECOA | All |
| **ZIP Code / Proxy** | Article 10 (proxy detection) | Required | Disparate impact | ECOA | Fintech, Lending |

---

## 3. Fairness Metrics

```yaml
fairness_metrics:
  demographic_parity:
    name: "Demographic Parity Difference"
    description: "Difference in positive outcome rates between groups"
    formula: "P(Y_hat=1 | A=0) - P(Y_hat=1 | A=1)"
    threshold: "< 0.05 (5 percentage points)"
    interpretation: "Lower is better; 0 = perfect parity"

  equalized_odds:
    name: "Equalized Odds (FPR + TPR equality)"
    description: "True positive and false positive rates are equal across groups"
    formula: "P(Y_hat=1 | Y=1, A=0) = P(Y_hat=1 | Y=1, A=1) AND P(Y_hat=1 | Y=0, A=0) = P(Y_hat=1 | Y=0, A=1)"
    threshold: "FPR difference < 0.05, TPR difference < 0.05"
    interpretation: "Satisfies both TPR and FPR equality"

  equal_opportunity:
    name: "Equal Opportunity (TPR equality)"
    description: "True positive rates are equal across groups"
    formula: "P(Y_hat=1 | Y=1, A=0) - P(Y_hat=1 | Y=1, A=1)"
    threshold: "< 0.05"
    interpretation: "Only TPR equality required"

  calibration:
    name: "Calibration / Predictive Parity"
    description: "Predicted probability reflects actual outcome rate within each group"
    formula: "P(Y=1 | Y_hat=p, A=0) = P(Y=1 | Y_hat=p, A=1) = p"
    threshold: "Brier score < 0.15 per group"
    interpretation: "Well-calibrated predictions within each subgroup"

  disparate_impact_ratio:
    name: "Disparate Impact Ratio (4/5ths Rule)"
    description: "Ratio of positive outcome rates; 4/5ths rule threshold"
    formula: "P(Y_hat=1 | A=1) / P(Y_hat=1 | A=0)"
    threshold: ">= 0.80 (4/5ths rule)"
    interpretation: "Ratio < 0.80 indicates disparate impact under US law"
```

---

## 4. Bias Audit Report Schema

```json
{
  "report_id": "bias-uuid-v4",
  "model_id": "model-123",
  "model_version": "2.3.1",
  "arm_id": "ARM-02",
  "timestamp": "2026-06-28T14:00:00Z",
  "regulatory_frameworks": ["EU_AI_ACT", "NYC_144", "ECOA"],
  "overall_fairness": "FAIL",
  "protected_attributes": [
    {
      "attribute": "gender",
      "groups": ["Male", "Female", "Non-binary"],
      "metrics": {
        "demographic_parity": {
          "Male_approval_rate": 0.78,
          "Female_approval_rate": 0.72,
          "difference": 0.06,
          "threshold": 0.05,
          "status": "MARGINAL"
        },
        "equalized_odds": {
          "FPR_difference": 0.04,
          "TPR_difference": 0.03,
          "threshold": 0.05,
          "status": "PASS"
        },
        "disparate_impact_ratio": 0.92,
        "status": "PASS"
      },
      "overall_status": "MARGINAL"
    },
    {
      "attribute": "race",
      "groups": ["White", "Black", "Asian", "Hispanic"],
      "metrics": {
        "demographic_parity": {
          "White_approval_rate": 0.82,
          "Black_approval_rate": 0.68,
          "difference": 0.14,
          "threshold": 0.05,
          "status": "FAIL"
        },
        "equalized_odds": {
          "FPR_difference": 0.11,
          "TPR_difference": 0.08,
          "threshold": 0.05,
          "status": "FAIL"
        },
        "disparate_impact_ratio": 0.83,
        "status": "MARGINAL"
      },
      "overall_status": "FAIL"
    }
  ],
  "proxy_discrimination": [
    {
      "feature": "zip_code",
      "proxy_for": "race",
      "shap_importance": 0.08,
      "correlation_with_protected": 0.67,
      "recommendation": "REMOVE or encode at higher granularity"
    }
  ],
  "subgroup_performance": [
    {
      "subgroup": "Black_Female_under_30",
      "n": 145,
      "accuracy": 0.71,
      "precision": 0.64,
      "recall": 0.58,
      "f1": 0.61,
      "compared_to_overall": -0.11
    }
  ],
  "statistical_confidence": {
    "confidence_level": 0.95,
    "bootstrap_iterations": 1000,
    "ci_method": "percentile_bootstrap"
  },
  "compliance_mapping": {
    "EU_AI_ACT": {
      "article": "Article 10 (High-risk AI systems)",
      "requirement": "Bias testing and mitigation for high-risk systems",
      "status": "NON_COMPLIANT",
      "gap": "Demographic parity difference 14% exceeds 5% threshold"
    },
    "NYC_144": {
      "requirement": "Annual bias audit for automated employment decision tools",
      "status": "FAIL",
      "gap": "2 of 3 protected attributes FAIL fairness test"
    }
  },
  "recommendations": [
    "Remove zip_code feature (proxy discrimination detected)",
    "Apply reweighting bias mitigation technique",
    "Apply adversarial debiasing during retraining",
    "Expected improvement: demographic parity difference -8%"
  ]
}
```

---

## 5. Subgroup Performance Breakdown

The arm generates subgroup performance tables with **intersectional analysis**:

| Subgroup | N | Accuracy | Precision | Recall | F1 | Demographic Parity | Fairness Status |
|----------|---|----------|-----------|--------|----|-------------------|-----------------|
| Overall | 12,000 | 0.82 | 0.76 | 0.88 | 0.82 | — | — |
| White Male | 3,200 | 0.88 | 0.84 | 0.91 | 0.87 | +0.06 | PASS |
| White Female | 2,800 | 0.85 | 0.81 | 0.89 | 0.85 | +0.03 | PASS |
| Black Male | 1,500 | 0.74 | 0.68 | 0.82 | 0.74 | -0.08 | MARGINAL |
| Black Female | 1,450 | 0.71 | 0.64 | 0.78 | 0.71 | -0.11 | FAIL |
| Asian Male | 1,800 | 0.86 | 0.83 | 0.90 | 0.86 | +0.04 | PASS |
| Hispanic Female | 1,250 | 0.76 | 0.70 | 0.84 | 0.77 | -0.06 | MARGINAL |

---

## 6. Invocation Contract

```yaml
arm:
  id: "ARM-02"
  name: "bias_auditor"
  trigger:
    - type: "scheduled"
      cron: "0 0 1 */3 *"
      description: "Quarterly for all regulated models"
    - type: "on_demand"
      endpoint: "/v1/ai/bias/{model_id}"
      method: "POST"
    - type: "event_driven"
      event: "regulatory_audit_request"
      queue: "d6-compliance"

  input:
    schema: "BiasAuditRequest"
    fields:
      model_id: "UUID"
      model_version: "string (semver)"
      predictions_uri: "string (S3/MinIO)"
      ground_truth_uri: "string (optional)"
      protected_attributes: "array[string]"
      regulatory_frameworks: "array[enum]"
      confidence_level: "float (default: 0.95)"
      bootstrap_iterations: "int (default: 1000)"
      intersectional_depth: "int (default: 2)"

  output:
    schema: "BiasAuditResponse"
    fields:
      report_id: "UUID"
      overall_fairness: "enum [pass, marginal, fail, error]"
      protected_attributes: "array[ProtectedAttributeAudit]"
      proxy_discrimination: "array[ProxyFinding]"
      subgroup_performance: "array[SubgroupMetric]"
      compliance_mapping: "object"
      recommendations: "array[string]"
      ledger_hash: "string (P2 reference)"
      next_arm: "ARM-06 (retrain_recommender) if fail"

  timeout:
    default_ms: 1800000
    max_ms: 3600000

  retry:
    policy: "exponential_backoff"
    max_attempts: 3
    base_ms: 2000

  fallback:
    on_timeout: "return single-attribute analysis with warn status"
    on_error: "log to P2 and alert D5 + G1"
```

---

## 7. Confidence Intervals & Statistical Validation

All fairness metrics include **bootstrap percentile confidence intervals**:

```python
# Pseudocode for bootstrap CI
from sklearn.utils import resample

def bootstrap_ci(metric_func, data, n_iterations=1000, confidence=0.95):
    scores = []
    for _ in range(n_iterations):
        sample = resample(data)
        scores.append(metric_func(sample))
    alpha = 1 - confidence
    lower = np.percentile(scores, alpha/2 * 100)
    upper = np.percentile(scores, (1 - alpha/2) * 100)
    return lower, upper
```

---

## 8. Tool Bindings

| Tool ID | Tool Name | Role in Arm | Execution Mode |
|---------|-----------|-------------|---------------|
| `T-03` | `bias_metric_computer` | Fairness metric calculation | Python/CPU |
| `T-04` | `fairness_auditor` | Regulatory compliance mapping | Python/CPU |
| `T-07` | `shap_explainer` | Proxy discrimination detection | Python/CPU |
| `T-13` | `model_lineage_tracker` | Model version and attribute metadata | FastAPI/DB |

---

**Document Owner:** GAI-OBSERVE Advisory Architecture Team  
**Next Review:** 2026-07-28  
**Classification:** Internal — Arm Specification