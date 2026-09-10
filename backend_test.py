#!/usr/bin/env python3
"""
ACASO Omniverse Backend Testing - Round with Self-Scan, Local Node, Research Browser, Companion
"""
import requests
import sys
import json
import time
import base64
from io import BytesIO
from datetime import datetime

# Read backend URL from frontend/.env
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BASE_URL = line.split('=', 1)[1].strip() + '/api'
                break
except Exception as e:
    print(f"Could not read backend URL: {e}")
    sys.exit(1)

print(f"Testing backend at: {BASE_URL}")

class TestRunner:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failed_tests = []

    def test(self, name, fn):
        """Run a single test"""
        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        try:
            fn()
            self.tests_passed += 1
            print(f"✅ PASSED")
            return True
        except AssertionError as e:
            self.tests_failed += 1
            self.failed_tests.append({"name": name, "error": str(e)})
            print(f"❌ FAILED: {e}")
            return False
        except Exception as e:
            self.tests_failed += 1
            self.failed_tests.append({"name": name, "error": f"Exception: {e}"})
            print(f"❌ FAILED with exception: {e}")
            return False

    def summary(self):
        print(f"\n{'='*60}")
        print(f"📊 Test Summary")
        print(f"{'='*60}")
        print(f"Total: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {self.tests_failed} ❌")
        if self.failed_tests:
            print(f"\nFailed tests:")
            for ft in self.failed_tests:
                print(f"  - {ft['name']}: {ft['error']}")
        return 0 if self.tests_failed == 0 else 1

runner = TestRunner()

# ==================== SELF-SCAN TESTS ====================
print("\n" + "="*60)
print("SELF-SCAN TESTS")
print("="*60)

def test_self_scan_config_default():
    """GET /api/self/scan/config returns default values"""
    r = requests.get(f"{BASE_URL}/self/scan/config")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data['enabled'] == False, f"Expected enabled=false, got {data['enabled']}"
    assert data['interval_hours'] == 24, f"Expected interval_hours=24, got {data['interval_hours']}"
    assert data['running'] == False, f"Expected running=false, got {data['running']}"
    print(f"   Config: enabled={data['enabled']}, interval_hours={data['interval_hours']}, running={data['running']}")

runner.test("Self-scan config default values", test_self_scan_config_default)

def test_self_scan_config_enable():
    """PUT /api/self/scan/config enable with interval 12"""
    r = requests.put(f"{BASE_URL}/self/scan/config", json={"enabled": True, "interval_hours": 12})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data['enabled'] == True, f"Expected enabled=true, got {data['enabled']}"
    assert data['interval_hours'] == 12, f"Expected interval_hours=12, got {data['interval_hours']}"
    assert data['next_run_at'] is not None, f"Expected next_run_at to be set, got None"
    print(f"   Enabled: next_run_at={data['next_run_at']}")

runner.test("Self-scan config enable with interval 12", test_self_scan_config_enable)

def test_self_scan_config_invalid_interval():
    """PUT /api/self/scan/config with interval_hours=0 should return 400"""
    r = requests.put(f"{BASE_URL}/self/scan/config", json={"enabled": True, "interval_hours": 0})
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print(f"   Correctly rejected interval_hours=0")

runner.test("Self-scan config reject interval_hours=0", test_self_scan_config_invalid_interval)

def test_self_scan_config_disable():
    """PUT /api/self/scan/config disable"""
    r = requests.put(f"{BASE_URL}/self/scan/config", json={"enabled": False})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data['enabled'] == False, f"Expected enabled=false, got {data['enabled']}"
    assert data['next_run_at'] is None, f"Expected next_run_at=null, got {data['next_run_at']}"
    print(f"   Disabled: next_run_at={data['next_run_at']}")

runner.test("Self-scan config disable", test_self_scan_config_disable)

