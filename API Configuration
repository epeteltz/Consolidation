from typing import Dict, Any

# This file contains the configuration for various bank Open Banking APIs.
# To add a new bank, simply add a new key-value pair to the bank_api_configs dictionary.

DEFAULT_BANK_ID = "discount_bank"

bank_api_configs: Dict[str, Dict[str, Any]] = {
    "discount_bank": {
        # IMPORTANT: These are conceptual endpoints and credentials. You must replace them with the
        # actual, official values from Discount Bank's Open Banking API documentation.
        "BASE_URL": "https://api.discountbank.co.il/v1",
        "AUTH_ENDPOINT": "/oauth/token",
        "TRANSACTIONS_ENDPOINT": "/accounts/{ACCOUNT_ID}/transactions",
        
        "API_KEY": "YOUR_API_KEY_HERE",
        "CLIENT_SECRET": "YOUR_CLIENT_SECRET_HERE",
        "ACCOUNT_ID": "YOUR_ACCOUNT_ID_HERE",
        
        "ACCOUNT_TYPE": "current account",
        "CURRENCY": "ILS",
        
        # This mapping ensures API response keys are converted to our master file's columns.
        "MAPPING": {
            "date": "Transaction Date",
            "description": "Transaction Description",
            "currency": "Currency",
            "amount": "Credit/Debit",
            "note": "Note"
        }
    }
    # Add other bank configurations here as needed
    # "leumi_bank": {
    #     "BASE_URL": "...",
    #     "AUTH_ENDPOINT": "...",
    #     "TRANSACTIONS_ENDPOINT": "...",
    #     "API_KEY": "...",
    #     "CLIENT_SECRET": "...",
    #     "ACCOUNT_ID": "...",
    #     "ACCOUNT_TYPE": "...",
    #     "CURRENCY": "...",
    #     "MAPPING": {
    #         "api_date_key": "Transaction Date",
    #         ...
    #     }
    # }
}
