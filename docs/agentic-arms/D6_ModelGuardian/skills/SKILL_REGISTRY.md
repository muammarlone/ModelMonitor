# SKILL_REGISTRY.md
## Persona D6 — The Model Guardian | Skill Definitions

**Version:** 1.0.0  
**Status:** Production-ready  
**Date:** 2026-06-28  
**Owner:** D6 The Model Guardian  
**Parent:** `AGENTIC_ARMS_OVERVIEW.md`  
**Master Strategy:** `C:\KimiWork Projects\GAI-OBSERVE-DESIGN\skills-hooks-plugins-strategy\STRATEGY.md`

---

## 1. Skill Registry Overview

All skills leveraged by D6 arms are defined in this document. Each skill has a trigger, input/output contract, procedure, quality gates, error handling, evidence requirements, and usage examples. Skills are mapped from the master strategy's skill registry to D6-specific use cases.

---

## 2. Skill Definitions

### stock-assistant (Metric Monitoring)

```yaml
skill:
  name: "stock-assistant"
  description: "Financial data and technical indicator monitoring adapted for ML model metric time-series tracking (drift, performance, bias trends)"
  owner: "D6 The Model Guardian (adapted from D1/D5/G4)"
  trigger: "scheduled_cron OR threshold_breach OR on_demand_analysis"
  input:
    schema: "MetricMonitorRequest"
    fields:
      watchlist: "array[model_id]"
      metrics: "array[enum: drift_psi, accuracy, precision, recall, bias_score, fairness_index]"
      window: "enum[1h, 24h, 7d, 30d]"
      alert_thresholds: "object (per-metric thresholds)"
  output:
    schema: "MetricMonitorResponse"
    fields:
      metric_snapshots: "array[ModelMetricSnapshot]"
      alerts: "array[ThresholdAlert]"
      trend_direction: "enum[improving, stable, declining, volatile]"
      recommendation: "string"
  procedure:
    - "Fetch metric time-series from Prometheus/TimescaleDB for each model in watchlist"
    - "Compute technical indicators: moving average, RSI, Bollinger Bands on metric trends"
    - "Compare current values to alert thresholds"
    - "Generate alerts with severity classification"
    - "Produce trend analysis with directional recommendation"
  quality_gates:
    - "Data freshness: last metric < 5 minutes old"
    - "Threshold validation: all thresholds in valid range"
    - "Model existence: all model_ids exist in registry"
    - "Alert deduplication: no duplicate alerts within 15 minutes"
  error_handling:
    on_missing_data: "return cached snapshot with staleness warning"
    on_threshold_invalid: "return error with valid threshold range"
    on_model_not_found: "skip model and log warning"
  evidence:
    - "Prometheus query logs"
    - "Metric snapshot JSON"
    - "Alert dispatch records"
  example:
    request: "{watchlist: ['model-123'], metrics: ['accuracy', 'drift_psi'], window: '24h', alert_thresholds: {accuracy: 0.85, drift_psi: 0.25}}"
    response: "{metric_snapshots: [...], alerts: [{model_id: 'model-123', metric: 'accuracy', current: 0.82, threshold: 0.85, severity: 'SIGNIFICANT'}], trend_direction: 'declining', recommendation: 'Schedule drift detection and retrain evaluation'}"
```

### seaborn-visualization (Performance Charts)

