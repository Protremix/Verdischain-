"""
Tests for EvolvixOS Agent Orchestration Engine + API
"""

import pytest
import asyncio
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestration_engine import (
    WorkflowRegistry, WorkflowExecutor, Workflow, WorkflowStep,
    WorkflowStatus, StepStatus, StepType, WorkflowTemplate
)
from orchestration_api import app


# =========================================================================
# Workflow Model Tests
# =========================================================================

class TestWorkflowModels:
    def test_workflow_step_creation(self):
        step = WorkflowStep(id="s1", name="Test", step_type=StepType.LOG)
        assert step.id == "s1"
        assert step.name == "Test"
        assert step.step_type == StepType.LOG
        assert step.status == StepStatus.PENDING

    def test_workflow_step_to_dict(self):
        step = WorkflowStep(id="s1", name="Test", step_type=StepType.LOG)
        d = step.to_dict()
        assert d["step_type"] == "log"
        assert d["status"] == "pending"

    def test_workflow_creation(self):
        step = WorkflowStep(id="s1", name="Step1", step_type=StepType.LOG)
        wf = Workflow(id="wf1", name="Test WF", description="Test", steps=[step])
        assert wf.id == "wf1"
        assert wf.status == WorkflowStatus.PENDING
        assert len(wf.steps) == 1

    def test_workflow_to_dict(self):
        step = WorkflowStep(id="s1", name="Step1", step_type=StepType.LOG)
        wf = Workflow(id="wf1", name="Test", description="Desc", steps=[step])
        d = wf.to_dict()
        assert d["status"] == "pending"
        assert len(d["steps"]) == 1

    def test_step_types(self):
        assert StepType.AGENT_TASK.value == "agent_task"
        assert StepType.GATEWAY_CALL.value == "gateway_call"
        assert StepType.CONDITION.value == "condition"
        assert StepType.LOG.value == "log"
        assert StepType.WAIT.value == "wait"

    def test_workflow_statuses(self):
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.RUNNING.value == "running"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"


# =========================================================================
# Workflow Registry Tests
# =========================================================================

class TestWorkflowRegistry:
    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.mark.asyncio
    async def test_create_workflow(self, registry):
        wf = await registry.create_workflow(
            name="Test",
            description="Test workflow",
            step_defs=[
                {"name": "Step1", "step_type": "log", "config": {"message": "hello"}},
            ],
        )
        assert wf.name == "Test"
        assert len(wf.steps) == 1
        assert wf.steps[0].step_type == StepType.LOG
        assert wf.status == WorkflowStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_workflow(self, registry):
        wf = await registry.create_workflow(
            name="Get Test",
            description="",
            step_defs=[{"name": "S1", "step_type": "log"}],
        )
        retrieved = await registry.get_workflow(wf.id)
        assert retrieved is not None
        assert retrieved.name == "Get Test"

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, registry):
        result = await registry.get_workflow("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_workflows(self, registry):
        await registry.create_workflow("W1", "", [{"name": "S1", "step_type": "log"}])
        await registry.create_workflow("W2", "", [{"name": "S2", "step_type": "log"}])
        all_wfs = await registry.list_workflows()
        assert len(all_wfs) >= 2

    @pytest.mark.asyncio
    async def test_list_workflows_by_status(self, registry):
        wf = await registry.create_workflow("Status Test", "", [{"name": "S", "step_type": "log"}])
        wf.status = WorkflowStatus.COMPLETED
        completed = await registry.list_workflows(status="completed")
        assert any(w.id == wf.id for w in completed)

    @pytest.mark.asyncio
    async def test_delete_workflow(self, registry):
        wf = await registry.create_workflow("Delete", "", [{"name": "S", "step_type": "log"}])
        deleted = await registry.delete_workflow(wf.id)
        assert deleted == True
        assert await registry.get_workflow(wf.id) is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, registry):
        deleted = await registry.delete_workflow("nonexistent")
        assert deleted == False

    @pytest.mark.asyncio
    async def test_default_templates(self, registry):
        templates = await registry.list_templates()
        assert len(templates) >= 4

    @pytest.mark.asyncio
    async def test_get_template(self, registry):
        template = await registry.get_template("code-review-pipeline")
        assert template is not None
        assert template.name == "Code Review Pipeline"
        assert len(template.step_definitions) == 3

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, registry):
        template = await registry.get_template("nonexistent")
        assert template is None

    @pytest.mark.asyncio
    async def test_create_from_template(self, registry):
        wf = await registry.create_from_template(
            "code-review-pipeline",
            input_data={"code": "print('hello')"},
        )
        assert wf.name == "Code Review Pipeline"
        assert len(wf.steps) == 3
        assert wf.metadata["template_id"] == "code-review-pipeline"


