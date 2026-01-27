import os

#load data preprocessed data into final csv
def load_processed_data(summaries, output_dir="data/processed/"):
    os.makedirs(output_dir, exist_ok=True)

    for name, df in summaries.items():
        path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(path, index=False)