```yaml
skill:
  name: "seaborn-visualization"
  description: "Data visualization for model performance charts, drift distribution plots, bias heatmaps, and explainability plots with CJK label support"
  owner: "D6 The Model Guardian (adapted from D1/D8/G4)"
  trigger: "report_generation OR dashboard_update OR on_demand_plot"
  input:
    schema: "VisualizationRequest"
    fields:
      data: "DataFrame or JSON"
      chart_type: "enum[drift_distribution, performance_line, bias_heatmap, shap_waterfall, confidence_histogram, calibration_plot]"
      theme: "enum[gai-observe-dark, gai-observe-light, governance-signal]"
      dimensions: "object {width, height, dpi}"
      labels: "object {title, x, y, subtitle}"
  output:
    schema: "VisualizationResponse"
    fields:
      plot_uri: "string (PNG/SVG path)"
      plot_data: "object (serialized plot data)"
      alt_text: "string (accessibility description)"
  procedure:
    - "Validate data schema against chart_type requirements"
    - "Apply GAI-OBSERVE theme via theme-factory tokens"
    - "Generate chart using seaborn + matplotlib with CJK font support"
    - "Add annotations, thresholds, and reference lines"
    - "Save to S3/MinIO with accessibility alt text"
    - "Return URI and metadata"
  quality_gates:
    - "Data completeness: no missing required columns"
    - "Theme compliance: all colors from GAI-OBSERVE token set"
    - "Accessibility: alt text generated for all charts"
    - "Resolution: min 300 DPI for PDF, 150 DPI for web"
  error_handling:
    on_invalid_data: "return error with required schema"
    on_theme_missing: "fallback to default GAI-OBSERVE dark theme"
  evidence:
    - "Generated plot files"
    - "Theme audit logs"
    - "Data lineage for plot source"
  example:
    request: "{data: {psi: [0.34, 0.21, 0.12], features: ['credit_score', 'income', 'age']}, chart_type: 'drift_distribution', theme: 'gai-observe-dark', labels: {title: 'Feature Drift Analysis', x: 'PSI', y: 'Feature'}}"
    response: "{plot_uri: 's3://d6-reports/drift-uuid/drift_bars.png', alt_text: 'Bar chart showing PSI values for three features, credit_score highest at 0.34'}"
```

### xlsx (Data Analysis)

```yaml
skill:
  name: "xlsx"
  description: "Excel spreadsheet generation for model analysis, drift metrics, bias audits, and performance reports with formulas and conditional formatting"
  owner: "D6 The Model Guardian (adapted from D1/G4)"
  trigger: "report_export OR data_analysis OR regulatory_submission"
  input:
    schema: "ExcelExportRequest"
    fields:
      sheets: "array[SheetConfig]"
      formulas: "boolean (include Excel formulas)"
      conditional_formatting: "boolean (color-code thresholds)"
      branding: "boolean (apply GAI-OBSERVE theme)"
  output:
    schema: "ExcelExportResponse"
    fields:
      file_uri: "string (.xlsx path)"
      sheet_count: "int"
      formula_count: "int"
  procedure:
    - "Structure data into sheets with headers and metadata"
    - "Apply Excel formulas for derived metrics (e.g., delta calculations)"
    - "Apply conditional formatting: red for FAIL, yellow for MARGINAL, green for PASS"
    - "Apply GAI-OBSERVE branded header/footer styles"
    - "Save to S3/MinIO with checksum"
  quality_gates:
    - "Formula accuracy: all formulas evaluate correctly"
    - "Formatting: conditional rules cover all thresholds"
    - "Branding: header contains GAI-OBSERVE logo and document metadata"
    - "Accessibility: sheet names and table headers are descriptive"
  error_handling:
    on_formula_error: "replace with static value and flag"
    on_branding_missing: "generate plain header with document metadata"
  evidence:
    - "Generated .xlsx files"
    - "Formula validation logs"
    - "Checksum verification"
  example:
    request: "{sheets: [{name: 'Drift Summary', data: [...]}, {name: 'Feature Breakdown', data: [...]}], formulas: true, conditional_formatting: true, branding: true}"
    response: "{file_uri: 's3://d6-reports/drift-uuid/drift_analysis.xlsx', sheet_count: 2, formula_count: 15}"
```

### report-writing (Model Reports)

