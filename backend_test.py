#!/usr/bin/env python3
"""
Backend API Testing Suite for TikTok Auditorium
Tests Phase 0-1 + Module A: Audience Avatar CRUD endpoints
"""

import base64
import io
import json
import requests
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Use the production URL from frontend/.env
BASE_URL = "https://tikaudit.preview.emergentagent.com/api"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.test_data = {}  # Store IDs for dependent tests
        
    def log_pass(self, test_name: str):
        print(f"✅ PASS: {test_name}")
        self.passed += 1
        
    def log_fail(self, test_name: str, error: str):
        print(f"❌ FAIL: {test_name} - {error}")
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} passed")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")
        return self.failed == 0

def test_health_endpoint(results: TestResults):
    """Test GET /api/health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Health endpoint status", f"Expected 200, got {response.status_code}")
            return
            
        data = response.json()
        
        # Check required fields
        if "ok" not in data:
            results.log_fail("Health endpoint response", "Missing 'ok' field")
            return
            
        if "mongo" not in data:
            results.log_fail("Health endpoint response", "Missing 'mongo' field")
            return
            
        if not isinstance(data["ok"], bool):
            results.log_fail("Health endpoint response", "'ok' field should be boolean")
            return
            
        if not isinstance(data["mongo"], bool):
            results.log_fail("Health endpoint response", "'mongo' field should be boolean")
            return
            
        if not data["ok"]:
            results.log_fail("Health endpoint response", "'ok' should be true")
            return
            
        results.log_pass("Health endpoint")
        print(f"   Health response: ok={data['ok']}, mongo={data['mongo']}")
        
    except Exception as e:
        results.log_fail("Health endpoint", f"Request failed: {str(e)}")

def test_orgs_crud(results: TestResults):
    """Test POST /api/orgs and GET /api/orgs"""
    org_id = None
    
    try:
        # Test creating an organization
        org_data = {"name": "Avatar Test Organization"}
        response = requests.post(f"{BASE_URL}/orgs", json=org_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Create org", f"Expected 200, got {response.status_code}: {response.text}")
            return None
            
        org_response = response.json()
        
        # Validate org creation response
        required_fields = ["id", "name", "created_at"]
        for field in required_fields:
            if field not in org_response:
                results.log_fail("Create org response", f"Missing '{field}' field")
                return None
                
        if org_response["name"] != org_data["name"]:
            results.log_fail("Create org response", f"Name mismatch: expected '{org_data['name']}', got '{org_response['name']}'")
            return None
            
        org_id = org_response["id"]
        results.test_data["org_id"] = org_id
        results.log_pass("Create organization")
        print(f"   Created org: {org_response['name']} (ID: {org_id})")
        
        # Test listing organizations
        response = requests.get(f"{BASE_URL}/orgs", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("List orgs", f"Expected 200, got {response.status_code}")
            return org_id
            
        orgs_list = response.json()
        
        if not isinstance(orgs_list, list):
            results.log_fail("List orgs response", "Expected list response")
            return org_id
            
        # Check if our created org is in the list
        found_org = None
        for org in orgs_list:
            if org.get("id") == org_id:
                found_org = org
                break
                
        if not found_org:
            results.log_fail("List orgs", f"Created org with ID {org_id} not found in list")
            return org_id
            
        results.log_pass("List organizations")
        print(f"   Found {len(orgs_list)} organizations, including our created org")
        
        return org_id
        
    except Exception as e:
        results.log_fail("Orgs CRUD", f"Request failed: {str(e)}")
        return None

def test_projects_crud(results: TestResults, org_id: str):
    """Test POST /api/projects, GET /api/projects, and GET /api/projects/{id}"""
    if not org_id:
        results.log_fail("Projects CRUD", "No org_id provided")
        return None
        
    project_id = None
    
    try:
        # Test creating a project
        project_data = {
            "org_id": org_id,
            "name": "Avatar Test Project",
            "timezone": "UTC",
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/projects", json=project_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Create project", f"Expected 200, got {response.status_code}: {response.text}")
            return None
            
        project_response = response.json()
        
        # Validate project creation response
        required_fields = ["id", "org_id", "name", "timezone", "language", "created_at"]
        for field in required_fields:
            if field not in project_response:
                results.log_fail("Create project response", f"Missing '{field}' field")
                return None
                
        if project_response["org_id"] != org_id:
            results.log_fail("Create project response", f"org_id mismatch: expected '{org_id}', got '{project_response['org_id']}'")
            return None
            
        project_id = project_response["id"]
        results.test_data["project_id"] = project_id
        results.log_pass("Create project")
        print(f"   Created project: {project_response['name']} (ID: {project_id})")
        
        # Test listing projects
        response = requests.get(f"{BASE_URL}/projects", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("List projects", f"Expected 200, got {response.status_code}")
            return project_id
            
        projects_list = response.json()
        
        if not isinstance(projects_list, list):
            results.log_fail("List projects response", "Expected list response")
            return project_id
            
        # Check if our created project is in the list
        found_project = None
        for project in projects_list:
            if project.get("id") == project_id:
                found_project = project
                break
                
        if not found_project:
            results.log_fail("List projects", f"Created project with ID {project_id} not found in list")
            return project_id
            
        results.log_pass("List projects")
        print(f"   Found {len(projects_list)} projects, including our created project")
        
        # Test getting specific project
        response = requests.get(f"{BASE_URL}/projects/{project_id}", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Get project by ID", f"Expected 200, got {response.status_code}")
            return project_id
            
        single_project = response.json()
        
        if single_project.get("id") != project_id:
            results.log_fail("Get project by ID", f"ID mismatch: expected '{project_id}', got '{single_project.get('id')}'")
            return project_id
            
        results.log_pass("Get project by ID")
        print(f"   Retrieved project: {single_project['name']}")
        
        return project_id
        
    except Exception as e:
        results.log_fail("Projects CRUD", f"Request failed: {str(e)}")
        return None

# ─── AUDIENCE AVATAR TESTS ────────────────────────────────────────────────────

def test_create_avatar_valid(results: TestResults):
    """Test creating avatar with valid data and hashtag normalization"""
    project_id = results.test_data.get("project_id")
    if not project_id:
        results.log_fail("Create Avatar - Valid Data", "No project_id available")
        return
        
    try:
        # Test 1: Create avatar with hashtag normalization (no # prefix)
        avatar_data = {
            "project_id": project_id,
            "name": "Fitness Enthusiast",
            "hashtags": ["fitness", "workout", "health"],  # No # prefix - should be normalized
            "geolocation": "United States",
            "language": "en",
            "notes": "Target audience for fitness content"
        }
        
        response = requests.post(f"{BASE_URL}/audience/avatars", json=avatar_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Create Avatar - Hashtag Normalization", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        avatar = response.json()
        results.test_data["avatar_id"] = avatar["id"]
        
        # Verify hashtag normalization
        expected_hashtags = ["#fitness", "#workout", "#health"]
        if avatar["hashtags"] != expected_hashtags:
            results.log_fail("Create Avatar - Hashtag Normalization", f"Expected: {expected_hashtags}, Got: {avatar['hashtags']}")
            return
            
        # Verify other fields
        if (avatar["name"] != "Fitness Enthusiast" or 
            avatar["geolocation"] != "United States" or
            avatar["language"] != "en" or
            avatar["notes"] != "Target audience for fitness content"):
            results.log_fail("Create Avatar - Data Storage", "Avatar data not stored correctly")
            return
            
        results.log_pass("Create Avatar - Valid Data & Hashtag Normalization")
        print(f"   Created avatar: {avatar['name']} with hashtags: {avatar['hashtags']}")
        
    except Exception as e:
        results.log_fail("Create Avatar - Valid Data", f"Request failed: {str(e)}")

def test_create_avatar_with_hash_prefix(results: TestResults):
    """Test creating avatar with hashtags that already have # prefix"""
    project_id = results.test_data.get("project_id")
    if not project_id:
        results.log_fail("Create Avatar - Hash Prefix", "No project_id available")
        return
        
    try:
        avatar_data = {
            "project_id": project_id,
            "name": "Tech Influencer",
            "hashtags": ["#technology", "#AI", "#Programming"],  # Already have # prefix
            "geolocation": "Silicon Valley",
            "language": "en"
        }
        
        response = requests.post(f"{BASE_URL}/audience/avatars", json=avatar_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Create Avatar - Hash Prefix", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        avatar = response.json()
        results.test_data["avatar_id_2"] = avatar["id"]
        
        # Verify hashtags are normalized to lowercase but keep # prefix
        expected_hashtags = ["#technology", "#ai", "#programming"]
        if avatar["hashtags"] != expected_hashtags:
            results.log_fail("Create Avatar - Hash Prefix", f"Expected: {expected_hashtags}, Got: {avatar['hashtags']}")
            return
            
        results.log_pass("Create Avatar - Existing Hash Prefix")
        print(f"   Created avatar: {avatar['name']} with normalized hashtags: {avatar['hashtags']}")
        
    except Exception as e:
        results.log_fail("Create Avatar - Hash Prefix", f"Request failed: {str(e)}")

def test_list_avatars(results: TestResults):
    """Test listing avatars for a project"""
    project_id = results.test_data.get("project_id")
    if not project_id:
        results.log_fail("List Avatars", "No project_id available")
        return
        
    try:
        response = requests.get(f"{BASE_URL}/audience/avatars?project_id={project_id}", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("List Avatars", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        avatars = response.json()
        
        if not isinstance(avatars, list):
            results.log_fail("List Avatars", "Expected list response")
            return
            
        if len(avatars) < 2:  # Should have at least the 2 we created
            results.log_fail("List Avatars", f"Expected at least 2 avatars, found {len(avatars)}")
            return
            
        results.log_pass("List Avatars")
        print(f"   Found {len(avatars)} avatars for project")
        
    except Exception as e:
        results.log_fail("List Avatars", f"Request failed: {str(e)}")

def test_get_avatar_by_id(results: TestResults):
    """Test getting single avatar by ID"""
    avatar_id = results.test_data.get("avatar_id")
    if not avatar_id:
        results.log_fail("Get Avatar by ID", "No avatar_id available")
        return
        
    try:
        response = requests.get(f"{BASE_URL}/audience/avatars/{avatar_id}", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Get Avatar by ID", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        avatar = response.json()
        
        if avatar["id"] != avatar_id or avatar["name"] != "Fitness Enthusiast":
            results.log_fail("Get Avatar by ID", "Avatar data mismatch when retrieved by ID")
            return
            
        results.log_pass("Get Avatar by ID")
        print(f"   Retrieved avatar: {avatar['name']}")
        
    except Exception as e:
        results.log_fail("Get Avatar by ID", f"Request failed: {str(e)}")

def test_update_avatar(results: TestResults):
    """Test updating avatar name and hashtags"""
    avatar_id = results.test_data.get("avatar_id")
    if not avatar_id:
        results.log_fail("Update Avatar", "No avatar_id available")
        return
        
    try:
        update_data = {
            "name": "Updated Fitness Expert",
            "hashtags": ["fitness", "nutrition", "wellness", "lifestyle"]  # Test normalization on update
        }
        
        response = requests.patch(f"{BASE_URL}/audience/avatars/{avatar_id}", json=update_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Update Avatar", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        avatar = response.json()
        
        # Verify name update
        if avatar["name"] != "Updated Fitness Expert":
            results.log_fail("Update Avatar", f"Name update failed. Expected: 'Updated Fitness Expert', Got: '{avatar['name']}'")
            return
            
        # Verify hashtag normalization on update
        expected_hashtags = ["#fitness", "#nutrition", "#wellness", "#lifestyle"]
        if avatar["hashtags"] != expected_hashtags:
            results.log_fail("Update Avatar", f"Hashtag update failed. Expected: {expected_hashtags}, Got: {avatar['hashtags']}")
            return
            
        results.log_pass("Update Avatar")
        print(f"   Updated avatar: {avatar['name']} with hashtags: {avatar['hashtags']}")
        
    except Exception as e:
        results.log_fail("Update Avatar", f"Request failed: {str(e)}")

def test_delete_avatar(results: TestResults):
    """Test deleting avatar"""
    avatar_id = results.test_data.get("avatar_id_2")  # Delete the second avatar
    if not avatar_id:
        results.log_fail("Delete Avatar", "No avatar_id_2 available")
        return
        
    try:
        response = requests.delete(f"{BASE_URL}/audience/avatars/{avatar_id}", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Delete Avatar", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        result = response.json()
        
        if result.get("status") != "deleted" or result.get("id") != avatar_id:
            results.log_fail("Delete Avatar", "Delete response format incorrect")
            return
            
        results.log_pass("Delete Avatar")
        print(f"   Deleted avatar with ID: {avatar_id}")
        
    except Exception as e:
        results.log_fail("Delete Avatar", f"Request failed: {str(e)}")

def test_avatar_error_scenarios(results: TestResults):
    """Test various error scenarios for avatar endpoints"""
    project_id = results.test_data.get("project_id")
    
    try:
        # Test 1: Create avatar with invalid project_id
        invalid_data = {
            "project_id": "invalid_project_id",
            "name": "Test Avatar",
            "hashtags": ["test"],
            "geolocation": "Test Location"
        }
        
        response = requests.post(f"{BASE_URL}/audience/avatars", json=invalid_data, timeout=10)
        
        if response.status_code != 400:
            results.log_fail("Avatar Error - Invalid Project ID", f"Expected 400, got {response.status_code}")
        else:
            results.log_pass("Avatar Error - Invalid Project ID")
            print("   Correctly rejected invalid project_id")
            
        # Test 2: Create avatar with missing required fields
        missing_fields_data = {
            "project_id": project_id,
            "name": "Test"  # Missing hashtags and geolocation
        }
        
        response = requests.post(f"{BASE_URL}/audience/avatars", json=missing_fields_data, timeout=10)
        
        if response.status_code != 422:
            results.log_fail("Avatar Error - Missing Fields", f"Expected 422, got {response.status_code}")
        else:
            results.log_pass("Avatar Error - Missing Required Fields")
            print("   Correctly rejected missing required fields")
            
        # Test 3: Get non-existent avatar
        fake_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but non-existent
        response = requests.get(f"{BASE_URL}/audience/avatars/{fake_id}", timeout=10)
        
        if response.status_code != 404:
            results.log_fail("Avatar Error - Get Non-existent", f"Expected 404, got {response.status_code}")
        else:
            results.log_pass("Avatar Error - Get Non-existent")
            print("   Correctly returned 404 for non-existent avatar")
            
        # Test 4: Update non-existent avatar
        response = requests.patch(f"{BASE_URL}/audience/avatars/{fake_id}", json={"name": "Test"}, timeout=10)
        
        if response.status_code != 404:
            results.log_fail("Avatar Error - Update Non-existent", f"Expected 404, got {response.status_code}")
        else:
            results.log_pass("Avatar Error - Update Non-existent")
            print("   Correctly returned 404 for updating non-existent avatar")
            
        # Test 5: Delete non-existent avatar
        response = requests.delete(f"{BASE_URL}/audience/avatars/{fake_id}", timeout=10)
        
        if response.status_code != 404:
            results.log_fail("Avatar Error - Delete Non-existent", f"Expected 404, got {response.status_code}")
        else:
            results.log_pass("Avatar Error - Delete Non-existent")
            print("   Correctly returned 404 for deleting non-existent avatar")
            
    except Exception as e:
        results.log_fail("Avatar Error Scenarios", f"Request failed: {str(e)}")

def main():
    """Run all backend tests including new Avatar API tests"""
    print(f"🚀 Starting TikTok Auditorium Backend Tests (Phase 0-1 + Module A)")
    print(f"📡 Testing against: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = TestResults()
    
    # Test 1: Health endpoint
    print("\n1️⃣ Testing Health Endpoint")
    test_health_endpoint(results)
    
    # Test 2: Organizations CRUD
    print("\n2️⃣ Testing Organizations CRUD")
    org_id = test_orgs_crud(results)
    
    # Test 3: Projects CRUD (depends on org_id)
    print("\n3️⃣ Testing Projects CRUD")
    project_id = test_projects_crud(results, org_id)
    
    # NEW: Module A - Audience Avatar Tests
    print("\n🎯 MODULE A: AUDIENCE AVATAR TESTS")
    print("="*40)
    
    print("\n4️⃣ Testing Create Avatar - Valid Data")
    test_create_avatar_valid(results)
    
    print("\n5️⃣ Testing Create Avatar - Hash Prefix")
    test_create_avatar_with_hash_prefix(results)
    
    print("\n6️⃣ Testing List Avatars")
    test_list_avatars(results)
    
    print("\n7️⃣ Testing Get Avatar by ID")
    test_get_avatar_by_id(results)
    
    print("\n8️⃣ Testing Update Avatar")
    test_update_avatar(results)
    
    print("\n9️⃣ Testing Delete Avatar")
    test_delete_avatar(results)
    
    print("\n🔟 Testing Avatar Error Scenarios")
    test_avatar_error_scenarios(results)
    
    # Final summary
    success = results.summary()
    
    if success:
        print("\n🎉 All tests passed! Backend Phase 0-1 + Module A are working correctly.")
        sys.exit(0)
    else:
        print(f"\n💥 {results.failed} test(s) failed. Backend needs attention.")
        sys.exit(1)

if __name__ == "__main__":
    main()