# Extraction Evaluation System

This evaluation system measures the accuracy, precision, recall, and F1 score of the document extraction pipeline for the following 9 fields:

1. Bill of lading number
2. Container Number
3. Consignee Name
4. Consignee Address
5. Date of export
6. Date
7. Line Items Count
8. Average Gross Weight
9. Average Price

## Setup

### 1. Prepare Ground Truth Data

Create a JSON file containing the expected values for each test document. The format is:

```json
{
  "doc_id": {
    "filename": "document_filename.pdf",
    "fields": {
      "Bill of lading number": "expected_value",
      "Container Number": "expected_value",
      ...
    }
  }
}
```

See `ground_truth_example.json` for a complete example.

### 2. Prepare Test Documents

Place all test documents in a single directory (e.g., `test_documents/`). The filenames in your ground truth JSON must match the actual filenames.

## Running the Evaluation

```bash
python run_evaluation.py <ground_truth.json> <test_docs_directory>
```

### Example

```bash
python run_evaluation.py ground_truth_example.json ../testDocs
```

## Metrics Explained

### Per-Field Metrics

For each of the 9 fields, the evaluator calculates:

- **Accuracy**: (TP + TN) / (TP + TN + FP + FN)
- **Precision**: TP / (TP + FP) - Of all fields extracted, how many were correct?
- **Recall**: TP / (TP + FN) - Of all fields that should be extracted, how many were found?
- **F1 Score**: 2 × (Precision × Recall) / (Precision + Recall) - Harmonic mean of precision and recall

Where:
- **TP (True Positive)**: Field correctly extracted with correct value
- **FP (False Positive)**: Field extracted with incorrect value
- **FN (False Negative)**: Field missing or empty when it should have a value
- **TN (True Negative)**: Field correctly identified as not present

### Overall Metrics

Aggregates metrics across all fields and documents to provide system-wide performance.

## Output

The script produces two outputs:

1. **Console Output**: Formatted summary of overall and per-field metrics
2. **JSON File**: Detailed results saved to `evaluation_results.json`

### Sample Output

```
================================================================================
EVALUATION RESULTS
================================================================================

OVERALL METRICS:
--------------------------------------------------------------------------------
Accuracy:  87.50%
Precision: 85.00%
Recall:    89.47%
F1 Score:  87.18%
Total Fields Evaluated: 18

PER-FIELD METRICS:
--------------------------------------------------------------------------------

Bill of lading number:
  Accuracy:  100.00%
  Precision: 100.00%
  Recall:    100.00%
  F1 Score:  100.00%
  TP: 1, FP: 0, FN: 0, TN: 1

Container Number:
  Accuracy:  100.00%
  Precision: 100.00%
  Recall:    100.00%
  F1 Score:  100.00%
  TP: 1, FP: 0, FN: 0, TN: 1
...
```

## Customization

### Adding More Fields

Edit the `FIELDS` list in `run_evaluation.py`:

```python
FIELDS = [
    "Bill of lading number",
    "Container Number",
    ...
    "Your New Field"
]
```

### Adjusting Value Matching

The `_values_match()` method normalizes and compares values. Modify this method to:
- Handle fuzzy matching
- Ignore whitespace/formatting differences
- Apply custom comparison logic for specific fields

### API Key

Ensure your `.env` file in the project root contains:

```
OPENAI_API_KEY=your_api_key_here
```

## Troubleshooting

### Document Processing Errors

If a document fails to process, the error will be logged and the evaluator will continue with remaining documents.

### Empty Extractions

If all extractions are empty, verify:
1. API key is set correctly
2. Documents are in the correct format
3. LLM service is functioning properly

### Field Name Mismatches

Ensure field names in ground truth JSON exactly match the field names in the `FIELDS` list.

