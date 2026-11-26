# FortyGuard Product Evaluation


## Executive Summary

### Evaluation Overview

This evaluation examined the FortyGuard platform through its Dashboard, REST API, and MCP interface. The assessment focused on functionality, geographic coverage, data quality, tool accessibility, and credit usage.

### Key Findings

**1. REST API and Heatmap**
- Heatmap generation was successfully completed for a test location in West Virginia.
- The successful response contained 81 GeoJSON features, with all returned tiles reporting a temperature of 34.76°C.
- Two New York heatmap requests returned HTTP 400 with an `OUT_OF_COVERAGE` error.
- Spatial validation of the West Virginia result showed 82.664% coverage of the original area of interest. The remaining uncovered area was concentrated near the southern boundary and requires clarification of the expected tile-coverage behavior.

**2. MCP Functionality**
- MCP connection and tool discovery were successful; 11 tools were identified.
- `credit_balance`, `heatmap_read`, `env_params`, and selected monitoring operations were tested.
- The environmental parameters request returned 24 hourly records and completed successfully.
- Several tools were reviewed through their schemas but were not executed. Their status is documented in the relevant sections.

**3. Dashboard**
- Dashboard functionality was explored, including saving a heatmap tile capture to the Gallery.
- A Heat Intelligence report was generated successfully through the Dashboard.
- The report provided geographic and environmental analysis, although some values lacked sufficient methodological or source traceability.

**4. Satellite MCP Issue**
- A Satellite MCP request was attempted for the West Virginia test location.
- The client received an `SSE stream ended without a response` error.
- No activity ID, segmentation result, or corresponding Dashboard history record was obtained.
- However, the credit balance decreased by 14,400 Credits.
- The backend execution status remains unconfirmed. This is documented as an unresolved execution and billing discrepancy, and the request should not be repeated until Support investigates it.

### Credit Usage

- Latest verified balance after the Satellite request: **974,260 Credits**.
- Environmental parameters request: 2,900 Credits.
- Satellite request: 14,400 Credits deducted despite no result being returned to the client.
- Other operation costs and historical balances are documented in the relevant test sections.

### Overall Assessment

The evaluation confirmed successful heatmap generation in the tested West Virginia area, successful retrieval of environmental parameters through MCP, and successful Dashboard report generation. It also identified geographic coverage limitations, incomplete spatial coverage within the tested AOI, data-traceability concerns, and an unresolved Satellite credit deduction.

The results demonstrate that several core workflows are operational in the tested scenarios. However, further clarification from FortyGuard Support is required regarding the Satellite request and its associated credit deduction. Untested tools and inconclusive results are explicitly identified throughout this report.


## 1. Account Setup

- Dashboard login: Successful
- Password change: Not located
- API key regeneration: Not located

## 2. Usage Limits

- Daily heatmap usage limit observed: 30 requests per day

## 3. API Testing

### Test 1: Heatmap API – Documentation Example

- Endpoint: `POST /v1/heatmap`
- Authentication header: `api-key`
- Test coordinates: New York City (official documentation example)
- Test date: 2026-11-19
- HTTP Status: 400
- Error code: `OUT_OF_COVERAGE`
- Result: Request rejected due to coverage validation.
- Observation: The documented NYC coordinates were rejected despite being used exactly as provided.
- Activity ID: Not returned.

### Test 2: Heatmap API – Original Documentation Date

- Endpoint: `POST /v1/heatmap`
- Test coordinates: New York City (official documentation example)
- Test date: 2024-07-15
- HTTP Status: 400
- Error code: `OUT_OF_COVERAGE`
- Error field: `polygon_aoi`
- Result: Same coverage error as Test 1.
- Observation: Changing the requested date did not resolve the coverage error.
- Activity ID: Not returned.

### Current Findings

- The API returned a structured error response.
- The error identifies the affected field and provides an error code.
- The documented example did not work with either tested date.
- Successful heatmap generation was verified using a supported West Virginia location.