```yaml
skill:
  name: "report-writing"
  description: "Structured long-form report generation for model drift, bias, performance, and explainability with regulatory compliance sections"
  owner: "D6 The Model Guardian (adapted from G5/D8/D3)"
  trigger: "arm_completion OR regulatory_request OR quarterly_audit"
  input:
    schema: "ReportRequest"
    fields:
      report_type: "enum[drift, bias, performance, explainability, comprehensive]"
      model_id: "UUID"
      arm_results: "array[ArmResult]"
      regulatory_frameworks: "array[enum]"
      audience: "enum[technical, executive, regulatory, board]"
      format: "enum[markdown, pdf, docx, html]"
  output:
    schema: "ReportResponse"
    fields:
      report_uri: "string"
      word_count: "int"
      sections: "array[string]"
      compliance_checklist: "object"
  procedure:
    - "Aggregate arm results into structured sections"
    - "Generate executive summary with key findings and recommendations"
    - "Write technical deep-dive with statistical evidence"
    - "Map findings to regulatory compliance requirements"
    - "Generate visual summaries with seaborn-visualization"
    - "Assemble into requested format using md-to-pdf or docx"
  quality_gates:
    - "Evidence completeness: every claim backed by data or calculation"
    - "Regulatory mapping: all applicable frameworks covered"
    - "Audience appropriateness: technical depth matches audience"
    - "P3 verification: all statistical claims pass Hallucination Guard"
  error_handling:
    on_missing_data: "include 'data unavailable' section with explanation"
    on_p3_rejection: "revise claim with corrected evidence and resubmit"
  evidence:
    - "Report source markdown"
    - "P3 verification log"
    - "Arm result JSON files"
  example:
    request: "{report_type: 'comprehensive', model_id: 'model-123', arm_results: [{arm_id: 'ARM-01', status: 'fail'}, {arm_id: 'ARM-02', status: 'fail'}], regulatory_frameworks: ['EU_AI_ACT', 'NYC_144'], audience: 'regulatory', format: 'pdf'}"
    response: "{report_uri: 's3://d6-reports/comprehensive-model-123.pdf', word_count: 4500, sections: ['Executive Summary', 'Drift Analysis', 'Bias Audit', 'Performance Review', 'Explainability', 'Compliance Mapping', 'Recommendations'], compliance_checklist: {'EU_AI_ACT': 'NON_COMPLIANT', 'NYC_144': 'FAIL'}}"
```

### deep-research-swarm (ML Research)

```yaml
skill:
  name: "deep-research-swarm"
  description: "Multi-agent deep research for ML monitoring methods, bias mitigation techniques, and drift detection literature with evidence-backed findings"
  owner: "D6 The Model Guardian (adapted from G3/G4/D4)"
  trigger: "method_inquiry OR technique_evaluation OR literature_review"
  input:
    schema: "ResearchRequest"
    fields:
      topic: "string"
      research_questions: "array[string]"
      sources: "array[enum: scholar, arxiv, web, industry_report]"
      depth: "enum[rapid, standard, comprehensive]"
      cross_reference_min: "int (default: 5)"
  output:
    schema: "ResearchResponse"
    fields:
      research_brief: "string (markdown)"
      citations: "array[Citation]"
      evidence_summary: "object"
      confidence_score: "float"
      recommended_actions: "array[string]"
  procedure:
    - "Decompose topic into sub-questions for parallel agent research"
    - "Dispatch agents to search configured sources (scholar, arxiv, web)"
    - "Cross-reference findings across minimum 5 sources"
    - "Synthesize evidence into structured brief with citations"
    - "Score confidence based on source quality and agreement"
    - "Generate actionable recommendations"
  quality_gates:
    - "Source diversity: minimum 3 distinct source types"
    - "Citation validity: all citations verifiable"
    - "Evidence threshold: every claim has supporting source"
    - "P3 verification: all claims pass Hallucination Guard"
  error_handling:
    on_source_failure: "retry with alternative source"
    on_low_confidence: "flag for manual review and expand search"
  evidence:
    - "Research brief markdown"
    - "Citation list with DOI/URL"
    - "Agent search logs"
  example:
    request: "{topic: 'bias mitigation techniques for lending models', research_questions: ['What are the most effective reweighting methods?', 'How does adversarial debiasing compare?'], sources: ['scholar', 'arxiv'], depth: 'comprehensive', cross_reference_min: 5}"
    response: "{research_brief: '...', citations: [...], confidence_score: 0.92, recommended_actions: ['Apply reweighting with class-balanced sampling', 'Validate with demographic parity < 5%'] }"
```

