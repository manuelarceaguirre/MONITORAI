import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset, TargetDriftPreset
from evidently.metrics import *
import json
from datetime import datetime
from pathlib import Path

class CreditDataAnalyzer:
    def __init__(self):
        # Create output directory for results
        self.output_dir = Path("analysis_results")
        self.output_dir.mkdir(exist_ok=True)
        
    def analyze_data(self, reference_data, current_data):
        """Analyze data and return key insights"""
        
        # Create report with key metrics
        report = Report(metrics=[
            # Overall data drift
            DataDriftPreset(),
            
            # Data quality
            DataQualityPreset(),
            
            # Target drift (Credit_Score)
            TargetDriftPreset(),
        ])
        
        # Run analysis
        report.run(reference_data=reference_data, current_data=current_data)
        
        # Extract results
        results = self._extract_key_insights(report)
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _extract_key_insights(self, report):
        """Extract key insights from the report"""
        
        json_report = report.json()
        metrics = json_report['metrics']
        
        insights = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_features': len(report.metrics[0].get_result().data_drift.keys()),
                'drifted_features': sum(1 for f in report.metrics[0].get_result().data_drift.values() if f.get('drift_detected', False)),
            },
            'data_drift': {
                'drifted_features': [
                    {
                        'feature': feature,
                        'p_value': details['p_value'],
                        'drift_score': details['drift_score']
                    }
                    for feature, details in report.metrics[0].get_result().data_drift.items()
                    if details.get('drift_detected', False)
                ],
                'stable_features': [
                    feature for feature, details in report.metrics[0].get_result().data_drift.items()
                    if not details.get('drift_detected', False)
                ]
            },
            'data_quality': {
                'current_data': report.metrics[1].get_result().current,
                'reference_data': report.metrics[1].get_result().reference
            },
            'target_drift': {
                'drift_detected': report.metrics[2].get_result().drift_detected,
                'p_value': report.metrics[2].get_result().p_value
            }
        }
        
        return insights

    def _save_results(self, results):
        """Save results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed JSON results
        with open(self.output_dir / f'drift_analysis_{timestamp}.json', 'w') as f:
            json.dump(results, f, indent=4)
        
        # Create and save summary report
        summary = self._create_summary_report(results)
        with open(self.output_dir / f'summary_{timestamp}.txt', 'w') as f:
            f.write(summary)
            
    def _create_summary_report(self, results):
        """Create a human-readable summary report"""
        
        summary = [
            "Credit Score Data Analysis Summary",
            "================================",
            f"\nAnalysis timestamp: {results['timestamp']}",
            
            "\nOverall Drift Summary:",
            f"- Total features analyzed: {results['summary']['total_features']}",
            f"- Features with drift detected: {results['summary']['drifted_features']}",
            
            "\nDrifted Features:",
        ]
        
        # Add drifted features details
        for feature in results['data_drift']['drifted_features']:
            summary.append(
                f"- {feature['feature']}:"
                f" (p-value: {feature['p_value']:.4f},"
                f" drift score: {feature['drift_score']:.4f})"
            )
            
        summary.extend([
            "\nTarget Variable (Credit_Score) Analysis:",
            f"- Drift detected: {results['target_drift']['drift_detected']}",
            f"- P-value: {results['target_drift']['p_value']:.4f}",
            
            "\nData Quality Metrics:",
            "Current Data:",
        ])
        
        # Add data quality metrics
        for metric, value in results['data_quality']['current_data'].items():
            summary.append(f"- {metric}: {value}")
            
        return "\n".join(summary)

def run_analysis():
    # Load data
    reference_data = pd.read_csv("Credit_score_cleaned_data.csv")
    
    # Create synthetic current data with some drift (for testing)
    current_data = reference_data.copy()
    current_data['Credit_Utilization_Ratio'] *= 1.1  # Introduce some drift
    current_data['Annual_Income'] += current_data['Annual_Income'] * 0.05
    
    # Initialize analyzer
    analyzer = CreditDataAnalyzer()
    
    # Run analysis
    results = analyzer.analyze_data(reference_data, current_data)
    
    print("\nAnalysis complete! Results saved in 'analysis_results' directory.")
    print("\nKey findings:")
    print(f"- Number of drifted features: {results['summary']['drifted_features']}")
    print(f"- Target drift detected: {results['target_drift']['drift_detected']}")
    
    # Print path to results
    print("\nDetailed results saved to:")
    print(f"- {analyzer.output_dir}/drift_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    print(f"- {analyzer.output_dir}/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

if __name__ == "__main__":
    run_analysis() 