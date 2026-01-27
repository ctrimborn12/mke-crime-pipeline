from extract import extract_data
from transform import transform_data
from load import load_processed_data

def run_pipeline():
    extract_data()
    summaries = transform_data()
    load_processed_data(summaries)

if __name__ == "__main__":
    run_pipeline()