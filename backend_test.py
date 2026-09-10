#!/usr/bin/env python3
"""
ACASO Omniverse Backend Test - Companion Watch Mode + Apex Nexus
LLM Budget: MAX 2 /api/companion/watch calls, ONE /api/apex/generate call (prompt_library, count 10)
"""
import requests
import sys
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Get backend URL from frontend .env
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contest-ready-app.preview.emergentagent.com')
API = f"{BACKEND_URL}/api"

class TestRunner:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.llm_calls = {"watch": 0, "generate": 0}
        self.deliverable_id = None
        self.order_id = None
        self.unlock_token = None
        self.api_key = None

    def test(self, name, fn):
        """Run a test function"""
        self.tests_run += 1
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print('='*60)
        try:
            fn()
            self.tests_passed += 1
            print(f"✅ PASSED: {name}")
            return True
        except AssertionError as e:
            self.tests_failed += 1
            print(f"❌ FAILED: {name}")
            print(f"   Assertion: {e}")
            return False
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ ERROR: {name}")
            print(f"   Exception: {e}")
            return False

    def assert_eq(self, actual, expected, msg=""):
        if actual != expected:
            raise AssertionError(f"{msg} Expected {expected}, got {actual}")
        print(f"   ✓ {msg}: {actual}")

    def assert_in(self, item, container, msg=""):
        if item not in container:
            raise AssertionError(f"{msg} Expected {item} in {container}")
        print(f"   ✓ {msg}: {item} found")

    def assert_true(self, condition, msg=""):
        if not condition:
            raise AssertionError(f"{msg} Expected True, got {condition}")
        print(f"   ✓ {msg}")

    def assert_status(self, response, expected_status, msg=""):
        if response.status_code != expected_status:
            print(f"   Response body: {response.text[:500]}")
            raise AssertionError(f"{msg} Expected status {expected_status}, got {response.status_code}")
        print(f"   ✓ Status {response.status_code}")

    def create_test_image(self, text, bg_color="white", text_color="black", width=800, height=600):
        """Create a test image with text"""
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a larger font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Draw text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill=text_color, font=font)
        
        # Add some visual features (bars for dashboard)
        if "Weekly Report" in text:
            # Draw some bars
            bar_width = 60
            bar_spacing = 100
            for i in range(5):
                bar_height = 100 + i * 40
                x_pos = 100 + i * bar_spacing
                draw.rectangle([x_pos, height - bar_height - 50, x_pos + bar_width, height - 50], fill="blue")
        
        # Convert to base64 JPEG
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return base64.b64encode(buffer.getvalue()).decode()

    # ==================== COMPANION WATCH MODE TESTS ====================
    
    def test_watch_empty_image(self):
        """WATCH: POST /api/companion/watch with empty image_b64 -> 400"""
        r = requests.post(f"{API}/companion/watch", json={"image_b64": ""})
        self.assert_status(r, 400, "Empty image should return 400")

    def test_watch_error_frame(self):
        """WATCH: Error frame -> notable true, kind 'error', message mentions error"""
        if self.llm_calls["watch"] >= 2:
            print("⚠️  SKIPPED: LLM budget exhausted (2 watch calls max)")
            return
        
        self.llm_calls["watch"] += 1
        error_img = self.create_test_image(
            "ERROR: Build failed\nModuleNotFoundError: httpx",
            bg_color="red",
            text_color="white"
        )
        
        r = requests.post(f"{API}/companion/watch", json={
            "image_b64": error_img,
            "session_id": "ta-watch"
        }, timeout=60)
        self.assert_status(r, 200, "Watch error frame")
        
        data = r.json()
        self.assert_eq(data.get("notable"), True, "notable should be true for error")
        self.assert_eq(data.get("kind"), "error", "kind should be 'error'")
        self.assert_true(len(data.get("message", "")) > 0, "message should be non-empty")
        self.assert_true("error" in data.get("message", "").lower() or "httpx" in data.get("message", "").lower(), 
                        "message should mention error or httpx")
        self.assert_true(len(data.get("summary", "")) > 0, "summary should be non-empty")
        self.assert_true(len(data.get("model_label", "")) > 0, "model_label should be non-empty")
        print(f"   Message: {data.get('message')[:100]}")

    def test_watch_calm_frame(self):
        """WATCH: Calm dashboard -> notable false, kind 'none', message ''"""
        if self.llm_calls["watch"] >= 2:
            print("⚠️  SKIPPED: LLM budget exhausted (2 watch calls max)")
            return
        
        self.llm_calls["watch"] += 1
        dashboard_img = self.create_test_image(
            "Weekly Report",
            bg_color="lightblue",
            text_color="darkblue"
        )
        
        r = requests.post(f"{API}/companion/watch", json={
            "image_b64": dashboard_img,
            "session_id": "ta-watch-calm"
        }, timeout=60)
        self.assert_status(r, 200, "Watch calm frame")
        
        data = r.json()
        self.assert_eq(data.get("notable"), False, "notable should be false for calm dashboard")
        self.assert_eq(data.get("kind"), "none", "kind should be 'none'")
        self.assert_eq(data.get("message"), "", "message should be empty")
        print(f"   Summary: {data.get('summary', '')[:100]}")

    def test_watch_history(self):
        """WATCH: History API with session_id returns watch messages"""
        r = requests.get(f"{API}/companion/history", params={"session_id": "ta-watch"})
        self.assert_status(r, 200, "Get watch history")
        
        messages = r.json()
        self.assert_true(isinstance(messages, list), "History should be a list")
        
        # Find assistant messages with watch=true
        watch_msgs = [m for m in messages if m.get("role") == "assistant" and m.get("watch") == True]
        self.assert_true(len(watch_msgs) >= 1, f"Should have at least 1 watch message, got {len(watch_msgs)}")
        print(f"   Found {len(watch_msgs)} watch message(s)")

    def test_watch_history_delete(self):
        """WATCH: DELETE clears history"""
        r = requests.delete(f"{API}/companion/history", params={"session_id": "ta-watch"})
        self.assert_status(r, 200, "Delete watch history")
        
        # Verify cleared
        r = requests.get(f"{API}/companion/history", params={"session_id": "ta-watch"})
        messages = r.json()
        self.assert_eq(len(messages), 0, "History should be empty after delete")

    # ==================== APEX CATALOG TESTS ====================
    
    def test_apex_products(self):
        """APEX: GET /api/apex/products returns 3 products"""
        r = requests.get(f"{API}/apex/products")
        self.assert_status(r, 200, "Get Apex products")
        
        data = r.json()
        products = data.get("products", [])
        self.assert_eq(len(products), 3, "Should have 3 products")
        
        # Check product IDs
        product_ids = [p["id"] for p in products]
        self.assert_in("rfp_kit", product_ids, "rfp_kit product")
        self.assert_in("prompt_library", product_ids, "prompt_library product")
        self.assert_in("seo_pack", product_ids, "seo_pack product")
        
        # Check each product has required fields
        for p in products:
            self.assert_true("price_usd" in p, f"{p['id']} has price_usd")
            self.assert_true("tagline" in p, f"{p['id']} has tagline")
            self.assert_true("vector" in p, f"{p['id']} has vector")
        
        # Check payments
        payments = data.get("payments", {})
        self.assert_eq(payments.get("provider"), "manual", "Payment provider should be manual")
        self.assert_eq(payments.get("stripe_configured"), False, "Stripe should not be configured")
        self.assert_true("STRIPE_API_KEY" in payments.get("note", ""), "Note should mention STRIPE_API_KEY")

    # ==================== APEX GENERATE VALIDATION TESTS ====================
    
    def test_apex_generate_invalid_product(self):
        """APEX: Generate with invalid product -> 400"""
        r = requests.post(f"{API}/apex/generate", json={"product": "bogus"})
        self.assert_status(r, 400, "Invalid product should return 400")

    def test_apex_generate_prompt_library_no_domain(self):
        """APEX: Generate prompt_library without domain -> 400"""
        r = requests.post(f"{API}/apex/generate", json={"product": "prompt_library", "inputs": {}})
        self.assert_status(r, 400, "prompt_library without domain should return 400")

    def test_apex_generate_seo_pack_missing_fields(self):
        """APEX: Generate seo_pack without required fields -> 400"""
        r = requests.post(f"{API}/apex/generate", json={
            "product": "seo_pack",
            "inputs": {"business": "x"}
        })
        self.assert_status(r, 400, "seo_pack without service and city_region should return 400")

    def test_apex_generate_rfp_kit_no_input(self):
        """APEX: Generate rfp_kit without opportunity_id or rfp_text -> 400"""
        r = requests.post(f"{API}/apex/generate", json={"product": "rfp_kit", "inputs": {}})
        self.assert_status(r, 400, "rfp_kit without opportunity_id or rfp_text should return 400")

    def test_apex_generate_prompt_library(self):
        """APEX: Generate prompt_library (ONE LLM call)"""
        if self.llm_calls["generate"] >= 1:
            print("⚠️  SKIPPED: LLM budget exhausted (1 generate call max)")
            return
        
        self.llm_calls["generate"] += 1
        print("   Generating prompt library (this takes 20-40s)...")
        
        r = requests.post(f"{API}/apex/generate", json={
            "product": "prompt_library",
            "inputs": {
                "domain": "courier dispatch operations",
                "audience": "dispatchers",
                "use_cases": "delay notices, damage claims",
                "count": 10
            }
        }, timeout=120)
        self.assert_status(r, 200, "Generate prompt_library")
        
        data = r.json()
        self.deliverable_id = data.get("id")
        self.api_key = data.get("api_key")
        
        self.assert_true(len(data.get("id", "")) > 0, "Should have id")
        self.assert_true("Prompt Library" in data.get("title", ""), "Title should contain 'Prompt Library'")
        self.assert_true(len(data.get("markdown", "")) > 1500, f"Markdown should be > 1500 chars, got {len(data.get('markdown', ''))}")
        
        prompts = data.get("data", {}).get("prompts", [])
        self.assert_true(8 <= len(prompts) <= 12, f"Should have 8-12 prompts, got {len(prompts)}")
        
        self.assert_true(len(data.get("api_key", "")) == 32, f"API key should be 32 hex chars, got {len(data.get('api_key', ''))}")
        self.assert_true(isinstance(data.get("placeholders"), int), "placeholders should be int")
        self.assert_true(len(data.get("model_label", "")) > 0, "model_label should be non-empty")
        self.assert_true(isinstance(data.get("duration_s"), (int, float)), "duration_s should be numeric")
        
        print(f"   Generated: {data.get('title')}")
        print(f"   Prompts: {len(prompts)}")
        print(f"   Duration: {data.get('duration_s')}s")

    def test_apex_deliverables_list(self):
        """APEX: GET /api/apex/deliverables lists without markdown"""
        r = requests.get(f"{API}/apex/deliverables")
        self.assert_status(r, 200, "List deliverables")
        
        deliverables = r.json()
        self.assert_true(isinstance(deliverables, list), "Should return a list")
        
        if len(deliverables) > 0:
            d = deliverables[0]
            self.assert_true("markdown" not in d, "List should not include markdown field")
            self.assert_true("id" in d, "Should have id")
            self.assert_true("title" in d, "Should have title")

    def test_apex_deliverable_get(self):
        """APEX: GET /api/apex/deliverables/{id} includes markdown and data"""
        if not self.deliverable_id:
            print("⚠️  SKIPPED: No deliverable_id from generate test")
            return
        
        r = requests.get(f"{API}/apex/deliverables/{self.deliverable_id}")
        self.assert_status(r, 200, "Get deliverable")
        
        data = r.json()
        self.assert_true("markdown" in data, "Should include markdown")
        self.assert_true("data" in data, "Should include data")
        self.assert_true(len(data.get("markdown", "")) > 0, "Markdown should be non-empty")

    def test_apex_deliverable_export_md(self):
        """APEX: Export deliverable as markdown"""
        if not self.deliverable_id:
            print("⚠️  SKIPPED: No deliverable_id from generate test")
            return
        
        r = requests.get(f"{API}/apex/deliverables/{self.deliverable_id}/export", params={"fmt": "md"})
        self.assert_status(r, 200, "Export as markdown")
        self.assert_true("text/markdown" in r.headers.get("Content-Type", ""), "Content-Type should be text/markdown")
        self.assert_true("attachment" in r.headers.get("Content-Disposition", ""), "Should have attachment header")
        self.assert_true("ACASO Apex Nexus" in r.text, "Should contain 'ACASO Apex Nexus'")

    def test_apex_deliverable_export_json(self):
        """APEX: Export deliverable as JSON"""
        if not self.deliverable_id:
            print("⚠️  SKIPPED: No deliverable_id from generate test")
            return
        
        r = requests.get(f"{API}/apex/deliverables/{self.deliverable_id}/export", params={"fmt": "json"})
        self.assert_status(r, 200, "Export as JSON")
        self.assert_eq(r.headers.get("Content-Type"), "application/json", "Content-Type should be application/json")
        
        data = r.json()
        self.assert_true("data" in data, "Should have data field")
        self.assert_true("prompts" in data.get("data", {}), "data should have prompts")

    # ==================== APEX ORDERS TESTS ====================
    
    def test_apex_order_invalid_email(self):
        """APEX: Create order with invalid email -> 400"""
        r = requests.post(f"{API}/apex/orders", json={
            "product": "prompt_library",
            "buyer_email": "bad"
        })
        self.assert_status(r, 400, "Invalid email should return 400")

    def test_apex_order_create(self):
        """APEX: Create order with valid data"""
        if not self.deliverable_id:
            print("⚠️  SKIPPED: No deliverable_id from generate test")
            return
        
        r = requests.post(f"{API}/apex/orders", json={
            "product": "prompt_library",
            "buyer_email": "buyer@test.com",
            "deliverable_id": self.deliverable_id
        })
        self.assert_status(r, 200, "Create order")
        
        data = r.json()
        self.order_id = data.get("id")
        self.unlock_token = data.get("unlock_token")
        
        self.assert_eq(data.get("status"), "pending_payment", "Status should be pending_payment")
        self.assert_eq(data.get("payment_provider"), "manual", "Payment provider should be manual")
        self.assert_eq(data.get("price_usd"), 49, "Price should be 49")
        self.assert_true(len(data.get("unlock_token", "")) == 32, "Unlock token should be 32 hex chars")

    def test_apex_order_wrong_product(self):
        """APEX: Create order with wrong product for deliverable -> 400"""
        if not self.deliverable_id:
            print("⚠️  SKIPPED: No deliverable_id from generate test")
            return
        
        r = requests.post(f"{API}/apex/orders", json={
            "product": "seo_pack",
            "buyer_email": "b@t.com",
            "deliverable_id": self.deliverable_id
        })
        self.assert_status(r, 400, "Wrong product should return 400")

    def test_apex_unlock_before_payment(self):
        """APEX: Unlock before payment -> 402"""
        if not self.unlock_token:
            print("⚠️  SKIPPED: No unlock_token from order test")
            return
        
        r = requests.get(f"{API}/apex/unlock/{self.unlock_token}")
        self.assert_status(r, 402, "Unlock before payment should return 402")

    def test_apex_library_before_payment(self):
        """APEX: Library API before payment -> 402"""
        if not self.deliverable_id or not self.api_key:
            print("⚠️  SKIPPED: No deliverable_id or api_key")
            return
        
        r = requests.get(f"{API}/apex/library/{self.deliverable_id}", params={"key": self.api_key})
        self.assert_status(r, 402, "Library API before payment should return 402")

    def test_apex_library_wrong_key(self):
        """APEX: Library API with wrong key -> 401"""
        if not self.deliverable_id:
            print("⚠️  SKIPPED: No deliverable_id")
            return
        
        r = requests.get(f"{API}/apex/library/{self.deliverable_id}", params={"key": "wrong"})
        self.assert_status(r, 401, "Wrong key should return 401")

    def test_apex_order_invalid_status(self):
        """APEX: PATCH order with invalid status -> 400"""
        if not self.order_id:
            print("⚠️  SKIPPED: No order_id from order test")
            return
        
        r = requests.patch(f"{API}/apex/orders/{self.order_id}", json={"status": "bogus"})
        self.assert_status(r, 400, "Invalid status should return 400")

    def test_apex_order_mark_paid(self):
        """APEX: PATCH order to paid"""
        if not self.order_id:
            print("⚠️  SKIPPED: No order_id from order test")
            return
        
        r = requests.patch(f"{API}/apex/orders/{self.order_id}", json={"status": "paid"})
        self.assert_status(r, 200, "Mark order as paid")
        
        data = r.json()
        self.assert_eq(data.get("status"), "paid", "Status should be paid")
        self.assert_true(data.get("paid_at") is not None, "paid_at should be set")

    def test_apex_unlock_after_payment(self):
        """APEX: Unlock after payment -> 200"""
        if not self.unlock_token:
            print("⚠️  SKIPPED: No unlock_token from order test")
            return
        
        r = requests.get(f"{API}/apex/unlock/{self.unlock_token}")
        self.assert_status(r, 200, "Unlock after payment should return 200")
        self.assert_true("text/markdown" in r.headers.get("Content-Type", ""), "Should return markdown")

    def test_apex_unlock_status(self):
        """APEX: Unlock with fmt=status returns JSON with api_key"""
        if not self.unlock_token:
            print("⚠️  SKIPPED: No unlock_token from order test")
            return
        
        r = requests.get(f"{API}/apex/unlock/{self.unlock_token}", params={"fmt": "status"})
        self.assert_status(r, 200, "Unlock status")
        
        data = r.json()
        self.assert_true("api_key" in data, "Should have api_key")

    def test_apex_library_after_payment(self):
        """APEX: Library API after payment -> 200"""
        if not self.deliverable_id or not self.api_key:
            print("⚠️  SKIPPED: No deliverable_id or api_key")
            return
        
        r = requests.get(f"{API}/apex/library/{self.deliverable_id}", params={"key": self.api_key})
        self.assert_status(r, 200, "Library API after payment")
        
        data = r.json()
        self.assert_true("prompts" in data, "Should have prompts array")
        self.assert_true(isinstance(data.get("prompts"), list), "prompts should be a list")

    def test_apex_orders_list(self):
        """APEX: GET /api/apex/orders shows downloads"""
        r = requests.get(f"{API}/apex/orders")
        self.assert_status(r, 200, "List orders")
        
        orders = r.json()
        if self.order_id:
            order = next((o for o in orders if o["id"] == self.order_id), None)
            if order:
                self.assert_true(order.get("downloads", 0) >= 1, f"Order should have downloads >= 1, got {order.get('downloads')}")

    def test_apex_order_refund(self):
        """APEX: PATCH order to refunded"""
        if not self.order_id:
            print("⚠️  SKIPPED: No order_id from order test")
            return
        
        r = requests.patch(f"{API}/apex/orders/{self.order_id}", json={"status": "refunded"})
        self.assert_status(r, 200, "Refund order")
        
        data = r.json()
        self.assert_eq(data.get("status"), "refunded", "Status should be refunded")

    def test_apex_unlock_after_refund(self):
        """APEX: Unlock after refund -> 402"""
        if not self.unlock_token:
            print("⚠️  SKIPPED: No unlock_token from order test")
            return
        
        r = requests.get(f"{API}/apex/unlock/{self.unlock_token}")
        self.assert_status(r, 402, "Unlock after refund should return 402")

    def test_apex_unlock_unknown_token(self):
        """APEX: Unlock with unknown token -> 404"""
        r = requests.get(f"{API}/apex/unlock/unknowntoken")
        self.assert_status(r, 404, "Unknown token should return 404")

    # ==================== LOCAL NODE TESTS ====================
    
    def test_local_node_help(self):
        """LOCAL NODE: --help contains --companion and --no-top"""
        import subprocess
        result = subprocess.run(
            ["python", "/app/handoff/local_node/acaso_node.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assert_eq(result.returncode, 0, "Help command should succeed")
        self.assert_true("--companion" in result.stdout, "--companion flag should be in help")
        self.assert_true("--no-top" in result.stdout, "--no-top flag should be in help")
        print(f"   Help output contains both flags")

    def test_local_node_served_file(self):
        """LOCAL NODE: GET /local-node/acaso_node.py contains 'launch_companion'"""
        r = requests.get(f"{BACKEND_URL}/local-node/acaso_node.py")
        self.assert_status(r, 200, "Serve local node file")
        self.assert_true("launch_companion" in r.text, "File should contain 'launch_companion'")

    def test_companion_webmanifest(self):
        """COMPANION: GET /companion.webmanifest returns valid JSON"""
        r = requests.get(f"{BACKEND_URL}/companion.webmanifest")
        self.assert_status(r, 200, "Get companion manifest")
        
        data = r.json()
        self.assert_eq(data.get("start_url"), "/?mode=companion", "start_url should be /?mode=companion")
        self.assert_true(isinstance(data.get("icons"), list), "Should have icons array")
        self.assert_true(len(data.get("icons", [])) >= 2, "Should have at least 2 icons")

    def test_companion_icon(self):
        """COMPANION: GET /companion-192.png returns image"""
        r = requests.get(f"{BACKEND_URL}/companion-192.png")
        self.assert_status(r, 200, "Get companion icon")
        self.assert_eq(r.headers.get("Content-Type"), "image/png", "Should be image/png")

    # ==================== REGRESSION TESTS ====================
    
    def test_regression_radar_sources(self):
        """REGRESSION: GET /api/radar/sources returns 3"""
        r = requests.get(f"{API}/radar/sources")
        self.assert_status(r, 200, "Get radar sources")
        
        sources = r.json()
        self.assert_eq(len(sources), 3, "Should have 3 radar sources")

    def test_regression_acaso_presets(self):
        """REGRESSION: GET /api/acaso/presets returns 3"""
        r = requests.get(f"{API}/acaso/presets")
        self.assert_status(r, 200, "Get ACASO presets")
        
        presets = r.json()
        self.assert_eq(len(presets), 3, "Should have 3 presets")

    def test_regression_self_scan_config(self):
        """REGRESSION: GET /api/self/scan/config returns enabled false"""
        r = requests.get(f"{API}/self/scan/config")
        self.assert_status(r, 200, "Get self scan config")
        
        data = r.json()
        self.assert_eq(data.get("enabled"), False, "Self scan should be disabled")

    def summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        print(f"Total tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"\nLLM Budget Usage:")
        print(f"  Watch calls: {self.llm_calls['watch']}/2")
        print(f"  Generate calls: {self.llm_calls['generate']}/1")
        print('='*60)
        
        if self.tests_failed == 0:
            print("✅ ALL TESTS PASSED")
            return 0
        else:
            print(f"❌ {self.tests_failed} TEST(S) FAILED")
            return 1

def main():
    print(f"ACASO Omniverse Backend Test")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API: {API}")
    print(f"Started: {datetime.now().isoformat()}")
    
    runner = TestRunner()
    
    # Run tests in order
    print("\n" + "="*60)
    print("COMPANION WATCH MODE TESTS")
    print("="*60)
    runner.test("Watch: Empty image -> 400", runner.test_watch_empty_image)
    runner.test("Watch: Error frame -> notable true", runner.test_watch_error_frame)
    runner.test("Watch: Calm frame -> notable false", runner.test_watch_calm_frame)
    runner.test("Watch: History API", runner.test_watch_history)
    runner.test("Watch: Delete history", runner.test_watch_history_delete)
    
    print("\n" + "="*60)
    print("APEX CATALOG TESTS")
    print("="*60)
    runner.test("Apex: Products catalog", runner.test_apex_products)
    
    print("\n" + "="*60)
    print("APEX GENERATE VALIDATION TESTS")
    print("="*60)
    runner.test("Apex: Invalid product", runner.test_apex_generate_invalid_product)
    runner.test("Apex: Prompt library no domain", runner.test_apex_generate_prompt_library_no_domain)
    runner.test("Apex: SEO pack missing fields", runner.test_apex_generate_seo_pack_missing_fields)
    runner.test("Apex: RFP kit no input", runner.test_apex_generate_rfp_kit_no_input)
    
    print("\n" + "="*60)
    print("APEX GENERATE (ONE LLM CALL)")
    print("="*60)
    runner.test("Apex: Generate prompt library", runner.test_apex_generate_prompt_library)
    
    print("\n" + "="*60)
    print("APEX DELIVERABLES TESTS")
    print("="*60)
    runner.test("Apex: List deliverables", runner.test_apex_deliverables_list)
    runner.test("Apex: Get deliverable", runner.test_apex_deliverable_get)
    runner.test("Apex: Export markdown", runner.test_apex_deliverable_export_md)
    runner.test("Apex: Export JSON", runner.test_apex_deliverable_export_json)
    
    print("\n" + "="*60)
    print("APEX ORDERS TESTS")
    print("="*60)
    runner.test("Apex: Order invalid email", runner.test_apex_order_invalid_email)
    runner.test("Apex: Create order", runner.test_apex_order_create)
    runner.test("Apex: Order wrong product", runner.test_apex_order_wrong_product)
    runner.test("Apex: Unlock before payment", runner.test_apex_unlock_before_payment)
    runner.test("Apex: Library before payment", runner.test_apex_library_before_payment)
    runner.test("Apex: Library wrong key", runner.test_apex_library_wrong_key)
    runner.test("Apex: Order invalid status", runner.test_apex_order_invalid_status)
    runner.test("Apex: Mark order paid", runner.test_apex_order_mark_paid)
    runner.test("Apex: Unlock after payment", runner.test_apex_unlock_after_payment)
    runner.test("Apex: Unlock status", runner.test_apex_unlock_status)
    runner.test("Apex: Library after payment", runner.test_apex_library_after_payment)
    runner.test("Apex: Orders list", runner.test_apex_orders_list)
    runner.test("Apex: Refund order", runner.test_apex_order_refund)
    runner.test("Apex: Unlock after refund", runner.test_apex_unlock_after_refund)
    runner.test("Apex: Unknown unlock token", runner.test_apex_unlock_unknown_token)
    
    print("\n" + "="*60)
    print("LOCAL NODE TESTS")
    print("="*60)
    runner.test("Local Node: Help output", runner.test_local_node_help)
    runner.test("Local Node: Served file", runner.test_local_node_served_file)
    runner.test("Companion: Webmanifest", runner.test_companion_webmanifest)
    runner.test("Companion: Icon", runner.test_companion_icon)
    
    print("\n" + "="*60)
    print("REGRESSION TESTS")
    print("="*60)
    runner.test("Regression: Radar sources", runner.test_regression_radar_sources)
    runner.test("Regression: ACASO presets", runner.test_regression_acaso_presets)
    runner.test("Regression: Self scan config", runner.test_regression_self_scan_config)
    
    return runner.summary()

if __name__ == "__main__":
    sys.exit(main())
