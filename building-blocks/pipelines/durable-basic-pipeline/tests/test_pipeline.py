import pytest
import sys
import os
from unittest.mock import MagicMock
import azure.durable_functions as df

# Add parent directory to sys.path so we can import function_app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from function_app import pipeline_orchestrator, update_pipeline_run_status, pipeline_step_activity

def test_pipeline_orchestrator():
    # Mock context
    context = MagicMock(spec=df.DurableOrchestrationContext)
    context.instance_id = "test-run-id"

    # Mock call_activity
    # orchestrator returns a generator
    gen = pipeline_orchestrator(context)

    # 1. Initialize Pipeline Run
    task1 = next(gen)
    assert context.call_activity.call_args_list[0][0][0] == "update_pipeline_run_status"
    assert context.call_activity.call_args_list[0][0][1]["status"] == "running"

    # 2. Execute Step 1
    task2 = gen.send(None)
    assert context.call_activity.call_args_list[1][0][0] == "pipeline_step_activity"
    assert context.call_activity.call_args_list[1][0][1]["name"] == "data_validation"

    # 3. Execute Step 2
    task3 = gen.send(None)
    assert context.call_activity.call_args_list[2][0][0] == "pipeline_step_activity"
    assert context.call_activity.call_args_list[2][0][1]["name"] == "ai_processing"

    # 4. Finalize Pipeline Run
    task4 = gen.send(None)
    assert context.call_activity.call_args_list[3][0][0] == "update_pipeline_run_status"
    assert context.call_activity.call_args_list[3][0][1]["status"] == "completed"

def test_update_pipeline_run_status_activity():
    status_data = {
        "id": "test-id",
        "status": "running"
    }
    result = update_pipeline_run_status(status_data)
    assert result is True

def test_pipeline_step_activity():
    step_data = {
        "run_id": "test-id",
        "name": "test-step"
    }
    result = pipeline_step_activity(step_data)
    assert result["run_id"] == "test-id"
    assert result["name"] == "test-step"
    assert result["status"] == "completed"
