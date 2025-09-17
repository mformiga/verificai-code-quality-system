#!/usr/bin/env python3
"""Test script for prompt save functionality"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login and return token"""
    login_data = {
        "username": "admin",
        "password": "Admin123!"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_prompt_save(token):
    """Test prompt save functionality"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    test_data = {
        "general": {
            "content": "Test content for general analysis - UPDATED VERSION",
            "description": "Updated test general prompt",
            "settings": {"temperature": 0.8}
        },
        "architectural": {
            "content": "Test content for architectural analysis - UPDATED VERSION",
            "description": "Updated test architectural prompt",
            "settings": {"temperature": 0.6}
        },
        "business": {
            "content": "Test content for business analysis - UPDATED VERSION",
            "description": "Updated test business prompt",
            "settings": {"temperature": 0.4}
        }
    }

    print("Testing prompt save...")
    response = requests.post(
        f"{BASE_URL}/api/v1/prompts/save",
        headers=headers,
        json=test_data
    )

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    return response.status_code == 200

def test_prompt_load(token):
    """Test prompt load functionality"""
    headers = {
        "Authorization": f"Bearer {token}"
    }

    print("Testing prompt load...")
    response = requests.get(
        f"{BASE_URL}/api/v1/prompts/config",
        headers=headers
    )

    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Configuration loaded successfully")
        for key, config in data.items():
            print(f"  {key}: {config['description'][:50]}...")
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200

if __name__ == "__main__":
    print("=== Testing Prompt Save/Load Functionality ===")

    # Test login
    print("1. Testing login...")
    token = test_login()
    if not token:
        print("Login failed")
        exit(1)
    print("Login successful")

    # Test prompt save
    print("\n2. Testing prompt save...")
    if test_prompt_save(token):
        print("Prompt save successful")
    else:
        print("Prompt save failed")

    # Test prompt load
    print("\n3. Testing prompt load...")
    if test_prompt_load(token):
        print("Prompt load successful")
    else:
        print("Prompt load failed")

    print("\n=== Test Complete ===")