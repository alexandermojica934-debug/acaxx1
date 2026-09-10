#!/usr/bin/env python3
"""
ACASO Omniverse Backend Test Suite - Self-Directive Scan & Local Node
Tests Self-Directive scan, Local Node system, and server-side research browser.
"""
import requests
import sys
import time
import json
from datetime import datetime

BASE_URL = "https://contest-ready-app.preview.emergentagent.com/api"

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.bridge_key = None
        self.node_id = None
        self.task_ids = []
        
    def test(self, name, fn):
        """Run a test function and track results"""
        print(f"\n{'='*70}")
        print(f"TEST: {name}")
        print('='*70)
        try:
            fn()
            self.passed += 1
            self.tests.append({"name": name, "status": "PASS"})
            print(f"✅ PASS: {name}")
        except AssertionError as e:
            self.failed += 1
            self.tests.append({"name": name, "status": "FAIL", "error": str(e)})
            print(f"❌ FAIL: {name}")
            print(f"   Error: {e}")
        except Exception as e:
            self.failed += 1
            self.tests.append({"name": name, "status": "ERROR", "error": str(e)})
            print(f"💥 ERROR: {name}")
            print(f"   Exception: {e}")
    
    def summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print(f"\n{'='*70}")
        print(f"TEST SUMMARY")
        print('='*70)
        print(f"Total: {total} | Passed: {self.passed} | Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100) if total > 0 else 0:.1f}%")
        if self.failed > 0:
            print("\nFailed tests:")
            for t in self.tests:
                if t["status"] != "PASS":
                    print(f"  - {t['name']}: {t.get('error', 'Unknown error')}")
        return 0 if self.failed == 0 else 1


runner = TestRunner()

# ============================================================================
# SELF-DIRECTIVE SCAN TESTS
# ============================================================================

def test_scan_config_default():
    """GET /api/self/scan/config returns enabled false by default"""
    r = requests.get(f"{BASE_URL}/self/scan/config")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "enabled" in data, "Missing 'enabled' field"
    assert "interval_hours" in data, "Missing 'interval_hours' field"
    assert "running" in data, "Missing 'running' field"
    assert data["running"] == False, "running should be false initially"
    print(f"   Config: enabled={data['enabled']}, interval={data['interval_hours']}h, running={data['running']}")

def test_scan_config_enable():
    """PUT /api/self/scan/config with enabled:true, interval_hours:12"""
    r = requests.put(f"{BASE_URL}/self/scan/config", json={"enabled": True, "interval_hours": 12})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["enabled"] == True, "enabled should be true"
    assert data["interval_hours"] == 12, f"interval should be 12, got {data['interval_hours']}"
    assert data["next_run_at"] is not None, "next_run_at should be set when enabled"
    print(f"   Enabled: interval={data['interval_hours']}h, next_run={data['next_run_at']}")

def test_scan_config_invalid_interval():
    """PUT /api/self/scan/config with interval_hours:0 returns 400"""
    r = requests.put(f"{BASE_URL}/self/scan/config", json={"interval_hours": 0})
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print(f"   Correctly rejected interval_hours=0")

def test_scan_config_disable():
    """PUT /api/self/scan/config with enabled:false sets next_run_at to null"""
    r = requests.put(f"{BASE_URL}/self/scan/config", json={"enabled": False})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["enabled"] == False, "enabled should be false"
    assert data["next_run_at"] is None, "next_run_at should be null when disabled"
    print(f"   Disabled: next_run_at={data['next_run_at']}")

def test_scan_run():
    """POST /api/self/scan/run returns status done with counts and findings"""
    print("   Running self-scan (may take 5-10s)...")
    r = requests.post(f"{BASE_URL}/self/scan/run", timeout=60)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "done", f"Expected status 'done', got {data['status']}"
    assert "counts" in data, "Missing 'counts' field"
    assert "findings" in data, "Missing 'findings' field"
    assert "proposal_ids" in data, "Missing 'proposal_ids' field"
    assert "duration_s" in data, "Missing 'duration_s' field"
    counts = data["counts"]
    print(f"   Scan complete: {counts.get('critical', 0)} critical, {counts.get('high', 0)} high, {counts.get('low', 0)} low")
    print(f"   Proposals: {len(data['proposal_ids'])}, Duration: {data['duration_s']:.2f}s")

