#!/usr/bin/env python3
"""
PII Model Evaluation Script
Comprehensively evaluates the PII detection model for accuracy
"""

import os
import json
import time
import argparse
import subprocess
import re
from typing import List, Dict, Any, Tuple

class PIIModelEvaluator:
    """Evaluates PII detection model performance"""
    
    def __init__(self, model_name: str = "pii-detector-enhanced"):
        self.model_name = model_name
        self.evaluation_dir = "evaluation"
        self.results_file = os.path.join(self.evaluation_dir, "evaluation_results.json")
        
        # Create evaluation directory if it doesn't exist
        os.makedirs(self.evaluation_dir, exist_ok=True)
        
        # PII types we expect to detect
        self.pii_types = [
            "name", "email", "phone", "address", "credit_card", 
            "date", "ssn", "drivers_license", "ip_address"
        ]
        
        # PII pattern detection for evaluation
        self.pii_patterns = {
            "name": r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            "ssn": r'\d{3}-\d{2}-\d{4}|\d{9}',
            "credit_card": r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}',
            "date": r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            "address": r'\d+ [A-Za-z]+ (?:St|Street|Ave|Avenue|Rd|Road), [A-Za-z]+, [A-Z]{2} \d{5}',
            "ip_address": r'(?:\d{1,3}\.){3}\d{1,3}'
        }
        
    def load_test_cases(self) -> List[str]:
        """Load test cases from file"""
        test_cases_file = os.path.join(self.evaluation_dir, "test_cases.json")
        
        # Check if test cases file exists
        if not os.path.exists(test_cases_file):
            # Create default test cases if file doesn't exist
            default_test_cases = [
                "My name is John Smith and my email is john.smith@example.com.",
                "Please contact Jane Doe at (555) 123-4567 or jane.doe@company.com.",
                "Patient: Michael Johnson, DOB: 05/12/1985, SSN: 123-45-6789",
                "Credit card: 4111-1111-1111-1111, Expiration: 12/25",
                "Address: 123 Main Street, Anytown, CA 90210",
                "Server IP: 192.168.1.1, Administrator: admin@server.com"
            ]
            
            with open(test_cases_file, "w") as f:
                json.dump({"test_cases": default_test_cases}, f, indent=2)
            
            return default_test_cases
        
        # Load test cases from file
        with open(test_cases_file, "r") as f:
            data = json.load(f)
            return data.get("test_cases", [])
    
    def evaluate_model(self) -> Dict[str, Any]:
        """Evaluate the model's PII detection performance"""
        test_cases = self.load_test_cases()
        results = {
            "model": self.model_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_cases": [],
            "summary": {}
        }
        
        print(f"Evaluating model: {self.model_name}")
        print(f"Running {len(test_cases)} test cases...")
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest case {i+1}/{len(test_cases)}")
            print(f"Input: {test_case}")
            
            # Run the model on the test case
            model_output, execution_time = self._run_model(test_case)
            
            if model_output:
                print(f"Output: {model_output}")
                
                # Analyze the results
                expected_pii = self._identify_expected_pii(test_case)
                detected_pii = self._analyze_redactions(model_output)
                
                # Calculate metrics
                metrics = self._calculate_metrics(expected_pii, detected_pii)
                
                # Store results
                case_result = {
                    "input": test_case,
                    "output": model_output,
                    "expected_pii": expected_pii,
                    "detected_pii": detected_pii,
                    "metrics": metrics,
                    "execution_time": execution_time
                }
                
                results["test_cases"].append(case_result)
                print(f"Metrics: {json.dumps(metrics, indent=2)}")
            else:
                print("Error: Failed to get model output")
                results["test_cases"].append({
                    "input": test_case,
                    "error": "Failed to get model output",
                    "execution_time": execution_time
                })
        
        # Calculate overall metrics
        results["summary"] = self._calculate_overall_metrics(results["test_cases"])
        
        # Save results
        with open(self.results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print("\nEvaluation complete!")
        print(f"Results saved to: {self.results_file}")
        print("\nSummary:")
        print(json.dumps(results["summary"], indent=2))
        
        return results
    
    def _run_model(self, text: str) -> Tuple[str, float]:
        """Run the model on the given text and time it"""
        start_time = time.time()
        
        try:
            # Create a prompt that instructs the model to redact PII
            prompt = f"""You are a PII (Personally Identifiable Information) redaction expert. Your task is to identify and replace specific types of PII in the given text.

TYPES OF PII TO DETECT AND REDACT:
- name: personal names (first names, last names, full names)
- email: email addresses (any format)
- phone: phone numbers (any format)
- address: physical addresses (complete addresses)
- credit_card: credit card numbers (any format)
- date: personal dates (birth dates, etc.)
- ssn: Social Security Numbers (any format)
- drivers_license: Driver's License numbers
- ip_address: IP addresses

REPLACEMENT MAPPING:
- name → [REDACTED_NAME]
- email → [REDACTED_EMAIL]
- phone → [REDACTED_PHONE]
- address → [REDACTED_ADDRESS]
- credit_card → [REDACTED_CREDIT_CARD]
- date → [REDACTED_DATE]
- ssn → [REDACTED_SSN]
- drivers_license → [REDACTED_DRIVERS_LICENSE]
- ip_address → [REDACTED_IP_ADDRESS]

CRITICAL INSTRUCTIONS:
1. CAREFULLY analyze the text and identify ALL instances of the specified PII types
2. Replace each identified PII with the corresponding replacement tag EXACTLY as shown
3. Maintain the original text structure, formatting, and punctuation
4. Be THOROUGH - it's better to redact something that might be PII than to miss it

INPUT TEXT:
{text}

REDACTED TEXT:"""

            # Use subprocess to call Ollama
            result = subprocess.run(
                ["ollama", "run", self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                # Clean up output to get just the generated text
                output = result.stdout.strip()
                
                # Extract just the redacted text part (after "REDACTED TEXT:")
                if "REDACTED TEXT:" in output:
                    output = output.split("REDACTED TEXT:", 1)[1].strip()
                
                return output, execution_time
            else:
                print(f"Error: {result.stderr}")
                return "", execution_time
                
        except subprocess.TimeoutExpired:
            print("Error: Model execution timed out (30s)")
            return "", 30.0
        except Exception as e:
            print(f"Error running model: {e}")
            return "", time.time() - start_time
    
    def _identify_expected_pii(self, text: str) -> Dict[str, List[str]]:
        """Identify expected PII in the test case"""
        expected_pii = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                expected_pii[pii_type] = matches
        
        return expected_pii
    
    def _analyze_redactions(self, redacted_text: str) -> Dict[str, int]:
        """Analyze redactions in the model output"""
        detected_pii = {}
        
        for pii_type in self.pii_types:
            tag = f"[REDACTED_{pii_type.upper()}]"
            count = redacted_text.count(tag)
            if count > 0:
                detected_pii[pii_type] = count
        
        return detected_pii
    
    def _calculate_metrics(self, expected_pii: Dict[str, List[str]], detected_pii: Dict[str, int]) -> Dict[str, Any]:
        """Calculate metrics for a single test case"""
        metrics = {
            "by_type": {},
            "overall": {}
        }
        
        total_expected = sum(len(items) for items in expected_pii.values())
        total_detected = sum(detected_pii.values())
        
        # Calculate metrics by PII type
        for pii_type in self.pii_types:
            expected_count = len(expected_pii.get(pii_type, []))
            detected_count = detected_pii.get(pii_type, 0)
            
            if expected_count == 0 and detected_count == 0:
                precision = 1.0
                recall = 1.0
                f1 = 1.0
            elif expected_count == 0:
                precision = 0.0
                recall = 1.0
                f1 = 0.0
            elif detected_count == 0:
                precision = 1.0
                recall = 0.0
                f1 = 0.0
            else:
                # Simplistic metrics assuming all detections are correct if counts match
                precision = min(1.0, expected_count / detected_count)
                recall = min(1.0, detected_count / expected_count)
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            
            metrics["by_type"][pii_type] = {
                "expected": expected_count,
                "detected": detected_count,
                "precision": precision,
                "recall": recall,
                "f1": f1
            }
        
        # Calculate overall metrics
        if total_expected == 0 and total_detected == 0:
            overall_precision = 1.0
            overall_recall = 1.0
            overall_f1 = 1.0
        elif total_expected == 0:
            overall_precision = 0.0
            overall_recall = 1.0
            overall_f1 = 0.0
        elif total_detected == 0:
            overall_precision = 1.0
            overall_recall = 0.0
            overall_f1 = 0.0
        else:
            # Simplistic overall metrics
            overall_precision = min(1.0, total_expected / total_detected)
            overall_recall = min(1.0, total_detected / total_expected)
            overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0
        
        metrics["overall"] = {
            "expected": total_expected,
            "detected": total_detected,
            "precision": overall_precision,
            "recall": overall_recall,
            "f1": overall_f1
        }
        
        return metrics
    
    def _calculate_overall_metrics(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall metrics across all test cases"""
        overall_metrics = {
            "by_type": {},
            "overall": {},
            "execution_time": {
                "average": 0,
                "min": float('inf'),
                "max": 0,
                "total": 0
            }
        }
        
        # Initialize metrics for each PII type
        for pii_type in self.pii_types:
            overall_metrics["by_type"][pii_type] = {
                "expected": 0,
                "detected": 0,
                "precision": 0,
                "recall": 0,
                "f1": 0
            }
        
        # Sum up metrics from all test cases
        valid_test_cases = 0
        for test_case in test_results:
            if "metrics" in test_case:
                valid_test_cases += 1
                
                # Add up type-specific metrics
                for pii_type, metrics in test_case["metrics"]["by_type"].items():
                    if pii_type in overall_metrics["by_type"]:
                        overall_metrics["by_type"][pii_type]["expected"] += metrics["expected"]
                        overall_metrics["by_type"][pii_type]["detected"] += metrics["detected"]
                
                # Track execution time
                execution_time = test_case.get("execution_time", 0)
                overall_metrics["execution_time"]["total"] += execution_time
                overall_metrics["execution_time"]["min"] = min(overall_metrics["execution_time"]["min"], execution_time)
                overall_metrics["execution_time"]["max"] = max(overall_metrics["execution_time"]["max"], execution_time)
        
        # Calculate averages and overall metrics
        if valid_test_cases > 0:
            overall_metrics["execution_time"]["average"] = overall_metrics["execution_time"]["total"] / valid_test_cases
            
            # Calculate precision, recall, and F1 for each PII type
            total_expected = 0
            total_detected = 0
            
            for pii_type, metrics in overall_metrics["by_type"].items():
                expected = metrics["expected"]
                detected = metrics["detected"]
                
                total_expected += expected
                total_detected += detected
                
                if expected == 0 and detected == 0:
                    metrics["precision"] = 1.0
                    metrics["recall"] = 1.0
                    metrics["f1"] = 1.0
                elif expected == 0:
                    metrics["precision"] = 0.0
                    metrics["recall"] = 1.0
                    metrics["f1"] = 0.0
                elif detected == 0:
                    metrics["precision"] = 1.0
                    metrics["recall"] = 0.0
                    metrics["f1"] = 0.0
                else:
                    metrics["precision"] = min(1.0, expected / detected)
                    metrics["recall"] = min(1.0, detected / expected)
                    metrics["f1"] = 2 * metrics["precision"] * metrics["recall"] / (metrics["precision"] + metrics["recall"]) if (metrics["precision"] + metrics["recall"]) > 0 else 0.0
            
            # Calculate overall metrics
            if total_expected == 0 and total_detected == 0:
                overall_precision = 1.0
                overall_recall = 1.0
                overall_f1 = 1.0
            elif total_expected == 0:
                overall_precision = 0.0
                overall_recall = 1.0
                overall_f1 = 0.0
            elif total_detected == 0:
                overall_precision = 1.0
                overall_recall = 0.0
                overall_f1 = 0.0
            else:
                overall_precision = min(1.0, total_expected / total_detected)
                overall_recall = min(1.0, total_detected / total_expected)
                overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0
            
            overall_metrics["overall"] = {
                "expected": total_expected,
                "detected": total_detected,
                "precision": overall_precision,
                "recall": overall_recall,
                "f1": overall_f1,
                "test_cases": valid_test_cases
            }
        
        # Handle case where min is still infinity
        if overall_metrics["execution_time"]["min"] == float('inf'):
            overall_metrics["execution_time"]["min"] = 0
            
        return overall_metrics

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Evaluate PII detection model")
    parser.add_argument("--model", default="pii-detector-enhanced", help="Model name to evaluate")
    args = parser.parse_args()
    
    evaluator = PIIModelEvaluator(model_name=args.model)
    evaluator.evaluate_model()

if __name__ == "__main__":
    main()