# =========================================================================
# Workflow Executor Tests
# =========================================================================

class TestWorkflowExecutor:
    @pytest.fixture
    def setup(self):
        reg = WorkflowRegistry()
        exec_ = WorkflowExecutor(reg)
        return reg, exec_

    @pytest.mark.asyncio
    async def test_execute_log_steps(self, setup):
        reg, exec_ = setup
        wf = await reg.create_workflow(
            "Log Test", "",
            [
                {"name": "Log1", "step_type": "log", "config": {"message": "hello"}},
                {"name": "Log2", "step_type": "log", "config": {"message": "world"}, "depends_on": ["Log1"]},
            ],
        )
        result = await exec_.execute(wf.id)
        assert result["status"] == "completed"
        assert result["steps"][0]["status"] == "completed"
        assert result["steps"][1]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_execute_parallel(self, setup):
        reg, exec_ = setup
        wf = await reg.create_workflow(
            "Parallel Test", "",
            [
                {"name": "A", "step_type": "log", "config": {"message": "a"}},
                {"name": "B", "step_type": "log", "config": {"message": "b"}},
                {"name": "C", "step_type": "log", "config": {"message": "c"}, "depends_on": ["A", "B"]},
            ],
        )
        result = await exec_.execute(wf.id)
        assert result["status"] == "completed"
        # A and B should complete before C
        c_step = [s for s in result["steps"] if s["name"] == "C"][0]
        assert c_step["status"] == "completed"

    @pytest.mark.asyncio
    async def test_execute_wait_step(self, setup):
        reg, exec_ = setup
        wf = await reg.create_workflow(
            "Wait Test", "",
            [
                {"name": "Wait", "step_type": "wait", "config": {"seconds": 0.1}},
                {"name": "Log", "step_type": "log", "depends_on": ["Wait"]},
            ],
        )
        result = await exec_.execute(wf.id)
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_execute_condition_true(self, setup):
        reg, exec_ = setup
        wf = await reg.create_workflow(
            "Condition Test", "",
            [
                {"name": "Log", "step_type": "log", "config": {"message": "test"}},
                {"name": "Check", "step_type": "condition", "config": {"condition": "True"}, "depends_on": ["Log"]},
            ],
        )
        result = await exec_.execute(wf.id)
        assert result["status"] == "completed"
        check_step = [s for s in result["steps"] if s["name"] == "Check"][0]
        assert check_step["output_data"]["condition_met"] == True

    @pytest.mark.asyncio
    async def test_execute_condition_false(self, setup):
        reg, exec_ = setup
        wf = await reg.create_workflow(
            "Condition False", "",
            [
                {"name": "Check", "step_type": "condition", "config": {"condition": "False"}},
            ],
        )
        result = await exec_.execute(wf.id)
        assert result["status"] == "completed"
        check_step = [s for s in result["steps"] if s["name"] == "Check"][0]
        assert check_step["output_data"]["condition_met"] == False

    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, setup):
        reg, exec_ = setup
        with pytest.raises(ValueError):
            await exec_.execute("nonexistent")

    @pytest.mark.asyncio
    async def test_cancel_workflow(self, setup):
        reg, exec_ = setup
        wf = await reg.create_workflow("Cancel Test", "", [
            {"name": "Wait", "step_type": "wait", "config": {"seconds": 10}},
        ])
        # Start execution in background
        task = asyncio.create_task(exec_.execute(wf.id))
        await asyncio.sleep(0.1)  # let it start
        cancelled = await exec_.cancel(wf.id)
        assert cancelled == True
        # Cancel the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_executor_stats(self, setup):
        reg, exec_ = setup
        wf = await reg.create_workflow("Stats", "", [{"name": "S", "step_type": "log"}])
        await exec_.execute(wf.id)
        stats = exec_.stats
        assert stats["total_executed"] >= 1
        assert stats["running"] == 0

    @pytest.mark.asyncio
    async def test_step_output_propagation(self, setup):
        reg, exec_ = setup
        wf = await reg.create_workflow(
            "Output Propagation", "",
            [
                {"name": "Producer", "step_type": "log", "config": {"message": "data"}},
                {"name": "Consumer", "step_type": "log", "config": {"message": "consume"}, "depends_on": ["Producer"]},
            ],
        )
        result = await exec_.execute(wf.id)
        assert result["status"] == "completed"
        # Global context should contain step outputs
        assert "Producer_output" in result["global_context"]

    @pytest.mark.asyncio
    async def test_transform_step(self, setup):
        reg, exec_ = setup
        wf = await reg.create_workflow(
            "Transform Test", "",
            [
                {"name": "Log", "step_type": "log", "config": {"message": "val"}},
                {"name": "Transform", "step_type": "transform", "config": {"map": {"result": "logged"}}, "depends_on": ["Log"]},
            ],
        )
        result = await exec_.execute(wf.id)
        assert result["status"] == "completed"


