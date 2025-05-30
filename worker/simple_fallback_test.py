#!/usr/bin/env python3
"""Simple fallback test - focuses on testing HTTP fallbacks when browser hangs"""

import time
import requests
from smart_automation_workflow import SmartAutomationWorkflow

def test_http_fallbacks():
    """Test HTTP fallback mechanisms directly"""
    print("=== TESTING HTTP FALLBACK MECHANISMS ===")
    
    workflow = SmartAutomationWorkflow()
    
    # Test 1: Direct HTTP session test
    print("\nTest 1: Direct HTTP session test")
    try:
        result = workflow._fetch_with_session("https://httpbin.org/forms/post")
        print(f"HTTP Session Success: {result.get('success')}")
        print(f"Method: {result.get('method')}")
        if result.get('success'):
            page_data = result.get('page_data', {})
            element_counts = page_data.get('element_counts', {})
            print(f"Interactive elements found: {element_counts.get('total_interactive', 0)}")
    except Exception as e:
        print(f"HTTP Session Error: {e}")
    
    # Test 2: Basic HTTP test
    print("\nTest 2: Basic HTTP test")
    try:
        result = workflow._fetch_basic("https://httpbin.org/html")
        print(f"Basic HTTP Success: {result.get('success')}")
        print(f"Method: {result.get('method')}")
        if result.get('success'):
            page_data = result.get('page_data', {})
            clean_content = page_data.get('clean_body_content', {})
            print(f"Content length: {clean_content.get('content_length', 0)}")
    except Exception as e:
        print(f"Basic HTTP Error: {e}")
    
    # Test 3: Full workflow with quick timeout (should fall back to HTTP)
    print("\nTest 3: Full workflow (should use HTTP fallbacks)")
    start_time = time.time()
    
    try:
        # Force browser failure by creating a workflow that will timeout quickly
        result = workflow.execute_smart_workflow(
            'Test automation with fallbacks',
            'https://httpbin.org/forms/post'
        )
        
        execution_time = time.time() - start_time
        print(f"Workflow Success: {result.get('success')}")
        print(f"Execution Time: {execution_time:.2f}s")
        print(f"Browser Used: {result.get('browser_used', 'unknown')}")
        
        # Check which method was actually used
        fetch_result = result.get('fetch_result', {})
        method_used = fetch_result.get('method', 'unknown')
        print(f"Scraping Method Used: {method_used}")
        
        # If it's HTTP method, that means browser failed and fallback worked
        if 'http' in method_used:
            print("✓ HTTP fallback mechanism working!")
        elif 'browser' in method_used:
            print("✓ Browser method worked (no fallback needed)")
        else:
            print("? Unknown method used")
            
        # Show some logs
        logs = result.get('logs', [])
        print(f"Log entries: {len(logs)}")
        if logs:
            print("Sample logs:")
            for log in logs[:3]:
                print(f"  - {log}")
    
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"Workflow Error: {e}")
        print(f"Time before error: {execution_time:.2f}s")
    
    print("\n=== FALLBACK TEST COMPLETE ===")

def test_simple_requests():
    """Test simple requests without any automation"""
    print("\n=== TESTING SIMPLE REQUESTS ===")
    
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/forms/post",
        "https://www.w3schools.com/"
    ]
    
    for url in urls:
        print(f"\nTesting: {url}")
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            end = time.time()
            
            print(f"  Status: {response.status_code}")
            print(f"  Time: {end - start:.2f}s")
            print(f"  Content length: {len(response.text)}")
            print(f"  Success: ✓")
            
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Success: ✗")

if __name__ == "__main__":
    # First test simple requests to make sure network is working
    test_simple_requests()
    
    # Then test fallback mechanisms
    test_http_fallbacks() 