### Test 3: Successful Heatmap Submission – West Virginia

- Endpoint: `POST /v1/heatmap`
- HTTP Status: 200
- Message: Heatmap Submitted Successfully
- Coordinates: 38.359224, -81.623467
- Date: 2024-07-15
- Activity ID: Returned successfully inside `data.activity_id`
- Result: Heatmap task submitted successfully.
- Observation: The API returns `activity_id` as a nested field inside `data`.
- Next step: Check asynchronous task status.

### Test 4: Successful Heatmap Generation – West Virginia

- Endpoint: `POST /v1/heatmap`
- HTTP Status: 200
- Submission: Successful
- Geographic coordinates: 38.359224, -81.623467
- Date: 2024-07-15
- Granularity: 100
- Output format: GeoJSON FeatureCollection
- Number of returned tiles: 81
- Temperature mean: 34.76°C
- Temperature minimum: 34.76°C
- Temperature maximum: 34.76°C
- Standard deviation: 0.0°C
- Temperature frequency: 81 tiles with an observed temperature of 34.76°C (approximately 35.0°C when rounded).

### API Data Quality Observations

- The API returned spatial polygon features with temperature attributes.
- Temperature statistics were included in the response.
- All observed tile temperatures were identical.
- Further testing is needed to determine whether this is expected behavior or a limitation of the selected parameters.

## 4. Data Quality

### 4.1 West Virginia – Spatial Coverage Validation

**Status: Observed coverage discrepancy – API contract verification required.**

The original West Virginia AOI was analyzed against the 81 polygons returned by the FortyGuard Heatmap API.

The spatial validation produced the following results:

- AOI area: 969,421.979 m².
- Number of returned polygons: 81.
- AOI coverage: 82.664%.
- Uncovered area: 168,058.871 m² (17.336%).
- The uncovered geometry contains one significant boundary-connected component.
- The uncovered area is concentrated along the southern AOI boundary.
- The tile grid extends approximately 6.587 m beyond the northern boundary, 1.643 m beyond the western boundary, and 30.369 m beyond the eastern boundary.
- The southernmost tile boundary starts approximately 192.362 m north of the AOI's southern boundary.
- The uncovered area shares approximately 873.705 m of boundary with the AOI boundary.

**Conclusion:**

The returned heatmap polygons do not cover the entire original AOI. The uncovered area is predominantly a southern boundary gap, rather than a significant isolated internal gap.

This is a confirmed spatial coverage observation, but not yet a confirmed API defect. Further verification of the API's expected AOI coverage behavior and tile-generation rules is required.

### 4.2 Temperature Consistency

- All 81 returned West Virginia tiles contained the same observed temperature value: 34.76°C.
- The calculated standard deviation was 0.0°C.
- This indicates no temperature variation across the returned tiles in this test.
- Further testing with different locations, dates, and parameters is required to determine whether this behavior is expected.

## 5. MCP Testing

### 5.1 MCP Connection and Discovery

- MCP connection: Successful
- MCP endpoint: `https://tos-mcp.app.fortyguard.com/mcp`
- MCP SDK version: 2.3.0
- Number of discovered tools: 11

Available tools:

1. `credit_balance`
2. `env_params`
3. `heatmap`
4. `heatmap_read`
5. `monitoring`
6. `report`
7. `report_read`
8. `satellite`
9. `streetview`
10. `temperature_routing`
11. `temperature_routing_read`

### 5.2 Credit Balance Test

- Tool: `credit_balance`
- Test status: Successful
- Available credits returned: 991,560 (historical balance at the time of this test)
- Execution cost: 0 credits
- Latest verified balance after subsequent tests: 974,260 Credits

**Observation:** The MCP credit balance operation successfully returned the available account credits without deducting credits.

### 5.3 Heatmap Read Test

