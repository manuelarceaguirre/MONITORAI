import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

def prepare_monitoring_data():
    # Create data directory
    data_dir = Path("monitoring_data")
    data_dir.mkdir(exist_ok=True)
    
    # Read the full dataset
    df = pd.read_csv("Credit_score_cleaned_data.csv")
    
    # Split into reference (older) and current (newer) data
    reference_data, current_data = train_test_split(
        df, 
        test_size=0.3,  # 70% reference, 30% current
        random_state=42
    )
    
    # Save datasets
    reference_data.to_csv(data_dir / "reference_data.csv", index=False)
    current_data.to_csv(data_dir / "current_data.csv", index=False)
    
    print(f"Data prepared in {data_dir}/")
    print(f"Reference data shape: {reference_data.shape}")
    print(f"Current data shape: {current_data.shape}")

if __name__ == "__main__":
    prepare_monitoring_data() 