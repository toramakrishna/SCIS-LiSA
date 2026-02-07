#!/usr/bin/env python3
"""
Test Ollama Cloud Connection
Tests connectivity to configured Ollama endpoint (Cloud or Local)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / '.env')

from ollama import Client


def test_ollama_connection():
    """Test connection to Ollama endpoint"""
    
    # Determine mode
    ollama_mode = os.getenv('OLLAMA_MODE', 'local').lower()
    
    if ollama_mode == 'cloud':
        # Cloud configuration
        ollama_host = os.getenv('OLLAMA_CLOUD_HOST', 'https://ollama.com')
        ollama_model = os.getenv('OLLAMA_CLOUD_MODEL', 'qwen3-coder-next')
        ollama_api_key = os.getenv('OLLAMA_API_KEY')
        mode_emoji = "🌩️"
        mode_name = "CLOUD"
    else:
        # Local configuration
        ollama_host = os.getenv('OLLAMA_LOCAL_HOST', 'http://localhost:11434')
        ollama_model = os.getenv('OLLAMA_LOCAL_MODEL', 'llama3.2')
        ollama_api_key = None
        mode_emoji = "🖥️"
        mode_name = "LOCAL"
    
    print("="*70)
    print(f"{mode_emoji}  OLLAMA {mode_name} CONNECTION TEST")
    print("="*70)
    print(f"Mode: {ollama_mode}")
    print(f"Host: {ollama_host}")
    print(f"Model: {ollama_model}")
    print(f"API Key: {'✓ Configured' if ollama_api_key else '✗ Not configured (local mode)'}")
    print("="*70)
    print()
    
    # Initialize client
    try:
        if ollama_api_key:
            print("Initializing Ollama cloud client with API key...")
            client = Client(
                host=ollama_host,
                headers={'Authorization': f'Bearer {ollama_api_key}'}
            )
        else:
            print("Initializing local Ollama client...")
            client = Client(host=ollama_host)
        print("✓ Client initialized")
    except Exception as e:
        print(f"✗ Failed to initialize client: {e}")
        return False
    
    print()
    
    # Test 1: List available models
    print("Test 1: Listing available models...")
    models = []  # Initialize models list
    try:
        models_response = client.list()
        models = models_response.get('models', [])
        print(f"✓ Found {len(models)} models available:")
        for model in models:  # Show all models
            model_name = model.get('name', 'unknown')
            print(f"  - {model_name}")
    except Exception as e:
        print(f"✗ Failed to list models: {e}")
        print("  This might be expected for cloud Ollama service")
        print("  Proceeding with generation test...")
    
    print()
    
    # Test 2: Check if specified model is available (only for local)
    if not ollama_api_key and models:
        print(f"Test 2: Checking if model '{ollama_model}' is available...")
        model_found = any(m.get('name', '').startswith(ollama_model) for m in models)
        if model_found:
            print(f"✓ Model '{ollama_model}' is available")
        else:
            print(f"⚠ Model '{ollama_model}' not found in local models")
            print("  Available models:")
            for model in models:
                print(f"  - {model.get('name', 'unknown')}")
            print()
            print(f"  To pull the model, run: ollama pull {ollama_model}")
        print()
    
    # Test 3: Test query generation
    print(f"Test 3: Testing text generation with model '{ollama_model}'...")
    try:
        response = client.generate(
            model=ollama_model,
            prompt="Say 'Hello from Ollama Cloud!' if you can read this.",
            stream=False,
            options={
                'temperature': 0.1,
                'num_predict': 50
            }
        )
        generated_text = response.get("response", "")
        print(f"✓ Model responded successfully!")
        print(f"  Response: {generated_text[:150]}...")
    except Exception as e:
        print(f"✗ Query generation failed: {e}")
        print("\n  Troubleshooting:")
        print("  1. Check if OLLAMA_HOST is correct in .env")
        print("  2. Verify OLLAMA_API_KEY is valid (for cloud)")
        print(f"  3. Ensure model '{ollama_model}' exists")
        print("  4. Check network connectivity")
        return False
    
    print()
    print("="*70)
    print("✓ ALL TESTS PASSED!")
    print("Your Ollama connection is working correctly.")
    print("="*70)
    return True


def main():
    """Run connection tests"""
    try:
        result = test_ollama_connection()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
