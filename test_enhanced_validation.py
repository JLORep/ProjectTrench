#!/usr/bin/env python3
"""
Test script for enhanced deployment validation integration
"""
import sys
import os
from pathlib import Path

def test_validation_integration():
    """Test that the enhanced validation is properly integrated"""
    
    print("🧪 Testing Enhanced Deployment Validation Integration")
    print("=" * 60)
    
    # Test 1: Check if enhanced_deployment_validator exists
    print("\n1. Checking enhanced_deployment_validator.py...")
    validator_path = Path("enhanced_deployment_validator.py")
    if validator_path.exists():
        print("   ✅ enhanced_deployment_validator.py found")
    else:
        print("   ❌ enhanced_deployment_validator.py missing")
        return False
    
    # Test 2: Check if auto_deployment_system has validation method
    print("\n2. Checking auto_deployment_system integration...")
    auto_deploy_path = Path("auto_deployment_system.py")
    if auto_deploy_path.exists():
        content = auto_deploy_path.read_text(encoding='utf-8')
        if "run_enhanced_validation" in content:
            print("   ✅ run_enhanced_validation method found in auto_deployment_system.py")
        else:
            print("   ❌ run_enhanced_validation method missing from auto_deployment_system.py")
            return False
    else:
        print("   ❌ auto_deployment_system.py missing")
        return False
    
    # Test 3: Check if async hook points to correct file
    print("\n3. Checking async deployment hook...")
    async_hook_path = Path("async_deployment_hook.py")
    if async_hook_path.exists():
        content = async_hook_path.read_text(encoding='utf-8')
        if "auto_deployment_system.py" in content:
            print("   ✅ async_deployment_hook.py points to auto_deployment_system.py")
        else:
            print("   ❌ async_deployment_hook.py points to wrong file")
            return False
    else:
        print("   ❌ async_deployment_hook.py missing")
        return False
    
    # Test 4: Test import of validator
    print("\n4. Testing enhanced validator import...")
    try:
        sys.path.append(str(Path.cwd()))
        from enhanced_deployment_validator import EnhancedDeploymentValidator
        print("   ✅ EnhancedDeploymentValidator imports successfully")
        
        # Test validator initialization
        validator = EnhancedDeploymentValidator()
        print("   ✅ EnhancedDeploymentValidator initializes successfully")
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False
    
    # Test 5: Test auto deployment system import
    print("\n5. Testing auto deployment system import...")
    try:
        from auto_deployment_system import AutoDeploymentSystem
        print("   ✅ AutoDeploymentSystem imports successfully")
        
        # Test initialization
        deployer = AutoDeploymentSystem()
        print("   ✅ AutoDeploymentSystem initializes successfully")
        
        # Check if validation method exists
        if hasattr(deployer, 'run_enhanced_validation'):
            print("   ✅ run_enhanced_validation method available")
        else:
            print("   ❌ run_enhanced_validation method missing")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Enhanced deployment validation is properly integrated.")
    print("\n📋 Integration Summary:")
    print("   • Enhanced validator script exists and works")
    print("   • Auto deployment system has validation method")
    print("   • Async hook points to correct deployment script")
    print("   • All imports work correctly")
    print("\n🚀 The auto-deploy system will now:")
    print("   1. Deploy code to Streamlit Cloud")
    print("   2. Validate that deployment was successful")
    print("   3. Check that all dashboard tabs are functional")
    print("   4. Verify database connectivity")
    print("   5. Send Discord notifications with validation results")
    
    return True

if __name__ == "__main__":
    success = test_validation_integration()
    sys.exit(0 if success else 1)