# This file contains the configuration for different bank and credit card formats.
# To add a new format, simply create a new entry in the 'file_formats' dictionary.

# The format maps define how to convert column names from a bank's CSV file
# to the standardized names used by the script.

# Master file columns are:
# Transaction Date; Transaction Account; Transaction Description; Currency; Credit/Debit; Category; Subcategory; Note; Year; Month; Day; Transaction Date2

file_formats = {
    # --- Configuration for Format A ---
    # This format is identified by the file prefix '19988560'.
    '19988560': {
        'format_map': {
            'Transaction Date': 'transaction_date',
            'Transaction Description': 'transaction_description',
            'Account Number': 'account_number',
            'Debit Amount': 'debit_amount',
            'Credit Amount': 'credit_amount',
        },
        'currency': 'GBP',
        'account_type': 'Current Account',
    },
    
    # --- Configuration for Format B ---
    # This format is identified by the file prefix '1231'.
    '1231': {
        'format_map': {
            'Transaction Date': 'transaction_date',
            'Transaction Description': 'transaction_description',
            'Transaction Amount': 'original_amount',
        },
        'currency': 'GBP',
        'account_type': 'Credit Card',
    },
}
