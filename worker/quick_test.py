#!/usr/bin/env python3
"""Quick test for trial and error functionality"""

from smart_automation_workflow import SmartAutomationWorkflow
import time

def quick_test():
    print("=== QUICK TRIAL AND ERROR TEST ===")
    
    workflow = SmartAutomationWorkflow()
    
    # Test 1: Valid site that should work
    print("\nTest 1: Valid site with forms")
    start = time.time()
    result1 = workflow.execute_smart_workflow(
        'Test basic automation', 
        'https://httpbin.org/forms/post'
    )
    time1 = time.time() - start
    
    print(f"Success: {result1.get('success')}")
    print(f"Browser: {result1.get('browser_used')}")
    print(f"Time: {time1:.2f}s")
    print(f"Method: {result1.get('fetch_result', {}).get('method', 'unknown')}")
    
    # Test 2: Check if fallbacks work
    print(f"\nTest 2: Checking fallback methods")
    fetch_result = result1.get('fetch_result', {})
    if 'methods_tried' in fetch_result:
        print(f"Methods tried: {fetch_result['methods_tried']}")
    else:
        print("Single method used (no fallback needed)")
    
    # Test 3: Invalid site (should fail gracefully)
    print(f"\nTest 3: Invalid site (should fail)")
    start = time.time()
    result2 = workflow.execute_smart_workflow(
        'Test invalid site', 
        'https://invalid-site-12345.com'
    )
    time2 = time.time() - start
    
    print(f"Success: {result2.get('success')} (Expected: False)")
    print(f"Time: {time2:.2f}s")
    print(f"Error handling: {'Good' if not result2.get('success') else 'Issue'}")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Valid site test: {'PASS' if result1.get('success') else 'FAIL'}")
    print(f"Invalid site test: {'PASS' if not result2.get('success') else 'FAIL'}")
    print(f"Trial and error system: {'WORKING' if result1.get('success') and not result2.get('success') else 'NEEDS CHECK'}")
    
    # Cleanup
    workflow.cleanup()
    print("\nTest complete!")

if __name__ == "__main__":
    quick_test() 