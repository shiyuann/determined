package internal

import (
	"context"

	"github.com/pkg/errors"
	log "github.com/sirupsen/logrus"

	"github.com/determined-ai/determined/master/pkg/model"
	"github.com/determined-ai/determined/proto/pkg/apiv1"
)

func (a *apiServer) CreateTrainingMetrics(
	_ context.Context, req *apiv1.CreateTrainingMetricsRequest,
) (*apiv1.CreateTrainingMetricsResponse, error) {
	log.Infof("adding training metrics %s (trial %d, batch %d to %d)",
		req.TrainingMetrics.Uuid, req.TrainingMetrics.TrialId,
		req.TrainingMetrics.StartBatch, req.TrainingMetrics.EndBatch)
	modelT, err := model.TrainingMetricsFromProto(req.TrainingMetrics)
	if err != nil {
		return nil, errors.Wrapf(
			err, "error adding training metrics %s (trial %d, batch %d to %d) in database",
			req.TrainingMetrics.Uuid, req.TrainingMetrics.TrialId,
			req.TrainingMetrics.StartBatch, req.TrainingMetrics.EndBatch)
	}
	err = a.m.db.AddStep(modelT)
	return &apiv1.CreateTrainingMetricsResponse{TrainingMetrics: req.TrainingMetrics},
		errors.Wrapf(err,
			"error adding training metrics %s (trial %d, batch %d to %d) in database",
			req.TrainingMetrics.Uuid, req.TrainingMetrics.TrialId,
			req.TrainingMetrics.StartBatch, req.TrainingMetrics.EndBatch)
}

func (a *apiServer) UpdateTrainingMetrics(
	_ context.Context, req *apiv1.UpdateTrainingMetricsRequest,
) (*apiv1.UpdateTrainingMetricsResponse, error) {
	log.Infof("updating training metrics %s (trial %d, batch %d to %d) state %s",
		req.TrainingMetrics.Uuid, req.TrainingMetrics.TrialId,
		req.TrainingMetrics.StartBatch, req.TrainingMetrics.EndBatch, req.TrainingMetrics.State)
	modelS, err := model.TrainingMetricsFromProto(req.TrainingMetrics)
	if err != nil {
		return nil, errors.Wrapf(
			err, "error updating training metrics %s (trial %d, batch %d to %d) in database",
			req.TrainingMetrics.Uuid, req.TrainingMetrics.TrialId,
			req.TrainingMetrics.StartBatch, req.TrainingMetrics.EndBatch)
	}
	err = a.m.db.UpdateStep(
		int(req.TrainingMetrics.TrialId), int(req.TrainingMetrics.EndBatch), *modelS)
	return &apiv1.UpdateTrainingMetricsResponse{TrainingMetrics: req.TrainingMetrics},
		errors.Wrapf(err,
			"error updating training metrics %s (trial %d, batch %d to %d) in database",
			req.TrainingMetrics.Uuid, req.TrainingMetrics.TrialId,
			req.TrainingMetrics.StartBatch, req.TrainingMetrics.EndBatch)
}

func (a *apiServer) CreateValidationMetrics(
	_ context.Context, req *apiv1.CreateValidationMetricsRequest,
) (*apiv1.CreateValidationMetricsResponse, error) {
	log.Infof("adding validation metrics %s (trial %d, batch %d)",
		req.ValidationMetrics.Uuid, req.ValidationMetrics.TrialId, req.ValidationMetrics.TotalBatches)
	modelV, err := model.ValidationMetricsFromProto(req.ValidationMetrics)
	if err != nil {
		return nil, errors.Wrapf(
			err, "error adding validation metrics %s (trial %d, batch %d) in database",
			req.ValidationMetrics.Uuid, req.ValidationMetrics.TrialId,
			req.ValidationMetrics.TotalBatches)
	}
	err = a.m.db.AddValidation(modelV)
	return &apiv1.CreateValidationMetricsResponse{ValidationMetrics: req.ValidationMetrics},
		errors.Wrapf(err, "error adding validation metrics %s (trial %d, batch %d) in database",
			req.ValidationMetrics.Uuid, req.ValidationMetrics.TrialId,
			req.ValidationMetrics.TotalBatches)
}

func (a *apiServer) UpdateValidationMetrics(
	_ context.Context, req *apiv1.UpdateValidationMetricsRequest,
) (*apiv1.UpdateValidationMetricsResponse, error) {
	log.Infof("updating validation metrics %s (trial %d, batch %d) state %s",
		req.ValidationMetrics.Uuid, req.ValidationMetrics.TrialId,
		req.ValidationMetrics.TotalBatches, req.ValidationMetrics.State)
	modelV, err := model.ValidationMetricsFromProto(req.ValidationMetrics)
	if err != nil {
		return nil, errors.Wrapf(
			err, "error updating validation metrics %s (trial %d, batch %d) in database",
			req.ValidationMetrics.Uuid, req.ValidationMetrics.TrialId,
			req.ValidationMetrics.TotalBatches)
	}
	err = a.m.db.UpdateValidation(
		int(req.ValidationMetrics.TrialId), int(req.ValidationMetrics.TotalBatches), *modelV)
	return &apiv1.UpdateValidationMetricsResponse{ValidationMetrics: req.ValidationMetrics},
		errors.Wrapf(err,
			"error updating validation metrics %s (trial %d, batch %d) in database",
			req.ValidationMetrics.Uuid, req.ValidationMetrics.TrialId,
			req.ValidationMetrics.TotalBatches)
}
