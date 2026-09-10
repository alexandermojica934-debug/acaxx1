#!/usr/bin/env python3
"""
ACASO Omniverse Authentication Backend Test
Tests owner authentication, JWT cookies, guard middleware, key-auth, password change, lockout
"""
import requests
import sys
import os
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contest-ready-app.preview.emergentagent.com')
API = f"{BACKEND_URL}/api"

# Test credentials from /app/memory/test_credentials.md
TEST_EMAIL = "owner@test.local"
TEST_PASSWORD = "Sovereign2027y"

class AuthTestRunner:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.cookie_token = None
        self.api_key = None

    def test(self, name, fn):
        """Run a test function"""
        self.tests_run += 1
        print(f"\n{'='*70}")
        print(f"TEST: {name}")
        print('='*70)
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
            import traceback
            traceback.print_exc()
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

    # ==================== AUTH STATUS TESTS ====================
    
    def test_auth_status(self):
        """AUTH: GET /api/auth/status -> has_owner true, registration_open false"""
        r = requests.get(f"{API}/auth/status")
        self.assert_status(r, 200, "Auth status should be public")
        
        data = r.json()
        self.assert_eq(data.get("has_owner"), True, "has_owner should be true")
        self.assert_eq(data.get("registration_open"), False, "registration_open should be false")

    def test_registration_closed(self):
        """AUTH: POST /api/auth/register -> 403 (closed)"""
        r = requests.post(f"{API}/auth/register", json={
            "email": "newowner@test.com",
            "password": "NewPassword123",
            "name": "New Owner"
        })
        self.assert_status(r, 403, "Registration should be closed")
        self.assert_true("closed" in r.text.lower() or "already exists" in r.text.lower(), 
                        "Error message should mention closed or already exists")

    # ==================== GUARD MIDDLEWARE TESTS ====================
    
    def test_guard_without_auth_missions(self):
        """GUARD: GET /api/missions without cookie -> 401 with has_owner true"""
        r = requests.get(f"{API}/missions")
        self.assert_status(r, 401, "Protected route should return 401")
        
        data = r.json()
        self.assert_eq(data.get("has_owner"), True, "Response should include has_owner true")
        self.assert_true("detail" in data, "Response should have detail field")

    def test_guard_without_auth_radar(self):
        """GUARD: GET /api/radar/sources without cookie -> 401"""
        r = requests.get(f"{API}/radar/sources")
        self.assert_status(r, 401, "Protected route should return 401")

    def test_guard_without_auth_bridge(self):
        """GUARD: GET /api/bridge/info without cookie -> 401"""
        r = requests.get(f"{API}/bridge/info")
        self.assert_status(r, 401, "Protected route should return 401")

    def test_guard_public_apex_unlock(self):
        """GUARD: GET /api/apex/unlock/whatever -> 404 (public, not 401)"""
        r = requests.get(f"{API}/apex/unlock/whatever")
        # Should be 404 (not found) not 401 (unauthorized) because it's public
        self.assert_true(r.status_code in [404, 402], f"Public unlock route should return 404 or 402, not 401")
        print(f"   ✓ Public route returned {r.status_code} (not 401)")

    def test_guard_public_auth_status(self):
        """GUARD: GET /api/auth/status -> 200 (public)"""
        r = requests.get(f"{API}/auth/status")
        self.assert_status(r, 200, "Auth status should be public")

    def test_guard_options_not_blocked(self):
        """GUARD: OPTIONS preflight not blocked"""
        r = requests.options(f"{API}/missions")
        # OPTIONS should not return 401
        self.assert_true(r.status_code != 401, f"OPTIONS should not be blocked, got {r.status_code}")
        print(f"   ✓ OPTIONS returned {r.status_code} (not 401)")

    # ==================== LOGIN TESTS ====================
    
    def test_login_wrong_password(self):
        """LOGIN: POST /api/auth/login wrong password -> 401 'Invalid email or password'"""
        r = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": "WrongPassword123"
        })
        self.assert_status(r, 401, "Wrong password should return 401")
        self.assert_true("invalid" in r.text.lower() and ("email" in r.text.lower() or "password" in r.text.lower()),
                        "Error should mention invalid email or password")

    def test_login_unknown_email(self):
        """LOGIN: POST /api/auth/login unknown email -> 401"""
        r = requests.post(f"{API}/auth/login", json={
            "email": "unknown@test.com",
            "password": "SomePassword123"
        })
        self.assert_status(r, 401, "Unknown email should return 401")

    def test_login_correct_no_remember(self):
        """LOGIN: POST /api/auth/login correct credentials, remember_me false -> 200, session_days 7"""
        r = self.session.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "remember_me": False
        })
        self.assert_status(r, 200, "Correct credentials should return 200")
        
        data = r.json()
        self.assert_true("user" in data, "Response should have user")
        self.assert_eq(data["user"]["email"], TEST_EMAIL, "User email should match")
        self.assert_eq(data.get("session_days"), 7, "Session days should be 7 without remember_me")
        
        # Check cookie
        self.assert_true("acaso_session" in self.session.cookies, "Should set acaso_session cookie")
        cookie = self.session.cookies.get("acaso_session")
        self.assert_true(len(cookie) > 20, "Cookie should be a JWT token")
        self.cookie_token = cookie
        print(f"   ✓ Cookie set: {cookie[:20]}...")
        
        # Check cookie attributes from Set-Cookie header
        set_cookie = r.headers.get("Set-Cookie", "")
        self.assert_true("HttpOnly" in set_cookie, "Cookie should be HttpOnly")
        self.assert_true("SameSite=lax" in set_cookie or "SameSite=Lax" in set_cookie, "Cookie should be SameSite=lax")
        # Secure only on https
        if BACKEND_URL.startswith("https"):
            self.assert_true("Secure" in set_cookie, "Cookie should be Secure on https")

    def test_login_correct_with_remember(self):
        """LOGIN: POST /api/auth/login with remember_me true -> session_days 30"""
        # Use a fresh session to test remember_me
        r = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "remember_me": True
        })
        self.assert_status(r, 200, "Login with remember_me should succeed")
        
        data = r.json()
        self.assert_eq(data.get("session_days"), 30, "Session days should be 30 with remember_me")

    # ==================== AUTHENTICATED REQUESTS TESTS ====================
    
    def test_auth_me_with_cookie(self):
        """AUTH: GET /api/auth/me with cookie -> user"""
        r = self.session.get(f"{API}/auth/me")
        self.assert_status(r, 200, "Auth me should work with cookie")
        
        data = r.json()
        self.assert_eq(data.get("email"), TEST_EMAIL, "Should return user email")
        self.assert_true("id" in data, "Should have user id")

    def test_protected_missions_with_cookie(self):
        """AUTH: GET /api/missions with cookie -> 200"""
        r = self.session.get(f"{API}/missions")
        self.assert_status(r, 200, "Missions should be accessible with cookie")

    def test_protected_radar_with_cookie(self):
        """AUTH: GET /api/radar/sources with cookie -> 200"""
        r = self.session.get(f"{API}/radar/sources")
        self.assert_status(r, 200, "Radar sources should be accessible with cookie")

    def test_protected_bridge_with_cookie(self):
        """AUTH: GET /api/bridge/info with cookie -> 200 with api_key"""
        r = self.session.get(f"{API}/bridge/info")
        self.assert_status(r, 200, "Bridge info should be accessible with cookie")
        
        data = r.json()
        self.assert_true("api_key" in data, "Should return api_key")
        self.api_key = data["api_key"]
        print(f"   ✓ API key: {self.api_key[:20]}...")

    # ==================== BEARER TOKEN ALTERNATIVE ====================
    
    def test_bearer_token_auth(self):
        """AUTH: Bearer token alternative - cookie value as Authorization header"""
        if not self.cookie_token:
            print("⚠️  SKIPPED: No cookie token from login test")
            return
        
        # Use a fresh session without cookies
        headers = {"Authorization": f"Bearer {self.cookie_token}"}
        r = requests.get(f"{API}/auth/me", headers=headers)
        self.assert_status(r, 200, "Bearer token should authenticate")
        
        data = r.json()
        self.assert_eq(data.get("email"), TEST_EMAIL, "Should return user email")

    # ==================== KEY-AUTH PASSTHROUGH ====================
    
    def test_key_auth_agent_missions(self):
        """KEY-AUTH: GET /api/agent/missions with X-ACASO-Key (no cookie) -> 200"""
        if not self.api_key:
            print("⚠️  SKIPPED: No api_key from bridge/info test")
            return
        
        headers = {"X-ACASO-Key": self.api_key}
        r = requests.get(f"{API}/agent/missions", headers=headers)
        self.assert_status(r, 200, "Key-auth should work for agent endpoints")

    def test_key_auth_acaso_presets(self):
        """KEY-AUTH: GET /api/acaso/presets with X-ACASO-Key (no cookie) -> 200"""
        if not self.api_key:
            print("⚠️  SKIPPED: No api_key from bridge/info test")
            return
        
        headers = {"X-ACASO-Key": self.api_key}
        r = requests.get(f"{API}/acaso/presets", headers=headers)
        self.assert_status(r, 200, "Key-auth should work for acaso endpoints")

    def test_key_auth_node_setup(self):
        """KEY-AUTH: GET /api/node/setup with X-ACASO-Key (no cookie) -> 200"""
        if not self.api_key:
            print("⚠️  SKIPPED: No api_key from bridge/info test")
            return
        
        headers = {"X-ACASO-Key": self.api_key}
        r = requests.get(f"{API}/node/setup", headers=headers)
        self.assert_status(r, 200, "Key-auth should work for node endpoints")

    def test_key_auth_wrong_key(self):
        """KEY-AUTH: Wrong key without cookie -> 401"""
        headers = {"X-ACASO-Key": "wrong_key_12345"}
        r = requests.get(f"{API}/agent/missions", headers=headers)
        self.assert_status(r, 401, "Wrong key should return 401")

    # ==================== CHANGE PASSWORD TESTS ====================
    
    def test_change_password_wrong_current(self):
        """CHANGE-PW: POST /api/auth/change-password wrong current -> 400"""
        r = self.session.post(f"{API}/auth/change-password", json={
            "current_password": "WrongCurrent123",
            "new_password": "NewPassword2028z"
        })
        self.assert_status(r, 400, "Wrong current password should return 400")
        self.assert_true("current" in r.text.lower() and "incorrect" in r.text.lower(),
                        "Error should mention current password incorrect")

    def test_change_password_weak_new(self):
        """CHANGE-PW: POST /api/auth/change-password weak new ('short') -> 400"""
        r = self.session.post(f"{API}/auth/change-password", json={
            "current_password": TEST_PASSWORD,
            "new_password": "short"
        })
        self.assert_status(r, 400, "Weak password should return 400")
        self.assert_true("10" in r.text or "character" in r.text.lower(),
                        "Error should mention password length requirement")

    def test_change_password_same_as_current(self):
        """CHANGE-PW: POST /api/auth/change-password same as current -> 400"""
        r = self.session.post(f"{API}/auth/change-password", json={
            "current_password": TEST_PASSWORD,
            "new_password": TEST_PASSWORD
        })
        self.assert_status(r, 400, "Same password should return 400")
        self.assert_true("differ" in r.text.lower() or "same" in r.text.lower(),
                        "Error should mention password must differ")

    def test_change_password_valid_new(self):
        """CHANGE-PW: POST /api/auth/change-password valid new 'Sovereign2028z' -> 200, new cookie"""
        old_cookie = self.session.cookies.get("acaso_session")
        
        r = self.session.post(f"{API}/auth/change-password", json={
            "current_password": TEST_PASSWORD,
            "new_password": "Sovereign2028z"
        })
        self.assert_status(r, 200, "Valid password change should succeed")
        
        data = r.json()
        self.assert_eq(data.get("ok"), True, "Response should have ok: true")
        
        # Check new cookie
        new_cookie = self.session.cookies.get("acaso_session")
        self.assert_true(new_cookie != old_cookie, "Should set a new cookie")
        print(f"   ✓ New cookie set (different from old)")
        
        # Old cookie should now be invalid
        old_session = requests.Session()
        old_session.cookies.set("acaso_session", old_cookie)
        r = old_session.get(f"{API}/missions")
        self.assert_status(r, 401, "Old cookie should be invalidated")
        print(f"   ✓ Old cookie invalidated")
        
        # New cookie should work
        r = self.session.get(f"{API}/missions")
        self.assert_status(r, 200, "New cookie should work")
        
        # Login with old password should fail
        r = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        self.assert_status(r, 401, "Login with old password should fail")
        
        # Login with new password should work
        r = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": "Sovereign2028z"
        })
        self.assert_status(r, 200, "Login with new password should work")

    def test_change_password_back(self):
        """CHANGE-PW: Change password back to 'Sovereign2027y'"""
        r = self.session.post(f"{API}/auth/change-password", json={
            "current_password": "Sovereign2028z",
            "new_password": TEST_PASSWORD
        })
        self.assert_status(r, 200, "Change password back should succeed")
        
        # Verify login with original password works
        r = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        self.assert_status(r, 200, "Login with original password should work")
        print(f"   ✓ Password restored to {TEST_PASSWORD}")

    # ==================== LOGOUT TEST ====================
    
    def test_logout(self):
        """LOGOUT: POST /api/auth/logout -> ok and cookie cleared"""
        r = self.session.post(f"{API}/auth/logout")
        self.assert_status(r, 200, "Logout should succeed")
        
        data = r.json()
        self.assert_eq(data.get("ok"), True, "Response should have ok: true")
        
        # Check cookie cleared in Set-Cookie header
        set_cookie = r.headers.get("Set-Cookie", "")
        self.assert_true("acaso_session" in set_cookie, "Should clear acaso_session cookie")
        self.assert_true("max-age=0" in set_cookie.lower() or "expires" in set_cookie.lower(),
                        "Cookie should be expired")
        
        # Verify session is invalid
        r = self.session.get(f"{API}/auth/me")
        self.assert_status(r, 401, "Session should be invalid after logout")

    # ==================== REGRESSION TESTS WITH COOKIE ====================
    
    def test_regression_deliberations(self):
        """REGRESSION: GET /api/acaso/deliberations with cookie -> 200"""
        # Login first
        self.session.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        r = self.session.get(f"{API}/acaso/deliberations")
        self.assert_status(r, 200, "Deliberations should be accessible")

    def test_regression_opportunities(self):
        """REGRESSION: GET /api/radar/opportunities with cookie -> 200 list"""
        r = self.session.get(f"{API}/radar/opportunities")
        self.assert_status(r, 200, "Opportunities should be accessible")
        
        data = r.json()
        self.assert_true(isinstance(data, list), "Should return a list")

    def test_regression_apex_products(self):
        """REGRESSION: GET /api/apex/products with cookie -> 200"""
        r = self.session.get(f"{API}/apex/products")
        self.assert_status(r, 200, "Apex products should be accessible")

    def test_regression_self_scan_config(self):
        """REGRESSION: GET /api/self/scan/config with cookie -> 200"""
        r = self.session.get(f"{API}/self/scan/config")
        self.assert_status(r, 200, "Self scan config should be accessible")

    def test_regression_node_nodes(self):
        """REGRESSION: GET /api/node/nodes with cookie -> 200"""
        r = self.session.get(f"{API}/node/nodes")
        self.assert_status(r, 200, "Node nodes should be accessible")

    # ==================== LOCKOUT TEST (LAST) ====================
    
    def test_lockout_mechanism(self):
        """LOCKOUT: 8 failed logins -> 423 'Too many failed attempts' (RUN LAST)"""
        print("   ⚠️  WARNING: This test locks the account for 10 minutes!")
        print("   Performing 8 consecutive failed login attempts...")
        
        # Perform 8 failed login attempts
        for i in range(8):
            r = requests.post(f"{API}/auth/login", json={
                "email": TEST_EMAIL,
                "password": f"WrongPassword{i}"
            })
            print(f"   Attempt {i+1}/8: {r.status_code}")
            if i < 7:
                self.assert_status(r, 401, f"Failed attempt {i+1} should return 401")
        
        # 9th attempt with CORRECT password should return 423
        r = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        self.assert_status(r, 423, "After 8 failures, even correct password should return 423")
        self.assert_true("too many" in r.text.lower() or "locked" in r.text.lower(),
                        "Error should mention too many attempts or locked")
        
        print("   ✓ Account locked for 10 minutes")
        print("   ⚠️  NOTE: Account is now locked. Wait 10 minutes or restart backend to unlock.")

    def summary(self):
        """Print test summary"""
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print('='*70)
        print(f"Total tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print('='*70)
        
        if self.tests_failed == 0:
            print("✅ ALL TESTS PASSED")
            return 0
        else:
            print(f"❌ {self.tests_failed} TEST(S) FAILED")
            return 1

def main():
    print(f"ACASO Omniverse Authentication Backend Test")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API: {API}")
    print(f"Test credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
    print(f"Started: {datetime.now().isoformat()}")
    
    runner = AuthTestRunner()
    
    # Run tests in order
    print("\n" + "="*70)
    print("AUTH STATUS TESTS")
    print("="*70)
    runner.test("Auth status endpoint", runner.test_auth_status)
    runner.test("Registration closed", runner.test_registration_closed)
    
    print("\n" + "="*70)
    print("GUARD MIDDLEWARE TESTS")
    print("="*70)
    runner.test("Guard: missions without auth", runner.test_guard_without_auth_missions)
    runner.test("Guard: radar without auth", runner.test_guard_without_auth_radar)
    runner.test("Guard: bridge without auth", runner.test_guard_without_auth_bridge)
    runner.test("Guard: public apex unlock", runner.test_guard_public_apex_unlock)
    runner.test("Guard: public auth status", runner.test_guard_public_auth_status)
    runner.test("Guard: OPTIONS not blocked", runner.test_guard_options_not_blocked)
    
    print("\n" + "="*70)
    print("LOGIN TESTS")
    print("="*70)
    runner.test("Login: wrong password", runner.test_login_wrong_password)
    runner.test("Login: unknown email", runner.test_login_unknown_email)
    runner.test("Login: correct (remember_me false)", runner.test_login_correct_no_remember)
    runner.test("Login: correct (remember_me true)", runner.test_login_correct_with_remember)
    
    print("\n" + "="*70)
    print("AUTHENTICATED REQUESTS TESTS")
    print("="*70)
    runner.test("Auth: /api/auth/me with cookie", runner.test_auth_me_with_cookie)
    runner.test("Auth: /api/missions with cookie", runner.test_protected_missions_with_cookie)
    runner.test("Auth: /api/radar/sources with cookie", runner.test_protected_radar_with_cookie)
    runner.test("Auth: /api/bridge/info with cookie", runner.test_protected_bridge_with_cookie)
    
    print("\n" + "="*70)
    print("BEARER TOKEN ALTERNATIVE")
    print("="*70)
    runner.test("Bearer token auth", runner.test_bearer_token_auth)
    
    print("\n" + "="*70)
    print("KEY-AUTH PASSTHROUGH")
    print("="*70)
    runner.test("Key-auth: /api/agent/missions", runner.test_key_auth_agent_missions)
    runner.test("Key-auth: /api/acaso/presets", runner.test_key_auth_acaso_presets)
    runner.test("Key-auth: /api/node/setup", runner.test_key_auth_node_setup)
    runner.test("Key-auth: wrong key", runner.test_key_auth_wrong_key)
    
    print("\n" + "="*70)
    print("CHANGE PASSWORD TESTS")
    print("="*70)
    runner.test("Change-pw: wrong current", runner.test_change_password_wrong_current)
    runner.test("Change-pw: weak new", runner.test_change_password_weak_new)
    runner.test("Change-pw: same as current", runner.test_change_password_same_as_current)
    runner.test("Change-pw: valid new", runner.test_change_password_valid_new)
    runner.test("Change-pw: restore original", runner.test_change_password_back)
    
    print("\n" + "="*70)
    print("LOGOUT TEST")
    print("="*70)
    runner.test("Logout", runner.test_logout)
    
    print("\n" + "="*70)
    print("REGRESSION TESTS WITH COOKIE")
    print("="*70)
    runner.test("Regression: deliberations", runner.test_regression_deliberations)
    runner.test("Regression: opportunities", runner.test_regression_opportunities)
    runner.test("Regression: apex products", runner.test_regression_apex_products)
    runner.test("Regression: self scan config", runner.test_regression_self_scan_config)
    runner.test("Regression: node nodes", runner.test_regression_node_nodes)
    
    # Ask user if they want to run lockout test
    print("\n" + "="*70)
    print("LOCKOUT TEST (OPTIONAL - LOCKS ACCOUNT FOR 10 MINUTES)")
    print("="*70)
    print("⚠️  WARNING: The lockout test will lock the account for 10 minutes.")
    print("⚠️  This should be run LAST after all other tests are complete.")
    print("⚠️  Skipping lockout test to avoid blocking remaining tests.")
    # runner.test("Lockout mechanism", runner.test_lockout_mechanism)
    
    return runner.summary()

if __name__ == "__main__":
    sys.exit(main())
