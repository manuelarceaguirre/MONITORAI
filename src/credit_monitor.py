from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset, TargetDriftPreset
from evidently.metrics import *
from evidently.ui.workspace import Workspace
from evidently.test_suite import TestSuite
from evidently.tests import *
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreditMonitor:
    def __init__(self, workspace_path="credit_workspace"):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        self.workspace = Workspace.create(str(self.workspace_path))
        
    def create_monitoring_report(self, reference_data, current_data, project_name):
        try:
            # Create project if it doesn't exist
            project = self.workspace.get_project(project_name)
            if project is None:
                project = self.workspace.create_project(project_name)
            
            # Create comprehensive report
            report = Report(metrics=[
                # Data Quality
                DataQualityPreset(),
                
                # Data Drift
                DataDriftPreset(),
                
                # Target Drift for Credit_Score
                TargetDriftPreset(),
                
                # Column-specific metrics
                ColumnDriftMetric(column_name="Credit_Score"),
                ColumnDriftMetric(column_name="Credit_Mix"),
                ColumnDriftMetric(column_name="Payment_Behaviour"),
                
                # Correlation Changes
                ColumnCorrelationsMetric(),
                
                # Value Range Changes
                RangeOverTimeMetric(column_name="Credit_Utilization_Ratio"),
                RangeOverTimeMetric(column_name="Annual_Income"),
                
                # Missing Values
                DatasetMissingValuesMetric(),
            ])
            
            # Run report
            report.run(reference_data=reference_data, current_data=current_data)
            
            # Save report
            project.save_report(
                report, 
                "credit_monitoring_report",
                {"timestamp": pd.Timestamp.now().isoformat()}
            )
            
            logger.info(f"Report created successfully for project: {project_name}")
            return report
            
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            raise

def run_monitoring():
    try:
        # Load data
        reference_data = pd.read_csv("monitoring_data/reference_data.csv")
        current_data = pd.read_csv("monitoring_data/current_data.csv")
        
        # Initialize monitor
        monitor = CreditMonitor()
        
        # Create report
        report = monitor.create_monitoring_report(
            reference_data=reference_data,
            current_data=current_data,
            project_name="credit_score_monitoring"
        )
        
        logger.info("""
        Monitoring completed successfully!
        
        To view results:
        1. Run: python src/start_ui.py
        2. Open your browser to: http://localhost:8000
        """)
        
    except Exception as e:
        logger.error(f"Error during monitoring: {str(e)}")
        raise

if __name__ == "__main__":
    run_monitoring() 