"""
src/timonelo/harvester/vault.py

Immutable Content-Addressable Evidence Vault.
Stores raw artifacts by SHA-256 byte digest:
evidence/raw/sha256/{ab}/{abcdef....}.pdf
"""

import os
from typing import Tuple


class EvidenceVault:
    def __init__(self, vault_root: str = "evidence/raw/sha256"):
        self.vault_root = vault_root
        os.makedirs(self.vault_root, exist_ok=True)

    def get_artifact_path(self, sha256: str) -> Tuple[str, str]:
        """Returns (absolute_path, relative_vault_path)."""
        prefix = sha256[:2]
        filename = f"{sha256}.pdf"
        rel_path = os.path.join(self.vault_root, prefix, filename).replace("\\", "/")
        abs_path = os.path.abspath(rel_path)
        return abs_path, rel_path

    def has_artifact(self, sha256: str) -> bool:
        abs_path, _ = self.get_artifact_path(sha256)
        return os.path.isfile(abs_path)

    def store_artifact(self, data: bytes, sha256: str) -> Tuple[str, bool]:
        """
        Stores artifact bytes into vault idempotently.
        Returns: (vault_rel_path, is_duplicate)
        """
        abs_path, rel_path = self.get_artifact_path(sha256)
        
        if os.path.isfile(abs_path):
            # Duplicate detection: file already exists with same SHA-256
            return rel_path, True

        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        temp_path = f"{abs_path}.tmp"
        with open(temp_path, "wb") as f:
            f.write(data)
        os.replace(temp_path, abs_path)

        return rel_path, False