- Tool: `heatmap_read`
- Test status: Successful
- Plan: Premium
- Existing heatmap: West Virginia (WV)
- Activity ID: `d217d8b4-bf08-41f6-83ca-67975221d616`
- Returned status: `completed`
- Minimum temperature: 34.76°C
- Maximum temperature: 34.76°C
- Mean temperature: 34.76°C
- Standard deviation: 0.0°C
- Actual execution cost: 0 credits
- Data modification: None; the operation reads existing heatmap statistics.

**Observation:** The tool successfully retrieved persisted temperature statistics from an existing heatmap without creating or modifying heatmap data.

### 5.4 Monitoring Tool Test

- Tool: `monitoring`

**Operation: `list_monitors`**

- Status: Successful
- Returned monitors: 0
- Execution cost: 0 credits

**Operation: `list_alerts`**

- Status: Failed
- Error category: `invalid_input`
- Error message: The request input is invalid.
- Tested with: `limit: 10`
- Execution cost: No credits deducted

**Observation:** The `list_monitors` operation works successfully. However, `list_alerts` returns an input validation error even though the operation is listed in the tool schema and the request includes a valid limit. No monitors were found in the account, which may be relevant to this behavior. The exact cause remains unconfirmed.

## 6. Dashboard Evaluation

### 6.1 General Dashboard Functionality

- Dashboard login: Successful
- Daily heatmap usage limit observed: 30 requests per day
- Password change option: Not located
- API key regeneration option: Not located
- Tile capture action: Available and tested
- Tile capture confirmation: Successfully displayed
- Captured tile data: Added to the Gallery

### 6.2 Heat Intelligence Report Generation

- Report generation through Dashboard: Successful
- Report creation confirmation: "Heat Intelligence report created successfully"
- Report content retrieval and inspection: Successful
- Report Activity ID (`analytics_id`): Not located
- Report generation workflow: Successfully tested through the Dashboard

### 6.3 Analysis Coverage

The generated Heat Intelligence report provided two major analytical categories.

**Geographic Information**

- General location and geographic classification
- Terrain and elevation
- Proximity to water bodies
- Green spaces and vegetation
- Land cover and surface materials
- Building density and height
- Shadow coverage
- Urban geometry and street canyon effects

**Environmental Factors**

- Air quality and atmospheric opacity
- Climate classification and historical weather
- Climate trends and projections
- Soil moisture and permeability
- Surface heat retention
- Humidity levels
- Solar radiation
- Nighttime cooling rates
- Thermal comfort
- Seasonal Urban Heat Island variability

### 6.4 Report Quality Assessment

**Strengths**

- Broad geographic and environmental analysis.
- Well-organized report structure.
- Relevant explanations of how geographic and urban characteristics affect temperature.
- Consideration of multiple interacting environmental factors.
- Useful contextual information for understanding urban heat behavior.

**Limitations**

- Some reported values appear to be estimates rather than directly measured data.
- Estimated metrics, including Sky View Factor, urban-rural temperature differences, vegetation coverage, and surface cooling effects, lack clearly demonstrated measurement methodologies.
- General geographic knowledge is mixed with date-specific weather observations and assumptions.
- Sources are often identified by name without direct links or precise dataset references.
- Some numerical conclusions require independent verification.
- The report does not consistently distinguish measured, modeled, estimated, and inferred values.

### 6.5 Overall Dashboard Assessment

The Dashboard successfully supported tile capture and Heat Intelligence report generation. The Heat Intelligence feature produced a comprehensive, structured report combining geographic and environmental context.

The main improvement opportunity is transparency regarding data sources, calculation methods, and the distinction between measured values and model-generated estimates.

The report activity identifier was not located, so the corresponding MCP `report_read` workflow could not be tested.

## 7. Recommendations

