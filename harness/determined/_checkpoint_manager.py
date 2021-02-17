import logging
import pathlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import determined as det
from determined_common import storage
from determined_common.api import request as req


class CheckpointManager:
    """
    CheckpointManager manages checkpoint creating and updating. It is responsible for
    handling the error and mark the checkpoints to be errored if anything fails.
    """

    def __init__(
        self,
        master_url: str,
        storage_mgr: storage.StorageManager,
        trial_id: int = 0,
        batch_number: int = 0,
        experiment_config: Optional[Dict[str, Any]] = None,
        experiment_id: int = 0,
        hparams: Optional[Dict[str, Any]] = None,
    ):
        self.master_url = master_url
        self.storage_mgr = storage_mgr
        self._storage_ctx = self.storage_mgr.store_path()

        self.trial_id = trial_id
        self.batch_number = batch_number
        self.experiment_config = experiment_config
        self.experiment_id = experiment_id
        self.hparams = hparams
        self.start_time = datetime.now(timezone.utc)
        self.state = "STATE_ACTIVE"

    def __enter__(self) -> "CheckpointManager":
        logging.info(f"Saving checkpoint trial {self.trial_id} batch {self.batch_number}.")

        self.storage_id, self.storage_path = next(self._storage_ctx)

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

    def complete(self, checkpoint_info: Dict[str, Any]) -> storage.StorageMetadata:
        logging.info(
            f"Finishing saving checkpoint {self.storage_id} for "
            f"trial {self.trial_id} batch {self.batch_number}."
        )

        metadata = storage.StorageMetadata(
            self.storage_id,
            storage.StorageManager._list_directory(pathlib.Path(self.storage_path)),
            checkpoint_info.get("framework", ""),
            checkpoint_info.get("format", ""),
        )

        start_time = self.start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time = (
            datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        ckpt = {
            "uuid": metadata.storage_id,
            "trial_id": self.trial_id,
            "batch_number": self.batch_number,
            "start_time": start_time,
            "end_time": end_time,
            "state": "STATE_COMPLETED",
            "experiment_config": self.experiment_config,
            "experiment_id": self.experiment_id,
            "hparams": self.hparams,
            "resources": metadata.resources,
            "metadata": metadata.__dict__,
            "determined_version": det.__version__,
            "framework": metadata.framework,
            "format": metadata.format,
        }

        r = req.put(self.master_url, "/api/v1/checkpoints", body={"checkpoint": ckpt})
        if not hasattr(r, "headers"):
            raise Exception(r)

        self.state = "STATE_COMPLETED"

        return metadata

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
        try:
            next(self._storage_ctx)
        except StopIteration:
            pass

        if self.state == "STATE_COMPLETED":
            return

        self.failed()
