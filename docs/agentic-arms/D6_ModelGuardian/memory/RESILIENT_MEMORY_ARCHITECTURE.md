# RESILIENT_MEMORY_ARCHITECTURE.md
## Persona D6 — The Model Guardian | 3-Layer Resilient Memory

**Version:** 1.0.0  
**Status:** Production-ready  
**Date:** 2026-06-28  
**Owner:** D6 The Model Guardian  
**Parent:** `AGENTIC_ARMS_OVERVIEW.md`  
**Master Strategy:** `C:\KimiWork Projects\GAI-OBSERVE-DESIGN\skills-hooks-plugins-strategy\STRATEGY.md`  
**Backend Standards:** `C:\KimiWork Projects\GAI-OBSERVE-DESIGN\architecture.md`

---

## 1. Executive Summary

D6 requires a **resilient memory architecture** capable of storing high-velocity model metrics, long-term baselines, and episodic audit trails with full regulatory compliance. The architecture follows the GAI-OBSERVE standard three-layer pattern: Short-Term Memory (STM) for active monitoring, Long-Term Memory (LTM) for baselines and thresholds, and Episodic Memory (EM) for time-series audit trails.

---

## 2. Memory Architecture Overview

```mermaid
flowchart TB
    subgraph LAYER1["LAYER 1: Short-Term Memory (STM)"]
        A1["Redis Cache<br/>Active Sessions<br/>Alert Buffers<br/>TTL: 24h active / 7d recent"]
        A2["pgvector<br/>128-dim Embeddings<br/>Semantic Retrieval<br/>Turn-level"]
    end

    subgraph LAYER2["LAYER 2: Long-Term Memory (LTM)"]
        B1["PostgreSQL JSONB<br/>Model Baselines<br/>Drift Patterns<br/>Bias Thresholds<br/>Fairness Configs"]
        B2["Filesystem<br/>Report Archives<br/>Plot Assets<br/>Ledger References"]
    end

    subgraph LAYER3["LAYER 3: Episodic Memory (EM)"]
        C1["TimescaleDB<br/>Time-Series Metrics<br/>Audit Sessions<br/>Retrain Episodes<br/>Incident Investigations"]
    end

    LAYER1 -->|Sync (append-only, CRDT)| LAYER2
    LAYER2 -->|Archive (compression)| LAYER3

    style LAYER1 fill:#ffcccc
    style LAYER2 fill:#ffffcc
    style LAYER3 fill:#ccffcc
```

---

## 3. Layer 1: Short-Term Memory (STM)

### 3.1 Storage Backend

| Component | Technology | Purpose | TTL |
|-----------|------------|---------|-----|
| **Active Cache** | Redis 7.2 | Active monitoring sessions, metric buffers, alert queues | 24 hours |
| **Recent Cache** | Redis 7.2 | Recently completed analyses, pending cross-arm chains | 7 days |
| **Vector Store** | pgvector (PostgreSQL) | 128-dimensional embeddings for semantic metric retrieval | 7 days |

### 3.2 STM Schema

```json
{
  "stm_entry": {
    "turn_id": "uuid-v4",
    "timestamp": "2026-06-28T14:00:00Z",
    "persona_id": "D6",
    "arm_id": "ARM-01",
    "model_id": "model-123",
    "metric_name": "drift_psi",
    "metric_value": 0.34,
    "drift_score": 0.34,
    "bias_score": null,
    "confidence": 0.91,
    "alert_status": "SIGNIFICANT",
    "embedding": [0.12, -0.05, 0.33, ...],
    "ttl": 86400
  }
}
```

### 3.3 Special STM Collections

