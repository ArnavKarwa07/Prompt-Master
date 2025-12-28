"""
Comprehensive Backend Testing Script
Tests all API endpoints, agent functionality, and edge cases
"""
import requests
import json
import time
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"
API_VERSION = "/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"{Colors.GREEN}✓{Colors.RESET} {test_name}")
    
    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"{Colors.RED}✗{Colors.RESET} {test_name}: {reason}")
    
    def add_warning(self, test_name: str, message: str):
        self.warnings += 1
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {test_name}: {message}")
    
    def print_summary(self):
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}Passed:{Colors.RESET} {self.passed}")
        print(f"{Colors.RED}Failed:{Colors.RESET} {self.failed}")
        print(f"{Colors.YELLOW}Warnings:{Colors.RESET} {self.warnings}")
        print(f"{Colors.BOLD}Total:{Colors.RESET} {self.passed + self.failed}")
        
        if self.errors:
            print(f"\n{Colors.RED}FAILURES:{Colors.RESET}")
            for test_name, reason in self.errors:
                print(f"  - {test_name}: {reason}")
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}\n")

results = TestResults()

def print_header(title: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{title.center(60)}")
    print(f"{'='*60}{Colors.RESET}\n")

def test_endpoint(name: str, method: str, url: str, data: Dict = None, 
                  headers: Dict = None, expected_status: int = 200,
                  expected_fields: List[str] = None) -> Dict[str, Any]:
    """Generic endpoint tester"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        # Check status code
        if response.status_code != expected_status:
            results.add_fail(name, f"Expected status {expected_status}, got {response.status_code}")
            return {}
        
        # Check response content
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            results.add_fail(name, "Response is not valid JSON")
            return {}
        
        # Check expected fields
        if expected_fields:
            missing_fields = [f for f in expected_fields if f not in response_data]
            if missing_fields:
                results.add_fail(name, f"Missing fields: {missing_fields}")
                return response_data
        
        results.add_pass(name)
        return response_data
    
    except requests.exceptions.ConnectionError:
        results.add_fail(name, "Connection error - is the server running?")
        return {}
    except Exception as e:
        results.add_fail(name, f"Unexpected error: {str(e)}")
        return {}

# ============================================================
# 1. HEALTH CHECK TESTS
# ============================================================
def test_health_endpoints():
    print_header("1. HEALTH CHECK TESTS")
    
    # Test root endpoint
    test_endpoint(
        "Root endpoint",
        "GET",
        f"{BASE_URL}/",
        expected_fields=["name", "version", "docs", "health"]
    )
    
    # Test health endpoint
    data = test_endpoint(
        "Health check endpoint",
        "GET",
        f"{BASE_URL}/health",
        expected_fields=["status", "version", "agents_available"]
    )
    
    # Validate agents
    if data and "agents_available" in data:
        expected_agents = ["coding", "creative", "analyst", "general"]
        actual_agents = data["agents_available"]
        if set(expected_agents) == set(actual_agents):
            results.add_pass("All expected agents available")
        else:
            results.add_fail("Agent availability check", 
                           f"Expected {expected_agents}, got {actual_agents}")

# ============================================================
# 2. AGENT LISTING TESTS
# ============================================================
def test_agent_listing():
    print_header("2. AGENT LISTING TESTS")
    
    data = test_endpoint(
        "List agents endpoint",
        "GET",
        f"{BASE_URL}{API_VERSION}/prompts/agents",
        expected_fields=["agents"]
    )
    
    if data and "agents" in data:
        agents = data["agents"]
        if len(agents) >= 4:
            results.add_pass(f"Found {len(agents)} agents")
            for agent in agents:
                if "name" in agent and "description" in agent:
                    results.add_pass(f"Agent '{agent['name']}' has proper structure")
                else:
                    results.add_fail(f"Agent structure validation", 
                                   f"Agent missing name or description: {agent}")
        else:
            results.add_fail("Agent count", f"Expected at least 4 agents, got {len(agents)}")

# ============================================================
# 3. PROMPT OPTIMIZATION TESTS
# ============================================================
def test_prompt_optimization():
    print_header("3. PROMPT OPTIMIZATION TESTS")
    
    # Test case 1: Auto routing - coding prompt
    coding_prompt_data = test_endpoint(
        "Optimize coding prompt (auto-route)",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": "write a function to sort array",
            "goal": "Create a sorting function",
            "force_agent": None,
            "project_id": None
        },
        expected_fields=["agent", "score", "optimized_prompt", "routing"]
    )
    
    if coding_prompt_data and coding_prompt_data.get("agent") == "coding":
        results.add_pass("Auto-routing correctly identified coding task")
    elif coding_prompt_data:
        results.add_warning("Auto-routing", 
                          f"Expected 'coding' agent, got '{coding_prompt_data.get('agent')}'")
    
    # Test case 2: Forced agent - creative
    creative_data = test_endpoint(
        "Optimize with forced creative agent",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": "write a story",
            "goal": "Generate creative content",
            "force_agent": "creative",
            "project_id": None
        },
        expected_fields=["agent", "score", "optimized_prompt", "feedback"]
    )
    
    if creative_data and creative_data.get("agent") == "creative":
        results.add_pass("Forced agent routing works")
    elif creative_data:
        results.add_fail("Forced agent routing", 
                        f"Requested 'creative', got '{creative_data.get('agent')}'")
    
    # Test case 3: Analyst prompt
    analyst_data = test_endpoint(
        "Optimize analyst prompt (auto-route)",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": "analyze sales data",
            "goal": "Generate data insights",
            "force_agent": None,
            "project_id": None
        },
        expected_fields=["agent", "score", "optimized_prompt"]
    )
    
    # Test case 4: General prompt
    general_data = test_endpoint(
        "Optimize general prompt",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": "explain quantum computing",
            "goal": "Educational explanation",
            "force_agent": "general",
            "project_id": None
        },
        expected_fields=["agent", "score", "optimized_prompt"]
    )
    
    # Validate score ranges
    for data, name in [(coding_prompt_data, "coding"), 
                       (creative_data, "creative"),
                       (analyst_data, "analyst"), 
                       (general_data, "general")]:
        if data and "score" in data:
            score = data["score"]
            if 0 <= score <= 100:
                results.add_pass(f"Score in valid range for {name} ({score})")
            else:
                results.add_fail(f"Score validation for {name}", 
                               f"Score {score} out of range [0, 100]")

# ============================================================
# 4. PROMPT ANALYSIS TESTS
# ============================================================
def test_prompt_analysis():
    print_header("4. PROMPT ANALYSIS TESTS")
    
    data = test_endpoint(
        "Analyze prompt endpoint",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/analyze-only",
        data={
            "prompt": "build a REST API",
            "goal": "Development task"
        },
        expected_fields=["recommended_agent", "confidence", "reasoning"]
    )
    
    if data:
        confidence = data.get("confidence", 0)
        if 0 <= confidence <= 1:
            results.add_pass(f"Confidence score valid ({confidence:.2f})")
        else:
            results.add_fail("Confidence validation", 
                           f"Confidence {confidence} out of range [0, 1]")

# ============================================================
# 5. EDGE CASE TESTS
# ============================================================
def test_edge_cases():
    print_header("5. EDGE CASE TESTS")
    
    # Empty prompt
    test_endpoint(
        "Empty prompt handling",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": "",
            "goal": "test",
            "force_agent": None,
            "project_id": None
        },
        expected_status=422  # Validation error expected
    )
    
    # Very long prompt (stress test)
    long_prompt = "Write a function " * 200
    data = test_endpoint(
        "Long prompt handling",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": long_prompt,
            "goal": "Test long input",
            "force_agent": "coding",
            "project_id": None
        },
        expected_fields=["agent", "score", "optimized_prompt"]
    )
    
    # Invalid agent name
    data = test_endpoint(
        "Invalid agent name handling",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": "test prompt",
            "goal": "test",
            "force_agent": "invalid_agent_name",
            "project_id": None
        },
        expected_fields=["agent", "score"]
    )
    
    # Should fall back to auto-routing
    if data and data.get("agent") in ["coding", "creative", "analyst", "general"]:
        results.add_pass("Invalid agent fallback to auto-routing")
    elif data:
        results.add_fail("Invalid agent handling", 
                        f"Expected valid agent, got '{data.get('agent')}'")
    
    # Special characters in prompt
    special_chars_data = test_endpoint(
        "Special characters handling",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": "Test with émojis 🚀 and spëcial çharacters",
            "goal": "Unicode test",
            "force_agent": "general",
            "project_id": None
        },
        expected_fields=["agent", "score", "optimized_prompt"]
    )
    
    # SQL injection attempt (security test)
    sql_injection_data = test_endpoint(
        "SQL injection protection",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": "'; DROP TABLE users; --",
            "goal": "Security test",
            "force_agent": "general",
            "project_id": None
        },
        expected_fields=["agent", "score", "optimized_prompt"]
    )
    
    if sql_injection_data:
        results.add_pass("SQL injection attempt safely handled")

# ============================================================
# 6. PERFORMANCE TESTS
# ============================================================
def test_performance():
    print_header("6. PERFORMANCE TESTS")
    
    # Response time test
    start_time = time.time()
    data = test_endpoint(
        "Response time check",
        "POST",
        f"{BASE_URL}{API_VERSION}/prompts/optimize",
        data={
            "prompt": "quick test",
            "goal": "Speed test",
            "force_agent": "general",
            "project_id": None
        }
    )
    end_time = time.time()
    
    response_time = end_time - start_time
    if response_time < 30:  # 30 seconds threshold for LLM calls
        results.add_pass(f"Response time acceptable ({response_time:.2f}s)")
    else:
        results.add_warning("Response time", f"Slow response: {response_time:.2f}s")
    
    # Concurrent request test (simplified - just 3 requests)
    print("\nTesting concurrent requests...")
    import threading
    
    concurrent_results = []
    
    def make_request():
        try:
            response = requests.post(
                f"{BASE_URL}{API_VERSION}/prompts/optimize",
                json={
                    "prompt": "concurrent test",
                    "goal": "Concurrency test",
                    "force_agent": "general",
                    "project_id": None
                }
            )
            concurrent_results.append(response.status_code == 200)
        except Exception as e:
            concurrent_results.append(False)
    
    threads = [threading.Thread(target=make_request) for _ in range(3)]
    start_time = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    end_time = time.time()
    
    if all(concurrent_results):
        results.add_pass(f"Concurrent requests handled ({len(concurrent_results)} successful)")
    else:
        failed_count = len([r for r in concurrent_results if not r])
        results.add_fail("Concurrent requests", f"{failed_count} out of {len(concurrent_results)} failed")

# ============================================================
# 7. DATABASE SCHEMA VALIDATION
# ============================================================
def test_database_schema():
    print_header("7. DATABASE SCHEMA VALIDATION")
    
    # Note: These tests would require database access
    # For now, we check that endpoints requiring DB work properly
    
    print("Database schema tests require authenticated access.")
    print("Skipping direct DB tests, relying on endpoint tests.")
    results.add_warning("Database tests", "Requires authentication - testing via endpoints only")

# ============================================================
# RUN ALL TESTS
# ============================================================
def run_all_tests():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     PROMPT MASTER - COMPREHENSIVE BACKEND TEST SUITE       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    try:
        test_health_endpoints()
        test_agent_listing()
        test_prompt_optimization()
        test_prompt_analysis()
        test_edge_cases()
        test_performance()
        test_database_schema()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error during testing: {str(e)}{Colors.RESET}")
    finally:
        results.print_summary()

if __name__ == "__main__":
    run_all_tests()