def test_scan_list():
    """GET /api/self/scans lists scans"""
    r = requests.get(f"{BASE_URL}/self/scans")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), "Expected list of scans"
    assert len(data) > 0, "Should have at least one scan from previous test"
    print(f"   Found {len(data)} scan(s)")

# ============================================================================
# LOCAL NODE SETUP & REGISTRATION TESTS
# ============================================================================

def test_node_setup():
    """GET /api/node/setup returns protocol and download list"""
    r = requests.get(f"{BASE_URL}/node/setup")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["protocol"] == "node-1.0", f"Expected protocol 'node-1.0', got {data['protocol']}"
    assert "download" in data, "Missing 'download' field"
    assert isinstance(data["download"], list), "download should be a list"
    assert "/local-node/acaso_node.py" in data["download"], "Missing acaso_node.py in downloads"
    print(f"   Protocol: {data['protocol']}, Downloads: {len(data['download'])}")

def test_bridge_key():
    """GET /api/bridge/info returns api_key"""
    r = requests.get(f"{BASE_URL}/bridge/info")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "api_key" in data, "Missing 'api_key' field"
    runner.bridge_key = data["api_key"]
    print(f"   Bridge key: {runner.bridge_key[:20]}...")

def test_node_register_no_key():
    """POST /api/node/register WITHOUT X-ACASO-Key returns 401"""
    r = requests.post(f"{BASE_URL}/node/register", json={"name": "test", "os": "Linux", "allowed_roots": [], "capabilities": []})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print(f"   Correctly rejected request without key")

def test_node_register_with_key():
    """POST /api/node/register WITH key returns node doc"""
    assert runner.bridge_key, "Bridge key not fetched"
    headers = {"X-ACASO-Key": runner.bridge_key}
    body = {
        "name": "test-node",
        "os": "Linux",
        "allowed_roots": ["/tmp/tn_root"],
        "capabilities": ["files", "shell"]
    }
    r = requests.post(f"{BASE_URL}/node/register", headers=headers, json=body)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "id" in data, "Missing 'id' field"
    assert data["name"] == "test-node", f"Expected name 'test-node', got {data['name']}"
    assert "/tmp/tn_root" in data["allowed_roots"], "Missing /tmp/tn_root in allowed_roots"
    assert "files" in data["capabilities"], "Missing 'files' capability"
    assert "shell" in data["capabilities"], "Missing 'shell' capability"
    runner.node_id = data["id"]
    print(f"   Registered node: {data['id'][:8]}... with roots={data['allowed_roots']}")

# ============================================================================
# LOCAL NODE TASK TESTS (without real node client)
# ============================================================================

def test_task_create_readonly():
    """POST /api/node/tasks with kind:file_list returns status queued, requires_approval false"""
    assert runner.node_id, "Node not registered"
    body = {
        "node_id": runner.node_id,
        "kind": "file_list",
        "params": {"path": "/tmp/tn_root"}
    }
    r = requests.post(f"{BASE_URL}/node/tasks", json=body)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "queued", f"Expected status 'queued', got {data['status']}"
    assert data["requires_approval"] == False, "Read-only task should not require approval"
    runner.task_ids.append(data["id"])
    print(f"   Created read-only task: {data['id'][:8]}... status={data['status']}")

def test_task_create_write():
    """POST /api/node/tasks with kind:file_write returns status proposed, requires_approval true"""
    assert runner.node_id, "Node not registered"
    body = {
        "node_id": runner.node_id,
        "kind": "file_write",
        "params": {"path": "/tmp/tn_root/a.txt", "content": "hello"}
    }
    r = requests.post(f"{BASE_URL}/node/tasks", json=body)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "proposed", f"Expected status 'proposed', got {data['status']}"
    assert data["requires_approval"] == True, "Write task should require approval"
    runner.task_ids.append(data["id"])
    print(f"   Created write task: {data['id'][:8]}... status={data['status']}")

