"""
Fidelis Endpoint Pack

This pack provides integration with Fidelis Endpoint EDR platform.

## Capabilities
- Fetch and normalize alerts
- Query endpoint events (processes, network, files)
- Isolate compromised hosts
- Terminate malicious processes
- Retrieve host details and asset information

## Configuration
Required configuration parameters:
- server_url: Fidelis server URL (e.g., https://fidelis.example.com)
- username: API username
- password: API password
- fidelis_isolate_script_id: Script ID for host isolation
- fidelis_terminate_process_script_id: Script ID for process termination

## Usage
```python
from adapter.packs.Fidelis import FidelisAdapter

config = {
    "server_url": "https://fidelis.example.com",
    "username": "api_user",
    "password": "api_password",
    "fidelis_isolate_script_id": "script_001",
    "fidelis_terminate_process_script_id": "script_002"
}

adapter = FidelisAdapter(tenant_id="tenant_001", config=config)
alerts = adapter.client.list_alerts(limit=10)
```
