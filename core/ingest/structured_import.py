"""
Structured Data Ingestion Pipeline
Sovereignty Stack - Core

Ethical Constraint:
    "Memory is an ethical act."
    Every transformation of meaning must log its own provenance.

Initialization Clause:
    What drives us is people —
    keeping them safe, keeping them healthy, keeping them connected,
    ensuring they live in truth, and empowering them with agency.
"""

import pandas as pd
import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, BinaryIO
from pathlib import Path

from .pl_parser import parse_pl_report

# Ethical declaration
ETHICAL_CANON = "Memory is an ethical act."
INITIALIZATION_CLAUSE = """What drives us is people —
keeping them safe, keeping them healthy, keeping them connected,
ensuring they live in truth, and empowering them with agency."""


class StructuredImporter:
    """
    Ingests structured financial data (Excel/CSV) into Core
    with full provenance tracking and SAGE governance
    """
    
    def __init__(self, reasoner, storage):
        """
        Args:
            reasoner: Core reasoner instance
            storage: Core storage instance
        """
        self.reasoner = reasoner
        self.storage = storage
        
        # Column mapping: file column → ontology field
        self.column_mappings = {
            # Standard mappings
            "date": ["date", "transaction_date", "trans_date", "dt"],
            "description": ["description", "desc", "memo", "details", "transaction"],
            "amount": ["amount", "amt", "value", "total"],
            "category": ["category", "cat", "type", "class"],
            "vendor": ["vendor", "payee", "merchant", "supplier"],
            "account": ["account", "acct", "account_name"],
            "type": ["transaction_type", "trans_type", "debit_credit"],
        }
    
    def ingest_file(self, file_path: str, source_name: str, actor: str = "System") -> Dict[str, Any]:
        """
        Ingest a structured file (Excel or CSV)
        
        Args:
            file_path: Path to file
            source_name: Original filename
            actor: Who initiated the import
            
        Returns:
            Ingestion summary with governance statistics
        """
        # Generate batch provenance ID
        batch_id = str(uuid.uuid4())
        file_hash = self._compute_file_hash(file_path)
        
        # Try P&L parser first (for formatted reports)
        try:
            transactions = parse_pl_report(file_path)
            if transactions:
                # Convert to DataFrame for processing
                df = pd.DataFrame(transactions)
            else:
                # Fall back to standard parsing
                if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                    df = pd.read_excel(file_path)
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    raise ValueError(f"Unsupported file format: {file_path}")
                # Map columns
                df = self._map_columns(df)
        except Exception as e:
            # Fall back to standard parsing
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            # Map columns
            df = self._map_columns(df)
        
        # Log batch provenance entry
        batch_provenance = {
            "batch_id": batch_id,
            "source_file": source_name,
            "file_hash": file_hash,
            "records": len(df),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "actor": actor,
            "ethic": ETHICAL_CANON,
            "initialization": INITIALIZATION_CLAUSE,
            "status": "Started"
        }
        
        self.storage.log_provenance(
            object_id=batch_id,
            action="batch_ingest_started",
            actor=actor,
            metadata=batch_provenance
        )
        
        # Normalize data (df already has correct columns from P&L parser or mapping)
        normalized_df = self._normalize_data(df)
        
        # Ingest records
        results = {
            "batch_id": batch_id,
            "source_file": source_name,
            "total_records": len(normalized_df),
            "ingested": 0,
            "coherent": 0,
            "flagged": 0,
            "denied": 0,
            "failed": 0,
            "records": []
        }
        
        for idx, row in normalized_df.iterrows():
            try:
                # Create transaction object
                transaction_data = row.to_dict()
                transaction_data = {k: v for k, v in transaction_data.items() if pd.notna(v)}
                
                # Add batch metadata
                transaction_data["batch_id"] = batch_id
                transaction_data["row_number"] = idx + 1
                
                # Ingest through Core reasoner
                reasoned = self.reasoner.ingest(
                    object_type="Transaction",
                    data=transaction_data,
                    actor=f"{actor} (batch {batch_id})"
                )
                
                # Update statistics
                results["ingested"] += 1
                
                sage_decision = reasoned.get("sage", {}).get("decision", "unknown")
                if sage_decision == "allow":
                    results["coherent"] += 1
                elif sage_decision == "flag":
                    results["flagged"] += 1
                elif sage_decision == "deny":
                    results["denied"] += 1
                
                results["records"].append({
                    "row": idx + 1,
                    "object_id": reasoned["symbolic"]["id"],
                    "decision": sage_decision,
                    "coherence": reasoned["sage"]["coherence_score"]
                })
                
            except Exception as e:
                results["failed"] += 1
                results["records"].append({
                    "row": idx + 1,
                    "error": str(e)
                })
        
        # Compute summary statistics
        results["average_coherence"] = sum(
            r.get("coherence", 0) for r in results["records"] if "coherence" in r
        ) / max(results["ingested"], 1)
        
        results["average_trust"] = 0.5  # Placeholder - would compute from SAGE
        
        # Log completion
        batch_provenance["status"] = "Completed"
        batch_provenance["results"] = {
            "ingested": results["ingested"],
            "coherent": results["coherent"],
            "flagged": results["flagged"],
            "denied": results["denied"],
            "failed": results["failed"]
        }
        
        self.storage.log_provenance(
            object_id=batch_id,
            action="batch_ingest_completed",
            actor=actor,
            metadata=batch_provenance
        )
        
        return results
    
    def _map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map file columns to ontology fields
        """
        mapped = pd.DataFrame()
        
        # Convert all column names to lowercase for matching
        df.columns = [str(col).lower().strip() for col in df.columns]
        
        for ontology_field, possible_names in self.column_mappings.items():
            # Find matching column
            matched_col = None
            for col in df.columns:
                if col in possible_names:
                    matched_col = col
                    break
            
            if matched_col:
                mapped[ontology_field] = df[matched_col]
        
        return mapped
    
    def _normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data types and formats
        """
        normalized = df.copy()
        
        # Normalize amounts
        if "amount" in normalized.columns:
            normalized["amount"] = normalized["amount"].apply(self._normalize_amount)
        
        # Normalize dates
        if "date" in normalized.columns:
            normalized["date"] = pd.to_datetime(normalized["date"], errors='coerce')
            normalized["date"] = normalized["date"].dt.strftime('%Y-%m-%d')
        
        # Trim strings
        for col in normalized.columns:
            if normalized[col].dtype == 'object':
                normalized[col] = normalized[col].str.strip()
        
        # Infer transaction type from amount if not present
        if "type" not in normalized.columns and "amount" in normalized.columns:
            normalized["type"] = normalized["amount"].apply(
                lambda x: "income" if x > 0 else "expense"
            )
        
        return normalized
    
    def _normalize_amount(self, value) -> float:
        """
        Normalize amount values
        - Convert parentheses to negative
        - Remove currency symbols
        - Handle empty values
        """
        if pd.isna(value):
            return 0.0
        
        # Convert to string
        value_str = str(value).strip()
        
        # Handle parentheses (negative)
        if value_str.startswith('(') and value_str.endswith(')'):
            value_str = '-' + value_str[1:-1]
        
        # Remove currency symbols and commas
        value_str = value_str.replace('$', '').replace(',', '').replace('€', '').replace('£', '')
        
        try:
            return float(value_str)
        except ValueError:
            return 0.0
    
    def _compute_file_hash(self, file_path: str) -> str:
        """
        Compute SHA-256 hash of file for provenance
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()


def create_importer(reasoner, storage) -> StructuredImporter:
    """Factory function to create importer instance"""
    return StructuredImporter(reasoner, storage)
