# PLUGIN_REGISTRY.md
## Persona D6 — The Model Guardian | Plugin Configurations

**Version:** 1.0.0  
**Status:** Production-ready  
**Date:** 2026-06-28  
**Owner:** D6 The Model Guardian  
**Parent:** `AGENTIC_ARMS_OVERVIEW.md`  
**Master Strategy:** `C:\KimiWork Projects\GAI-OBSERVE-DESIGN\skills-hooks-plugins-strategy\STRATEGY.md`

---

## 1. Plugin Registry Overview

All plugins for D6 arms are configured in this document. Each plugin has installation, configuration, authentication, health check, quota, and security specifications. Plugins are organized by layer: ML Lifecycle, Data Quality, Explainability, Observability, Infrastructure, and AI/ML Frameworks.

---

## 2. ML Lifecycle Plugins

### MLflow

```yaml
plugin:
  name: "MLflow"
  type: "ml_lifecycle"
  version: "2.14.0"
  description: "Experiment tracking, model registry, model versioning, and artifact storage"
  installation: "pip install mlflow==2.14.0"
  config:
    tracking_uri: "http://localhost:5000"
    registry_uri: "postgresql://mlflow:mlflow@localhost:5433/mlflow_registry"
    artifact_store: "s3://gai-observe-mlflow-artifacts"
    backend_store: "postgresql"
    default_experiment_name: "d6-model-guardian"
  auth:
    method: "JWT + MLflow tracking token"
    token_rotation: "30 days"
    rbac: "experiment-level permissions"
  health_check:
    endpoint: "/health"
    expected_status: 200
    expected_response: '{"status": "healthy"}'
    interval: "60s"
  quotas:
    max_experiments: 10000
    max_runs_per_experiment: 1000
    max_artifact_size: "1 GB"
    rate_limit: "100 requests/minute"
  security:
    tls: true
    mTLS: "optional (production)"
    secrets: "Vault-backed"
    audit: "all experiment CRUD logged to P2"
  arm_integration:
    arms: ["ARM-01", "ARM-02", "ARM-03", "ARM-04", "ARM-05", "ARM-06"]
    usage: "All arms log experiments, metrics, and artifacts to MLflow"
```

### DVC

```yaml
plugin:
  name: "DVC"
  type: "data_versioning"
  version: "3.48.0"
  description: "Dataset versioning, reproducibility, and pipeline tracking for ML experiments"
  installation: "pip install dvc[s3]==3.48.0"
  config:
    remote: "s3://gai-observe-dvc-remote"
    autostage: true
    cache_dir: "/opt/dvc/cache"
  auth:
    method: "AWS IAM role + S3 bucket policy"
    role_arn: "arn:aws:iam::ACCOUNT:role/dvc-access"
  health_check:
    command: "dvc version"
    expected_output: "contains '3.48.0'"
  quotas:
    max_file_size: "10 GB"
    max_cache_size: "500 GB"
  security:
    encryption: "AES-256-S3"
    access_log: "S3 access logs → P2"
  arm_integration:
    arms: ["ARM-01", "ARM-06"]
    usage: "Version baseline and current datasets for drift detection and retraining"
```

### Weights & Biases

```yaml
plugin:
  name: "Weights & Biases"
  type: "experiment_tracking"
  version: "0.17.0"
  description: "Rich experiment visualization, sweeps, and collaboration for ML teams"
  installation: "pip install wandb==0.17.0"
  config:
    project: "gai-observe-d6"
    entity: "gai-observe"
    mode: "online"
  auth:
    method: "API key"
    key_source: "Vault"
  health_check:
    endpoint: "https://api.wandb.ai/healthz"
  quotas:
    rate_limit: "300 requests/minute"
  security:
    tls: true
    data_residency: "US-EAST-1"
  arm_integration:
    arms: ["ARM-03"]
    usage: "Advanced training metric visualization and hyperparameter sweeps"
```

---

## 3. Data Quality & Drift Detection Plugins

### Evidently AI

```yaml
plugin:
  name: "Evidently AI"
  type: "drift_detection"
  version: "0.4.32"
  description: "Open-source ML and data monitoring with drift detection, data quality, and model performance reports"
  installation: "pip install evidently==0.4.32"
  config:
    dashboard_port: 8082
    workspace: "d6-evidently-workspace"
    project_name: "gai-observe-model-guardian"
  auth:
    method: "none (local) / JWT (remote)"
  health_check:
    endpoint: "http://localhost:8082/health"
    expected_status: 200
  quotas:
    max_rows_per_report: 1000000
    max_columns: 500
  security:
    data_locality: "true — analysis runs locally, no data leaves environment"
    pii_handling: "redact before ingestion"
  arm_integration:
    arms: ["ARM-01", "ARM-03"]
    usage: "Drift detection reports and data quality monitoring dashboards"
```

