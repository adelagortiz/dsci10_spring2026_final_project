import os
from config import DATA_DIR, RESULTS_DIR, MERGED_FILE, CLUSTERED_FILE
from process import build_dataset
from analyze import run_analysis

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # step 1: load and merge all three datasets
    df = build_dataset()

    # step 2: save the merged dataset before clustering
    output_path = os.path.join(DATA_DIR, MERGED_FILE)
    df.to_csv(output_path, index=False)
    print(f"Merged data saved to {output_path}")

    # step 3: run clustering and generate charts
    df = run_analysis(df)

    # step 4: save the final dataset with cluster labels
    final_path = os.path.join(DATA_DIR, CLUSTERED_FILE)
    df.to_csv(final_path, index=False)
    print(f"Clustered data saved to {final_path}")

    print("\nPipeline complete.")