### kimi-data-tools-v2 (Benchmark Research)

```yaml
skill:
  name: "kimi-data-tools-v2"
  description: "Web search, URL fetch, and structured data retrieval for ML benchmark research, regulatory updates, and competitive monitoring"
  owner: "D6 The Model Guardian (adapted from G6/D4/P1)"
  trigger: "benchmark_lookup OR regulatory_update OR competitive_intelligence"
  input:
    schema: "DataToolsRequest"
    fields:
      query: "string"
      tool: "enum[search, fetch, finance, datasource]"
      limit: "int (default: 5)"
      include_content: "boolean (default: false)"
  output:
    schema: "DataToolsResponse"
    fields:
      results: "array[SearchResult]"
      sources: "array[string]"
      relevance_score: "float"
      timestamp: "datetime"
  procedure:
    - "Route query to appropriate data tool (search, fetch, finance, datasource)"
    - "Execute query with configured limit and content inclusion"
    - "Filter and rank results by relevance"
    - "Return structured results with source attribution"
  quality_gates:
    - "Source freshness: web results < 30 days old"
    - "Relevance: results match query intent"
    - "Attribution: every result has verifiable source"
  error_handling:
    on_tool_failure: "fallback to alternative data source"
    on_no_results: "return empty with suggestion for refined query"
  evidence:
    - "Search result JSON"
    - "Source URL list"
  example:
    request: "{query: 'EU AI Act bias testing requirements 2026', tool: 'search', limit: 5, include_content: true}"
    response: "{results: [{title: 'EU AI Act Technical Standards...', url: '...', snippet: '...'}], sources: ['eur-lex.europa.eu'], relevance_score: 0.94}"
```

### swarm-coding (Monitoring Pipeline Generation)

```yaml
skill:
  name: "swarm-coding"
  description: "Multi-agent code generation for monitoring pipeline scaffolding, test suites, and FastAPI service generation for D6 arms"
  owner: "D6 The Model Guardian (adapted from D9/D7/D2)"
  trigger: "pipeline_request OR test_generation OR service_scaffold"
  input:
    schema: "SwarmCodingRequest"
    fields:
      task_type: "enum[pipeline, test_suite, service, config]"
      arm_id: "string"
      tech_stack: "object {framework, database, cache}"
      requirements: "array[string]"
      tests_required: "boolean"
  output:
    schema: "SwarmCodingResponse"
    fields:
      code_files: "array[CodeFile]"
      test_files: "array[TestFile]"
      config_files: "array[ConfigFile]"
      coverage_estimate: "float"
      build_instructions: "string"
  procedure:
    - "Decompose task into parallel sub-tasks for agent swarm"
    - "Assign agents to generate code, tests, and configs"
    - "Merge outputs with conflict resolution"
    - "Validate generated code against Pydantic v2 and FastAPI standards"
    - "Estimate test coverage from generated test suite"
  quality_gates:
    - "Code style: passes ruff + black formatting"
    - "Type safety: passes mypy"
    - "Security: passes Bandit scan"
    - "Standards: follows GAI-OBSERVE backend standards"
  error_handling:
    on_merge_conflict: "flag for manual review with conflict diff"
    on_test_failure: "generate additional test cases"
  evidence:
    - "Generated code files"
    - "Test coverage report"
    - "Security scan results"
  example:
    request: "{task_type: 'service', arm_id: 'ARM-01', tech_stack: {framework: 'FastAPI', database: 'PostgreSQL', cache: 'Redis'}, requirements: ['Drift detection endpoint', 'PSI calculation', 'Alert dispatch'], tests_required: true}"
    response: "{code_files: [{path: 'main.py', content: '...'}, {path: 'drift.py', content: '...'}], test_files: [...], coverage_estimate: 0.85}"
```

