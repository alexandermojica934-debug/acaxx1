#!/usr/bin/env python3
"""
ACASO Omniverse Backend API Test Suite
Tests File Analyzer, Self-Directive, and Attachments features
"""
import requests
import sys
import io
import time
from datetime import datetime

BASE_URL = "https://contest-ready-app.preview.emergentagent.com/api"

class TestRunner:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.fileset_id = None
        self.mission_id = None
        self.file_ids = []
        self.attachment_ids = []
        self.proposal_id = None

    def test(self, name, method, endpoint, expected_status, data=None, files=None, json_data=None):
        """Run a single API test"""
        url = f"{BASE_URL}/{endpoint}"
        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, timeout=60)
                elif json_data is not None:
                    response = requests.post(url, json=json_data, timeout=60)
                else:
                    response = requests.post(url, data=data, timeout=60)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=30)
            else:
                print(f"❌ Unsupported method {method}")
                self.tests_failed += 1
                return False, {}

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASS - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                self.tests_failed += 1
                print(f"❌ FAIL - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.text[:200]}")
                except:
                    pass
                return False, {}

        except Exception as e:
            self.tests_failed += 1
            print(f"❌ FAIL - Error: {str(e)}")
            return False, {}

    def run_all_tests(self):
        print("=" * 70)
        print("ACASO OMNIVERSE BACKEND API TEST SUITE")
        print("=" * 70)
        
        # ==================== FILE ANALYZER TESTS ====================
        print("\n" + "=" * 70)
        print("FILE ANALYZER TESTS")
        print("=" * 70)
        
        # Test 1: Create fileset
        success, resp = self.test(
            "Create fileset",
            "POST",
            "filesets",
            200,
            json_data={"title": "Test Analysis Set"}
        )
        if success and resp.get("id"):
            self.fileset_id = resp["id"]
            print(f"   Created fileset: {self.fileset_id}")
        
        # Test 2: List filesets
        self.test("List filesets", "GET", "filesets", 200)
        
        if self.fileset_id:
            # Test 3: Upload text file
            text_content = b"# Test Document\nThis is a test file for analysis.\nLine 3\nLine 4"
            success, resp = self.test(
                "Upload text file (.txt)",
                "POST",
                f"filesets/{self.fileset_id}/files",
                200,
                files={"file": ("test.txt", text_content, "text/plain")},
                data={"rel_path": "test.txt"}
            )
            if success and resp.get("id"):
                self.file_ids.append(resp["id"])
                print(f"   Uploaded file: {resp['id']}")
            
            # Test 4: Upload markdown file
            md_content = b"# Markdown Test\n## Section 1\nSome content here."
            success, resp = self.test(
                "Upload markdown file (.md)",
                "POST",
                f"filesets/{self.fileset_id}/files",
                200,
                files={"file": ("readme.md", md_content, "text/markdown")},
                data={"rel_path": "readme.md"}
            )
            if success and resp.get("id"):
                self.file_ids.append(resp["id"])
            
            # Test 5: Upload JSON file
            json_content = b'{"key": "value", "test": true}'
            success, resp = self.test(
                "Upload JSON file (.json)",
                "POST",
                f"filesets/{self.fileset_id}/files",
                200,
                files={"file": ("data.json", json_content, "application/json")},
                data={"rel_path": "data.json"}
            )
            if success and resp.get("id"):
                self.file_ids.append(resp["id"])
            
            # Test 6: Upload Python file
            py_content = b"# Python test\ndef hello():\n    return 'world'\n"
            success, resp = self.test(
                "Upload Python file (.py)",
                "POST",
                f"filesets/{self.fileset_id}/files",
                200,
                files={"file": ("script.py", py_content, "text/x-python")},
                data={"rel_path": "script.py"}
            )
            if success and resp.get("id"):
                self.file_ids.append(resp["id"])
            
            # Test 7: Upload image (binary, not readable)
            # Create a minimal 1x1 PNG
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            success, resp = self.test(
                "Upload PNG image (binary, readable=false)",
                "POST",
                f"filesets/{self.fileset_id}/files",
                200,
                files={"file": ("image.png", png_data, "image/png")},
                data={"rel_path": "image.png"}
            )
            if success and resp.get("id"):
                self.file_ids.append(resp["id"])
                if not resp.get("readable"):
                    print("   ✓ Image correctly marked as readable=false")
            
            # Test 8: Reject unsupported file type (.exe)
            exe_content = b"MZ\x90\x00"  # Fake exe header
            self.test(
                "Reject unsupported file (.exe) - expect 400",
                "POST",
                f"filesets/{self.fileset_id}/files",
                400,
                files={"file": ("malware.exe", exe_content, "application/x-msdownload")},
                data={"rel_path": "malware.exe"}
            )
            
            # Test 9: List files in fileset
            success, resp = self.test(
                "List files in fileset",
                "GET",
                f"filesets/{self.fileset_id}/files",
                200
            )
            if success:
                print(f"   Found {len(resp)} files")
            
            # Test 10: Download a file
            if self.file_ids:
                self.test(
                    "Download file",
                    "GET",
                    f"files/{self.file_ids[0]}/download",
                    200
                )
            
            # Test 11: Analyze fileset (requires files present)
            print("\n⏳ Running AI analysis (may take 10-15 seconds)...")
            success, resp = self.test(
                "Analyze fileset with AI",
                "POST",
                f"filesets/{self.fileset_id}/analyze",
                200,
                json_data={"question": "Summarize these files"}
            )
            if success:
                print(f"   Analysis ID: {resp.get('id')}")
                print(f"   Model: {resp.get('model_label')}")
                print(f"   Analysis preview: {resp.get('analysis', '')[:100]}...")
            
            # Test 12: List analyses
            self.test(
                "List analyses for fileset",
                "GET",
                f"filesets/{self.fileset_id}/analyses",
                200
            )
            
            # Test 13: Delete a file
            if self.file_ids:
                self.test(
                    "Delete file",
                    "DELETE",
                    f"files/{self.file_ids[0]}",
                    200
                )
        
        # Test 14: Analyze without files (should fail with 400)
        success, resp = self.test(
            "Create empty fileset for error test",
            "POST",
            "filesets",
            200,
            json_data={"title": "Empty Set"}
        )
        if success and resp.get("id"):
            empty_id = resp["id"]
            self.test(
                "Analyze empty fileset - expect 400",
                "POST",
                f"filesets/{empty_id}/analyze",
                400,
                json_data={}
            )
        
        # ==================== SELF-DIRECTIVE TESTS ====================
        print("\n" + "=" * 70)
        print("SELF-DIRECTIVE TESTS")
        print("=" * 70)
        
        # Test 15: Get manifest
        success, resp = self.test(
            "Get self-directive manifest",
            "GET",
            "self/manifest",
            200
        )
        if success:
            print(f"   Preview only: {resp.get('preview_only')}")
            print(f"   Files available: {len(resp.get('files', []))}")
        
        # Test 16: Get source of safe file
        success, resp = self.test(
            "Get source of _playground_notes.md",
            "GET",
            "self/source?path=frontend/src/_playground_notes.md",
            200
        )
        if success:
            print(f"   File size: {resp.get('size')} chars")
        
        # Test 17: Block access to .env (should return 403)
        self.test(
            "Block access to backend/.env - expect 403",
            "GET",
            "self/source?path=backend/.env",
            403
        )
        
        # Test 18: Propose a change to playground file
        print("\n⏳ Generating patch proposal (may take 10-15 seconds)...")
        success, resp = self.test(
            "Propose change to _playground_notes.md",
            "POST",
            "self/propose",
            200,
            json_data={
                "instruction": "Change version from 1 to 2 and add a line saying 'Updated by test'",
                "paths": ["frontend/src/_playground_notes.md"]
            }
        )
        if success and resp.get("id"):
            self.proposal_id = resp["id"]
            print(f"   Proposal ID: {self.proposal_id}")
            print(f"   Status: {resp.get('status')}")
            print(f"   Diffs: {len(resp.get('diffs', []))} files")
        
        # Test 19: Try to apply without approval (should fail with 400)
        if self.proposal_id:
            self.test(
                "Apply without approval - expect 400",
                "POST",
                "self/apply",
                400,
                json_data={"id": self.proposal_id, "approved": False}
            )
            
            # Test 20: Apply with approval
            success, resp = self.test(
                "Apply with approval",
                "POST",
                "self/apply",
                200,
                json_data={"id": self.proposal_id, "approved": True}
            )
            if success:
                print(f"   Status: {resp.get('status')}")
            
            # Give hot-reload a moment
            time.sleep(1)
            
            # Test 21: Rollback
            success, resp = self.test(
                "Rollback applied change",
                "POST",
                "self/rollback",
                200,
                json_data={"id": self.proposal_id}
            )
            if success:
                print(f"   Status: {resp.get('status')}")
        
        # Test 22: Get history
        success, resp = self.test(
            "Get self-directive history",
            "GET",
            "self/history",
            200
        )
        if success:
            print(f"   History entries: {len(resp)}")
        
        # ==================== ATTACHMENTS TESTS ====================
        print("\n" + "=" * 70)
        print("ATTACHMENTS (BUG BOUNTY) TESTS")
        print("=" * 70)
        
        # Test 23: Create a bug bounty mission first
        print("\n⏳ Compiling bug bounty mission (may take 10-15 seconds)...")
        success, resp = self.test(
            "Compile bug bounty mission",
            "POST",
            "compile-bounty",
            200,
            json_data={
                "directive": "Test security engagement for attachment testing",
                "platform": "HackerOne"
            }
        )
        if success and resp.get("id"):
            self.mission_id = resp["id"]
            print(f"   Mission ID: {self.mission_id}")
            print(f"   Title: {resp.get('title')}")
        
        if self.mission_id:
            # Test 24: Upload text attachment
            text_attach = b"Security finding details here"
            success, resp = self.test(
                "Upload text attachment",
                "POST",
                f"missions/{self.mission_id}/attachments",
                200,
                files={"file": ("evidence.txt", text_attach, "text/plain")}
            )
            if success and resp.get("id"):
                self.attachment_ids.append(resp["id"])
                print(f"   Attachment ID: {resp['id']}")
            
            # Test 25: Upload image attachment
            success, resp = self.test(
                "Upload image attachment",
                "POST",
                f"missions/{self.mission_id}/attachments",
                200,
                files={"file": ("screenshot.png", png_data, "image/png")}
            )
            if success and resp.get("id"):
                self.attachment_ids.append(resp["id"])
            
            # Test 26: Upload JSON attachment
            json_attach = b'{"vulnerability": "XSS", "severity": "high"}'
            success, resp = self.test(
                "Upload JSON attachment",
                "POST",
                f"missions/{self.mission_id}/attachments",
                200,
                files={"file": ("report.json", json_attach, "application/json")}
            )
            if success and resp.get("id"):
                self.attachment_ids.append(resp["id"])
            
            # Test 27: Reject .exe attachment
            self.test(
                "Reject .exe attachment - expect 400",
                "POST",
                f"missions/{self.mission_id}/attachments",
                400,
                files={"file": ("exploit.exe", exe_content, "application/x-msdownload")}
            )
            
            # Test 28: List attachments
            success, resp = self.test(
                "List mission attachments",
                "GET",
                f"missions/{self.mission_id}/attachments",
                200
            )
            if success:
                print(f"   Found {len(resp)} attachments")
            
            # Test 29: Download attachment
            if self.attachment_ids:
                self.test(
                    "Download attachment",
                    "GET",
                    f"attachments/{self.attachment_ids[0]}/download",
                    200
                )
            
            # Test 30: Delete attachment
            if self.attachment_ids:
                self.test(
                    "Delete attachment",
                    "DELETE",
                    f"attachments/{self.attachment_ids[0]}",
                    200
                )
        
        # ==================== SUMMARY ====================
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total tests run: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print("=" * 70)
        
        return 0 if self.tests_failed == 0 else 1

if __name__ == "__main__":
    runner = TestRunner()
    sys.exit(runner.run_all_tests())