1. Verify the official geographic coverage boundaries and ensure documentation examples use supported locations.
2. Clarify the expected AOI coverage behavior and tile-generation rules.
3. Investigate why all returned temperature values were identical in the West Virginia test.
4. Investigate the `list_alerts` input validation error.
5. Improve API documentation with verified working examples and clearer coverage requirements.
6. Improve Heat Intelligence report transparency by providing traceable sources, calculation methodologies, and clear labeling of measured versus estimated results.
7. Provide easier access to activity identifiers for generated reports and other asynchronous tasks.
8. Prioritize further MCP testing based on business value, confirmed input requirements, and verified operation costs. Avoid unnecessary paid requests.
9. Ask FortyGuard Support to investigate the Satellite MCP request, verify its backend execution status, and review the 14,400-Credit deduction. Request restoration if the operation did not complete successfully.

## 8. Evaluation Limitations

- Geographic coverage tests were conducted using a limited number of locations.
- Temperature consistency was evaluated using one successful West Virginia heatmap dataset.
- The observed spatial coverage discrepancy has not yet been confirmed as an API defect.
- The cause of the `list_alerts` validation error remains unknown.
- Not all MCP tools have been tested.
- Paid MCP operations were executed for env_params (2,900 credits) and satellite (14,400 credits). The Satellite request has an unresolved result and billing discrepancy.
- The Heat Intelligence report was reviewed through the Dashboard, but its activity identifier was not obtained.
- Some report values and conclusions could not be independently verified against their underlying data sources.
- The evaluation reflects the features, responses, and behavior observed during the testing period.
- The latest verified account balance recorded during testing was 974,260 Credits after the Satellite request. This is a historical test observation, not a confirmation of the current balance at submission time.

## 9. Environmental Parameters Testing (MCP)

### 9.1 Test Execution
- Tool: `env_params`
- MCP connection: Successful
- Test status: Completed successfully
- Location: Charleston, West Virginia
- Latitude: 38.359224
- Longitude: -81.623467
- Test date: 2024-07-15
- Reference temperature: 28.1°C
- Date filter: Full day (filter_type = 3)
- Returned hourly intervals: 24
- Activity ID: `b3ba03fd-6b3b-4aab-b3ec-aeddf7a6e0bf`

### 9.2 Credit Usage
- Balance before: 991,560 Credits
- Balance after: 988,660 Credits
- Actual cost: 2,900 Credits
- Expected cost: 2,900 Credits
- Cost verification: Exact match
- Operation status: Success

### 9.3 Returned Environmental Parameters

| Parameter | Value |
|---|---:|
| Apparent temperature | 24.8°C |
| Relative humidity | 73.6% |
| Precipitation | 0.0 mm |
| Cloud cover | 0 octas |
| Wet bulb temperature | 19.5°C |
| Elevation | 186 m |
| AQI | 78.6 |

The primary parameter values are based on the first hourly snapshot at 00:00 local time.

### 9.4 Hourly Data Availability

The response included 24 hourly values for:
- Heat index
- Apparent temperature
- Relative humidity
- Precipitation
- Cloud cover
- Wet bulb temperature
- Air-quality-related indices
- CO and O3-related indices

Methane (ppb) and CO2 (ppm) returned null values for all 24 hourly records.

### 9.5 Observations

- MCP connection and session initialization were successful after correcting stream handling.
- The env_params operation completed without a tool error.
- The response provided hourly environmental data for a full day.
- The primary values represent the first hourly snapshot rather than daily averages.
- Solar irradiance values were provided as modeled clear-sky estimates.
- Some atmospheric fields were unavailable and returned null values.
- The actual credit deduction exactly matched the documented expected cost of 2,900 Credits.

### 9.6 Activity Reference

- Activity ID: `b3ba03fd-6b3b-4aab-b3ec-aeddf7a6e0bf`
- Trace ID: `a9dd6fb1c656`

## 10. Satellite MCP Testing

### 10.1 Test Execution

