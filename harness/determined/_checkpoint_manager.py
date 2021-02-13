import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import determined as det
from determined_common.api import request as req


class CheckpointManager:
    """
    CheckpointManager manages checkpoint creating and updating. It is responsible for
    handling the error and mark the checkpoints to be errored if anything fails.
    """

    def __init__(
        self,
        master_url: str,
        trial_id: int = 0,
        batch_number: int = 0,
        experiment_config: Optional[Dict[str, Any]] = None,
        experiment_id: int = 0,
        hparams: Optional[Dict[str, Any]] = None,
    ):
        self.master_url = master_url
        self.trial_id = trial_id
        self.batch_number = batch_number
        self.experiment_config = experiment_config
        self.experiment_id = experiment_id
        self.hparams = hparams
        self.start_time = datetime.now(timezone.utc)
        self.state = "STATE_ACTIVE"

    def __enter__(self) -> "CheckpointManager":
        logging.info(f"Saving checkpoint trial {self.trial_id} batch {self.batch_number}.")
        ckpt = {
            "trial_id": self.trial_id,
            "batch_number": self.batch_number,
            "start_time": self.start_time.astimezone(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "state": self.state,
            "experiment_config": self.experiment_config,
            "experiment_id": self.experiment_id,
            "hparams": self.hparams,
        }

        r = req.post(self.master_url, "/api/v1/checkpoints", body={"checkpoint": ckpt})
        if not hasattr(r, "headers"):
            raise Exception(r)
        return self

    def complete(
        self,
        uuid: str,
        resources: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        framework: Optional[str] = None,
        format: Optional[str] = None,
    ) -> None:
        logging.info(
            f"Finishing saving checkpoint {uuid} for "
            f"trial {self.trial_id} batch {self.batch_number}."
        )
        start_time = self.start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = (
            datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        ckpt = {
            "uuid": uuid,
            "trial_id": self.trial_id,
            "batch_number": self.batch_number,
            "start_time": start_time,
            "end_time": end_time,
            "state": "STATE_COMPLETED",
            "experiment_config": self.experiment_config,
            "experiment_id": self.experiment_id,
            "hparams": self.hparams,
            "resources": resources,
            "metadata": metadata,
            "determined_version": det.__version__,
            "framework": framework,
            "format": format,
        }

        r = req.put(self.master_url, "/api/v1/checkpoints", body={"checkpoint": ckpt})
        if not hasattr(r, "headers"):
            raise Exception(r)

        self.state = "STATE_COMPLETED"

    def failed(self) -> None:
        logging.info(
            f"Failed saving checkpoint for trial {self.trial_id} batch {self.batch_number}."
        )
        start_time = self.start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = (
            datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        ckpt = {
            "trial_id": self.trial_id,
            "batch_number": self.batch_number,
            "start_time": start_time,
            "end_time": end_time,
            "state": "STATE_ERRORED",
            "experiment_config": self.experiment_config,
            "experiment_id": self.experiment_id,
            "hparams": self.hparams,
            "determined_version": det.__version__,
            "format": format,
        }

        r = req.put(self.master_url, "/api/v1/checkpoints", body={"checkpoint": ckpt})
        if not hasattr(r, "headers"):
            raise Exception(r)

        self.state = "STATE_ERRORED"

    def __exit__(self, exc_type, exc_value, exc_traceback):  # type: ignore
        if self.state == "STATE_COMPLETED":
            return

        self.failed()
