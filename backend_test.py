#!/usr/bin/env python3
"""
ACASO Omniverse Backend API Test Suite
Tests Council of Weavers, Voice Chat, Voice Commander, and Opportunity Radar
"""
import requests
import sys
import time
from datetime import datetime

# Read backend URL from frontend/.env
try:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip()
                break
except Exception as e:
    print(f"❌ Could not read REACT_APP_BACKEND_URL from /app/frontend/.env: {e}")
    sys.exit(1)

API = f"{BASE_URL}/api"
print(f"🔗 Testing against: {API}\n")

class TestRunner:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.critical_failures = []
        
        # Store IDs for later tests
        self.deliberation_id = None
        self.mission_id = None
        self.voice_session_id = f"test-{int(time.time())}"
        self.opportunity_id = None

    def test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30, critical=False):
        """Run a single API test"""
        url = f"{API}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=timeout)
            else:
                print(f"❌ Unknown method: {method}")
                self.tests_failed += 1
                return False, {}

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASS - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.tests_failed += 1
                print(f"❌ FAIL - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response: {response.text[:200]}")
                if critical:
                    self.critical_failures.append(name)
                return False, {}

        except requests.exceptions.Timeout:
            self.tests_failed += 1
            print(f"❌ FAIL - Request timeout after {timeout}s")
            if critical:
                self.critical_failures.append(name)
            return False, {}
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ FAIL - Error: {str(e)}")
            if critical:
                self.critical_failures.append(name)
            return False, {}

    def run_all_tests(self):
        print("=" * 80)
        print("ACASO OMNIVERSE BACKEND API TEST SUITE")
        print("=" * 80)
        
        # ===== COUNCIL OF WEAVERS =====
        print("\n" + "=" * 80)
        print("COUNCIL OF WEAVERS TESTS")
        print("=" * 80)
        
        # Test 1: Get presets
        success, data = self.test(
            "GET /api/acaso/presets returns 3 presets",
            "GET", "acaso/presets", 200, critical=True
        )
        if success:
            if len(data) == 3:
                print(f"   ✓ Found 3 presets: {[p.get('id') for p in data]}")
                if all(p.get('id') in ['genesis', 'hunter', 'foresight'] for p in data):
                    print(f"   ✓ All expected preset IDs present")
                else:
                    print(f"   ⚠ Unexpected preset IDs")
            else:
                print(f"   ⚠ Expected 3 presets, got {len(data)}")
        
        # Test 2: Deliberate with short challenge (should fail)
        success, data = self.test(
            "POST /api/acaso/deliberate with challenge <20 chars returns 400",
            "POST", "acaso/deliberate", 400,
            data={"challenge": "short", "challenge_type": "test"}
        )
        
        # Test 3: Real deliberation (ONE CALL ONLY - brevity mode)
        print("\n⚠️  Running ONE deliberation (30-120s) - brevity mode to conserve budget")
        success, data = self.test(
            "POST /api/acaso/deliberate with real challenge",
            "POST", "acaso/deliberate", 200,
            data={
                "challenge": "Should we launch a micro-SaaS for indie hackers or focus on consulting? Budget: $5k, 3 months.",
                "challenge_type": "product_strategy",
                "preset_id": "genesis"
            },
            timeout=180,
            critical=True
        )
        if success:
            self.deliberation_id = data.get('id')
            print(f"   ✓ Deliberation ID: {self.deliberation_id}")
            print(f"   ✓ Duration: {data.get('duration_s')}s")
            print(f"   ✓ Weavers: {len(data.get('weavers', []))} (expected 4)")
            if data.get('sovereign_directive'):
                print(f"   ✓ Sovereign directive present ({len(data.get('sovereign_directive'))} chars)")
            if data.get('weak_signals'):
                print(f"   ✓ Weak signals present")
            if data.get('council_consulted'):
                print(f"   ✓ Council consulted: {data.get('council_consulted')}")
        
        # Test 4: List deliberations
        success, data = self.test(
            "GET /api/acaso/deliberations lists deliberations",
            "GET", "acaso/deliberations", 200
        )
        if success and self.deliberation_id:
            found = any(d.get('id') == self.deliberation_id for d in data)
            if found:
                print(f"   ✓ Found our deliberation in the list")
            else:
                print(f"   ⚠ Our deliberation not in list")
        
        # Test 5: Export deliberation
        if self.deliberation_id:
            success, data = self.test(
                f"GET /api/acaso/deliberations/{self.deliberation_id}/export returns markdown",
                "GET", f"acaso/deliberations/{self.deliberation_id}/export", 200
            )
        
        # Test 6: Deliberation to mission (idempotent)
        if self.deliberation_id:
            success, data = self.test(
                "POST /api/acaso/deliberations/{id}/to-mission creates mission",
                "POST", f"acaso/deliberations/{self.deliberation_id}/to-mission", 200,
                data={"mode": "Move"},
                timeout=120,
                critical=True
            )
            if success:
                self.mission_id = data.get('id')
                print(f"   ✓ Mission ID: {self.mission_id}")
                print(f"   ✓ Mission title: {data.get('title')}")
                if data.get('source_deliberation_id') == self.deliberation_id:
                    print(f"   ✓ source_deliberation_id matches")
            
            # Test idempotency
            success2, data2 = self.test(
                "POST /api/acaso/deliberations/{id}/to-mission is idempotent",
                "POST", f"acaso/deliberations/{self.deliberation_id}/to-mission", 200,
                data={"mode": "Move"},
                timeout=120
            )
            if success and success2:
                if data.get('id') == data2.get('id'):
                    print(f"   ✓ Idempotent: same mission ID returned")
                else:
                    print(f"   ⚠ Not idempotent: different mission IDs")
        
        # Test 7: Verify mission in missions list
        if self.mission_id:
            success, data = self.test(
                "GET /api/missions includes the mission from deliberation",
                "GET", "missions", 200
            )
            if success:
                found = any(m.get('id') == self.mission_id for m in data)
                if found:
                    print(f"   ✓ Mission found in /api/missions")
                else:
                    print(f"   ⚠ Mission not found in /api/missions")
        
        # ===== VOICE CHAT =====
        print("\n" + "=" * 80)
        print("VOICE CHAT TESTS")
        print("=" * 80)
        
        # Test 8: Voice chat fast mode
        success, data = self.test(
            "POST /api/voice/chat with mode:fast returns reply",
            "POST", "voice/chat", 200,
            data={
                "message": "What is ACASO?",
                "session_id": self.voice_session_id,
                "mode": "fast"
            },
            timeout=60,
            critical=True
        )
        if success:
            reply = data.get('reply', {})
            if reply.get('content'):
                print(f"   ✓ Reply content present ({len(reply.get('content'))} chars)")
            if reply.get('mode') == 'fast':
                print(f"   ✓ Reply mode is 'fast'")
        
        # Test 9: Get voice history
        success, data = self.test(
            "GET /api/voice/history returns messages",
            "GET", "voice/history", 200,
            params={"session_id": self.voice_session_id}
        )
        if success:
            if len(data) >= 2:
                print(f"   ✓ Found {len(data)} messages (expected ≥2)")
            else:
                print(f"   ⚠ Expected ≥2 messages, got {len(data)}")
        
        # Test 10: Delete voice history
        success, data = self.test(
            "DELETE /api/voice/history clears messages",
            "DELETE", "voice/history", 200,
            params={"session_id": self.voice_session_id}
        )
        
        # ===== VOICE COMMANDER =====
        print("\n" + "=" * 80)
        print("VOICE COMMANDER TESTS")
        print("=" * 80)
        
        # Test 11: Command parsing - open radar (no LLM)
        success, data = self.test(
            "POST /api/voice/command 'open radar' returns intent open_tab",
            "POST", "voice/command", 200,
            data={"transcript": "open radar", "session_id": None}
        )
        if success:
            if data.get('intent') == 'open_tab':
                print(f"   ✓ Intent: open_tab")
            if data.get('args', {}).get('tab') == 'radar':
                print(f"   ✓ Args.tab: radar")
            if data.get('parser') == 'rules':
                print(f"   ✓ Parser: rules (no LLM)")
            if data.get('navigate_tab') == 'radar':
                print(f"   ✓ navigate_tab: radar")
        
        # Test 12: Command parsing - go to council tab with execute:false
        success, data = self.test(
            "POST /api/voice/command 'go to the council tab' with execute:false",
            "POST", "voice/command", 200,
            data={"transcript": "go to the council tab", "execute": False}
        )
        if success:
            if data.get('intent') == 'open_tab':
                print(f"   ✓ Intent: open_tab")
            if data.get('args', {}).get('tab') == 'council':
                print(f"   ✓ Args.tab: council")
        
        # Test 13: Empty transcript returns 400
        success, data = self.test(
            "POST /api/voice/command with empty transcript returns 400",
            "POST", "voice/command", 400,
            data={"transcript": ""}
        )
        
        # ===== OPPORTUNITY RADAR =====
        print("\n" + "=" * 80)
        print("OPPORTUNITY RADAR TESTS")
        print("=" * 80)
        
        # Test 14: Get sources
        success, data = self.test(
            "GET /api/radar/sources returns 3 sources",
            "GET", "radar/sources", 200,
            critical=True
        )
        if success:
            if len(data) == 3:
                print(f"   ✓ Found 3 sources")
                sources = {s.get('id'): s for s in data}
                
                # Check sam_gov configured false
                if 'sam_gov' in sources and sources['sam_gov'].get('configured') == False:
                    print(f"   ✓ sam_gov configured: false (SAM_GOV_API_KEY not set)")
                
                # Check grants_gov and github_bounties configured true
                if 'grants_gov' in sources and sources['grants_gov'].get('configured') == True:
                    print(f"   ✓ grants_gov configured: true")
                if 'github_bounties' in sources and sources['github_bounties'].get('configured') == True:
                    print(f"   ✓ github_bounties configured: true")
            else:
                print(f"   ⚠ Expected 3 sources, got {len(data)}")
        
        # Test 15: Save profile
        success, data = self.test(
            "PUT /api/radar/profile saves profile",
            "PUT", "radar/profile", 200,
            data={
                "entity_type": "llc",
                "state": "MA",
                "skills": ["AI", "software"],
                "keywords": ["small business technology"]
            }
        )
        if success:
            if data.get('entity_type') == 'llc':
                print(f"   ✓ entity_type saved: llc")
            if data.get('state') == 'MA':
                print(f"   ✓ state saved: MA")
        
        # Test 16: Get profile
        success, data = self.test(
            "GET /api/radar/profile returns saved profile",
            "GET", "radar/profile", 200
        )
        if success:
            if data.get('entity_type') == 'llc':
                print(f"   ✓ entity_type: llc")
        
        # Test 17: Discover opportunities (FIRST CALL - max 2 total due to GitHub rate limit)
        print("\n⚠️  Running FIRST /api/radar/discover (30-60s) - live external APIs")
        success, data = self.test(
            "POST /api/radar/discover returns runs for 3 sources",
            "POST", "radar/discover", 200,
            data={"limit": 8},
            timeout=120,
            critical=True
        )
        if success:
            runs = data.get('runs', [])
            print(f"   ✓ Got {len(runs)} source runs")
            
            for run in runs:
                source = run.get('source')
                http_status = run.get('http_status')
                error = run.get('error')
                fetched = run.get('fetched', 0)
                
                if source == 'sam_gov':
                    if error and error.startswith('not_configured'):
                        print(f"   ✓ sam_gov: not_configured error (expected)")
                    else:
                        print(f"   ⚠ sam_gov: expected not_configured error, got: {error or 'success'}")
                
                elif source in ['grants_gov', 'github_bounties']:
                    if http_status == 200 and fetched > 0:
                        print(f"   ✓ {source}: HTTP 200, fetched {fetched} records")
                    elif error:
                        print(f"   ⚠ {source}: error (may be live API issue): {error[:100]}")
                    else:
                        print(f"   ⚠ {source}: HTTP {http_status}, fetched {fetched}")
        
        # Test 18: List opportunities
        success, data = self.test(
            "GET /api/radar/opportunities returns records",
            "GET", "radar/opportunities", 200,
            critical=True
        )
        if success and len(data) > 0:
            print(f"   ✓ Found {len(data)} opportunities")
            
            # Check first record for required fields
            opp = data[0]
            self.opportunity_id = opp.get('id')
            
            required_fields = [
                'source_url', 'retrieved_at', 'http_status', 'parser_version',
                'evidence', 'score', 'barrier', 'status', 'is_demo', 'days_remaining'
            ]
            
            for field in required_fields:
                if field in opp:
                    print(f"   ✓ Field '{field}' present")
                else:
                    print(f"   ⚠ Field '{field}' missing")
            
            # Check source_url starts with http
            if opp.get('source_url', '').startswith('http'):
                print(f"   ✓ source_url starts with http")
            
            # Check evidence array non-empty with source_location
            evidence = opp.get('evidence', [])
            if evidence and len(evidence) > 0:
                print(f"   ✓ evidence array non-empty ({len(evidence)} items)")
                if all('source_location' in e for e in evidence):
                    print(f"   ✓ All evidence items have source_location")
            
            # Check score
            score = opp.get('score', {})
            if 0 <= score.get('total', -1) <= 100:
                print(f"   ✓ score.total in range 0-100: {score.get('total')}")
            if score.get('label') in ['Strong fit', 'Possible fit', 'Possible fit (Skeptic pending)', 'Needs verification', 'Poor fit']:
                print(f"   ✓ score.label valid: {score.get('label')}")
            if score.get('breakdown') and len(score.get('breakdown')) == 8:
                print(f"   ✓ score.breakdown has 8 keys")
            
            # Check is_demo false
            if opp.get('is_demo') == False:
                print(f"   ✓ is_demo: false")
        
        # Test 19: Filter by type
        success, data = self.test(
            "GET /api/radar/opportunities?type=grant filters by type",
            "GET", "radar/opportunities", 200,
            params={"type": "grant"}
        )
        if success:
            if all(o.get('opportunity_type') == 'grant' for o in data):
                print(f"   ✓ All records are type 'grant'")
        
        # Test 20: Filter by source
        success, data = self.test(
            "GET /api/radar/opportunities?source=github_bounties filters by source",
            "GET", "radar/opportunities", 200,
            params={"source": "github_bounties"}
        )
        if success:
            if all(o.get('source') == 'github_bounties' for o in data):
                print(f"   ✓ All records are from 'github_bounties'")
        
        # Test 21: Filter by min_score
        success, data = self.test(
            "GET /api/radar/opportunities?min_score=50 filters by score",
            "GET", "radar/opportunities", 200,
            params={"min_score": 50}
        )
        if success:
            if all(o.get('score', {}).get('total', 0) >= 50 for o in data):
                print(f"   ✓ All records have score ≥50")
        
        # Test 22: Filter by low_barrier
        success, data = self.test(
            "GET /api/radar/opportunities?low_barrier=true filters by barrier",
            "GET", "radar/opportunities", 200,
            params={"low_barrier": True}
        )
        if success:
            if all(o.get('barrier', {}).get('label') == 'lower observed barrier' for o in data):
                print(f"   ✓ All records have lower observed barrier")
        
        # Test 23: Search by keyword
        if self.opportunity_id:
            # Get the opportunity to find a word from its title
            success_get, opp_data = self.test(
                f"GET /api/radar/opportunities/{self.opportunity_id} for keyword search",
                "GET", f"radar/opportunities/{self.opportunity_id}", 200
            )
            if success_get and opp_data.get('title'):
                # Extract a word from the title
                words = opp_data.get('title', '').split()
                if words:
                    keyword = words[0]
                    success, data = self.test(
                        f"GET /api/radar/opportunities?q={keyword} searches by keyword",
                        "GET", "radar/opportunities", 200,
                        params={"q": keyword}
                    )
                    if success and len(data) > 0:
                        print(f"   ✓ Found {len(data)} records matching '{keyword}'")
        
        # Test 24: Sort by deadline
        success, data = self.test(
            "GET /api/radar/opportunities?sort=deadline orders by deadline",
            "GET", "radar/opportunities", 200,
            params={"sort": "deadline", "limit": 10}
        )
        
        # Test 25: Get opportunity detail
        if self.opportunity_id:
            success, data = self.test(
                f"GET /api/radar/opportunities/{self.opportunity_id} returns full record",
                "GET", f"radar/opportunities/{self.opportunity_id}", 200,
                critical=True
            )
            if success:
                if 'description' in data:
                    print(f"   ✓ description field present")
                if 'similar' in data:
                    print(f"   ✓ similar[] field present ({len(data.get('similar', []))} items)")
        
        # Test 26: Patch opportunity - save
        if self.opportunity_id:
            success, data = self.test(
                f"PATCH /api/radar/opportunities/{self.opportunity_id} user_status:saved",
                "PATCH", f"radar/opportunities/{self.opportunity_id}", 200,
                data={"user_status": "saved"}
            )
            if success:
                if data.get('user_status') == 'saved':
                    print(f"   ✓ user_status: saved")
                if data.get('stage') == 'Reviewed':
                    print(f"   ✓ stage auto-updated to Reviewed")
        
        # Test 27: Patch opportunity - notes
        if self.opportunity_id:
            success, data = self.test(
                f"PATCH /api/radar/opportunities/{self.opportunity_id} notes",
                "PATCH", f"radar/opportunities/{self.opportunity_id}", 200,
                data={"notes": "test note"}
            )
            if success:
                if data.get('notes') == 'test note':
                    print(f"   ✓ notes persisted")
        
        # Test 28: Invalid user_status returns 400
        if self.opportunity_id:
            success, data = self.test(
                f"PATCH /api/radar/opportunities/{self.opportunity_id} invalid user_status returns 400",
                "PATCH", f"radar/opportunities/{self.opportunity_id}", 400,
                data={"user_status": "invalid"}
            )
        
        # Test 29: Filter saved opportunities
        success, data = self.test(
            "GET /api/radar/opportunities?saved=true includes saved",
            "GET", "radar/opportunities", 200,
            params={"saved": True}
        )
        if success and self.opportunity_id:
            found = any(o.get('id') == self.opportunity_id for o in data)
            if found:
                print(f"   ✓ Saved opportunity found in ?saved=true")
        
        # Test 30: Dismiss and filter
        if self.opportunity_id:
            success, data = self.test(
                f"PATCH /api/radar/opportunities/{self.opportunity_id} user_status:dismissed",
                "PATCH", f"radar/opportunities/{self.opportunity_id}", 200,
                data={"user_status": "dismissed"}
            )
            
            # Check it's hidden from default list
            success2, data2 = self.test(
                "GET /api/radar/opportunities excludes dismissed by default",
                "GET", "radar/opportunities", 200
            )
            if success2:
                found = any(o.get('id') == self.opportunity_id for o in data2)
                if not found:
                    print(f"   ✓ Dismissed opportunity hidden from default list")
            
            # Check it appears with include_dismissed
            success3, data3 = self.test(
                "GET /api/radar/opportunities?user_status=dismissed&include_dismissed=true shows dismissed",
                "GET", "radar/opportunities", 200,
                params={"user_status": "dismissed", "include_dismissed": True}
            )
            if success3:
                found = any(o.get('id') == self.opportunity_id for o in data3)
                if found:
                    print(f"   ✓ Dismissed opportunity found with include_dismissed=true")
        
        # Test 31: Analyze opportunity (ONE CALL ONLY)
        if self.opportunity_id:
            print("\n⚠️  Running ONE /api/radar/opportunities/{id}/analyze (30-120s)")
            success, data = self.test(
                f"POST /api/radar/opportunities/{self.opportunity_id}/analyze",
                "POST", f"radar/opportunities/{self.opportunity_id}/analyze", 200,
                data={"include_checklist": True},
                timeout=180,
                critical=True
            )
            if success:
                ai = data.get('ai', {})
                if 'fit' in ai:
                    print(f"   ✓ ai.fit present")
                if 'skeptic' in ai:
                    skeptic = ai['skeptic']
                    print(f"   ✓ ai.skeptic present")
                    if skeptic.get('verdict') in ['clear', 'caution', 'block']:
                        print(f"   ✓ skeptic.verdict: {skeptic.get('verdict')}")
                if 'checklist' in ai:
                    print(f"   ✓ ai.checklist present")
                if 'score' in data:
                    print(f"   ✓ score recomputed")
                if data.get('stage') == 'Reviewed':
                    print(f"   ✓ stage updated to Reviewed")
        
        # Test 32: Draft email (ONE CALL ONLY)
        if self.opportunity_id:
            print("\n⚠️  Running ONE /api/radar/opportunities/{id}/draft (30-120s)")
            success, data = self.test(
                f"POST /api/radar/opportunities/{self.opportunity_id}/draft kind:email",
                "POST", f"radar/opportunities/{self.opportunity_id}/draft", 200,
                data={"kind": "email"},
                timeout=180,
                critical=True
            )
            if success:
                if data.get('content'):
                    print(f"   ✓ content non-empty ({len(data.get('content'))} chars)")
                if 'placeholders' in data:
                    print(f"   ✓ placeholders: {data.get('placeholders')}")
                if data.get('model_label'):
                    print(f"   ✓ model_label: {data.get('model_label')}")
        
        # Test 33: Draft with invalid kind returns 400
        if self.opportunity_id:
            success, data = self.test(
                f"POST /api/radar/opportunities/{self.opportunity_id}/draft kind:bogus returns 400",
                "POST", f"radar/opportunities/{self.opportunity_id}/draft", 400,
                data={"kind": "bogus"}
            )
        
        # Test 34: Draft form_answers without form_text returns 400
        if self.opportunity_id:
            success, data = self.test(
                f"POST /api/radar/opportunities/{self.opportunity_id}/draft kind:form_answers without form_text returns 400",
                "POST", f"radar/opportunities/{self.opportunity_id}/draft", 400,
                data={"kind": "form_answers"}
            )
        
        # Test 35: Opportunity to mission (idempotent)
        if self.opportunity_id:
            success, data = self.test(
                f"POST /api/radar/opportunities/{self.opportunity_id}/to-mission creates mission",
                "POST", f"radar/opportunities/{self.opportunity_id}/to-mission", 200,
                timeout=120,
                critical=True
            )
            if success:
                opp_mission_id = data.get('id')
                print(f"   ✓ Mission ID: {opp_mission_id}")
                if data.get('source_opportunity_id') == self.opportunity_id:
                    print(f"   ✓ source_opportunity_id matches")
            
            # Check opportunity stage updated
            success2, opp_data = self.test(
                f"GET /api/radar/opportunities/{self.opportunity_id} after to-mission",
                "GET", f"radar/opportunities/{self.opportunity_id}", 200
            )
            if success2:
                if opp_data.get('stage') == 'Preparing':
                    print(f"   ✓ opportunity stage updated to Preparing")
            
            # Test idempotency
            success3, data3 = self.test(
                f"POST /api/radar/opportunities/{self.opportunity_id}/to-mission is idempotent",
                "POST", f"radar/opportunities/{self.opportunity_id}/to-mission", 200,
                timeout=120
            )
            if success and success3:
                if data.get('id') == data3.get('id'):
                    print(f"   ✓ Idempotent: same mission ID returned")
        
        # Test 36: Export opportunity
        if self.opportunity_id:
            success, data = self.test(
                f"GET /api/radar/opportunities/{self.opportunity_id}/export returns markdown",
                "GET", f"radar/opportunities/{self.opportunity_id}/export", 200
            )
        
        # Test 37: Natural language search (ONE CALL - allowed)
        print("\n⚠️  Running ONE /api/radar/search/nl (may use 1 LLM call)")
        success, data = self.test(
            "POST /api/radar/search/nl with query",
            "POST", "radar/search/nl", 200,
            data={"query": "small technology grants under $250,000 closing in 60 days"},
            timeout=60
        )
        if success:
            if 'proposed_filters' in data:
                print(f"   ✓ proposed_filters: {data.get('proposed_filters')}")
            if 'note' in data:
                print(f"   ✓ note present (not auto-applied)")
        
        # Test 38: Get runs
        success, data = self.test(
            "GET /api/radar/runs lists source runs",
            "GET", "radar/runs", 200
        )
        if success and len(data) > 0:
            print(f"   ✓ Found {len(data)} runs")
            run = data[0]
            if 'http_status' in run:
                print(f"   ✓ run has http_status")
            if 'parser_version' in run:
                print(f"   ✓ run has parser_version")
        
        # ===== SUMMARY =====
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total tests: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   - {failure}")
        
        return 0 if self.tests_failed == 0 else 1

if __name__ == "__main__":
    runner = TestRunner()
    sys.exit(runner.run_all_tests())
