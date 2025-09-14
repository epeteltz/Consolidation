import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, List, Any
import api_config

# --- Main Configuration ---
# Get the configuration from the new api_config file
BANK_ID = api_config.DEFAULT_BANK_ID
if BANK_ID not in api_config.bank_api_configs:
    raise ValueError(f"Configuration for bank '{BANK_ID}' not found in api_config.py")

BANK_CONFIG = api_config.bank_api_configs[BANK_ID]

def get_access_token() -> str:
    """
    Handles the authentication process to get an access token.
    This is a conceptual example; the actual process may be more complex (e.g., OAuth2).

    Returns:
        str: The access token string.
    
    Raises:
        requests.exceptions.RequestException: If the authentication request fails.
    """
    print("Attempting to retrieve access token...")
    
    # This is a conceptual payload. The actual payload (e.g., grant_type) will
    # be specified in the bank's API documentation.
    payload = {
        "client_id": BANK_CONFIG['API_KEY'],
        "client_secret": BANK_CONFIG['CLIENT_SECRET'],
        "grant_type": "client_credentials" # A common type for machine-to-machine auth
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{BANK_CONFIG['BASE_URL']}{BANK_CONFIG['AUTH_ENDPOINT']}",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if access_token:
            print("Access token retrieved successfully.")
            return access_token
        else:
            raise Exception("Failed to retrieve access token from response.")

    except requests.exceptions.RequestException as e:
        print(f"Error during authentication: {e}")
        raise
    except Exception as e:
        print(f"Authentication failed: {e}")
        raise

def get_transactions(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Retrieves transaction data for a specific account and date range.

    Args:
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        List[Dict[str, Any]]: A list of transaction dictionaries.
    
    Raises:
        Exception: If data retrieval or processing fails.
    """
    print(f"Retrieving transactions from {start_date} to {end_date}...")
    
    try:
        access_token = get_access_token()
    except Exception:
        return []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Conceptual query parameters for the date range
    params = {
        "from_date": start_date,
        "to_date": end_date
    }

    try:
        transactions_endpoint = BANK_CONFIG['TRANSACTIONS_ENDPOINT'].replace("{ACCOUNT_ID}", BANK_CONFIG['ACCOUNT_ID'])
        response = requests.get(f"{BANK_CONFIG['BASE_URL']}{transactions_endpoint}", headers=headers, params=params)
        response.raise_for_status()
        transactions_data = response.json()
        
        # The actual key for the list of transactions will be in the API documentation
        transactions = transactions_data.get("transactions", [])
        print(f"Successfully retrieved {len(transactions)} transactions.")
        
        return transactions

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving transactions: {e}")
        return []
    except json.JSONDecodeError:
        print("Error: Could not parse JSON response from API.")
        return []
        
def standardize_data(transactions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Converts a list of raw transaction dictionaries into a standardized DataFrame.

    Args:
        transactions (List[Dict[str, Any]]): A list of transaction dictionaries from the API.

    Returns:
        pd.DataFrame: A pandas DataFrame with standardized columns.
    """
    if not transactions:
        print("No transactions to standardize.")
        return pd.DataFrame()

    df = pd.DataFrame(transactions)
    
    # Standardized dataframe based on the configuration mapping
    standardized_df = pd.DataFrame()
    for api_key, master_col in BANK_CONFIG['MAPPING'].items():
        if api_key in df.columns:
            standardized_df[master_col] = df[api_key]
    
    # Add other non-mapped columns
    standardized_df['Transaction Account'] = BANK_CONFIG['ACCOUNT_ID']
    standardized_df['Category'] = ''
    standardized_df['Subcategory'] = ''

    # Ensure correct data types for the date and amount
    if 'Transaction Date' in standardized_df.columns:
        standardized_df['Transaction Date'] = pd.to_datetime(standardized_df['Transaction Date'])
    if 'Credit/Debit' in standardized_df.columns:
        standardized_df['Credit/Debit'] = pd.to_numeric(standardized_df['Credit/Debit'], errors='coerce')

    return standardized_df

if __name__ == '__main__':
    # Define the date range for the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    raw_transactions = get_transactions(start_date_str, end_date_str)
    
    if raw_transactions:
        master_df = standardize_data(raw_transactions)
        
        # Save the master file to an Excel file
        output_file = 'master_transactions_api.xlsx'
        try:
            master_df.to_excel(output_file, index=False)
            print(f"\nSuccessfully retrieved and saved transactions to '{output_file}'.")
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            
    else:
        print("\nFailed to retrieve transactions. The process was aborted.")
