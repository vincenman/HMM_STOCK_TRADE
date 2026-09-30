"""
Package initialization for models module.
"""
# Try to import HMM components, but make them optional
try:
    from .hmm_engine import HMMEngine
    from .model_manager import ModelManager
    HMM_AVAILABLE = True
except ImportError:
    HMMEngine = None
    ModelManager = None
    HMM_AVAILABLE = False

__all__ = ['HMMEngine', 'ModelManager', 'HMM_AVAILABLE']
