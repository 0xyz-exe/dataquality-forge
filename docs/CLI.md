# DataQuality Forge CLI Reference

The CLI runs standalone without requiring the web server.

## Installation

```bash
pip install -e .
```

## Commands

### Version
```bash
dataquality version
```

### Dataset Inspection
```bash
dataquality inspect ./examples/customers.csv
```

### Dataset Profiling
```bash
dataquality profile ./examples/customers.csv
# JSON Output:
dataquality profile ./examples/customers.csv --json
```

### Validation Execution
```bash
dataquality validate ./examples/customers.csv --rules ./examples/rules_customers.json
# Export HTML report:
dataquality validate ./examples/customers.csv --rules ./examples/rules_customers.json --export-html report.html
```

### Exit Codes
- `0`: Validation passed with 0 blocking failures.
- `1`: Execution error / unexpected exception.
- `2`: Invalid configuration or file not found.
- `3`: Validation completed with failing ERROR or CRITICAL rules.