# =========================================================================
# Orchestration API Tests
# =========================================================================

class TestOrchestrationAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_stats(self, client):
        resp = client.get("/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "executor" in data
        assert "total_templates" in data

    def test_list_templates(self, client):
        resp = client.get("/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 4

    def test_get_template(self, client):
        resp = client.get("/templates/code-review-pipeline")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Code Review Pipeline"

    def test_get_template_not_found(self, client):
        resp = client.get("/templates/nonexistent")
        assert resp.status_code == 404

    def test_create_workflow(self, client):
        resp = client.post("/workflows", json={
            "name": "API Test Workflow",
            "description": "Test",
            "steps": [
                {"name": "Step1", "step_type": "log", "config": {"message": "test"}},
            ],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "API Test Workflow"
        assert len(data["steps"]) == 1

    def test_list_workflows(self, client):
        client.post("/workflows", json={
            "name": "List Test",
            "description": "",
            "steps": [{"name": "S", "step_type": "log"}],
        })
        resp = client.get("/workflows")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1

    def test_get_workflow(self, client):
        create = client.post("/workflows", json={
            "name": "Get Test",
            "description": "",
            "steps": [{"name": "S", "step_type": "log"}],
        })
        wf_id = create.json()["id"]
        resp = client.get(f"/workflows/{wf_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == wf_id

    def test_get_workflow_not_found(self, client):
        resp = client.get("/workflows/nonexistent")
        assert resp.status_code == 404

    def test_delete_workflow(self, client):
        create = client.post("/workflows", json={
            "name": "Delete Test",
            "description": "",
            "steps": [{"name": "S", "step_type": "log"}],
        })
        wf_id = create.json()["id"]
        resp = client.delete(f"/workflows/{wf_id}")
        assert resp.status_code == 200
        assert resp.json()["success"] == True

    def test_delete_not_found(self, client):
        resp = client.delete("/workflows/nonexistent")
        assert resp.status_code == 404

    def test_execute_workflow(self, client):
        create = client.post("/workflows", json={
            "name": "Execute Test",
            "description": "",
            "steps": [
                {"name": "Log", "step_type": "log", "config": {"message": "exec"}},
            ],
        })
        wf_id = create.json()["id"]
        resp = client.post(f"/workflows/{wf_id}/execute")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"

    def test_execute_workflow_not_found(self, client):
        resp = client.post("/workflows/nonexistent/execute")
        assert resp.status_code == 400

    def test_instantiate_template(self, client):
        resp = client.post("/templates/instantiate", json={
            "template_id": "code-review-pipeline",
            "input_data": {"code": "x=1"},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Code Review Pipeline"
        assert len(data["steps"]) == 3

    def test_instantiate_template_not_found(self, client):
        resp = client.post("/templates/instantiate", json={
            "template_id": "nonexistent",
        })
        assert resp.status_code == 400

    def test_list_steps(self, client):
        create = client.post("/workflows", json={
            "name": "Steps Test",
            "description": "",
            "steps": [
                {"name": "A", "step_type": "log"},
                {"name": "B", "step_type": "log", "depends_on": ["A"]},
            ],
        })
        wf_id = create.json()["id"]
        resp = client.get(f"/workflows/{wf_id}/steps")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2

    def test_get_step(self, client):
        create = client.post("/workflows", json={
            "name": "Step Get",
            "description": "",
            "steps": [{"name": "OnlyStep", "step_type": "log"}],
        })
        wf_id = create.json()["id"]
        step_id = create.json()["steps"][0]["id"]
        resp = client.get(f"/workflows/{wf_id}/steps/{step_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "OnlyStep"

    def test_get_step_not_found(self, client):
        create = client.post("/workflows", json={
            "name": "Step NF",
            "description": "",
            "steps": [{"name": "S", "step_type": "log"}],
        })
        wf_id = create.json()["id"]
        resp = client.get(f"/workflows/{wf_id}/steps/nonexistent")
        assert resp.status_code == 404
