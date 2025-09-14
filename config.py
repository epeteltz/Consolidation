# This file contains the configuration for different bank and credit card file formats.
# The keys of the file_formats dictionary should be the unique file prefixes.

file_formats = {
    '1231': {
        'format_map': {
            'Transaction Date': 'transaction_date',
            'Transaction Description': 'transaction_description',
            'Transaction Amount': 'original_amount'
        },
        'currency': 'GBP',
        'account_type': 'Credit Card',
        'header_row': 1,
    },
    '19988560': {
        'format_map': {
            'Date': 'transaction_date',
            'Narrative': 'transaction_description',
            'Amount': 'original_amount'
        },
        'currency': 'GBP',
        'account_type': 'current account',
        'header_row': 1,
    },
    'עובר ושב': {
        'format_map': {
            'תאריך': 'transaction_date',
            'תיאור התנועה': 'transaction_description',
            '₪ זכות/חובה ': 'original_amount'
        },
        'currency': 'ILS',
        'account_type': 'current account',
        'header_row': 8,
        'account_number': 1920022824
    },
    'פירוט חיובים לכרטיס מאסטרקארד': {
        'format_map': {
            'תאריך עסקה': 'transaction_date',
            'שם בית עסק': 'transaction_description',
            'סכום חיוב': 'original_amount',
            'סוג עסקה': 'transaction_type',
            'הערות': 'Note',
        },
        'currency': 'ILS',
        'account_type': 'Credit Card',
        'header_row': 5
    }
}