def test_task_outside_root():
    """POST /api/node/tasks with path outside allowed root returns 400"""
    assert runner.node_id, "Node not registered"
    body = {
        "node_id": runner.node_id,
        "kind": "file_read",
        "params": {"path": "/etc/hosts"}
    }
    r = requests.post(f"{BASE_URL}/node/tasks", json=body)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert "outside" in r.text.lower(), "Error should mention path is outside allowed roots"
    print(f"   Correctly rejected path outside allowed roots")

def test_task_missing_capability():
    """POST /api/node/tasks with browser_open on node without browser capability returns 400"""
    assert runner.node_id, "Node not registered"
    body = {
        "node_id": runner.node_id,
        "kind": "browser_open",
        "params": {"url": "https://example.com", "session_id": "test"}
    }
    r = requests.post(f"{BASE_URL}/node/tasks", json=body)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert "browser" in r.text.lower(), "Error should mention missing browser capability"
    print(f"   Correctly rejected browser task on node without browser capability")

def test_task_invalid_kind():
    """POST /api/node/tasks with kind:bogus returns 400"""
    assert runner.node_id, "Node not registered"
    body = {
        "node_id": runner.node_id,
        "kind": "bogus",
        "params": {}
    }
    r = requests.post(f"{BASE_URL}/node/tasks", json=body)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print(f"   Correctly rejected invalid kind")

def test_task_browser_fill_submit():
    """POST /api/node/tasks with browser_fill and submit:true returns 400"""
    assert runner.node_id, "Node not registered"
    body = {
        "node_id": runner.node_id,
        "kind": "browser_fill",
        "params": {"session_id": "test", "submit": True}
    }
    r = requests.post(f"{BASE_URL}/node/tasks", json=body)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert "never submits" in r.text.lower() or "submit" in r.text.lower(), "Error should mention submit not allowed"
    print(f"   Correctly rejected browser_fill with submit=true")

def test_task_shell():
    """POST /api/node/tasks with kind:shell returns proposed"""
    assert runner.node_id, "Node not registered"
    body = {
        "node_id": runner.node_id,
        "kind": "shell",
        "params": {"command": "echo tn-ok", "cwd": "/tmp/tn_root"}
    }
    r = requests.post(f"{BASE_URL}/node/tasks", json=body)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "proposed", f"Expected status 'proposed', got {data['status']}"
    runner.task_ids.append(data["id"])
    print(f"   Created shell task: {data['id'][:8]}... status={data['status']}")

def test_task_decision_approve():
    """POST /api/node/tasks/{id}/decision with approved:true changes status to queued"""
    # Find a proposed task
    proposed = [tid for tid in runner.task_ids if tid]
    if not proposed:
        print("   ⚠️  No proposed tasks to approve")
        return
    tid = proposed[-1]  # Use the last one (shell task)
    r = requests.post(f"{BASE_URL}/node/tasks/{tid}/decision", json={"approved": True})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "queued", f"Expected status 'queued', got {data['status']}"
    print(f"   Approved task {tid[:8]}... -> status={data['status']}")

def test_task_decision_reject():
    """POST /api/node/tasks/{id}/decision with approved:false changes status to rejected"""
    # Create a new task to reject
    body = {
        "node_id": runner.node_id,
        "kind": "file_write",
        "params": {"path": "/tmp/tn_root/reject.txt", "content": "test"}
    }
    r = requests.post(f"{BASE_URL}/node/tasks", json=body)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    tid = r.json()["id"]
    
    r = requests.post(f"{BASE_URL}/node/tasks/{tid}/decision", json={"approved": False})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "rejected", f"Expected status 'rejected', got {data['status']}"
    print(f"   Rejected task {tid[:8]}... -> status={data['status']}")