| Collection | Purpose | Schema | TTL |
|------------|---------|--------|-----|
| **Active Monitoring Session** | Currently running monitoring sessions | `{session_id, model_id, arm_ids, start_time, status, last_heartbeat}` | Session lifetime + 1h |
| **Metric Alert Buffer** | Pending alerts awaiting dispatch or deduplication | `{alert_id, model_id, metric, severity, created_at, dispatched}` | 24h |
| **Model Health Snapshot** | Real-time health score cache | `{model_id, health_score, last_updated, metrics_summary}` | 5 min |
| **Cross-Arm Chain State** | Pending chained arm invocations | `{chain_id, from_arm, to_arm, payload, status, retry_count}` | 1h |

### 3.4 STM Resilience

- **Redis Sentinel:** High availability with automatic failover
- **RDB + AOF:** Dual persistence for crash recovery
- **LRU Eviction:** `allkeys-lru` policy when memory limit reached
- **Replication:** Master-replica with async replication (eventual consistency acceptable for STM)

---

## 4. Layer 2: Long-Term Memory (LTM)

### 4.1 Storage Backend

| Component | Technology | Purpose | Retention |
|-----------|------------|---------|-----------|
| **Structured Baselines** | PostgreSQL 15 JSONB | Model baselines, drift patterns, bias thresholds, fairness configs | Indefinite (versioned) |
| **Report Archives** | Filesystem (S3/MinIO) | Generated reports, plots, artifacts | 7 years (regulatory) |
| **Ledger References** | PostgreSQL 15 + P2 | Immutable references to P2 ledger entries | Indefinite |

### 4.2 LTM Schema

```json
{
  "ltm_entry": {
    "fact_id": "uuid-v4",
    "category": "model_baseline",
    "key": "model-123_v2.3.1_accuracy_baseline",
    "value": {
      "metric": "accuracy",
      "baseline_value": 0.89,
      "threshold_value": 0.85,
      "threshold_type": "minimum",
      "computed_at": "2025-10-15T00:00:00Z",
      "validation_method": "holdout_test",
      "dataset_id": "dataset-456"
    },
    "source": "ARM-03_performance_monitor",
    "timestamp": "2025-10-15T00:00:00Z",
    "confidence": 0.95,
    "expiry": "2026-10-15T00:00:00Z",
    "model_id": "model-123",
    "metric_type": "accuracy",
    "threshold_value": 0.85,
    "baseline_value": 0.89,
    "embedding": [0.08, 0.12, -0.03, ...]
  }
}
```

### 4.3 LTM Categories

| Category | Description | Example Key | Update Frequency |
|----------|-------------|-------------|-----------------|
| **model_baseline** | Performance baselines at deployment | `model-123_v2.3.1_accuracy_baseline` | Per deployment |
| **drift_pattern** | Recognized drift signatures | `drift_pattern_economic_downturn_v1` | Per discovery |
| **bias_baseline** | Fairness metric baselines | `model-123_v2.3.1_demographic_parity_baseline` | Per deployment |
| **fairness_threshold** | Regulatory fairness thresholds | `threshold_nyc144_demographic_parity` | Per regulation update |
| **performance_history** | Historical performance metrics | `model-123_monthly_accuracy_history` | Monthly aggregation |
| **retrain_decision** | Historical retrain decisions | `model-123_retrain_2026-03-15` | Per retrain event |
| **experiment_metadata** | MLflow experiment references | `exp_drift_detection_arm_2026-06` | Per experiment |

### 4.4 LTM Synchronization

- **Append-Only:** All LTM writes are append-only; updates create new versions
- **CRDT (Conflict-free Replicated Data Types):** For concurrent model updates across distributed instances
- **Versioning:** Every fact has a version number; queries default to latest
- **Compaction:** Annual compaction of obsolete versions (retain last 3 versions per key)

### 4.5 LTM Sync Protocol

```yaml
ltm_sync:
  method: "append-only with vector clock"
  conflict_resolution: "last-writer-wins per field with CRDT merge"
  replication: "async to read replicas, sync for critical baseline updates"
  backup:
    schedule: "daily at 02:00 UTC"
    target: "S3 encrypted bucket"
    retention: "90 days incremental, 7 years full"
  integrity:
    checksum: "SHA-256 per JSONB row"
    verification: "weekly full scan"
```

