"""
P&L Report Parser
Parses hierarchical Profit & Loss statements into flat transaction records
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime


def parse_pl_report(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a P&L report into transaction records
    
    Args:
        file_path: Path to Excel/CSV file
        
    Returns:
        List of transaction dictionaries
    """
    # Read file
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    
    # Extract date range from header (if present)
    date_str = None
    for idx in range(min(5, len(df))):
        cell = str(df.iloc[idx, 0])
        if 'january' in cell.lower() or 'jan' in cell.lower() or '-' in cell:
            date_str = cell
            break
    
    # Find the data section (starts with "Distribution account" or similar header)
    data_start = 0
    for idx, row in df.iterrows():
        cell = str(row.iloc[0]).lower()
        if 'distribution' in cell or 'account' in cell or 'total' in cell:
            data_start = idx + 1
            break
    
    # Parse transactions
    transactions = []
    current_category = None
    current_type = None  # income, expense, other_income, other_expense
    
    for idx in range(data_start, len(df)):
        row = df.iloc[idx]
        description = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        amount = row.iloc[1] if pd.notna(row.iloc[1]) else None
        
        # Skip empty rows
        if not description and amount is None:
            continue
        
        # Skip footer rows
        if 'accrual basis' in description.lower() or 'thursday' in description.lower():
            continue
        
        # Detect category headers (no amount)
        if amount is None or description.lower() in ['income', 'expenses', 'other income', 'other expenses', 'cost of goods sold']:
            # This is a category header
            current_category = description
            
            # Determine transaction type
            if 'income' in description.lower() and 'other' not in description.lower():
                current_type = 'income'
            elif 'expense' in description.lower() or 'cost' in description.lower():
                current_type = 'expense'
            elif 'other income' in description.lower():
                current_type = 'other_income'
            elif 'other expense' in description.lower():
                current_type = 'other_expense'
            
            continue
        
        # Skip subtotal rows
        if 'total for' in description.lower() or 'net' in description.lower() or 'gross' in description.lower():
            continue
        
        # This is a line item - create transaction
        transaction = {
            'description': description,
            'amount': float(amount),
            'category': current_category if current_category else 'Uncategorized',
            'transaction_type': current_type if current_type else 'expense',
            'date': datetime.now().strftime('%Y-%m-%d'),  # Use current date if not specified
            'vendor': description,  # Use description as vendor
            'account': 'DexaFit Denver'
        }
        
        transactions.append(transaction)
    
    return transactions
