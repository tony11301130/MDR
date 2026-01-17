# Vendor Pack Template

This is a template for creating new vendor integration packs.

## Steps to Create a New Pack

1. **Copy this template directory**
   ```bash
   cp -r adapter/packs/_template adapter/packs/YourVendorName
   ```

2. **Update pack_metadata.json**
   - Set the vendor name, description, and capabilities
   - Define required configuration fields
   - Specify supported capabilities

3. **Create client.py**
   - Implement API client for the vendor
   - Handle authentication and HTTP requests
   - Implement vendor-specific API methods

4. **Create adapter.py**
   - Extend `BaseAdapter` from `adapter.core.base_adapter`
   - Implement required methods: `normalize_alert`, `list_processes`, etc.
   - Use the client to fetch data and normalize it to MDR schemas

5. **Create mapper.py (optional)**
   - Extend `BaseMapper` from `adapter.core.mappers.base_mapper`
   - Implement vendor-specific data mapping logic
   - Convert vendor alerts to `MDRAlert` format

6. **Create __init__.py**
   - Export main classes (Client, Adapter, Mapper)
   - Set __version__

7. **Test your pack**
   ```python
   from adapter.core.factory import AdapterFactory
   
   config = {"server_url": "...", "api_key": "..."}
   adapter = AdapterFactory.get_adapter("YourVendorName", "tenant_001", config)
   ```

## Required Methods in Adapter

Your adapter should implement:
- `normalize_alert(raw_data)` - Convert vendor alert to MDRAlert
- `list_processes(hostname)` - Get process list from endpoint
- `get_host_details(hostname)` - Get host information
- `isolate_host(hostname)` - Isolate a compromised host (if supported)
- `terminate_process(hostname, pid)` - Kill a process (if supported)

## File Structure

```
YourVendorName/
├── __init__.py
├── pack_metadata.json
├── README.md
├── client.py
├── adapter.py
└── mapper.py (optional)
```
