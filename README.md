# FortyGuard Product Evaluation

## Project Overview

This repository contains a technical evaluation of the FortyGuard platform, focusing on its Dashboard, REST API, and Model Context Protocol (MCP) interface.

The evaluation examines:
- API functionality and geographic coverage.
- Heatmap generation and returned geospatial data.
- Spatial coverage and tile geometry.
- Environmental parameter retrieval.
- MCP tool discovery and selected tool operations.
- Dashboard functionality and Heat Intelligence report quality.
- Credit consumption and unresolved execution issues.

## Evaluation Report

The main evaluation document is:

- `evaluation_notes.md` ? Detailed findings, test procedures, observations, recommendations, and limitations.

## Repository Contents

### Main Python Scripts

The repository includes scripts for:
- API setup and execution (`main.py`).
- MCP connection and tool discovery (`mcp_client.py`).
- Credit balance and activity status checks (`check_balance.py`, `check_status.py`).
- Heatmap and temperature analysis.
- Spatial validation, tile geometry checks, and uncovered-area analysis.
- Spatial visualization and diagnostic analysis.

### Data and Evidence

- JSON files contain selected API responses and test outputs.
- CSV files contain extracted tile and spatial-validation results.
- PNG files contain spatial analysis visualizations.
- `mcp_tool_schemas.json` contains the discovered MCP tool schemas.
- Analysis and recovery folders contain supporting intermediate results.

## Key Results

- Heatmap generation completed successfully for the tested West Virginia location.
- The successful heatmap response contained 81 GeoJSON features.
- All 81 returned tiles reported a temperature of 34.76?C.
- Spatial validation measured 82.664% coverage of the original area of interest.
- Two New York heatmap requests returned `OUT_OF_COVERAGE`.
- MCP discovery identified 11 available tools.
- The `env_params` MCP request completed successfully and returned 24 hourly records.
- A Heat Intelligence report was generated successfully through the Dashboard.
- A Satellite MCP request resulted in a client-side missing-response error and an observed deduction of 14,400 Credits. Backend execution remains unconfirmed and requires Support investigation.

See `evaluation_notes.md` for the full evidence and interpretation.

## Important Limitations

- Geographic testing covered a limited number of locations.
- The spatial coverage discrepancy has not been confirmed as an API defect.
- Identical heatmap temperature values require further investigation.
- Not all discovered MCP tools were independently tested.
- The Satellite request remains inconclusive.
- Some Dashboard report values could not be independently verified against their underlying sources.

Untested tools are not classified as successful or defective.

## Security

- Do not share the `.env` file or expose API keys.
- Do not include credentials in screenshots, logs, or submitted evidence.
- The local virtual environment (`venv`) is not required as part of the evaluation report.
- Review `.gitignore` before publishing or sharing the repository.

## Reproducibility

The Python scripts and supporting data are included for reference. Execution may require installing the relevant dependencies and configuring valid FortyGuard credentials locally.

No API credentials are included in this repository documentation.
