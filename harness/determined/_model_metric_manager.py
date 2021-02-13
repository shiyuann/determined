import logging
from datetime import datetime, timezone
from typing import Any, Dict

from determined import util
from determined_common.api import request as req


class TrainingMetricManager:
    """
    TrainingMetricManager manages training metrics creating and updating. It is responsible for
    handling the error and mark the training metrics to be errored if anything fails.
    """

    def __init__(
        self,
        master_url: str,
        experiment_id: int = 0,
        trial_id: int = 0,
        step_id: int = 0,
        start_batch: int = 0,
        end_batch: int = 0,
    ):
        self.master_url = master_url
        self.experiment_id = experiment_id
        self.trial_id = trial_id
        self.step_id = step_id
        self.start_batch = start_batch
        self.end_batch = end_batch
        self.start_time = datetime.now(timezone.utc)
        self.state = "STATE_ACTIVE"

    def __enter__(self) -> "TrainingMetricManager":
        logging.info(
            f"Saving training metrics for trial {self.trial_id} step {self.step_id} "
            f"batch {self.start_batch} to {self.end_batch}."
        )
        training_metrics = {
            "experiment_id": self.experiment_id,
            "trial_id": self.trial_id,
            "step_id": self.step_id,
            "start_batch": self.start_batch,
            "end_batch": self.end_batch,
            "start_time": self.start_time.astimezone(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "state": self.state,
        }

        r = req.post(
            self.master_url,
            "/api/v1/training_metrics",
            body={"training_metrics": training_metrics},
        )
        if not hasattr(r, "headers"):
            raise Exception(r)
        return self

    def complete(self, metrics: Dict[str, Any]) -> None:
        logging.info(
            f"Finishing saving training metrics for trial {self.trial_id} "
            f"step {self.step_id} batch {self.start_batch} to {self.end_batch}."
        )
        start_time = self.start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = (
            datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        training_metrics = {
            "experiment_id": self.experiment_id,
            "trial_id": self.trial_id,
            "step_id": self.step_id,
            "start_batch": self.start_batch,
            "end_batch": self.end_batch,
            "start_time": start_time,
            "end_time": end_time,
            "state": "STATE_COMPLETED",
            "metrics": util.make_serializable(metrics),
        }

        r = req.put(
            self.master_url,
            "/api/v1/training_metrics",
            body={"training_metrics": training_metrics},
        )
        if not hasattr(r, "headers"):
            raise Exception(r)

        self.state = "STATE_COMPLETED"

    def failed(self) -> None:
        logging.info(
            f"Failed saving training metrics for trial {self.trial_id} "
            f"step {self.step_id} batch {self.start_batch} to {self.end_batch}."
        )
        start_time = self.start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = (
            datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        training_metrics = {
            "experiment_id": self.experiment_id,
            "trial_id": self.trial_id,
            "step_id": self.step_id,
            "start_batch": self.start_batch,
            "end_batch": self.end_batch,
            "start_time": start_time,
            "end_time": end_time,
            "metrics": {},
            "state": "STATE_ERRORED",
        }

        r = req.put(
            self.master_url,
            "/api/v1/training_metrics",
            body={"training_metrics": training_metrics},
        )
        if not hasattr(r, "headers"):
            raise Exception(r)

        self.state = "STATE_ERRORED"

    def __exit__(self, exc_type, exc_value, exc_traceback):  # type: ignore
        if self.state == "STATE_COMPLETED":
            return

        self.failed()


class ValidationMetricManager:
    """
    ValidationMetricManager manages validation metrics creating and updating. It is responsible for
    handling the error and mark the validation metrics to be errored if anything fails.
    """

    def __init__(
        self,
        master_url: str,
        experiment_id: int = 0,
        trial_id: int = 0,
        total_batches: int = 0,
    ):
        self.master_url = master_url
        self.experiment_id = experiment_id
        self.trial_id = trial_id
        self.total_batches = total_batches
        self.start_time = datetime.now(timezone.utc)
        self.state = "STATE_ACTIVE"

    def __enter__(self) -> "ValidationMetricManager":
        logging.info(
            f"Saving validation metrics for trial {self.trial_id} batch {self.total_batches}."
        )
        training_metrics = {
            "trial_id": self.trial_id,
            "total_batches": self.total_batches,
            "start_time": self.start_time.astimezone(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "state": self.state,
        }

        r = req.post(
            self.master_url,
            "/api/v1/validation_metrics",
            body={"validation_metrics": training_metrics},
        )
        if not hasattr(r, "headers"):
            raise Exception(r)
        return self

    def complete(self, metrics: Dict[str, Any]) -> None:
        logging.info(
            f"Finishing saving validation metrics for "
            f"trial {self.trial_id} batch {self.total_batches}."
        )
        start_time = self.start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = (
            datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        validation_metrics = {
            "experiment_id": self.experiment_id,
            "trial_id": self.trial_id,
            "total_batches": self.total_batches,
            "start_time": start_time,
            "end_time": end_time,
            "state": "STATE_COMPLETED",
            "metrics": util.make_serializable(metrics),
        }

        r = req.put(
            self.master_url,
            "/api/v1/validation_metrics",
            body={"validation_metrics": validation_metrics},
        )
        if not hasattr(r, "headers"):
            raise Exception(r)

        self.state = "STATE_COMPLETED"

    def failed(self) -> None:
        logging.info(
            f"Failed saving training metrics for trial {self.trial_id} batch {self.total_batches}."
        )
        start_time = self.start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = (
            datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        validation_metrics = {
            "experiment_id": self.experiment_id,
            "trial_id": self.trial_id,
            "total_batches": self.total_batches,
            "start_time": start_time,
            "end_time": end_time,
            "metrics": {},
            "state": "STATE_ERRORED",
        }

        r = req.put(
            self.master_url,
            "/api/v1/validation_metrics",
            body={"validation_metrics": validation_metrics},
        )
        if not hasattr(r, "headers"):
            raise Exception(r)

        self.state = "STATE_ERRORED"

    def __exit__(self, exc_type, exc_value, exc_traceback):  # type: ignore
        if self.state == "STATE_COMPLETED":
            return

        self.failed()