def test_self_scan_run():
    """POST /api/self/scan/run and verify no source modifications"""
    # Get git status before scan
    import subprocess
    before = subprocess.run(['git', 'status', '--short'], cwd='/app', capture_output=True, text=True).stdout
    
    print(f"   Running scan (may take up to 60s)...")
    r = requests.post(f"{BASE_URL}/self/scan/run", json={}, timeout=120)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data['status'] == 'done', f"Expected status=done, got {data['status']}"
    assert 'counts' in data, "Expected counts object"
    assert 'findings' in data, "Expected findings array"
    assert 'proposal_ids' in data, "Expected proposal_ids array"
    assert 'duration_s' in data, "Expected duration_s"
    
    counts = data['counts']
    print(f"   Scan results: critical={counts.get('critical', 0)}, high={counts.get('high', 0)}, low={counts.get('low', 0)}, info={counts.get('info', 0)}")
    print(f"   Proposals: {len(data['proposal_ids'])}, Duration: {data['duration_s']}s")
    
    # Check git status after scan
    after = subprocess.run(['git', 'status', '--short'], cwd='/app', capture_output=True, text=True).stdout
    
    # Filter out test_reports and backend_test.py changes
    before_filtered = '\n'.join([l for l in before.split('\n') if 'test_reports' not in l and 'backend_test.py' not in l])
    after_filtered = '\n'.join([l for l in after.split('\n') if 'test_reports' not in l and 'backend_test.py' not in l])
    
    assert before_filtered == after_filtered, f"Source files were modified by scan!\nBefore:\n{before_filtered}\nAfter:\n{after_filtered}"
    print(f"   ✓ No source files modified by scan")

runner.test("Self-scan run and verify no modifications", test_self_scan_run)

def test_self_scan_list():
    """GET /api/self/scans lists scans"""
    r = requests.get(f"{BASE_URL}/self/scans")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) > 0, "Expected at least one scan in history"
    print(f"   Found {len(data)} scan(s) in history")

runner.test("Self-scan list scans", test_self_scan_list)

# ==================== LOCAL NODE (OWNER SIDE) TESTS ====================
print("\n" + "="*60)
print("LOCAL NODE (OWNER SIDE) TESTS")
print("="*60)

def test_node_setup():
    """GET /api/node/setup returns protocol and download list"""
    r = requests.get(f"{BASE_URL}/node/setup")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data['protocol'] == 'node-1.0', f"Expected protocol=node-1.0, got {data['protocol']}"
    assert 'download' in data, "Expected download list"
    assert isinstance(data['download'], list), "Expected download to be a list"
    print(f"   Protocol: {data['protocol']}, Downloads: {len(data['download'])}")

runner.test("Node setup info", test_node_setup)

def test_node_list():
    """GET /api/node/nodes returns list (may be empty)"""
    r = requests.get(f"{BASE_URL}/node/nodes")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    print(f"   Found {len(data)} node(s)")

runner.test("Node list nodes", test_node_list)

def test_node_task_unknown_node():
    """POST /api/node/tasks for unknown node_id returns 404"""
    r = requests.post(f"{BASE_URL}/node/tasks", json={
        "node_id": "unknown-node-id-12345",
        "kind": "file_list",
        "params": {"path": "/tmp"}
    })
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"
    print(f"   Correctly returned 404 for unknown node")

runner.test("Node task for unknown node returns 404", test_node_task_unknown_node)

# ==================== LOCAL NODE (PROTOCOL WITH REAL CLIENT) TESTS ====================
print("\n" + "="*60)
print("LOCAL NODE (PROTOCOL WITH REAL CLIENT) TESTS")
print("="*60)

# Get API key first
def get_api_key():
    r = requests.get(f"{BASE_URL}/bridge/info")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    return r.json()['api_key']

api_key = get_api_key()
print(f"API Key obtained: {api_key[:20]}...")

# Clean up any previous test artifacts
import subprocess
subprocess.run(['rm', '-rf', '/tmp/acaso_ta_root'], capture_output=True)
subprocess.run(['rm', '-f', str(subprocess.run(['bash', '-c', 'echo ~/.acaso_node.json'], capture_output=True, text=True).stdout.strip())], capture_output=True)
subprocess.run(['mkdir', '-p', '/tmp/acaso_ta_root'], capture_output=True)

