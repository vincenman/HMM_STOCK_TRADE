"""
Model persistence and management.
"""
import pickle
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple

from config.settings import MODELS_DIR, MODEL_RETRAIN_DAYS
from data.database import db_manager, ModelMetadata
from models.hmm_engine import HMMEngine
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ModelManager:
    """Manages model persistence and lifecycle."""

    def __init__(self, models_dir: Path = MODELS_DIR):
        """
        Initialize ModelManager.

        Args:
            models_dir: Directory to store model files
        """
        self.models_dir = models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ModelManager initialized with directory: {models_dir}")

    def save_model(
        self,
        engine: HMMEngine,
        version: Optional[str] = None,
        set_active: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Save trained HMM model to disk and database.

        Args:
            engine: Trained HMM engine
            version: Model version string (default: timestamp)
            set_active: Set this model as active

        Returns:
            Tuple of (success, model_path)
        """
        if not engine.is_trained():
            logger.error("Cannot save untrained model")
            return False, None

        try:
            # Generate version if not provided
            if version is None:
                version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

            # Create model filename
            model_filename = f"hmm_model_{version}.pkl"
            model_path = self.models_dir / model_filename

            # Save model to disk
            with open(model_path, 'wb') as f:
                pickle.dump(engine, f)

            logger.info(f"Model saved to {model_path}")

            # Calculate convergence score
            convergence_score = None
            if engine.model is not None and hasattr(engine.model, 'monitor_'):
                convergence_score = float(engine.model.monitor_.history[-1])

            # Save metadata to database
            session = db_manager.get_session()
            try:
                # Deactivate old models if setting this as active
                if set_active:
                    session.query(ModelMetadata).update({ModelMetadata.is_active: False})

                # Create metadata entry
                metadata = ModelMetadata(
                    model_version=version,
                    training_date=datetime.utcnow(),
                    n_states=engine.n_states,
                    convergence_score=convergence_score,
                    model_path=str(model_path),
                    bull_state=engine.bull_state,
                    bear_state=engine.bear_state,
                    is_active=set_active,
                )

                session.add(metadata)
                session.commit()

                logger.info(f"Model metadata saved to database (version: {version})")
                return True, str(model_path)

            except Exception as e:
                session.rollback()
                logger.error(f"Error saving metadata: {e}")
                return False, None
            finally:
                db_manager.close_session(session)

        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False, None

    def load_model(
        self, version: Optional[str] = None, model_path: Optional[str] = None
    ) -> Optional[HMMEngine]:
        """
        Load HMM model from disk.

        Args:
            version: Model version to load (loads active model if None)
            model_path: Direct path to model file (overrides version)

        Returns:
            Loaded HMM engine or None
        """
        try:
            # Determine model path
            if model_path is None:
                if version is None:
                    # Load active model
                    metadata = db_manager.get_active_model_metadata()
                    if metadata is None:
                        logger.warning("No active model found in database")
                        return None
                    model_path = metadata.model_path
                else:
                    # Load specific version
                    model_filename = f"hmm_model_{version}.pkl"
                    model_path = self.models_dir / model_filename

            # Check if file exists
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return None

            # Load model
            with open(model_path, 'rb') as f:
                engine = pickle.load(f)

            logger.info(f"Model loaded from {model_path}")
            return engine

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None

    def should_retrain(self) -> bool:
        """
        Check if model should be retrained based on age.

        Returns:
            True if retraining is needed
        """
        metadata = db_manager.get_active_model_metadata()

        if metadata is None:
            logger.info("No active model found - retraining needed")
            return True

        # Check age
        age = datetime.utcnow() - metadata.training_date
        age_days = age.total_seconds() / 86400

        if age_days >= MODEL_RETRAIN_DAYS:
            logger.info(f"Model is {age_days:.1f} days old - retraining needed")
            return True

        logger.info(f"Model is {age_days:.1f} days old - no retraining needed")
        return False

    def get_model_info(self) -> dict:
        """
        Get information about the active model.

        Returns:
            Dictionary with model information
        """
        metadata = db_manager.get_active_model_metadata()

        if metadata is None:
            return {
                "exists": False,
                "version": None,
                "training_date": None,
                "age_days": None,
                "n_states": None,
                "bull_state": None,
                "bear_state": None,
            }

        age = datetime.utcnow() - metadata.training_date
        age_days = age.total_seconds() / 86400

        return {
            "exists": True,
            "version": metadata.model_version,
            "training_date": metadata.training_date,
            "age_days": age_days,
            "n_states": metadata.n_states,
            "bull_state": metadata.bull_state,
            "bear_state": metadata.bear_state,
            "convergence_score": metadata.convergence_score,
            "model_path": metadata.model_path,
        }

    def list_models(self) -> list:
        """
        List all saved models.

        Returns:
            List of model metadata dictionaries
        """
        session = db_manager.get_session()
        try:
            models = session.query(ModelMetadata).order_by(
                ModelMetadata.training_date.desc()
            ).all()

            return [
                {
                    "version": m.model_version,
                    "training_date": m.training_date,
                    "n_states": m.n_states,
                    "is_active": m.is_active,
                    "convergence_score": m.convergence_score,
                }
                for m in models
            ]
        finally:
            db_manager.close_session(session)

    def delete_old_models(self, keep_count: int = 5):
        """
        Delete old model files, keeping the most recent ones.

        Args:
            keep_count: Number of recent models to keep
        """
        try:
            session = db_manager.get_session()

            # Get all models ordered by date
            all_models = session.query(ModelMetadata).order_by(
                ModelMetadata.training_date.desc()
            ).all()

            # Delete old models
            if len(all_models) > keep_count:
                models_to_delete = all_models[keep_count:]

                for model in models_to_delete:
                    # Delete file
                    if os.path.exists(model.model_path):
                        os.remove(model.model_path)
                        logger.info(f"Deleted old model file: {model.model_path}")

                    # Delete metadata
                    session.delete(model)

                session.commit()
                logger.info(f"Deleted {len(models_to_delete)} old models")

        except Exception as e:
            logger.error(f"Error deleting old models: {e}")
            session.rollback()
        finally:
            db_manager.close_session(session)