### skill-creator (ML Procedure Authoring)

```yaml
skill:
  name: "skill-creator"
  description: "Create and update SKILL.md procedures for ML monitoring, drift detection, bias auditing, and explainability workflows"
  owner: "D6 The Model Guardian (adapted from D9/D8/D3)"
  trigger: "new_procedure OR procedure_update OR workflow_standardization"
  input:
    schema: "SkillCreateRequest"
    fields:
      skill_name: "string"
      domain: "enum[drift, bias, performance, explainability, retraining, general]"
      procedure_steps: "array[string]"
      quality_gates: "array[string]"
      error_scenarios: "array[string]"
      evidence_requirements: "array[string]"
  output:
    schema: "SkillCreateResponse"
    fields:
      skill_path: "string"
      skill_content: "string (markdown)"
      validation_status: "enum[pass, needs_review]"
      review_notes: "array[string]"
  procedure:
    - "Analyze domain requirements and existing skills"
    - "Draft SKILL.md with YAML frontmatter + markdown body"
    - "Include trigger conditions, input/output schemas, procedures, quality gates, error handling, evidence, and examples"
    - "Validate against GAI-OBSERVE skill standards"
    - "Submit for D8 review if documentation-related, G1 if compliance-related"
  quality_gates:
    - "Completeness: all required sections present"
    - "Accuracy: technical steps are correct and tested"
    - "Consistency: follows GAI-OBSERVE SKILL.md template"
    - "Review: approved by D8 or G1 as appropriate"
  error_handling:
    on_incomplete_input: "request missing fields with template"
    on_validation_failure: "return review notes for correction"
  evidence:
    - "Generated SKILL.md file"
    - "Review approval log"
    - "Version control commit"
  example:
    request: "{skill_name: 'drift-detection-procedure', domain: 'drift', procedure_steps: ['Load reference data', 'Load current data', 'Compute PSI', 'Compare thresholds'], quality_gates: ['PSI computed correctly', 'All features tested'], error_scenarios: ['Missing data', 'Empty feature list'], evidence_requirements: ['Drift report JSON', 'Feature breakdown table']}"
    response: "{skill_path: 'skills/drift-detection-procedure/SKILL.md', skill_content: '...', validation_status: 'pass', review_notes: []}"
```

### competitor-analysis (Model Comparison)

```yaml
skill:
  name: "competitor-analysis"
  description: "Compare D6 monitoring capabilities against Arthur, Fiddler, Arize, Weights & Biases, and cloud-native model monitoring with feature gap analysis"
  owner: "D6 The Model Guardian (adapted from G4/D1)"
  trigger: "competitive_intelligence OR product_positioning OR feature_gap_request"
  input:
    schema: "CompetitorAnalysisRequest"
    fields:
      competitors: "array[enum: arthur, fiddler, arize, wandb, mlflow, sagemaker, vertex_ai]"
      dimensions: "array[enum: drift_detection, bias_audit, explainability, pricing, deployment, integration]"
      output_format: "enum[table, report, presentation]"
  output:
    schema: "CompetitorAnalysisResponse"
    fields:
      comparison_matrix: "object"
      feature_gaps: "array[FeatureGap]"
      differentiation_points: "array[string]"
      positioning_recommendation: "string"
  procedure:
    - "Research each competitor's capabilities in specified dimensions"
    - "Score D6 capabilities on same dimensions"
    - "Identify feature gaps and competitive advantages"
    - "Generate comparison matrix with visual indicators"
    - "Produce positioning recommendations"
  quality_gates:
    - "Source accuracy: competitor data from official docs or verified sources"
    - "Fairness: no misrepresentation of competitor capabilities"
    - "Currency: competitor data < 90 days old"
  error_handling:
    on_source_unavailable: "mark as "unverified" and use last known data"
    on_dimension_unknown: "skip dimension with explanation"
  evidence:
    - "Competitor research notes"
    - "Comparison matrix JSON"
    - "Source URLs"
  example:
    request: "{competitors: ['arthur', 'fiddler', 'arize'], dimensions: ['drift_detection', 'bias_audit', 'explainability'], output_format: 'report'}"
    response: "{comparison_matrix: {drift_detection: {D6: 'excellent', Arthur: 'excellent', Fiddler: 'good'}}, feature_gaps: [{area: 'real-time dashboards', competitor: 'Arize', D6_status: 'planned'}], differentiation_points: ['Only D6 combines drift + bias + explainability + adversarial in one persona'], positioning_recommendation: 'Position as the comprehensive AI conscience — monitoring the monitors'}"
```