### Great Expectations

```yaml
plugin:
  name: "Great Expectations"
  type: "data_quality"
  version: "0.18.0"
  description: "Data validation, expectation suites, and profiling for data pipelines"
  installation: "pip install great_expectations==0.18.0"
  config:
    data_context: "FileDataContext"
    expectations_store: "s3://gai-observe-expectations"
    validations_store: "s3://gai-observe-validations"
    checkpoint_store: "s3://gai-observe-checkpoints"
  auth:
    method: "AWS IAM role"
  health_check:
    command: "great_expectations --version"
  quotas:
    max_expectations_per_suite: 1000
  security:
    encryption: "AES-256-S3"
  arm_integration:
    arms: ["ARM-01", "ARM-15"]
    usage: "Data quality validation before drift and bias analysis"
```

---

## 4. Explainability Plugins

### SHAP

```yaml
plugin:
  name: "SHAP"
  type: "explainability"
  version: "0.45.0"
  description: "Game-theoretic feature importance for model explanations (TreeSHAP, KernelSHAP, DeepSHAP)"
  installation: "pip install shap==0.45.0"
  config:
    js_lib_path: "shap/plots/resources"
    matplotlib_backend: "Agg"
  auth:
    method: "none (local library)"
  health_check:
    import: "import shap; print(shap.__version__)"
  quotas:
    max_samples_for_kernel: 1000
    max_features: 200
  security:
    data_locality: "true"
  arm_integration:
    arms: ["ARM-02", "ARM-04"]
    usage: "Global and local SHAP value computation for model explanations and proxy detection"
```

### LIME

```yaml
plugin:
  name: "LIME"
  type: "explainability"
  version: "0.2.0"
  description: "Local Interpretable Model-agnostic Explanations for individual prediction explanation"
  installation: "pip install lime==0.2.0"
  config:
    default_num_features: 10
    default_num_samples: 5000
  auth:
    method: "none (local library)"
  health_check:
    import: "import lime; print(lime.__version__)"
  quotas:
    max_features: 100
    max_samples: 10000
  security:
    data_locality: "true"
  arm_integration:
    arms: ["ARM-04"]
    usage: "Local explanation generation for individual predictions"
```

---

## 5. Observability Plugins

### Prometheus

```yaml
plugin:
  name: "Prometheus"
  type: "metrics_collection"
  version: "2.51.0"
  description: "Time-series metrics collection and alerting for model serving and infrastructure"
  installation: "docker run prom/prometheus:v2.51.0"
  config:
    scrape_interval: "15s"
    evaluation_interval: "15s"
    retention: "30d"
    storage_tsdb_retention: "30d"
    scrape_configs:
      - job_name: "d6-fastapi"
        static_configs:
          - targets: ["localhost:9000"]
        metrics_path: "/metrics"
  auth:
    method: "Bearer token + mTLS (production)"
  health_check:
    endpoint: "http://localhost:9090/-/healthy"
    expected_status: 200
  quotas:
    max_series_per_metric: 10000
    max_scrape_frequency: "1s"
  security:
    tls: true
    mTLS: "production only"
  arm_integration:
    arms: ["ARM-01", "ARM-02", "ARM-03", "ARM-04", "ARM-05", "ARM-06"]
    usage: "All arms expose metrics via /metrics endpoint for Prometheus scraping"
```

### Grafana

```yaml
plugin:
  name: "Grafana"
  type: "visualization"
  version: "10.4.0"
  description: "Interactive dashboards for model performance, drift, bias, and explainability metrics"
  installation: "docker run grafana/grafana:10.4.0"
  config:
    datasource: "Prometheus"
    dashboards_dir: "/var/lib/grafana/dashboards/d6"
    default_theme: "dark"
  auth:
    method: "JWT + Grafana API key"
    key_source: "Vault"
  health_check:
    endpoint: "http://localhost:3000/api/health"
    expected_status: 200
  quotas:
    max_dashboards: 500
    max_users: 100
  security:
    tls: true
    session_timeout: "8h"
  arm_integration:
    arms: ["ARM-01", "ARM-02", "ARM-03", "ARM-04"]
    usage: "Drift dashboards, bias dashboards, performance dashboards, explainability plots"
```

---

## 6. Infrastructure Plugins

### PostgreSQL

```yaml
plugin:
  name: "PostgreSQL"
  type: "database"
  version: "15.6"
  description: "Primary structured data store for D6 reports, metadata, and long-term memory"
  installation: "docker run postgres:15.6"
  config:
    port: 5433
    database: "gai_observe_d6"
    extensions: ["pgvector", "uuid-ossp", "jsonb"]
    max_connections: 200
    shared_buffers: "2GB"
  auth:
    method: "SCRAM-SHA-256 + JWT (app layer)"
    connection_pooler: "PgBouncer"
  health_check:
    endpoint: "SELECT 1"
    expected_response: "1"
  quotas:
    max_query_time: "30s"
    max_connections_per_user: 50
  security:
    tls: true
    encryption_at_rest: "AES-256"
    backup: "daily to S3"
  arm_integration:
    arms: ["All"]
    usage: "Structured storage for all arm reports, metadata, and memory layers"
```