- Tool: `satellite`
- Interface: MCP
- MCP connection: Successful
- Test location: Charleston, West Virginia, USA
- Latitude: 38.359224
- Longitude: -81.623467
- Requested imagery date: 2024-07-15
- Granularity: 100 meters
- Date filter: Single day (filter_type = 3)

### 10.2 Execution Result

- Client-side result: Error
- Error: `MCPError: SSE stream ended without a response`
- Activity ID: Not returned
- Segmentation result: Not received
- Dashboard Satellite view: No segmentations displayed
- Satellite history: No corresponding activity record found

### 10.3 Credit Usage

- Balance before request: 988,660 Credits
- Balance after request: 974,260 Credits
- Actual deduction: 14,400 Credits
- Deduction matched the documented Satellite operation cost.

### 10.4 Observations

- The MCP connection and session initialization succeeded before the Satellite tool call.
- The client did not receive a normal tool response.
- The account balance decreased by 14,400 Credits.
- No segmentation result or corresponding activity record was visible in the Dashboard.
- No activity identifier was returned to the client.
- The backend execution status could not be independently confirmed.

### 10.5 Assessment and Follow-up

This test revealed an unresolved execution and billing discrepancy: credits were deducted, but no result or activity record was made available to the evaluator.

The available evidence does not establish whether the backend processing completed, failed, or partially executed.

The request should not be repeated until FortyGuard Support investigates the transaction.

A support request should ask FortyGuard to:
1. Confirm the backend execution status.
2. Provide the activity/request ID and result if processing completed.
3. Restore the 14,400 credits if the request did not complete successfully.

**Evaluation status: Inconclusive due to missing response and activity record.**


## 11. Remaining MCP Tools – Schema Review

The input schemas and descriptions of the remaining MCP tools were reviewed to identify safe opportunities for further testing.

### 11.1 Report Read

- Tool: `report_read`
- Purpose: Retrieve an existing completed Heat Intelligence report.
- Required input: `analytics_id`
- Dashboard report activity identifier: Not located.
- Test status: Not executed.
- Reason: No confirmed analytics/activity identifier was available.
- Cost: Not independently verified; no request was made.

### 11.2 Temperature Routing Read

- Tool: `temperature_routing_read`
- Purpose: Retrieve an existing temperature-aware routing activity.
- Required input: `activity_id`
- Existing routing activity ID: Not available.
- Test status: Not executed.
- Reason: No previous routing activity was available to retrieve.
- Cost: Not independently verified; no request was made.

### 11.3 Report Generation

- Tool: `report`
- Purpose: Submit a new Heat Intelligence report for a geographic point and date.
- Required inputs include latitude, longitude, temperature in Fahrenheit, date, and one or more analysis categories.
- Premium plan cost stated in the tool description: 8,600 Credits.
- Test status: Not executed through MCP.
- Reason: A new paid report would consume additional credits, while Dashboard report generation had already been tested successfully.

### 11.4 Temperature Routing

- Tool: `temperature_routing`
- Purpose: Generate temperature-aware driving routes between two coordinate locations.
- Required inputs: Origin, destination, and departure time.
- Stated cost: 3,500 Credits.
- Geographic coverage: Contiguous United States.
- Test status: Not executed.
- Reason: The operation creates a new paid activity and was not essential to the minimum evaluation deliverable.

### 11.5 Remaining Tool Coverage

The following tools were discovered through MCP but were not independently tested during this evaluation:

- `streetview`
- `temperature_routing`
- `temperature_routing_read`
- `report`
- `report_read`

The Satellite tool was attempted, but its result remains inconclusive due to the missing response and activity record.

Tool discovery confirms that these tools are exposed through the MCP interface; it does not establish that their full functionality was successfully tested.

### 11.6 Testing Decision

Further paid requests were limited to avoid unnecessary credit consumption and to prioritize the completion of the evaluation deliverable.

Unexecuted tools are explicitly identified as untested rather than being treated as successful or defective.