# Start the client in background
print("\n🚀 Starting Local Node client in background...")
client_cmd = f"ACASO_URL=http://localhost:8001 ACASO_KEY={api_key} timeout 150 python /app/handoff/local_node/acaso_node.py --root /tmp/acaso_ta_root --shell --name ta-node &"
subprocess.run(['bash', '-c', client_cmd])
print("   Client started, waiting 6s for registration...")
time.sleep(6)

node_id = None

def test_node_registered():
    """Node should appear in list with online=true"""
    global node_id
    r = requests.get(f"{BASE_URL}/node/nodes")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    nodes = r.json()
    assert len(nodes) > 0, "Expected at least one node"
    node = nodes[0]
    node_id = node['id']
    assert node['online'] == True, f"Expected online=true, got {node['online']}"
    assert 'files' in node['capabilities'], "Expected 'files' capability"
    assert 'shell' in node['capabilities'], "Expected 'shell' capability"
    assert '/tmp/acaso_ta_root' in node['allowed_roots'], "Expected /tmp/acaso_ta_root in allowed_roots"
    print(f"   Node registered: {node['name']} ({node_id[:8]})")
    print(f"   Capabilities: {node['capabilities']}")
    print(f"   Allowed roots: {node['allowed_roots']}")

runner.test("Node registered and online", test_node_registered)