### Redis

```yaml
plugin:
  name: "Redis"
  type: "cache"
  version: "7.2"
  description: "Short-term memory cache, active session store, and metric alert buffer for D6"
  installation: "docker run redis:7.2"
  config:
    port: 6380
    maxmemory: "4GB"
    maxmemory_policy: "allkeys-lru"
    persistence: "RDB + AOF"
  auth:
    method: "ACL + Redis AUTH password"
    password_source: "Vault"
  health_check:
    command: "PING"
    expected_response: "PONG"
  quotas:
    max_key_size: "512 MB"
    max_value_size: "512 MB"
    max_clients: 10000
  security:
    tls: true
    encryption: "TLS 1.3"
  arm_integration:
    arms: ["All"]
    usage: "Active monitoring session cache, metric alert buffer, model health snapshot"
```

---

## 7. AI/ML Framework Plugins

### Ollama

```yaml
plugin:
  name: "Ollama"
  type: "local_llm"
  version: "0.1.38"
  description: "Local LLM inference for zero-cloud-cost explainability narrative generation and retrain rationale"
  installation: "docker run ollama/ollama:0.1.38"
  config:
    models: ["llama3:8b", "mistral:7b", "codellama:7b"]
    host: "0.0.0.0"
    port: 11434
  auth:
    method: "none (local) / basic auth (remote)"
  health_check:
    endpoint: "http://localhost:11434/api/tags"
    expected_status: 200
  quotas:
    max_concurrent_requests: 10
    max_context_length: 8192
  security:
    data_locality: "true — no data leaves host"
    model_signing: "SHA-256 checksums"
  arm_integration:
    arms: ["ARM-04", "ARM-06"]
    usage: "Explainability narrative generation, retrain rationale drafting, report summarization"
```

### LangChain

```yaml
plugin:
  name: "LangChain"
  type: "llm_orchestration"
  version: "0.2.0"
  description: "LLM orchestration, agent chaining, and RAG for explainability and knowledge synthesis"
  installation: "pip install langchain==0.2.0 langchain-openai==0.1.0 langchain-community==0.2.0"
  config:
    default_llm: "ollama/llama3:8b"
    vector_store: "pgvector"
    embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  auth:
    method: "JWT + API keys (for external LLMs)"
  health_check:
    import: "import langchain; print(langchain.__version__)"
  quotas:
    max_chain_length: 10
    max_context_tokens: 16000
  security:
    prompt_injection_detection: "enabled"
    output_filtering: "enabled"
  arm_integration:
    arms: ["ARM-04", "ARM-06"]
    usage: "Explainability chain-of-thought generation, RAG for regulatory knowledge"
```

### TensorFlow

```yaml
plugin:
  name: "TensorFlow"
  type: "ml_framework"
  version: "2.16.0"
  description: "Deep learning framework for model loading, inference, and adversarial testing"
  installation: "pip install tensorflow==2.16.0"
  config:
    gpu: "auto-detect"
    mixed_precision: true
    xla: true
  auth:
    method: "none (local library)"
  health_check:
    import: "import tensorflow as tf; print(tf.__version__)"
  quotas:
    max_gpu_memory: "80%"
  security:
    model_sandbox: "enabled"
  arm_integration:
    arms: ["ARM-05", "ARM-04"]
    usage: "Neural network model loading for adversarial testing and DeepSHAP"
```

### PyTorch

```yaml
plugin:
  name: "PyTorch"
  type: "ml_framework"
  version: "2.3.0"
  description: "Deep learning framework for model loading, inference, and explainability"
  installation: "pip install torch==2.3.0"
  config:
    device: "cuda if available else cpu"
    cudnn: true
  auth:
    method: "none (local library)"
  health_check:
    import: "import torch; print(torch.__version__)"
  quotas:
    max_gpu_memory: "80%"
  security:
    model_sandbox: "enabled"
  arm_integration:
    arms: ["ARM-04", "ARM-05"]
    usage: "PyTorch model loading for SHAP and adversarial testing"
```

### ONNX Runtime