def test_task_cancel():
    """POST /api/node/tasks/{id}/cancel on queued task returns ok"""
    # Create a new queued task
    body = {
        "node_id": runner.node_id,
        "kind": "file_list",
        "params": {"path": "/tmp/tn_root"}
    }
    r = requests.post(f"{BASE_URL}/node/tasks", json=body)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    tid = r.json()["id"]
    
    r = requests.post(f"{BASE_URL}/node/tasks/{tid}/cancel")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert r.json()["ok"] == True, "Expected ok:true"
    print(f"   Cancelled task {tid[:8]}...")

def test_task_result_no_key():
    """POST /api/node/tasks/{id}/result WITHOUT key returns 401"""
    tid = runner.task_ids[0] if runner.task_ids else "fake-id"
    r = requests.post(f"{BASE_URL}/node/tasks/{tid}/result", json={"status": "done"})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print(f"   Correctly rejected result post without key")

def test_task_list_filter():
    """GET /api/node/tasks?node_id=&status=proposed filters correctly"""
    assert runner.node_id, "Node not registered"
    r = requests.get(f"{BASE_URL}/node/tasks", params={"node_id": runner.node_id, "status": "proposed"})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), "Expected list of tasks"
    # All tasks should be proposed
    for task in data:
        assert task["status"] == "proposed", f"Expected all tasks to be proposed, got {task['status']}"
    print(f"   Found {len(data)} proposed task(s)")

def test_task_get_with_audit():
    """GET /api/node/tasks/{id} includes audit array"""
    tid = runner.task_ids[0] if runner.task_ids else None
    if not tid:
        print("   ⚠️  No tasks to test")
        return
    r = requests.get(f"{BASE_URL}/node/tasks/{tid}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "audit" in data, "Missing 'audit' field"
    assert isinstance(data["audit"], list), "audit should be a list"
    print(f"   Task {tid[:8]}... has {len(data['audit'])} audit entries")

# ============================================================================
# LOCAL NODE PLAN TEST (ONE CALL ONLY)
# ============================================================================

def test_node_plan():
    """POST /api/node/plan creates tasks (ONE CALL)"""
    assert runner.node_id, "Node not registered"
    body = {
        "node_id": runner.node_id,
        "goal": "create a folder notes inside /tmp/tn_root and write hello.md in it"
    }
    print("   Planning tasks (may take 10-20s with LLM)...")
    r = requests.post(f"{BASE_URL}/node/plan", json=body, timeout=120)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "id" in data, "Missing plan 'id' field"
    assert "tasks" in data, "Missing 'tasks' field"
    assert isinstance(data["tasks"], list), "tasks should be a list"
    assert len(data["tasks"]) > 0, "Plan should have at least one task"
    print(f"   Plan created: {len(data['tasks'])} task(s)")
    for task in data["tasks"]:
        status = task.get("status", "unknown")
        print(f"     - {task.get('kind', 'unknown')}: {task.get('title', 'no title')} [{status}]")

# ============================================================================
# SERVER-SIDE RESEARCH BROWSER TEST (ONE CALL ONLY)
# ============================================================================

def test_browse_research():
    """POST /api/browse/research returns page data (ONE CALL)"""
    body = {
        "url": "https://www.grants.gov",
        "question": "What is this site for?",
        "screenshot": True
    }
    print("   Researching page (may take 20-40s)...")
    r = requests.post(f"{BASE_URL}/browse/research", json=body, timeout=120)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "title" in data, "Missing 'title' field"
    assert data["title"], "title should not be empty"
    assert "http_status" in data, "Missing 'http_status' field"
    assert data["http_status"] == 200, f"Expected http_status 200, got {data['http_status']}"
    assert "chars" in data, "Missing 'chars' field"
    assert data["chars"] > 0, "chars should be > 0"
    assert "links" in data, "Missing 'links' field"
    assert isinstance(data["links"], list), "links should be a list"
    assert "forms" in data, "Missing 'forms' field"
    assert isinstance(data["forms"], list), "forms should be a list"
    assert "screenshot_b64" in data, "Missing 'screenshot_b64' field"
    assert data["screenshot_b64"], "screenshot_b64 should not be empty"
    assert "answer" in data, "Missing 'answer' field"
    assert data["answer"], "answer should not be empty"
    assert "text" in data["answer"], "answer should have 'text' field"
    print(f"   Page: {data['title']}, {data['chars']} chars, {len(data['links'])} links, {len(data['forms'])} forms")
    print(f"   Answer: {data['answer']['text'][:100]}...")

def test_browse_history():
    """GET /api/browse/history lists pages without screenshot_b64"""
    r = requests.get(f"{BASE_URL}/browse/history")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), "Expected list of pages"
    assert len(data) > 0, "Should have at least one page from previous test"
    # Verify screenshot_b64 is not included
    for page in data:
        assert "screenshot_b64" not in page, "screenshot_b64 should not be in history list"
    print(f"   Found {len(data)} page(s) in history")

