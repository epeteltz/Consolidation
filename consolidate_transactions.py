import csv
import pandas as pd
from typing import Dict, List, Any
import os
from config import file_formats

# This script consolidates bank and credit card transactions from different CSV formats
# into a single, standardized master file.


# --- Main processing function ---
def process_transactions(file_path: str, format_map: Dict[str, str], currency: str, account_type: str, account_number_prefix: str) -> pd.DataFrame:
    """
    Reads a CSV file, processes transactions, and returns a pandas DataFrame
    with the standardized structure.

    Args:
        file_path (str): The path to the input CSV file.
        format_map (Dict[str, str]): A dictionary mapping the input CSV's column names
                                     to the standardized column names.
        currency (str): The default currency of the account (e.g., 'EUR', 'USD').
        account_type (str): The type of account (e.g., 'Current Account', 'Credit Card').
        account_number_prefix (str): The account number to use, which is derived from the file name.

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
    df['Transaction Account'] = account_number_prefix
    # Corrected logic: The 'Credit/Debit' column now contains the numeric value of the transaction.
    df['Credit/Debit'] = df['original_amount']
    df['Category'] = ''
    df['Subcategory'] = ''
    df['Note'] = ''
    df['Year'] = df['transaction_date'].dt.year.astype('Int64')
    df['Month'] = df['transaction_date'].dt.month.astype('Int64')
    df['Day'] = df['transaction_date'].dt.day.astype('Int64')
    df['Transaction Date2'] = df['transaction_date']
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
    Consolidates transactions from a list of files and saves them to a master Excel file.

    Args:
        input_file_paths (List[str]): A list of file paths to process.
        output_file (str): The path to the output master Excel file.
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
            df = process_transactions(file_path, format_map, currency, account_type, prefix)
            if not df.empty:
                all_dfs.append(df)
        else:
            print(f"Error: No configuration found for file prefix '{prefix}'. Skipping '{file_path}'.")

    if all_dfs:
        final_df = pd.DataFrame()
        seen_keys = set()
        initial_total_rows = 0

        # Process each DataFrame for deduplication
        for df in all_dfs:
            initial_total_rows += len(df)
            df['temp_key'] = df.apply(lambda row: (row['Transaction Date'], row['Transaction Account'], row['Transaction Description'], row['Credit/Debit']), axis=1)

            # Find rows that are not in the consolidated dataframe yet
            new_transactions = df[~df['temp_key'].isin(seen_keys)]
            
            # Add the keys of the new transactions to our set
            seen_keys.update(new_transactions['temp_key'])
            
            final_df = pd.concat([final_df, new_transactions.drop(columns='temp_key')], ignore_index=True)
        
        final_count = len(final_df)
        if initial_total_rows > final_count:
            print(f"\nRemoved {initial_total_rows - final_count} duplicate transactions across different files.")

        # Use ExcelWriter to set custom column formats
        try:
            writer = pd.ExcelWriter(output_file, engine='xlsxwriter', datetime_format='YYYY-MM-DD')
            final_df.to_excel(writer, index=False, sheet_name='Transactions')

            # Get the workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Transactions']

            # Define the number format for currency
            currency_format = workbook.add_format({'num_format': '0.00'})
            
            # Find the column index for 'Credit/Debit'
            col_names = final_df.columns.values.tolist()
            try:
                credit_debit_col_idx = col_names.index('Credit/Debit')
                # Set the column format
                worksheet.set_column(credit_debit_col_idx, credit_debit_col_idx, None, currency_format)
            except ValueError:
                print("Warning: 'Credit/Debit' column not found, could not apply number format.")
            
            # Autofit all columns
            for i, col in enumerate(final_df.columns):
                max_len = max(final_df[col].astype(str).map(len).max(), len(col))
                worksheet.set_column(i, i, max_len + 2) # Adding a small buffer

            # Close the writer to save the file
            writer.close()
            
            print(f"\nSuccessfully consolidated transactions to '{output_file}'!")

        except ImportError:
            print("Error: The 'openpyxl' library is required to write to Excel files.")
            print("Please install it by running: pip install openpyxl")
            print("Falling back to saving as CSV.")
            final_df.to_csv('master_transactions.csv', index=False)
            print(f"Successfully consolidated transactions to 'master_transactions.csv' instead.")

    else:
        print("\nNo transactions were processed. The output file was not created.")


if __name__ == '__main__':
    # --- Example Usage ---
    # Find all CSV files in the current directory that have a configured prefix
    input_files = []
    for filename in os.listdir('.'):
        if filename.endswith('.csv'):
            prefix = filename.split('_')[0]
            if prefix in file_formats:
                input_files.append(filename)

    if not input_files:
        print("No CSV files found with a configured prefix. Please ensure your files are in the same directory.")
    else:
        # Run the consolidation process
        consolidate_data(input_files, 'master_transactions.xlsx')