---

## 5. Layer 3: Episodic Memory (EM)

### 5.1 Storage Backend

| Component | Technology | Purpose | Retention |
|-----------|------------|---------|-----------|
| **Time-Series Metrics** | TimescaleDB 2.14 | Model metrics, drift scores, bias scores, performance trends | 7 years |
| **Audit Sessions** | TimescaleDB 2.14 | Complete monitoring sessions, bias audits, investigations | 7 years |
| **Retrain Episodes** | TimescaleDB 2.14 | Retrain decision trails, validation results, deployment outcomes | 7 years |

### 5.2 EM Schema

```json
{
  "em_entry": {
    "session_id": "uuid-v4",
    "persona_id": "D6",
    "arm_id": "ARM-01",
    "model_id": "model-123",
    "start_time": "2026-06-28T13:00:00Z",
    "end_time": "2026-06-28T14:00:00Z",
    "metrics": {
      "psi_overall": 0.34,
      "accuracy_current": 0.82,
      "accuracy_baseline": 0.89,
      "precision_current": 0.76,
      "recall_current": 0.88
    },
    "drift_findings": [
      {
        "feature": "credit_score",
        "psi": 0.21,
        "status": "SIGNIFICANT",
        "root_cause": "economic downturn"
      }
    ],
    "bias_findings": [
      {
        "attribute": "race",
        "demographic_parity_difference": 0.14,
        "status": "FAIL"
      }
    ],
    "performance_trends": {
      "direction": "declining",
      "rate_per_week": -0.02,
      "projected_breach_date": "2026-07-15"
    },
    "retrain_decisions": {
      "recommended": true,
      "rationale": "Drift PSI > 0.25, accuracy drop > 5%, bias FAIL for 2+ attributes",
      "validation_gates": ["accuracy > 0.85", "demographic_parity < 0.05"],
      "expected_improvements": {"accuracy": 0.05, "demographic_parity": -0.08}
    },
    "embedding": [0.15, -0.08, 0.22, ...],
    "compression_ratio": 0.15
  }
}
```

### 5.3 EM Hypertable Design

```sql
-- TimescaleDB hypertable for D6 episodic memory
CREATE TABLE d6_episodic_memory (
    session_id UUID PRIMARY KEY,
    persona_id TEXT NOT NULL,
    arm_id TEXT NOT NULL,
    model_id UUID NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    metrics JSONB NOT NULL,
    drift_findings JSONB,
    bias_findings JSONB,
    performance_trends JSONB,
    retrain_decisions JSONB,
    embedding VECTOR(128),
    compression_ratio FLOAT
);

-- Convert to hypertable
SELECT create_hypertable('d6_episodic_memory', 'start_time', chunk_time_interval => INTERVAL '7 days');

-- Indexes for retrieval patterns
CREATE INDEX idx_em_model_time ON d6_episodic_memory (model_id, start_time DESC);
CREATE INDEX idx_em_arm ON d6_episodic_memory (arm_id, start_time DESC);
CREATE INDEX idx_em_alert ON d6_episodic_memory USING GIN (metrics);
CREATE INDEX idx_em_embedding ON d6_episodic_memory USING ivfflat (embedding vector_cosine_ops);
```

### 5.4 EM Retrieval Patterns

| Retrieval Query | Filter | Time Range | Index Used |
|-----------------|--------|------------|------------|
| **Model History** | `model_id = ?` | Any | `idx_em_model_time` |
| **Arm Sessions** | `arm_id = ?` | Any | `idx_em_arm` |
| **Alert Investigation** | `metrics->alert_status = 'CRITICAL'` | Last 30 days | `idx_em_alert` |
| **Semantic Search** | `embedding <-> query_vector` | Any | `idx_em_embedding` |
| **Retrain History** | `retrain_decisions->recommended = true` | Last 2 years | `idx_em_alert` |
| **Compliance Audit** | `arm_id = 'ARM-02'` | Custom range | `idx_em_arm` + `start_time` |

