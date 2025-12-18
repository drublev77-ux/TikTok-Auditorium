#!/usr/bin/env python3
"""
Backend API Testing Suite for TikTok Auditorium
Tests Phase 0-1 + Module A: Audience Avatar CRUD endpoints + Module B: Competitors + Module C: Creators
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

# ─── BILLING/PAYMENT TESTS ────────────────────────────────────────────────────

def test_billing_plans(results: TestResults):
    """Test subscription plans endpoints"""
    try:
        # Test list all plans
        response = requests.get(f"{BASE_URL}/billing/plans", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("List Billing Plans", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        plans = response.json()
        
        if not isinstance(plans, list) or len(plans) != 3:
            results.log_fail("List Billing Plans", f"Expected 3 plans, got {len(plans) if isinstance(plans, list) else 'non-list'}")
            return
            
        # Verify plan details
        expected_plans = {
            "basic": {"price_usd": 50, "name": "Basic"},
            "pro": {"price_usd": 100, "name": "Pro"}, 
            "agency": {"price_usd": 250, "name": "Agency"}
        }
        
        for plan in plans:
            plan_id = plan.get('id')
            if plan_id in expected_plans:
                expected = expected_plans[plan_id]
                if plan.get('price_usd') == expected['price_usd'] and plan.get('name') == expected['name']:
                    results.log_pass(f"Plan {plan_id} - Correct Details")
                    print(f"   Plan {plan_id}: ${plan['price_usd']} - {plan['name']}")
                else:
                    results.log_fail(f"Plan {plan_id} - Incorrect Details", f"Expected: {expected}, Got: price=${plan.get('price_usd')}, name={plan.get('name')}")
            else:
                results.log_fail("Plan Validation", f"Unexpected plan ID: {plan_id}")
        
        # Test individual plan endpoints
        for plan_id in ["basic", "pro", "agency"]:
            response = requests.get(f"{BASE_URL}/billing/plans/{plan_id}", timeout=10)
            if response.status_code == 200:
                plan_data = response.json()
                if plan_data.get('id') == plan_id:
                    results.log_pass(f"Get Individual Plan - {plan_id}")
                    print(f"   Retrieved {plan_id} plan successfully")
                else:
                    results.log_fail(f"Get Individual Plan - {plan_id}", "Plan ID mismatch in response")
            else:
                results.log_fail(f"Get Individual Plan - {plan_id}", f"Expected 200, got {response.status_code}")
        
        # Test invalid plan
        response = requests.get(f"{BASE_URL}/billing/plans/invalid", timeout=10)
        if response.status_code == 404:
            results.log_pass("Get Invalid Plan - 404 Response")
            print("   Correctly returned 404 for invalid plan")
        else:
            results.log_fail("Get Invalid Plan", f"Expected 404, got {response.status_code}")
            
    except Exception as e:
        results.log_fail("Billing Plans Tests", f"Request failed: {str(e)}")

def test_payment_methods(results: TestResults):
    """Test payment methods endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/billing/payment-methods", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Payment Methods", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        methods_data = response.json()
        
        # Verify required fields
        required_fields = ["methods", "crypto", "bank", "paypal"]
        for field in required_fields:
            if field not in methods_data:
                results.log_fail("Payment Methods Structure", f"Missing field '{field}'")
                return
                
        # Verify crypto wallet address
        crypto_wallet = methods_data['crypto'].get('wallet_address')
        expected_wallet = "0xcecd3bcf98d5642722258c346c5dc1cdb83c8986"
        if crypto_wallet == expected_wallet:
            results.log_pass("Crypto Wallet Address")
            print(f"   Crypto wallet: {crypto_wallet}")
        else:
            results.log_fail("Crypto Wallet Address", f"Expected: {expected_wallet}, Got: {crypto_wallet}")
            
        # Verify supported methods
        methods = methods_data['methods']
        expected_methods = ["crypto", "bank", "paypal"]
        if set(methods) == set(expected_methods):
            results.log_pass("Payment Methods List")
            print(f"   Supported methods: {methods}")
        else:
            results.log_fail("Payment Methods List", f"Expected: {expected_methods}, Got: {methods}")
            
    except Exception as e:
        results.log_fail("Payment Methods Test", f"Request failed: {str(e)}")