### theme-factory (Branded Reports)

```yaml
skill:
  name: "theme-factory"
  description: "Apply GAI-OBSERVE visual themes (colors, fonts, spacing) to D6 reports, dashboards, and presentations for consistent branding"
  owner: "D6 The Model Guardian (adapted from D8/D3/G4)"
  trigger: "report_generation OR dashboard_creation OR presentation_export"
  input:
    schema: "ThemeApplyRequest"
    fields:
      content: "object (report, dashboard, or presentation data)"
      theme: "enum[gai-observe-dark, gai-observe-light, governance-signal, editorial, advisory]"
      output_format: "enum[pdf, html, pptx, png]"
      brand_elements: "object {logo, wordmark, accent_color, typography}"
  output:
    schema: "ThemeApplyResponse"
    fields:
      themed_uri: "string"
      theme_applied: "boolean"
      token_audit: "object (verified tokens used)"
      accessibility_score: "float"
  procedure:
    - "Validate content structure against output format requirements"
    - "Map theme to GAI-OBSERVE CSS token set (colors, typography, spacing)"
    - "Apply brand elements (logo, wordmark, accent)"
    - "Run accessibility audit (contrast ratios, alt text)"
    - "Export to requested format with embedded theme"
  quality_gates:
    - "Token compliance: all visual values from approved token set"
    - "Accessibility: WCAG 2.1 AA contrast ratios"
    - "Brand consistency: logo, wordmark, accent colors correct"
    - "Format validity: output file passes format validation"
  error_handling:
    on_invalid_content: "return error with required content schema"
    on_theme_unavailable: "fallback to default GAI-OBSERVE dark theme"
    on_accessibility_fail: "flag for manual review with accessibility report"
  evidence:
    - "Themed output file"
    - "Token audit log"
    - "Accessibility report"
  example:
    request: "{content: {type: 'drift_report', data: {...}}, theme: 'governance-signal', output_format: 'pdf', brand_elements: {logo: 'gai-observe-logo.png', accent_color: '#coral-amber'}}"
    response: "{themed_uri: 's3://d6-reports/drift-uuid/drift_report_branded.pdf', theme_applied: true, token_audit: {colors_verified: 12, fonts_verified: 3}, accessibility_score: 0.98}"
```

---

## 3. Skill-to-Arm Mapping

| Skill | ARM-01 | ARM-02 | ARM-03 | ARM-04 | ARM-05 | ARM-06 | Primary Use |
|-------|--------|--------|--------|--------|--------|--------|-------------|
| stock-assistant | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | Metric monitoring, trend alerts |
| seaborn-visualization | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | Charts, plots, dashboards |
| xlsx | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | Excel exports, formula analysis |
| report-writing | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Comprehensive reports |
| deep-research-swarm | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ML research, method evaluation |
| kimi-data-tools-v2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Benchmark research, regulatory updates |
| swarm-coding | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Pipeline generation, test suites |
| skill-creator | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Procedure authoring |
| competitor-analysis | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | Competitive positioning |
| theme-factory | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | Branded reports, presentations |

---

**Document Owner:** GAI-OBSERVE Advisory Architecture Team  
**Next Review:** 2026-07-28  
**Classification:** Internal — Skill Registry