def test_browse_invalid_url():
    """POST /api/browse/research with invalid URL returns 502"""
    body = {
        "url": "not a url at all",
        "screenshot": False
    }
    r = requests.post(f"{BASE_URL}/browse/research", json=body, timeout=60)
    assert r.status_code == 502, f"Expected 502, got {r.status_code}"
    print(f"   Correctly handled invalid URL with 502")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

def main():
    print("\n" + "="*70)
    print("ACASO OMNIVERSE - SELF-DIRECTIVE & LOCAL NODE TEST SUITE")
    print("="*70)
    
    # Self-Directive Scan Tests
    print("\n" + "="*70)
    print("SELF-DIRECTIVE SCAN TESTS")
    print("="*70)
    runner.test("Scan config default", test_scan_config_default)
    runner.test("Scan config enable", test_scan_config_enable)
    runner.test("Scan config invalid interval", test_scan_config_invalid_interval)
    runner.test("Scan config disable", test_scan_config_disable)
    runner.test("Scan run", test_scan_run)
    runner.test("Scan list", test_scan_list)
    
    # Local Node Setup & Registration Tests
    print("\n" + "="*70)
    print("LOCAL NODE SETUP & REGISTRATION TESTS")
    print("="*70)
    runner.test("Node setup", test_node_setup)
    runner.test("Bridge key", test_bridge_key)
    runner.test("Node register no key", test_node_register_no_key)
    runner.test("Node register with key", test_node_register_with_key)
    
    # Local Node Task Tests
    print("\n" + "="*70)
    print("LOCAL NODE TASK TESTS")
    print("="*70)
    runner.test("Task create readonly", test_task_create_readonly)
    runner.test("Task create write", test_task_create_write)
    runner.test("Task outside root", test_task_outside_root)
    runner.test("Task missing capability", test_task_missing_capability)
    runner.test("Task invalid kind", test_task_invalid_kind)
    runner.test("Task browser fill submit", test_task_browser_fill_submit)
    runner.test("Task shell", test_task_shell)
    runner.test("Task decision approve", test_task_decision_approve)
    runner.test("Task decision reject", test_task_decision_reject)
    runner.test("Task cancel", test_task_cancel)
    runner.test("Task result no key", test_task_result_no_key)
    runner.test("Task list filter", test_task_list_filter)
    runner.test("Task get with audit", test_task_get_with_audit)
    
    # Local Node Plan Test (ONE CALL)
    print("\n" + "="*70)
    print("LOCAL NODE PLAN TEST (ONE LLM CALL)")
    print("="*70)
    runner.test("Node plan", test_node_plan)
    
    # Server-side Research Browser Tests (ONE CALL)
    print("\n" + "="*70)
    print("SERVER-SIDE RESEARCH BROWSER TESTS (ONE LLM CALL)")
    print("="*70)
    runner.test("Browse research", test_browse_research)
    runner.test("Browse history", test_browse_history)
    runner.test("Browse invalid URL", test_browse_invalid_url)
    
    return runner.summary()

if __name__ == "__main__":
    sys.exit(main())