def test_payment_requests_creation(results: TestResults):
    """Test creating payment requests"""
    org_id = results.test_data.get("org_id")
    if not org_id:
        results.log_fail("Payment Requests Creation", "No org_id available")
        return
        
    try:
        # Test 1: Create crypto payment request
        crypto_request = {
            "org_id": org_id,
            "plan_id": "basic",
            "payment_method": "crypto",
            "crypto_network": "erc20",
            "crypto_token": "USDT"
        }
        
        response = requests.post(f"{BASE_URL}/billing/payment-requests", json=crypto_request, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Create Crypto Payment Request", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        crypto_response = response.json()
        results.test_data['crypto_request_id'] = crypto_response['id']
        
        # Verify crypto payment details
        if (crypto_response.get('payment_method') == 'crypto' and 
            crypto_response.get('amount_usd') == 50 and
            crypto_response.get('plan_id') == 'basic' and
            crypto_response.get('status') == 'pending'):
            results.log_pass("Create Crypto Payment Request")
            print(f"   Created crypto payment request: ${crypto_response['amount_usd']} for {crypto_response['plan_name']}")
        else:
            results.log_fail("Create Crypto Payment Request", "Response data validation failed")
            
        # Test 2: Create bank payment request
        bank_request = {
            "org_id": org_id,
            "plan_id": "pro", 
            "payment_method": "bank"
        }
        
        response = requests.post(f"{BASE_URL}/billing/payment-requests", json=bank_request, timeout=10)
        
        if response.status_code == 200:
            bank_response = response.json()
            results.test_data['bank_request_id'] = bank_response['id']
            results.log_pass("Create Bank Payment Request")
            print(f"   Created bank payment request: ${bank_response['amount_usd']} for {bank_response['plan_name']}")
        else:
            results.log_fail("Create Bank Payment Request", f"Expected 200, got {response.status_code}")
            
        # Test 3: Create PayPal payment request
        paypal_request = {
            "org_id": org_id,
            "plan_id": "agency",
            "payment_method": "paypal"
        }
        
        response = requests.post(f"{BASE_URL}/billing/payment-requests", json=paypal_request, timeout=10)
        
        if response.status_code == 200:
            paypal_response = response.json()
            results.test_data['paypal_request_id'] = paypal_response['id']
            results.log_pass("Create PayPal Payment Request")
            print(f"   Created PayPal payment request: ${paypal_response['amount_usd']} for {paypal_response['plan_name']}")
        else:
            results.log_fail("Create PayPal Payment Request", f"Expected 200, got {response.status_code}")
            
    except Exception as e:
        results.log_fail("Payment Requests Creation", f"Request failed: {str(e)}")

def test_payment_requests_errors(results: TestResults):
    """Test payment request error scenarios"""
    org_id = results.test_data.get("org_id")
    
    try:
        # Test 1: Crypto request without required fields
        invalid_crypto = {
            "org_id": org_id,
            "plan_id": "basic",
            "payment_method": "crypto"
            # Missing crypto_network and crypto_token
        }
        
        response = requests.post(f"{BASE_URL}/billing/payment-requests", json=invalid_crypto, timeout=10)
        
        if response.status_code == 400:
            results.log_pass("Payment Request Error - Missing Crypto Fields")
            print("   Correctly rejected crypto request without network/token")
        else:
            results.log_fail("Payment Request Error - Missing Crypto Fields", f"Expected 400, got {response.status_code}")
        
        # Test 2: Invalid org_id
        invalid_org_request = {
            "org_id": "invalid_org_id",
            "plan_id": "basic",
            "payment_method": "bank"
        }
        
        response = requests.post(f"{BASE_URL}/billing/payment-requests", json=invalid_org_request, timeout=10)
        
        if response.status_code == 400:
            results.log_pass("Payment Request Error - Invalid Org ID")
            print("   Correctly rejected invalid org_id")
        else:
            results.log_fail("Payment Request Error - Invalid Org ID", f"Expected 400, got {response.status_code}")
        
        # Test 3: Invalid plan_id (Pydantic validation returns 422)
        invalid_plan_request = {
            "org_id": org_id,
            "plan_id": "invalid_plan",
            "payment_method": "bank"
        }
        
        response = requests.post(f"{BASE_URL}/billing/payment-requests", json=invalid_plan_request, timeout=10)
        
        if response.status_code == 422:  # Pydantic validation error for invalid enum value
            results.log_pass("Payment Request Error - Invalid Plan ID")
            print("   Correctly rejected invalid plan_id with 422 (Pydantic validation)")
        else:
            results.log_fail("Payment Request Error - Invalid Plan ID", f"Expected 422, got {response.status_code}")
            
    except Exception as e:
        results.log_fail("Payment Request Error Tests", f"Request failed: {str(e)}")

def test_payment_requests_retrieval(results: TestResults):
    """Test retrieving payment requests"""
    org_id = results.test_data.get("org_id")
    
    try:
        # Test 1: List payment requests for org
        response = requests.get(f"{BASE_URL}/billing/payment-requests?org_id={org_id}", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("List Payment Requests", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        requests_list = response.json()
        
        if isinstance(requests_list, list) and len(requests_list) >= 1:
            results.log_pass("List Payment Requests")
            print(f"   Found {len(requests_list)} payment requests for org")
        else:
            results.log_fail("List Payment Requests", f"Expected list with at least 1 item, got {type(requests_list)} with {len(requests_list) if isinstance(requests_list, list) else 0} items")
            
        # Test 2: Get specific payment request
        if 'crypto_request_id' in results.test_data:
            request_id = results.test_data['crypto_request_id']
            response = requests.get(f"{BASE_URL}/billing/payment-requests/{request_id}", timeout=10)
            
            if response.status_code == 200:
                request_data = response.json()
                if request_data.get('id') == request_id:
                    results.log_pass("Get Specific Payment Request")
                    print(f"   Retrieved payment request: {request_data.get('plan_name')} - ${request_data.get('amount_usd')}")
                else:
                    results.log_fail("Get Specific Payment Request", "Request ID mismatch")
            else:
                results.log_fail("Get Specific Payment Request", f"Expected 200, got {response.status_code}")
        
        # Test 3: Error scenarios
        # Invalid request_id
        response = requests.get(f"{BASE_URL}/billing/payment-requests/invalid_id", timeout=10)
        if response.status_code == 400:
            results.log_pass("Get Payment Request - Invalid ID Error")
            print("   Correctly rejected invalid request ID")
        else:
            results.log_fail("Get Payment Request - Invalid ID Error", f"Expected 400, got {response.status_code}")
        
        # Non-existent request
        fake_id = "507f1f77bcf86cd799439011"
        response = requests.get(f"{BASE_URL}/billing/payment-requests/{fake_id}", timeout=10)
        if response.status_code == 404:
            results.log_pass("Get Payment Request - Not Found Error")
            print("   Correctly returned 404 for non-existent request")
        else:
            results.log_fail("Get Payment Request - Not Found Error", f"Expected 404, got {response.status_code}")
            
    except Exception as e:
        results.log_fail("Payment Requests Retrieval", f"Request failed: {str(e)}")

def test_payment_confirmation(results: TestResults):
    """Test payment confirmation and subscription creation"""
    if 'crypto_request_id' not in results.test_data:
        results.log_fail("Payment Confirmation", "No crypto request ID available")
        return
        
    request_id = results.test_data['crypto_request_id']
    
    try:
        # Test 1: Confirm payment
        response = requests.patch(f"{BASE_URL}/billing/payment-requests/{request_id}/confirm", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Confirm Payment Request", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        confirm_response = response.json()
        
        if confirm_response.get('status') == 'confirmed':
            results.log_pass("Confirm Payment Request")
            print(f"   Payment confirmed for {confirm_response.get('plan_name')} plan")
        else:
            results.log_fail("Confirm Payment Request", f"Expected status 'confirmed', got '{confirm_response.get('status')}'")
            
        # Test 2: Try to confirm again (should fail)
        response = requests.patch(f"{BASE_URL}/billing/payment-requests/{request_id}/confirm", timeout=10)
        
        if response.status_code == 400:
            results.log_pass("Confirm Payment Request - Already Confirmed Error")
            print("   Correctly rejected re-confirmation of already confirmed payment")
        else:
            results.log_fail("Confirm Payment Request - Already Confirmed Error", f"Expected 400, got {response.status_code}")
            
    except Exception as e:
        results.log_fail("Payment Confirmation", f"Request failed: {str(e)}")

def test_subscription_retrieval(results: TestResults):
    """Test subscription retrieval after payment confirmation"""
    org_id = results.test_data.get("org_id")
    
    try:
        # Get subscription for org
        response = requests.get(f"{BASE_URL}/billing/subscription?org_id={org_id}", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Get Subscription", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        sub_response = response.json()
        
        # Check if subscription was created after payment confirmation
        if 'id' in sub_response and sub_response.get('status') == 'active':
            results.log_pass("Get Active Subscription")
            print(f"   Active subscription: {sub_response.get('plan_name')} ({sub_response.get('plan_id')})")
            print(f"   Status: {sub_response.get('status')}")
        elif sub_response.get('subscription') is None:
            results.log_pass("Get Subscription - No Subscription Found")
            print("   No subscription found (expected if payment wasn't confirmed)")
        else:
            results.log_fail("Get Subscription", f"Unexpected response format: {sub_response}")
            
        # Test invalid org_id
        response = requests.get(f"{BASE_URL}/billing/subscription?org_id=invalid_org", timeout=10)
        if response.status_code == 400:
            results.log_pass("Get Subscription - Invalid Org ID Error")
            print("   Correctly rejected invalid org_id")
        else:
            results.log_fail("Get Subscription - Invalid Org ID Error", f"Expected 400, got {response.status_code}")
            
    except Exception as e:
        results.log_fail("Subscription Retrieval", f"Request failed: {str(e)}")

# ─── MODULE B: COMPETITORS TESTS ──────────────────────────────────────────────

def test_competitors_crud(results: TestResults):
    """Test Module B: Competitors CRUD operations"""
    project_id = results.test_data.get("project_id")
    if not project_id:
        results.log_fail("Competitors CRUD", "No project_id available")
        return
        
    competitor_id = None
    
    try:
        # Test 1: POST /api/competitors - Create competitor
        competitor_data = {
            "project_id": project_id,
            "name": "TikTok Fitness Guru",
            "tiktok_url": "https://www.tiktok.com/@fitnessguru123",
            "notes": "Popular fitness content creator with high engagement"
        }
        
        response = requests.post(f"{BASE_URL}/competitors", json=competitor_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Create Competitor", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        competitor = response.json()
        competitor_id = competitor["id"]
        results.test_data["competitor_id"] = competitor_id
        
        # Verify required fields
        required_fields = ["id", "project_id", "name", "tiktok_url", "notes", "created_at", "updated_at"]
        missing_fields = [field for field in required_fields if field not in competitor]
        
        if not missing_fields and competitor["name"] == competitor_data["name"]:
            results.log_pass("Create Competitor")
            print(f"   Created competitor: {competitor['name']} (ID: {competitor_id})")
        else:
            results.log_fail("Create Competitor", f"Missing fields: {missing_fields}")
            return
            
        # Test 2: GET /api/competitors?project_id=X - List competitors
        response = requests.get(f"{BASE_URL}/competitors", params={"project_id": project_id}, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("List Competitors", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        competitors = response.json()
        
        if isinstance(competitors, list) and len(competitors) >= 1:
            found_competitor = any(c["id"] == competitor_id for c in competitors)
            if found_competitor:
                results.log_pass("List Competitors")
                print(f"   Found {len(competitors)} competitor(s) for project")
            else:
                results.log_fail("List Competitors", "Created competitor not found in list")
        else:
            results.log_fail("List Competitors", f"Expected list with >= 1 item, got: {type(competitors)}")
            
        # Test 3: GET /api/competitors/:id - Get single competitor
        response = requests.get(f"{BASE_URL}/competitors/{competitor_id}", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Get Single Competitor", f"Expected 200, got {response.status_code}: {response.text}")
        else:
            single_competitor = response.json()
            if single_competitor["id"] == competitor_id and single_competitor["name"] == "TikTok Fitness Guru":
                results.log_pass("Get Single Competitor")
                print(f"   Retrieved competitor: {single_competitor['name']}")
            else:
                results.log_fail("Get Single Competitor", "Competitor data mismatch")
                
        # Test 4: PATCH /api/competitors/:id - Update competitor
        update_data = {
            "name": "Updated Fitness Guru",
            "notes": "Updated notes about this competitor"
        }
        
        response = requests.patch(f"{BASE_URL}/competitors/{competitor_id}", json=update_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Update Competitor", f"Expected 200, got {response.status_code}: {response.text}")
        else:
            updated_competitor = response.json()
            if (updated_competitor["name"] == "Updated Fitness Guru" and 
                updated_competitor["notes"] == "Updated notes about this competitor"):
                results.log_pass("Update Competitor")
                print(f"   Updated competitor: {updated_competitor['name']}")
            else:
                results.log_fail("Update Competitor", "Update data not reflected correctly")
                
        # Test 5: DELETE /api/competitors/:id - Delete competitor
        response = requests.delete(f"{BASE_URL}/competitors/{competitor_id}", timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Delete Competitor", f"Expected 200, got {response.status_code}: {response.text}")
        else:
            delete_result = response.json()
            if delete_result.get("status") == "deleted":
                results.log_pass("Delete Competitor")
                print(f"   Deleted competitor with ID: {competitor_id}")
            else:
                results.log_fail("Delete Competitor", f"Unexpected response: {delete_result}")
                
    except Exception as e:
        results.log_fail("Competitors CRUD", f"Request failed: {str(e)}")

def test_competitors_errors(results: TestResults):
    """Test Competitors API error scenarios"""
    try:
        # Test 1: Invalid project_id
        response = requests.get(f"{BASE_URL}/competitors", params={"project_id": "invalid_id"}, timeout=10)
        
        if response.status_code == 400:
            results.log_pass("Competitors Error - Invalid Project ID")
            print("   Correctly returned 400 for invalid project_id")
        else:
            results.log_fail("Competitors Error - Invalid Project ID", f"Expected 400, got {response.status_code}")
            
        # Test 2: Missing required fields
        invalid_data = {"project_id": "507f1f77bcf86cd799439011"}  # Missing name and tiktok_url
        response = requests.post(f"{BASE_URL}/competitors", json=invalid_data, timeout=10)
        
        if response.status_code == 422:
            results.log_pass("Competitors Error - Missing Fields")
            print("   Correctly returned 422 for missing required fields")
        else:
            results.log_fail("Competitors Error - Missing Fields", f"Expected 422, got {response.status_code}")
            
        # Test 3: Get non-existent competitor
        fake_id = "507f1f77bcf86cd799439011"
        response = requests.get(f"{BASE_URL}/competitors/{fake_id}", timeout=10)
        
        if response.status_code == 404:
            results.log_pass("Competitors Error - Get Non-existent")
            print("   Correctly returned 404 for non-existent competitor")
        else:
            results.log_fail("Competitors Error - Get Non-existent", f"Expected 404, got {response.status_code}")
            
    except Exception as e:
        results.log_fail("Competitors Error Tests", f"Request failed: {str(e)}")

# ─── MODULE C: CREATORS TESTS ─────────────────────────────────────────────────

def test_creators_crud(results: TestResults):
    """Test Module C: Creators CRUD operations with categories"""
    project_id = results.test_data.get("project_id")
    if not project_id:
        results.log_fail("Creators CRUD", "No project_id available")
        return
        
    creator_ids = []
    
    try:
        # Test 1: POST /api/creators - Create creator with category "fitness"
        fitness_creator_data = {
            "project_id": project_id,
            "name": "Fitness Blogger Sarah",
            "tiktok_url": "https://www.tiktok.com/@sarahfitness",
            "category": "fitness",
            "notes": "Popular fitness blogger with workout routines"
        }
        
        response = requests.post(f"{BASE_URL}/creators", json=fitness_creator_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Create Fitness Creator", f"Expected 200, got {response.status_code}: {response.text}")
            return
            
        fitness_creator = response.json()
        creator_ids.append(fitness_creator["id"])
        results.test_data["fitness_creator_id"] = fitness_creator["id"]
        
        # Verify required fields
        required_fields = ["id", "project_id", "name", "tiktok_url", "category", "notes", "created_at", "updated_at"]
        missing_fields = [field for field in required_fields if field not in fitness_creator]
        
        if not missing_fields and fitness_creator["category"] == "fitness":
            results.log_pass("Create Fitness Creator")
            print(f"   Created fitness creator: {fitness_creator['name']} (Category: {fitness_creator['category']})")
        else:
            results.log_fail("Create Fitness Creator", f"Missing fields: {missing_fields}")
            
        # Test 2: POST /api/creators - Create another creator with category "beauty"
        beauty_creator_data = {
            "project_id": project_id,
            "name": "Beauty Guru Emma",
            "tiktok_url": "https://www.tiktok.com/@emmabeauty",
            "category": "beauty",
            "notes": "Makeup tutorials and beauty tips"
        }
        
        response = requests.post(f"{BASE_URL}/creators", json=beauty_creator_data, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Create Beauty Creator", f"Expected 200, got {response.status_code}: {response.text}")
        else:
            beauty_creator = response.json()
            creator_ids.append(beauty_creator["id"])
            results.test_data["beauty_creator_id"] = beauty_creator["id"]
            
            if beauty_creator["category"] == "beauty":
                results.log_pass("Create Beauty Creator")
                print(f"   Created beauty creator: {beauty_creator['name']} (Category: {beauty_creator['category']})")
            else:
                results.log_fail("Create Beauty Creator", f"Category mismatch: expected 'beauty', got '{beauty_creator['category']}'")
                
        # Test 3: GET /api/creators?project_id=X - List all creators
        response = requests.get(f"{BASE_URL}/creators", params={"project_id": project_id}, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("List All Creators", f"Expected 200, got {response.status_code}: {response.text}")
        else:
            creators = response.json()
            if isinstance(creators, list) and len(creators) >= 2:
                categories = [creator["category"] for creator in creators]
                if "fitness" in categories and "beauty" in categories:
                    results.log_pass("List All Creators")
                    print(f"   Found {len(creators)} creators with categories: {set(categories)}")
                else:
                    results.log_fail("List All Creators", f"Missing expected categories. Found: {categories}")
            else:
                results.log_fail("List All Creators", f"Expected list with >= 2 items, got: {len(creators) if isinstance(creators, list) else 'not a list'}")
                
        # Test 4: GET /api/creators?project_id=X&category=fitness - Filter by category
        response = requests.get(f"{BASE_URL}/creators", params={"project_id": project_id, "category": "fitness"}, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Filter Creators by Fitness", f"Expected 200, got {response.status_code}: {response.text}")
        else:
            fitness_creators = response.json()
            if isinstance(fitness_creators, list) and len(fitness_creators) == 1 and fitness_creators[0]["category"] == "fitness":
                results.log_pass("Filter Creators by Fitness")
                print(f"   Found 1 fitness creator: {fitness_creators[0]['name']}")
            else:
                results.log_fail("Filter Creators by Fitness", f"Expected 1 fitness creator, got: {len(fitness_creators) if isinstance(fitness_creators, list) else 'not a list'}")
                
        # Test 5: GET /api/creators/categories/list?project_id=X - Get categories list
        response = requests.get(f"{BASE_URL}/creators/categories/list", params={"project_id": project_id}, timeout=10)
        
        if response.status_code != 200:
            results.log_fail("Get Creator Categories", f"Expected 200, got {response.status_code}: {response.text}")
        else:
            categories = response.json()
            if isinstance(categories, list) and "fitness" in categories and "beauty" in categories:
                results.log_pass("Get Creator Categories")
                print(f"   Found categories: {sorted(categories)}")
            else:
                results.log_fail("Get Creator Categories", f"Missing expected categories. Got: {categories}")
                
        # Test 6: GET /api/creators/:id - Get single creator
        if creator_ids:
            response = requests.get(f"{BASE_URL}/creators/{creator_ids[0]}", timeout=10)
            
            if response.status_code != 200:
                results.log_fail("Get Single Creator", f"Expected 200, got {response.status_code}: {response.text}")
            else:
                single_creator = response.json()
                if single_creator["id"] == creator_ids[0] and single_creator["name"] == "Fitness Blogger Sarah":
                    results.log_pass("Get Single Creator")
                    print(f"   Retrieved creator: {single_creator['name']}")
                else:
                    results.log_fail("Get Single Creator", "Creator data mismatch")
                    
        # Test 7: PATCH /api/creators/:id - Update creator
        if creator_ids:
            update_data = {
                "name": "Updated Fitness Sarah",
                "category": "health",
                "notes": "Updated notes about health and fitness"
            }
            
            response = requests.patch(f"{BASE_URL}/creators/{creator_ids[0]}", json=update_data, timeout=10)
            
            if response.status_code != 200:
                results.log_fail("Update Creator", f"Expected 200, got {response.status_code}: {response.text}")
            else:
                updated_creator = response.json()
                if (updated_creator["name"] == "Updated Fitness Sarah" and 
                    updated_creator["category"] == "health" and 
                    updated_creator["notes"] == "Updated notes about health and fitness"):
                    results.log_pass("Update Creator")
                    print(f"   Updated creator: {updated_creator['name']} (Category: {updated_creator['category']})")
                else:
                    results.log_fail("Update Creator", "Update data not reflected correctly")
                    
        # Test 8: DELETE /api/creators/:id - Delete creators
        for i, creator_id in enumerate(creator_ids):
            response = requests.delete(f"{BASE_URL}/creators/{creator_id}", timeout=10)
            
            if response.status_code != 200:
                results.log_fail(f"Delete Creator {i+1}", f"Expected 200, got {response.status_code}: {response.text}")
            else:
                delete_result = response.json()
                if delete_result.get("status") == "deleted":
                    results.log_pass(f"Delete Creator {i+1}")
                    print(f"   Deleted creator with ID: {creator_id}")
                else:
                    results.log_fail(f"Delete Creator {i+1}", f"Unexpected response: {delete_result}")
                    
    except Exception as e:
        results.log_fail("Creators CRUD", f"Request failed: {str(e)}")

def test_creators_errors(results: TestResults):
    """Test Creators API error scenarios"""
    project_id = results.test_data.get("project_id")
    
    try:
        # Test 1: Invalid creator_id
        response = requests.get(f"{BASE_URL}/creators/invalid_id", timeout=10)
        
        if response.status_code == 400:
            results.log_pass("Creators Error - Invalid Creator ID")
            print("   Correctly returned 400 for invalid creator_id")
        else:
            results.log_fail("Creators Error - Invalid Creator ID", f"Expected 400, got {response.status_code}")
            
        # Test 2: Missing required fields
        invalid_data = {"project_id": project_id}  # Missing name and tiktok_url
        response = requests.post(f"{BASE_URL}/creators", json=invalid_data, timeout=10)
        
        if response.status_code == 422:
            results.log_pass("Creators Error - Missing Fields")
            print("   Correctly returned 422 for missing required fields")
        else:
            results.log_fail("Creators Error - Missing Fields", f"Expected 422, got {response.status_code}")
            
        # Test 3: Get non-existent creator
        fake_id = "507f1f77bcf86cd799439011"
        response = requests.get(f"{BASE_URL}/creators/{fake_id}", timeout=10)
        
        if response.status_code == 404:
            results.log_pass("Creators Error - Get Non-existent")
            print("   Correctly returned 404 for non-existent creator")
        else:
            results.log_fail("Creators Error - Get Non-existent", f"Expected 404, got {response.status_code}")
            
        # Test 4: Invalid project_id for categories
        response = requests.get(f"{BASE_URL}/creators/categories/list", params={"project_id": "invalid_id"}, timeout=10)
        
        if response.status_code == 400:
            results.log_pass("Creators Error - Invalid Project ID for Categories")
            print("   Correctly returned 400 for invalid project_id in categories endpoint")
        else:
            results.log_fail("Creators Error - Invalid Project ID for Categories", f"Expected 400, got {response.status_code}")
            
    except Exception as e:
        results.log_fail("Creators Error Tests", f"Request failed: {str(e)}")

def main():
    """Run all backend tests including Avatar API, Billing/Payment, Competitors, and Creators tests"""
    print(f"🚀 Starting TikTok Auditorium Backend Tests (Phase 0-1 + Module A + Billing + Module B + Module C)")
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
    
    # Module A - Audience Avatar Tests
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
    
    # Billing/Payment Tests
    print("\n💳 BILLING/PAYMENT SYSTEM TESTS")
    print("="*40)
    
    print("\n1️⃣1️⃣ Testing Billing Plans")
    test_billing_plans(results)
    
    print("\n1️⃣2️⃣ Testing Payment Methods")
    test_payment_methods(results)
    
    print("\n1️⃣3️⃣ Testing Payment Request Creation")
    test_payment_requests_creation(results)
    
    print("\n1️⃣4️⃣ Testing Payment Request Errors")
    test_payment_requests_errors(results)
    
    print("\n1️⃣5️⃣ Testing Payment Request Retrieval")
    test_payment_requests_retrieval(results)
    
    print("\n1️⃣6️⃣ Testing Payment Confirmation")
    test_payment_confirmation(results)
    
    print("\n1️⃣7️⃣ Testing Subscription Retrieval")
    test_subscription_retrieval(results)
    
    # NEW: Module B - Competitors Tests
    print("\n🏆 MODULE B: COMPETITORS API TESTS")
    print("="*40)
    
    print("\n1️⃣8️⃣ Testing Competitors CRUD Operations")
    test_competitors_crud(results)
    
    print("\n1️⃣9️⃣ Testing Competitors Error Scenarios")
    test_competitors_errors(results)
    
    # NEW: Module C - Creators Tests
    print("\n🎨 MODULE C: CREATORS API TESTS")
    print("="*40)
    
    print("\n2️⃣0️⃣ Testing Creators CRUD Operations")
    test_creators_crud(results)
    
    print("\n2️⃣1️⃣ Testing Creators Error Scenarios")
    test_creators_errors(results)
    
    # Final summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Backend Phase 0-1 + Module A + Billing/Payment + Module B + Module C are working correctly.")
        sys.exit(0)
    else:
        print(f"\n💥 {results.failed} test(s) failed. Backend needs attention.")
        sys.exit(1)

if __name__ == "__main__":
    main()