#!/usr/bin/env python3
"""
Comprehensive Test Suite for Local Mem0 Chrome Extension
Combines infrastructure validation with LLM effectiveness testing
"""

import sys
import importlib.util
from datetime import datetime

def load_test_module(file_path):
    """Dynamically load a test module"""
    spec = importlib.util.spec_from_file_location("test_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_comprehensive_tests():
    """Run all test suites and provide comprehensive assessment"""
    print("🧠 COMPREHENSIVE LOCAL MEM0 CHROME EXTENSION TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    test_results = {}
    
    # Phase 1: Infrastructure and Deterministic Tests
    print("\n🔧 PHASE 1: INFRASTRUCTURE VALIDATION")
    print("-" * 50)
    try:
        deterministic_module = load_test_module("test_deterministic_mem0.py")
        infrastructure_result = deterministic_module.run_deterministic_tests()
        test_results["infrastructure"] = infrastructure_result
        
        if infrastructure_result:
            print("✅ Infrastructure is solid and ready for LLM testing")
        else:
            print("❌ Infrastructure issues detected - fixing these is critical")
            
    except Exception as e:
        print(f"❌ Infrastructure tests failed to run: {e}")
        test_results["infrastructure"] = False
    
    # Phase 2: LLM Effectiveness Tests
    print("\n🤖 PHASE 2: LLM EFFECTIVENESS VALIDATION")
    print("-" * 50)
    
    if test_results.get("infrastructure", False):
        try:
            llm_module = load_test_module("test_llm_intention.py")
            llm_result = llm_module.run_llm_intention_tests()
            test_results["llm_effectiveness"] = llm_result
            
        except Exception as e:
            print(f"❌ LLM effectiveness tests failed to run: {e}")
            test_results["llm_effectiveness"] = False
    else:
        print("⏭️  Skipping LLM tests due to infrastructure failures")
        test_results["llm_effectiveness"] = None
    
    # Final Assessment
    print("\n" + "=" * 70)
    print("🎯 FINAL ASSESSMENT")
    print("=" * 70)
    
    print("\n📊 Test Results Summary:")
    for test_type, result in test_results.items():
        if result is True:
            print(f"  ✅ {test_type.replace('_', ' ').title()}: PASSED")
        elif result is False:
            print(f"  ❌ {test_type.replace('_', ' ').title()}: FAILED")
        else:
            print(f"  ⏭️  {test_type.replace('_', ' ').title()}: SKIPPED")
    
    # Overall system assessment
    infrastructure_ok = test_results.get("infrastructure", False)
    llm_effective = test_results.get("llm_effectiveness", False)
    
    print(f"\n🎪 OVERALL SYSTEM STATUS:")
    
    if infrastructure_ok and llm_effective:
        print("🎉 EXCELLENT: Your local Mem0 system is fully functional!")
        print("   • Infrastructure is solid")
        print("   • LLM is effective and useful")
        print("   • Chrome extension should work perfectly")
        system_status = "excellent"
        
    elif infrastructure_ok and not llm_effective:
        print("⚠️  GOOD: Infrastructure works, but LLM needs improvement")
        print("   • All APIs and services are functional")
        print("   • LLM effectiveness is below threshold")
        print("   • Consider: Different model, better prompts, or tuning")
        system_status = "good"
        
    elif infrastructure_ok and llm_effective is None:
        print("✅ INFRASTRUCTURE READY: LLM tests were skipped")
        print("   • All infrastructure components working")
        print("   • Run LLM tests separately when ready")
        system_status = "infrastructure_ready"
        
    else:
        print("🚨 NEEDS ATTENTION: Infrastructure issues must be fixed first")
        print("   • Basic connectivity or API issues detected")
        print("   • Fix infrastructure before testing LLM effectiveness")
        system_status = "needs_attention"
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if system_status == "excellent":
        print("   • Your setup is optimal - enjoy using the extension!")
        print("   • Consider running these tests periodically to ensure continued performance")
        
    elif system_status == "good":
        print("   • Try adjusting LLM parameters in mem0-server/local_mem0_with_rag.py:")
        print("     - Lower temperature (0.0-0.3) for more focused responses")
        print("     - Adjust prompts for better memory extraction")
        print("   • Consider using a different Ollama model if available")
        
    elif system_status == "infrastructure_ready":
        print("   • Run LLM effectiveness tests: python3 test_llm_intention.py")
        print("   • Infrastructure is solid, so LLM issues should be easy to fix")
        
    else:
        print("   • Check that Ollama is running: curl http://localhost:11434/api/version")
        print("   • Check that Qdrant is running: curl http://localhost:6333/")
        print("   • Check that mem0 server is running: curl http://localhost:8000/")
        print("   • Review mem0-server logs for specific error messages")
    
    # Return codes for automation
    print(f"\n🏁 TEST COMPLETED")
    print(f"   System Status: {system_status.upper()}")
    print(f"   Infrastructure: {'✅ PASS' if infrastructure_ok else '❌ FAIL'}")
    print(f"   LLM Effectiveness: {'✅ PASS' if llm_effective else '❌ FAIL' if llm_effective is False else '⏭️ SKIPPED'}")
    
    return system_status in ["excellent", "good", "infrastructure_ready"]

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1) 