### 5.5 EM Compression

- **Automatic Compression:** Enabled after 30 days
- **Compression Ratio:** Target 15:1 (from ~10 KB to ~0.7 KB per session)
- **Decompression:** On-demand for audit queries; < 100ms latency
- **Cold Storage:** After 1 year, compress and archive to S3 Glacier

---

## 6. Memory Hooks & Resilience

### 6.1 Memory Hooks

```yaml
memory_hooks:
  - name: "model_baseline_tracking"
    trigger: "model_deployed"
    action: "Store baseline metrics in LTM with expiry = deployment_date + 1 year"
    target: "LTM (PostgreSQL)"

  - name: "drift_pattern_recognition"
    trigger: "drift_detected with status = SIGNIFICANT"
    action: "Compare to known drift patterns in LTM; if match, annotate with pattern_id; if novel, create new pattern entry"
    target: "LTM (PostgreSQL) + EM (TimescaleDB)"

  - name: "bias_trend_analysis"
    trigger: "bias_audit_completed"
    action: "Append results to time-series in EM; compare to previous audits; flag worsening trends"
    target: "EM (TimescaleDB)"

  - name: "retrain_decision_history"
    trigger: "retrain_recommendation_generated"
    action: "Store full decision context in EM with embedding for semantic retrieval"
    target: "EM (TimescaleDB) + STM (Redis)"

  - name: "alert_buffer_flush"
    trigger: "alert_dispatch or alert_timeout"
    action: "Move from STM alert buffer to EM audit trail"
    target: "STM (Redis) → EM (TimescaleDB)"
```

### 6.2 Resilience Patterns

| Pattern | Implementation | RTO | RPO |
|---------|---------------|-----|-----|
| **STM Failover** | Redis Sentinel (3-node) | < 30s | < 1s |
| **LTM Replication** | PostgreSQL streaming replication | < 5 min | < 1 min |
| **EM Replication** | TimescaleDB multi-node | < 5 min | < 1 min |
| **Cross-Region Backup** | S3 cross-region replication | < 1 hour | < 1 hour |
| **Disaster Recovery** | Daily snapshot + WAL archiving | < 4 hours | < 1 hour |

### 6.3 Privacy & Compliance

```yaml
memory_privacy:
  model_data_anonymization:
    method: "k-anonymity with k=5"
    fields: ["name", "ssn", "email", "phone"]
    applied_at: "ingestion_time"

  protected_attribute_redaction:
    method: "tokenization with reversible mapping"
    fields: ["gender", "race", "age", "disability"]
    storage: "Vault-encrypted lookup table"
    access_control: "role_d6-audit_only"

  aggregated_fairness_metrics:
    rule: "Never store individual-level predictions with protected attributes together"
    enforcement: "Schema validation + runtime check"

  gdpr_right_to_erasure:
    support: "Model-level deletion (cascade to all memory layers)"
    procedure: "1. Identify model_id → 2. Delete from STM → 3. Soft-delete LTM (retain hash) → 4. Archive EM with retention note → 5. Log to P2"
```

---

## 7. Memory Performance Budgets

| Layer | Write Latency | Read Latency | Throughput | Capacity |
|-------|--------------|--------------|------------|----------|
| **STM** | < 1 ms | < 5 ms | 100K ops/sec | 4 GB |
| **LTM** | < 50 ms | < 100 ms | 10K rows/sec | 500 GB |
| **EM** | < 100 ms | < 500 ms | 1K rows/sec | 10 TB |

---

**Document Owner:** GAI-OBSERVE Advisory Architecture Team  
**Next Review:** 2026-07-28  
**Classification:** Internal — Architecture
