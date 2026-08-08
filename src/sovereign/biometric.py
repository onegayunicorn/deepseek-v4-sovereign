"""Sovereign biometric module — re-exports the biometric auth router."""

from __future__ import annotations

from sovereign.auth.biometric_router import BiometricSession, BiometricSignal, install_biometric_auth

__all__ = ["BiometricSession", "BiometricSignal", "install_biometric_auth"]
