import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.document_processor import DocumentProcessor
from app.services.llm_service import LLMService


class ExtractionEvaluator:
    
    FIELDS = [
        "Bill of lading number",
        "Container Number",
        "Consignee Name",
        "Consignee Address",
        "Date of export",
        "Date",
        "Line Items Count",
        "Average Gross Weight",
        "Average Price"
    ]
    
    def __init__(self, ground_truth_path: str):
        self.ground_truth = self._load_ground_truth(ground_truth_path)
        self.llm_service = LLMService()
        self.doc_processor = DocumentProcessor(self.llm_service)
    
    def _load_ground_truth(self, path: str) -> Dict[str, Dict[str, Any]]:
        with open(path, 'r') as f:
            return json.load(f)
    
    def _normalize_value(self, value: Any) -> str:
        if value is None or value == "":
            return ""
        return str(value).strip().lower()
    
    def _values_match(self, extracted: Any, expected: Any) -> bool:
        norm_extracted = self._normalize_value(extracted)
        norm_expected = self._normalize_value(expected)
        
        if not norm_expected:
            return not norm_extracted
        
        if not norm_extracted:
            return False
        
        return norm_extracted == norm_expected
    
    def evaluate_single_document(self, doc_path: str, expected: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
        file_path = Path(doc_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        extracted_result = self.doc_processor.process_document(
            file_content=file_content,
            filename=file_path.name,
            fields_to_extract=self.FIELDS
        )
        
        extracted_data = extracted_result.get('extracted_data', {})
        
        results = {}
        for field in self.FIELDS:
            extracted_value = extracted_data.get(field)
            expected_value = expected.get(field)
            
            match = self._values_match(extracted_value, expected_value)
            has_expected = self._normalize_value(expected_value) != ""
            has_extracted = self._normalize_value(extracted_value) != ""
            
            if match:
                if has_expected:
                    results[field] = {'TP': 1, 'FP': 0, 'FN': 0, 'TN': 0}
                else:
                    results[field] = {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 1}
            else:
                if has_expected and has_extracted:
                    results[field] = {'TP': 0, 'FP': 1, 'FN': 1, 'TN': 0}
                elif has_expected and not has_extracted:
                    results[field] = {'TP': 0, 'FP': 0, 'FN': 1, 'TN': 0}
                elif not has_expected and has_extracted:
                    results[field] = {'TP': 0, 'FP': 1, 'FN': 0, 'TN': 0}
                else:
                    results[field] = {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 1}
        
        return results
    
    def evaluate_all(self, test_docs_dir: str) -> Dict[str, Any]:
        field_metrics = defaultdict(lambda: {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 0})
        document_results = {}
        
        for doc_id, doc_info in self.ground_truth.items():
            doc_path = os.path.join(test_docs_dir, doc_info['filename'])
            expected_fields = doc_info['fields']
            
            print(f"Evaluating: {doc_info['filename']}")
            
            try:
                doc_results = self.evaluate_single_document(doc_path, expected_fields)
                document_results[doc_id] = {
                    'filename': doc_info['filename'],
                    'field_results': doc_results
                }
                
                for field, metrics in doc_results.items():
                    for metric_name, value in metrics.items():
                        field_metrics[field][metric_name] += value
                        
            except Exception as e:
                print(f"Error evaluating {doc_info['filename']}: {e}")
                document_results[doc_id] = {
                    'filename': doc_info['filename'],
                    'error': str(e)
                }
        
        return self._calculate_metrics(field_metrics, document_results)
    
    def _calculate_metrics(self, field_metrics: Dict, document_results: Dict) -> Dict[str, Any]:
        results = {
            'per_field_metrics': {},
            'overall_metrics': {},
            'document_results': document_results
        }
        
        overall_tp = 0
        overall_fp = 0
        overall_fn = 0
        overall_tn = 0
        
        for field, metrics in field_metrics.items():
            tp = metrics['TP']
            fp = metrics['FP']
            fn = metrics['FN']
            tn = metrics['TN']
            
            overall_tp += tp
            overall_fp += fp
            overall_fn += fn
            overall_tn += tn
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0
            
            results['per_field_metrics'][field] = {
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1': round(f1, 4),
                'accuracy': round(accuracy, 4),
                'true_positives': tp,
                'false_positives': fp,
                'false_negatives': fn,
                'true_negatives': tn
            }
        
        overall_precision = overall_tp / (overall_tp + overall_fp) if (overall_tp + overall_fp) > 0 else 0.0
        overall_recall = overall_tp / (overall_tp + overall_fn) if (overall_tp + overall_fn) > 0 else 0.0
        overall_f1 = 2 * (overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0
        overall_accuracy = (overall_tp + overall_tn) / (overall_tp + overall_tn + overall_fp + overall_fn) if (overall_tp + overall_tn + overall_fp + overall_fn) > 0 else 0.0
        
        results['overall_metrics'] = {
            'precision': round(overall_precision, 4),
            'recall': round(overall_recall, 4),
            'f1': round(overall_f1, 4),
            'accuracy': round(overall_accuracy, 4),
            'total_fields_evaluated': overall_tp + overall_fp + overall_fn + overall_tn
        }
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        print("\n" + "="*80)
        print("EVALUATION RESULTS")
        print("="*80)
        
        print("\nOVERALL METRICS:")
        print("-" * 80)
        overall = results['overall_metrics']
        print(f"Accuracy:  {overall['accuracy']:.2%}")
        print(f"Precision: {overall['precision']:.2%}")
        print(f"Recall:    {overall['recall']:.2%}")
        print(f"F1 Score:  {overall['f1']:.2%}")
        print(f"Total Fields Evaluated: {overall['total_fields_evaluated']}")
        
        print("\nPER-FIELD METRICS:")
        print("-" * 80)
        for field, metrics in results['per_field_metrics'].items():
            print(f"\n{field}:")
            print(f"  Accuracy:  {metrics['accuracy']:.2%}")
            print(f"  Precision: {metrics['precision']:.2%}")
            print(f"  Recall:    {metrics['recall']:.2%}")
            print(f"  F1 Score:  {metrics['f1']:.2%}")
            print(f"  TP: {metrics['true_positives']}, FP: {metrics['false_positives']}, "
                  f"FN: {metrics['false_negatives']}, TN: {metrics['true_negatives']}")
        
        print("\n" + "="*80)


def main():
    if len(sys.argv) < 3:
        print("Usage: python run_evaluation.py <ground_truth.json> <test_docs_directory>")
        print("\nExample: python run_evaluation.py ground_truth.json ../testDocs")
        sys.exit(1)
    
    ground_truth_path = sys.argv[1]
    test_docs_dir = sys.argv[2]
    
    if not os.path.exists(ground_truth_path):
        print(f"Error: Ground truth file not found: {ground_truth_path}")
        sys.exit(1)
    
    if not os.path.isdir(test_docs_dir):
        print(f"Error: Test documents directory not found: {test_docs_dir}")
        sys.exit(1)
    
    evaluator = ExtractionEvaluator(ground_truth_path)
    results = evaluator.evaluate_all(test_docs_dir)
    
    evaluator.print_results(results)
    
    output_path = "evaluation_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    main()

