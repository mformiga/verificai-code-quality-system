#!/usr/bin/env python3
"""
Detailed deployment status check for Render
"""
import requests
import json
from datetime import datetime

API_KEY = "rnd_9l8WcN5WIEbLWbs8K4esvlQ3TJgi"
BASE_URL = "https://api.render.com/v1"

def get_service_deployment_status(service_name="verificai-code-quality-system"):
    """Get detailed deployment status for a specific service"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # First, get all services to find our service ID
    response = requests.get(f"{BASE_URL}/services", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get services: {response.status_code}")
        return

    services = response.json()

    # Find our service
    service_id = None
    for item in services:
        if isinstance(item, dict) and 'service' in item:
            service = item['service']
            if service.get('name') == service_name:
                service_id = service.get('id')
                service_url = service.get('url')
                print(f"Found service: {service_name}")
                print(f"Service ID: {service_id}")
                print(f"Service URL: {service_url}")
                break

    if not service_id:
        print(f"Service {service_name} not found")
        return

    # Get detailed service information
    response = requests.get(f"{BASE_URL}/services/{service_id}", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get service details: {response.status_code}")
        return

    service_details = response.json()

    print(f"\n=== Service Details ===")
    print(f"Name: {service_details.get('name')}")
    print(f"Status: {service_details.get('status')}")
    print(f"URL: {service_details.get('url')}")
    print(f"Service Type: {service_details.get('serviceType')}")
    print(f"Created: {service_details.get('createdAt')}")
    print(f"Updated: {service_details.get('updatedAt')}")

    # Check current deployment
    current_deploy = service_details.get('currentDeploy', {})
    if current_deploy:
        print(f"\n=== Current Deployment ===")
        print(f"Status: {current_deploy.get('status')}")
        print(f"Created: {current_deploy.get('createdAt')}")
        print(f"Started: {current_deploy.get('startedAt')}")
        print(f"Finished: {current_deploy.get('finishedAt')}")
        print(f"Build Duration: {current_deploy.get('buildDuration')}")

    # Get deployment history
    response = requests.get(f"{BASE_URL}/services/{service_id}/deploys", headers=headers)
    if response.status_code == 200:
        deploys = response.json()
        if deploys:
            print(f"\n=== Recent Deployments ===")
            for i, deploy in enumerate(deploys[:5]):  # Show last 5 deployments
                print(f"\nDeployment {i+1}:")
                print(f"  Status: {deploy.get('status')}")
                print(f"  Created: {deploy.get('createdAt')}")
                print(f"  Commit: {deploy.get('commit', {}).get('message', 'No commit message')}")
                print(f"  Commit ID: {deploy.get('commit', {}).get('id', 'No commit ID')}")
                print(f"  Finished: {deploy.get('finishedAt', 'Still running')}")

                # Check if this deploy was triggered by deploy.yaml
                if deploy.get('commit', {}).get('message') and 'deploy.yaml' in deploy.get('commit', {}).get('message', ''):
                    print(f"  *** This deploy was triggered by deploy.yaml commit ***")

    # Check for any deployment logs or errors
    response = requests.get(f"{BASE_URL}/services/{service_id}/events", headers=headers)
    if response.status_code == 200:
        events = response.json()
        if events:
            print(f"\n=== Recent Events ===")
            for event in events[:5]:  # Show last 5 events
                print(f"Event: {event.get('type')} - {event.get('createdAt')}")

def main():
    print(f"=== Render Deployment Status Check ===")
    print(f"Time: {datetime.now().isoformat()}")
    get_service_deployment_status()

if __name__ == "__main__":
    main()