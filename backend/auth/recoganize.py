"""
Backward-compatibility alias module for recognize.py.
Handles legacy typo 'recoganize' gracefully.
"""

from .recognize import AuthenticateFace, authenticate_face

__all__ = ["AuthenticateFace", "authenticate_face"]
