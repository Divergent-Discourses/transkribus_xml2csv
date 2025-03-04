import os
import pandas as pd

def merge_csv_files(input_folder, output_file):
    """
    Merges all CSV files in the specified input folder and saves the result to output_file.
    """
    input_folder = os.path.abspath(input_folder)
    output_file = os.path.abspath(output_file)

    print(f"Reading CSV files from: {input_folder}")
    print(f"Saving merged file to: {output_file}")

    if not os.path.exists(input_folder):
        print(f"Error: Input folder does not exist - {input_folder}")
        return
    
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))  # Create output directory if it doesn't exist

    all_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.csv')]

    if not all_files:
        print("No CSV files found in the input directory.")
        return

    df_list = []
    for file in all_files:
        try:
            print(f"Reading file: {file}")
            df = pd.read_csv(file)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if df_list:
        merged_df = pd.concat(df_list, ignore_index=True)
        merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"Successfully merged {len(df_list)} files into {output_file}")
    else:
        print("No valid CSV files to merge.")

# Example usage
input_folder = "./data/processed_csv"
output_file = "./data/merged_csv/merged_pages.csv"

# Run the processing
if __name__ == "__main__":
    merge_csv_files(input_folder, output_file)