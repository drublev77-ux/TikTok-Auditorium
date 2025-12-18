#!/usr/bin/env python3
"""
Backend API Testing for TikTok Auditorium Phase 0-1
Tests all core endpoints: health, orgs, projects, manual imports
"""

import base64
import io
import json
import requests
import sys
from datetime import datetime
from typing import Dict, Any

# Use the production URL from frontend/.env
BASE_URL = "https://tikaudit.preview.emergentagent.com/api"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
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
        org_data = {"name": "Acme Digital Marketing"}
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
            "name": "TikTok Campaign Analysis Q1 2024",
            "timezone": "America/New_York",
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

def test_manual_import_success(results: TestResults, project_id: str):
    """Test POST /api/imports/manual with valid data"""
    if not project_id:
        results.log_fail("Manual import", "No project_id provided")
        return
        
    try:
        # Test with items array (account + video)
        import_data = {
            "project_id": project_id,
            "items": [
                {
                    "type": "account",
                    "url": "https://www.tiktok.com/@charlidamelio"
                },
                {
                    "type": "video", 
                    "url": "https://www.tiktok.com/@charlidamelio/video/7234567890123456789"
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/imports/manual", json=import_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Manual import with items", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        import_response = response.json()
        
        # Validate manual import response
        required_fields = ["id", "project_id", "status", "total_items", "created_at"]
        for field in required_fields:
            if field not in import_response:
                results.log_fail("Manual import response", f"Missing '{field}' field")
                return
                
        if import_response["project_id"] != project_id:
            results.log_fail("Manual import response", f"project_id mismatch: expected '{project_id}', got '{import_response['project_id']}'")
            return
            
        if import_response["total_items"] != 2:
            results.log_fail("Manual import response", f"total_items mismatch: expected 2, got {import_response['total_items']}")
            return
            
        results.log_pass("Manual import with items")
        print(f"   Import created: {import_response['total_items']} items, status: {import_response['status']}")
        
        # Test with CSV data
        csv_content = "type,url\naccount,https://www.tiktok.com/@mrbeast\nvideo,https://www.tiktok.com/@mrbeast/video/7345678901234567890"
        csv_base64 = base64.b64encode(csv_content.encode()).decode()
        
        csv_import_data = {
            "project_id": project_id,
            "csv_base64": csv_base64
        }
        
        response = requests.post(f"{BASE_URL}/imports/manual", json=csv_import_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Manual import with CSV", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        csv_response = response.json()
        
        if csv_response["total_items"] != 2:
            results.log_fail("Manual import CSV response", f"total_items mismatch: expected 2, got {csv_response['total_items']}")
            return
            
        results.log_pass("Manual import with CSV")
        print(f"   CSV import created: {csv_response['total_items']} items")
        
    except Exception as e:
        results.log_fail("Manual import", f"Request failed: {str(e)}")

def test_manual_import_errors(results: TestResults):
    """Test POST /api/imports/manual with invalid data"""
    try:
        # Test with invalid project_id
        invalid_data = {
            "project_id": "invalid_project_id_123",
            "items": [
                {
                    "type": "account",
                    "url": "https://www.tiktok.com/@test"
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/imports/manual", json=invalid_data, timeout=10)
        
        if response.status_code not in [400, 404]:
            results.log_fail("Manual import invalid project_id", f"Expected 400 or 404, got {response.status_code}")
        else:
            error_response = response.json()
            if "detail" not in error_response:
                results.log_fail("Manual import invalid project_id", "Missing error detail in response")
            else:
                results.log_pass("Manual import invalid project_id")
                print(f"   Correctly rejected invalid project_id: {error_response['detail']}")
        
        # Test with invalid CSV base64
        invalid_csv_data = {
            "project_id": "507f1f77bcf86cd799439011",  # Valid ObjectId format but non-existent
            "csv_base64": "invalid_base64_data!!!"
        }
        
        response = requests.post(f"{BASE_URL}/imports/manual", json=invalid_csv_data, timeout=10)
        
        if response.status_code not in [400, 404]:
            results.log_fail("Manual import invalid CSV", f"Expected 400 or 404, got {response.status_code}")
        else:
            error_response = response.json()
            if "detail" not in error_response:
                results.log_fail("Manual import invalid CSV", "Missing error detail in response")
            else:
                results.log_pass("Manual import invalid CSV")
                print(f"   Correctly rejected invalid CSV: {error_response['detail']}")
        
    except Exception as e:
        results.log_fail("Manual import error handling", f"Request failed: {str(e)}")

def main():
    """Run all backend tests"""
    print(f"🚀 Starting TikTok Auditorium Backend Tests")
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
    
    # Test 4: Manual Import Success Cases
    print("\n4️⃣ Testing Manual Import (Success Cases)")
    test_manual_import_success(results, project_id)
    
    # Test 5: Manual Import Error Cases
    print("\n5️⃣ Testing Manual Import (Error Cases)")
    test_manual_import_errors(results)
    
    # Final summary
    success = results.summary()
    
    if success:
        print("\n🎉 All tests passed! Backend is working correctly.")
        sys.exit(0)
    else:
        print(f"\n💥 {results.failed} test(s) failed. Backend needs attention.")
        sys.exit(1)

if __name__ == "__main__":
    main()