def test_node_file_list():
    """POST file_list task (auto-approved, should complete)"""
    r = requests.post(f"{BASE_URL}/node/tasks", json={
        "node_id": node_id,
        "kind": "file_list",
        "params": {"path": "/tmp/acaso_ta_root"}
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    task = r.json()
    assert task['status'] == 'queued', f"Expected status=queued, got {task['status']}"
    assert task['requires_approval'] == False, f"Expected requires_approval=false"
    task_id = task['id']
    print(f"   Task created: {task_id[:8]}, status={task['status']}")
    
    # Wait for completion
    print(f"   Waiting 8s for task completion...")
    time.sleep(8)
    
    r = requests.get(f"{BASE_URL}/node/tasks/{task_id}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    task = r.json()
    assert task['status'] == 'done', f"Expected status=done, got {task['status']}"
    assert 'result' in task, "Expected result"
    assert 'items' in task['result'], "Expected result.items"
    print(f"   Task completed: {len(task['result']['items'])} items")

runner.test("Node file_list task", test_node_file_list)

def test_node_file_write_proposed():
    """POST file_write task (should be proposed, not auto-approved)"""
    r = requests.post(f"{BASE_URL}/node/tasks", json={
        "node_id": node_id,
        "kind": "file_write",
        "params": {"path": "/tmp/acaso_ta_root/a.txt", "content": "hello"}
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    task = r.json()
    assert task['status'] == 'proposed', f"Expected status=proposed, got {task['status']}"
    assert task['requires_approval'] == True, f"Expected requires_approval=true"
    task_id = task['id']
    print(f"   Task created: {task_id[:8]}, status={task['status']}")
    
    # Wait 6s and verify file does NOT exist yet
    print(f"   Waiting 6s and verifying file does NOT exist...")
    time.sleep(6)
    import os
    assert not os.path.exists('/tmp/acaso_ta_root/a.txt'), "File should not exist before approval"
    print(f"   ✓ File does not exist (correctly waiting for approval)")
    
    # Approve the task
    r = requests.post(f"{BASE_URL}/node/tasks/{task_id}/decision", json={"approved": True})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print(f"   Task approved")
    
    # Wait for completion
    print(f"   Waiting 8s for task completion...")
    time.sleep(8)
    
    # Verify file exists with correct content
    assert os.path.exists('/tmp/acaso_ta_root/a.txt'), "File should exist after approval"
    with open('/tmp/acaso_ta_root/a.txt', 'r') as f:
        content = f.read()
    assert content == 'hello', f"Expected content='hello', got '{content}'"
    print(f"   ✓ File created with correct content")
    
    # Verify task status
    r = requests.get(f"{BASE_URL}/node/tasks/{task_id}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    task = r.json()
    assert task['status'] == 'done', f"Expected status=done, got {task['status']}"

runner.test("Node file_write task (proposed, approved, executed)", test_node_file_write_proposed)

def test_node_file_write_outside_root():
    """POST file_write with path outside allowed roots returns 400"""
    r = requests.post(f"{BASE_URL}/node/tasks", json={
        "node_id": node_id,
        "kind": "file_write",
        "params": {"path": "/etc/hosts", "content": "test"}
    })
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print(f"   Correctly rejected path outside allowed roots")

runner.test("Node file_write outside allowed roots returns 400", test_node_file_write_outside_root)

def test_node_shell_task():
    """POST shell task (proposed, approve, execute)"""
    r = requests.post(f"{BASE_URL}/node/tasks", json={
        "node_id": node_id,
        "kind": "shell",
        "params": {"command": "echo ok-shell", "cwd": "/tmp/acaso_ta_root"}
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    task = r.json()
    assert task['status'] == 'proposed', f"Expected status=proposed, got {task['status']}"
    task_id = task['id']
    print(f"   Task created: {task_id[:8]}, status={task['status']}")
    
    # Approve
    r = requests.post(f"{BASE_URL}/node/tasks/{task_id}/decision", json={"approved": True})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print(f"   Task approved")
    
    # Wait for completion
    print(f"   Waiting 8s for task completion...")
    time.sleep(8)
    
    # Verify result
    r = requests.get(f"{BASE_URL}/node/tasks/{task_id}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    task = r.json()
    assert task['status'] == 'done', f"Expected status=done, got {task['status']}"
    assert 'result' in task, "Expected result"
    assert 'stdout' in task['result'], "Expected result.stdout"
    assert 'ok-shell' in task['result']['stdout'], f"Expected 'ok-shell' in stdout, got {task['result']['stdout']}"
    print(f"   ✓ Shell command executed: {task['result']['stdout'].strip()}")

runner.test("Node shell task", test_node_shell_task)

def test_node_browser_no_capability():
    """POST browser_open task should return 400 (node lacks browser capability)"""
    r = requests.post(f"{BASE_URL}/node/tasks", json={
        "node_id": node_id,
        "kind": "browser_open",
        "params": {"url": "https://example.com"}
    })
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert 'browser' in r.json()['detail'].lower(), "Expected error about browser capability"
    print(f"   Correctly rejected browser task (no capability)")

runner.test("Node browser_open without capability returns 400", test_node_browser_no_capability)

def test_node_decision_on_non_proposed():
    """POST decision on a done task returns 400"""
    # Get a done task
    r = requests.get(f"{BASE_URL}/node/tasks", params={"node_id": node_id, "status": "done", "limit": 1})
    tasks = r.json()
    if len(tasks) > 0:
        task_id = tasks[0]['id']
        r = requests.post(f"{BASE_URL}/node/tasks/{task_id}/decision", json={"approved": True})
        assert r.status_code == 400, f"Expected 400, got {r.status_code}"
        print(f"   Correctly rejected decision on done task")
    else:
        print(f"   Skipped (no done tasks)")

runner.test("Node decision on non-proposed task returns 400", test_node_decision_on_non_proposed)

def test_node_cancel_done_task():
    """POST cancel on a done task returns 400"""
    r = requests.get(f"{BASE_URL}/node/tasks", params={"node_id": node_id, "status": "done", "limit": 1})
    tasks = r.json()
    if len(tasks) > 0:
        task_id = tasks[0]['id']
        r = requests.post(f"{BASE_URL}/node/tasks/{task_id}/cancel")
        assert r.status_code == 400, f"Expected 400, got {r.status_code}"
        print(f"   Correctly rejected cancel on done task")
    else:
        print(f"   Skipped (no done tasks)")

runner.test("Node cancel done task returns 400", test_node_cancel_done_task)

def test_node_register_without_key():
    """POST /api/node/register without X-ACASO-Key returns 401"""
    r = requests.post(f"{BASE_URL}/node/register", json={
        "name": "test-node",
        "os": "Linux",
        "allowed_roots": ["/tmp"],
        "capabilities": ["files"]
    })
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print(f"   Correctly rejected registration without key")

runner.test("Node register without key returns 401", test_node_register_without_key)

def test_node_plan():
    """POST /api/node/plan generates tasks"""
    r = requests.post(f"{BASE_URL}/node/plan", json={
        "node_id": node_id,
        "goal": "create a folder notes inside my root and write hello.md in it"
    }, timeout=120)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    plan = r.json()
    assert 'tasks' in plan, "Expected tasks array"
    assert len(plan['tasks']) > 0, "Expected at least one task"
    print(f"   Plan created: {len(plan['tasks'])} task(s)")
    print(f"   Summary: {plan.get('summary', '')}")
    
    # All tasks should be proposed
    for t in plan['tasks']:
        if 'status' in t:
            assert t['status'] == 'proposed', f"Expected status=proposed, got {t['status']}"
    
    # Reject all tasks
    for t in plan['tasks']:
        if 'id' in t:
            r = requests.post(f"{BASE_URL}/node/tasks/{t['id']}/decision", json={"approved": False})
            assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print(f"   All tasks rejected")

runner.test("Node plan tasks", test_node_plan)

# Clean up node
print("\n🧹 Cleaning up Local Node...")
subprocess.run(['pkill', '-f', 'acaso_node.py'], capture_output=True)
time.sleep(2)
subprocess.run(['rm', '-rf', '/tmp/acaso_ta_root'], capture_output=True)
home_dir = subprocess.run(['bash', '-c', 'echo ~'], capture_output=True, text=True).stdout.strip()
subprocess.run(['rm', '-f', f'{home_dir}/.acaso_node.json'], capture_output=True)

if node_id:
    r = requests.delete(f"{BASE_URL}/node/nodes/{node_id}")
    if r.status_code == 200:
        print(f"   Node deleted: {node_id[:8]}")

# ==================== RESEARCH BROWSER TESTS ====================
print("\n" + "="*60)
print("RESEARCH BROWSER TESTS")
print("="*60)

def test_browse_research_valid():
    """POST /api/browse/research with valid URL and question"""
    print(f"   Fetching page (may take 30s)...")
    r = requests.post(f"{BASE_URL}/browse/research", json={
        "url": "https://www.sba.gov/funding-programs/grants",
        "question": "Who does SBA give grants to?",
        "screenshot": True
    }, timeout=60)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data['title'], "Expected non-empty title"
    assert data['http_status'] == 200, f"Expected http_status=200, got {data['http_status']}"
    assert data['chars'] > 500, f"Expected chars > 500, got {data['chars']}"
    assert isinstance(data['links'], list), "Expected links array"
    assert isinstance(data['forms'], list), "Expected forms array"
    assert data['screenshot_b64'], "Expected non-empty screenshot_b64"
    assert 'answer' in data, "Expected answer object"
    assert data['answer']['text'], "Expected non-empty answer text"
    assert data['answer']['model_label'], "Expected model_label"
    print(f"   Page loaded: {data['title']}")
    print(f"   HTTP {data['http_status']}, {data['chars']} chars, {len(data['links'])} links, {len(data['forms'])} forms")
    print(f"   Answer: {data['answer']['text'][:100]}...")

runner.test("Research browser with valid URL", test_browse_research_valid)

def test_browse_research_invalid_url():
    """POST /api/browse/research with invalid URL returns 502"""
    r = requests.post(f"{BASE_URL}/browse/research", json={
        "url": "not a url at all",
        "screenshot": False
    }, timeout=60)
    assert r.status_code == 502, f"Expected 502, got {r.status_code}"
    print(f"   Correctly returned 502 for invalid URL")

runner.test("Research browser with invalid URL returns 502", test_browse_research_invalid_url)

def test_browse_history():
    """GET /api/browse/history lists pages"""
    r = requests.get(f"{BASE_URL}/browse/history")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) > 0, "Expected at least one page in history"
    print(f"   Found {len(data)} page(s) in history")

runner.test("Research browser history", test_browse_history)

# ==================== COMPANION TESTS ====================
print("\n" + "="*60)
print("COMPANION TESTS")
print("="*60)

def test_companion_empty_message():
    """POST /api/companion/chat with empty message and no image returns 400"""
    r = requests.post(f"{BASE_URL}/companion/chat", json={
        "message": "",
        "session_id": "test-empty"
    })
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print(f"   Correctly rejected empty message")

runner.test("Companion empty message returns 400", test_companion_empty_message)

def test_companion_with_image():
    """POST /api/companion/chat with message and image"""
    # Generate test image with PIL
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("   Skipped (PIL not available)")
        return
    
    # Create image with number 7421
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw large text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        font = ImageFont.load_default()
    
    draw.text((100, 100), "7421", fill='black', font=font)
    
    # Draw some shapes
    draw.rectangle([50, 50, 150, 100], outline='red', width=3)
    draw.ellipse([250, 150, 350, 250], outline='blue', width=3)
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    image_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    print(f"   Sending message with image (may take time for vision model)...")
    r = requests.post(f"{BASE_URL}/companion/chat", json={
        "message": "What number is written in this image?",
        "image_b64": image_b64,
        "session_id": "ta-comp"
    }, stream=True, timeout=120)
    
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert 'text/event-stream' in r.headers.get('content-type', ''), "Expected text/event-stream"
    
    # Parse SSE stream
    events = []
    full_content = ""
    for line in r.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    event = json.loads(line[6:])
                    events.append(event)
                    if event['type'] == 'delta':
                        full_content += event['content']
                    elif event['type'] == 'done':
                        full_content = event.get('content', full_content)
                except:
                    pass
    
    # Verify events
    assert len(events) > 0, "Expected at least one event"
    assert events[0]['type'] == 'session', f"Expected first event type=session, got {events[0]['type']}"
    assert events[-1]['type'] == 'done', f"Expected last event type=done, got {events[-1]['type']}"
    assert events[-1]['model_label'], "Expected model_label in done event"
    
    # Verify content mentions 7421
    assert '7421' in full_content or '7,421' in full_content, f"Expected content to mention 7421, got: {full_content}"
    print(f"   ✓ Response mentions 7421: {full_content[:100]}...")
    print(f"   Model: {events[-1]['model_label']}")

runner.test("Companion with message and image", test_companion_with_image)

def test_companion_history():
    """GET /api/companion/history returns messages"""
    r = requests.get(f"{BASE_URL}/companion/history", params={"session_id": "ta-comp"})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) == 2, f"Expected 2 messages (user + assistant), got {len(data)}"
    assert data[0]['role'] == 'user', f"Expected first message role=user, got {data[0]['role']}"
    assert data[0]['had_image'] == True, f"Expected user message had_image=true"
    assert data[1]['role'] == 'assistant', f"Expected second message role=assistant, got {data[1]['role']}"
    print(f"   Found {len(data)} messages in history")

runner.test("Companion history", test_companion_history)

def test_companion_clear():
    """DELETE /api/companion/history clears messages"""
    r = requests.delete(f"{BASE_URL}/companion/history", params={"session_id": "ta-comp"})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    
    # Verify cleared
    r = requests.get(f"{BASE_URL}/companion/history", params={"session_id": "ta-comp"})
    data = r.json()
    assert len(data) == 0, f"Expected 0 messages after clear, got {len(data)}"
    print(f"   History cleared")

runner.test("Companion clear history", test_companion_clear)

# ==================== REGRESSION TESTS ====================
print("\n" + "="*60)
print("REGRESSION TESTS")
print("="*60)

def test_radar_sources():
    """GET /api/radar/sources returns 3 sources"""
    r = requests.get(f"{BASE_URL}/radar/sources")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert len(data) == 3, f"Expected 3 sources, got {len(data)}"
    print(f"   Found {len(data)} sources")

runner.test("Radar sources", test_radar_sources)

def test_acaso_presets():
    """GET /api/acaso/presets returns 3 presets"""
    r = requests.get(f"{BASE_URL}/acaso/presets")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert len(data) == 3, f"Expected 3 presets, got {len(data)}"
    print(f"   Found {len(data)} presets")

runner.test("ACASO presets", test_acaso_presets)

def test_missions_list():
    """GET /api/missions returns list"""
    r = requests.get(f"{BASE_URL}/missions")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    print(f"   Found {len(data)} mission(s)")

runner.test("Missions list", test_missions_list)

# ==================== SUMMARY ====================
sys.exit(runner.summary())
