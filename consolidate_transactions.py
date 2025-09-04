import csv
import pandas as pd
from typing import Dict, List, Any
import os
from config import file_formats

# This script consolidates bank and credit card transactions from different CSV formats
# into a single, standardized master file.


# --- Main processing function ---
def process_transactions(file_path: str, format_map: Dict[str, str], currency: str, account_type: str) -> pd.DataFrame:
    """
    Reads a CSV file, processes transactions, and returns a pandas DataFrame
    with the standardized structure.

    Args:
        file_path (str): The path to the input CSV file.
        format_map (Dict[str, str]): A dictionary mapping the input CSV's column names
                                     to the standardized column names.
        currency (str): The default currency of the account (e.g., 'EUR', 'USD').
        account_type (str): The type of account (e.g., 'Current Account', 'Credit Card').

    Returns:
        pd.DataFrame: A DataFrame containing the standardized transaction data.
                      Returns an empty DataFrame on error.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return pd.DataFrame()

    # Rename columns based on the format map
    df = df.rename(columns=format_map)
    
    # Check for both 'debit_amount' and 'credit_amount' columns. If they exist, combine them.
    if 'debit_amount' in df.columns and 'credit_amount' in df.columns:
        # Fill NaN values with 0 to enable numerical operations
        df['debit_amount'] = pd.to_numeric(df['debit_amount'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        df['credit_amount'] = pd.to_numeric(df['credit_amount'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        # Calculate original_amount: credit is positive, debit is negative
        df['original_amount'] = df['credit_amount'] - df['debit_amount']
    
    # Ensure all required columns exist in the DataFrame
    required_cols = list(set(format_map.values()))
    if not all(col in df.columns for col in required_cols if col not in ['debit_amount', 'credit_amount']):
        missing_cols = [col for col in required_cols if col not in df.columns and col not in ['debit_amount', 'credit_amount']]
        print(f"Error: Missing required columns in '{file_path}': {missing_cols}")
        return pd.DataFrame()

    # Convert the transaction_date column to datetime objects for easy extraction
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], dayfirst=True)

    # Create new columns to match the desired master structure
    df['Transaction Account'] = df['account_number']
    df['Credit/Debit'] = df['original_amount'].apply(lambda x: 'Credit' if x >= 0 else 'Debit')
    df['Category'] = ''
    df['Subcategory'] = ''
    df['Note'] = ''
    df['Year'] = ''
    df['Month'] = ''
    df['Day'] = ''
    df['Transaction Date2'] = ''
    df['Currency'] = currency

    # Reformat the original transaction date to a string in the desired format
    df['Transaction Date'] = df['transaction_date'].dt.strftime('%Y-%m-%d')
    if 'transaction_description' in df.columns:
        df['Transaction Description'] = df['transaction_description']

    # Keep only the required columns and reorder them
    master_columns = [
        'Transaction Date',
        'Transaction Account',
        'Transaction Description',
        'Currency',
        'Credit/Debit',
        'Category',
        'Subcategory',
        'Note',
        'Year',
        'Month',
        'Day',
        'Transaction Date2',
    ]
    
    final_df = df[master_columns]

    return final_df


def consolidate_data(input_file_paths: List[str], output_file: str):
    """
    Consolidates transactions from a list of files and saves them to a master CSV file.

    Args:
        input_file_paths (List[str]): A list of file paths to process.
        output_file (str): The path to the output master CSV file.
    """
    all_dfs = []
    
    # Process each file in the list
    for file_path in input_file_paths:
        file_name = os.path.basename(file_path)
        # Get the file prefix, which is the part before the first underscore
        prefix = file_name.split('_')[0]
        
        # Look up the configuration based on the file prefix
        if prefix in file_formats:
            format_info = file_formats[prefix]
            format_map = format_info['format_map']
            currency = format_info['currency']
            account_type = format_info['account_type']

            print(f"Processing '{file_path}' using format '{prefix}'...")
            df = process_transactions(file_path, format_map, currency, account_type)
            if not df.empty:
                all_dfs.append(df)
        else:
            print(f"Error: No configuration found for file prefix '{prefix}'. Skipping '{file_path}'.")

    if all_dfs:
        # Concatenate all DataFrames into one
        consolidated_df = pd.concat(all_dfs, ignore_index=True)
        consolidated_df.to_csv(output_file, index=False)
        print(f"\nSuccessfully consolidated transactions to '{output_file}'!")
    else:
        print("\nNo transactions were processed. The output file was not created.")


if __name__ == '__main__':
    # --- Example Usage ---
    # Define a list of input file paths to process.
    # The script will automatically look up the correct format based on the file name prefix.
    
    # Create dummy CSV files for demonstration purposes
    dummy_bank_A_data = """Transaction Date,Transaction Type,Sort Code,Account Number,Transaction Description,Debit Amount,Credit Amount,Balance
01/09/2025,FPI,'30-80-88,19988560,CLM LTD,,3102.15,5938.02
01/09/2025,DD,'30-80-88,19988560,AJ BELL SECURITIES,250.00,,2835.87
01/09/2025,DD,'30-80-88,19988560,AJ BELL SECURITIES,250.00,,3085.87
01/09/2025,DD,'30-80-88,19988560,LLOYDS CASHBACK,69.98,,3335.87
15/08/2025,DD,'30-80-88,19988560,SANTANDER MORTGAGE,2349.54,,3405.85
"""
    with open('19988560_20252204_0309.csv', 'w') as f:
        f.write(dummy_bank_A_data)

    input_files = [
        '19988560_20252204_0309.csv',
    ]

    # Run the consolidation process
    consolidate_data(input_files, 'master_transactions.csv')
