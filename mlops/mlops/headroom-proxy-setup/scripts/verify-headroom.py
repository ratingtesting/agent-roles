#!/usr/bin/env python3
"""
Verify Headroom proxy setup on Windows.

Usage:
    python scripts/verify-headroom.py [--port 8787] [--key ENV_VAR_NAME]
"""

import argparse
import os
import socket
import json
import sys
import subprocess
import time

def check_port(port, timeout=5):
    """Check if a port is listening."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(('127.0.0.1', port))
        s.close()
        return True
    except Exception:
        return False

def http_get(port, path, headers=None, timeout=10):
    """Simple HTTP GET using sockets (reliable on Windows)."""
    req = f"GET {path} HTTP/1.0\r\nHost: 127.0.0.1\r\n"
    if headers:
        for k, v in headers.items():
            req += f"{k}: {v}\r\n"
    req += "\r\n"
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(('127.0.0.1', port))
        s.sendall(req.encode())
        data = b''
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        s.close()
        
        # Parse response
        parts = data.split(b'\r\n\r\n', 1)
        if len(parts) != 2:
            return None, None
        headers_raw, body = parts
        status_line = headers_raw.split(b'\r\n')[0].decode()
        return status_line, body.decode()
    except Exception as e:
        return None, str(e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8787)
    parser.add_argument('--key-env', default='API_9ROUTER_KEY')
    args = parser.parse_args()
    
    key = os.environ.get(args.key_env)
    if not key:
        print(f"❌ {args.key_env} not set in environment")
        return 1
    
    print(f"=== Verifying Headroom on port {args.port} ===")
    
    # 1. Port listening
    if not check_port(args.port):
        print(f"❌ Port {args.port} not listening")
        return 1
    print(f"✅ Port {args.port} listening")
    
    # 2. Health check
    status, body = http_get(args.port, '/health')
    if not status or '200' not in status:
        print(f"❌ Health check failed: {status}")
        return 1
    
    health = json.loads(body)
    print(f"✅ Health: ready={health.get('ready')}, backend={health.get('config',{}).get('backend')}, openai={health.get('config',{}).get('openai_api_url')}, anthropic={health.get('config',{}).get('anthropic_api_url')}")
    
    if health.get('config',{}).get('backend') != 'anyllm-openai':
        print(f"⚠️  WARNING: backend is '{health.get('config',{}).get('backend')}', expected 'anyllm-openai'")
        print("   Set HEADROOM_BACKEND=anyllm-openai in .cmd")
    
    # 3. Model list
    headers = {'Authorization': f'Bearer {key}'}
    status, body = http_get(args.port, '/v1/models', headers)
    if not status or '200' not in status:
        print(f"❌ /v1/models failed: {status}")
        return 1
    
    models = json.loads(body)
    model_ids = [m['id'] for m in models.get('data', [])]
    print(f"✅ /v1/models: {len(model_ids)} models (first 5: {model_ids[:5]})")
    
    # 4. Chat completion test (use first model from list)
    if model_ids:
        test_model = model_ids[0]
        print(f"Testing chat completion with model: {test_model}")
        
        # For this we'd need POST - use curl
        import subprocess
        result = subprocess.run([
            'curl', '-sv', '-X', 'POST',
            f'http://127.0.0.1:{args.port}/v1/chat/completions',
            '-H', f'Authorization: Bearer {key}',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                'model': test_model,
                'max_tokens': 10,
                'messages': [{'role': 'user', 'content': 'hi'}]
            })
        ], capture_output=True, text=True, timeout=30)
        
        # Check response
        if '200' in result.stdout or '200' in result.stderr:
            print("✅ Chat completion works!")
        elif 'model_not_found' in result.stderr:
            print(f"⚠️  Model {test_model} not found on upstream — try another model")
            print("   Available:", model_ids[:10])
        else:
            print(f"❌ Chat completion failed")
            print("stdout:", result.stdout[:500])
            print("stderr:", result.stderr[:500])
            return 1
    
    print("=== All checks passed ===")
    return 0

if __name__ == '__main__':
    sys.exit(main())