```yaml
plugin:
  name: "ONNX Runtime"
  type: "inference_engine"
  version: "1.17.0"
  description: "High-performance cross-platform inference engine for standardized model deployment"
  installation: "pip install onnxruntime==1.17.0"
  config:
    execution_providers: ["CUDAExecutionProvider", "CPUExecutionProvider"]
    session_options:
      intra_op_num_threads: 4
      inter_op_num_threads: 4
  auth:
    method: "none (local library)"
  health_check:
    import: "import onnxruntime as ort; print(ort.__version__)"
  quotas:
    max_model_size: "2 GB"
  security:
    model_validation: "ONNX checker enabled"
  arm_integration:
    arms: ["ARM-01", "ARM-03", "ARM-04"]
    usage: "Standardized model inference for drift detection, performance monitoring, and explainability"
```

### JupyterHub

```yaml
plugin:
  name: "JupyterHub"
  type: "notebook_environment"
  version: "4.1.0"
  description: "Multi-user Jupyter environment for exploratory analysis, prototyping, and report generation"
  installation: "docker run jupyterhub/jupyterhub:4.1.0"
  config:
    authenticator: "NativeAuthenticator"
    spawner: "DockerSpawner"
    default_image: "gai-observe/d6-notebook:latest"
  auth:
    method: "JWT + JupyterHub OAuth"
  health_check:
    endpoint: "http://localhost:8000/hub/api"
    expected_status: 200
  quotas:
    max_users: 50
    max_memory_per_user: "4GB"
    max_cpu_per_user: 2
  security:
    csp: "enabled"
    xsrf: "enabled"
    notebook_encryption: "TLS 1.3"
  arm_integration:
    arms: ["ARM-01", "ARM-02", "ARM-04"]
    usage: "Interactive drift analysis, bias exploration, and explainability prototyping"
```

### scikit-learn

```yaml
plugin:
  name: "scikit-learn"
  type: "ml_library"
  version: "1.5.0"
  description: "Classical ML library for drift detection, performance metrics, and preprocessing"
  installation: "pip install scikit-learn==1.5.0"
  config:
    n_jobs: -1
  auth:
    method: "none (local library)"
  health_check:
    import: "import sklearn; print(sklearn.__version__)"
  quotas:
    max_samples: 1000000
  security:
    data_locality: "true"
  arm_integration:
    arms: ["ARM-01", "ARM-02", "ARM-03", "ARM-04"]
    usage: "Statistical tests, metrics computation, preprocessing, model loading"
```

### pandas

```yaml
plugin:
  name: "pandas"
  type: "data_manipulation"
  version: "2.2.0"
  description: "Data manipulation and analysis library for all D6 data processing pipelines"
  installation: "pip install pandas==2.2.0"
  config:
    display_max_rows: 100
    display_max_columns: 50
  auth:
    method: "none (local library)"
  health_check:
    import: "import pandas; print(pandas.__version__)"
  quotas:
    max_memory: "8GB"
  security:
    data_locality: "true"
  arm_integration:
    arms: ["All"]
    usage: "Universal data processing for all arms"
```

### numpy

```yaml
plugin:
  name: "numpy"
  type: "numerical_computing"
  version: "1.26.0"
  description: "Numerical computing foundation for all D6 statistical operations"
  installation: "pip install numpy==1.26.0"
  config:
    default_dtype: "float64"
  auth:
    method: "none (local library)"
  health_check:
    import: "import numpy; print(numpy.__version__)"
  quotas:
    max_array_size: "8GB"
  security:
    data_locality: "true"
  arm_integration:
    arms: ["All"]
    usage: "Numerical operations, statistical distributions, array operations for all arms"
```

---

## 8. Plugin-to-Arm Summary Matrix

| Plugin | Type | ARM-01 | ARM-02 | ARM-03 | ARM-04 | ARM-05 | ARM-06 | Priority |
|--------|------|--------|--------|--------|--------|--------|--------|----------|
| MLflow | ML Lifecycle | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | P0 |
| DVC | Data Versioning | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | P1 |
| Evidently AI | Drift Detection | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | P0 |
| Great Expectations | Data Quality | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | P1 |
| SHAP | Explainability | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | P0 |
| LIME | Explainability | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | P1 |
| Weights & Biases | Experiment Tracking | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | P2 |
| Prometheus | Metrics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | P0 |
| Grafana | Visualization | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | P0 |
| PostgreSQL | Database | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | P0 |
| Redis | Cache | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | P0 |
| Ollama | Local LLM | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | P1 |
| LangChain | LLM Orchestration | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | P1 |
| TensorFlow | ML Framework | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | P1 |
| PyTorch | ML Framework | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | P1 |
| ONNX Runtime | Inference Engine | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | P1 |
| JupyterHub | Notebooks | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | P2 |
| scikit-learn | ML Library | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | P0 |
| pandas | Data Processing | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | P0 |
| numpy | Numerical | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | P0 |

---

**Document Owner:** GAI-OBSERVE Advisory Architecture Team  
**Next Review:** 2026-07-28  
**Classification:** Internal — Plugin Registry
