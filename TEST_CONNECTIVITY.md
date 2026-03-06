# z/VM Connectivity Test Guide

This guide explains how to test the z/VM connectivity validation with your real credentials.

## Test Configuration

The following test files have been created with your z/VM credentials:

### 1. `inventories/default/group_vars/all.yaml`
- Installation type: `zvm`
- Node list: `bastion-zvm`
- Other settings: dummy values (not needed for connectivity test)

### 2. `inventories/default/host_vars/bastion-zvm.yaml`
**Real z/VM credentials configured:**
- z/VM Hypervisor: `boea3e06`
- z/VM Guest: `A3E06001`
- z/VM User: `a3e06001`
- z/VM Password: `ocp4ever`

### 3. `inventories/default/hosts`
- Inventory file with bastion-zvm node

## Prerequisites

Before running the test, ensure you have:

```bash
# Install tessia-baselib (required for z/VM connectivity)
pip3 install tessia-baselib

# Install Ansible (if not already installed)
pip3 install ansible
```

## Running the Test

### Option 1: Use the Test Script (Recommended)

```bash
# Make the script executable (already done)
chmod +x test_zvm_connectivity.sh

# Run the test
./test_zvm_connectivity.sh
```

### Option 2: Run Ansible Directly

```bash
# Test connectivity only
ansible-playbook playbooks/0_setup_zvm.yaml \
    -i inventories/default/hosts \
    --tags validate_zvm_connection \
    -v
```

### Option 3: Run Full Setup Playbook

```bash
# This will run all setup tasks including connectivity test
ansible-playbook playbooks/0_setup_zvm.yaml \
    -i inventories/default/hosts
```

## Expected Output

### Success Output

If the connection is successful, you should see:

```
TASK [Display z/VM connectivity test summary]
ok: [localhost] => {
    "msg": [
        "=== Testing z/VM Connectivity ===",
        "Nodes to test: 1",
        "['bastion-zvm']"
    ]
}

TASK [validate_zvm_connection : Display node being tested]
ok: [localhost] => {
    "msg": "Testing z/VM connectivity for bastion-zvm (A3E06001 on boea3e06)"
}

TASK [validate_zvm_connection : Test z/VM hypervisor connection for bastion-zvm]
changed: [localhost]

TASK [validate_zvm_connection : Display z/VM connection test result for bastion-zvm]
ok: [localhost] => {
    "msg": [
        "Connecting to z/VM hypervisor: boea3e06",
        "Attempting login...",
        "✓ Successfully logged in to z/VM hypervisor",
        "✓ Successfully logged off from z/VM hypervisor",
        "",
        "z/VM connection test: PASSED"
    ]
}
```

### Failure Output

If the connection fails, you'll see an error message like:

```
TASK [validate_zvm_connection : Test z/VM hypervisor connection for bastion-zvm]
fatal: [localhost]: FAILED! => {
    "msg": "✗ z/VM connection test FAILED: [error details]"
}
```

## What This Test Does

The connectivity test:
1. ✅ Validates network connectivity to z/VM hypervisor `boea3e06`
2. ✅ Tests z/VM user credentials (`a3e06001` / `ocp4ever`)
3. ✅ Verifies tessia-baselib can communicate with z/VM
4. ✅ Performs login and logoff operations

**Important:** This test does **NOT** create any VMs. It only validates connectivity!

## Troubleshooting

### Error: "tessia-baselib not found"
```bash
pip3 install tessia-baselib
```

### Error: "Connection refused" or "Network unreachable"
- Verify network connectivity: `ping boea3e06`
- Check if z/VM hypervisor is accessible from your machine
- Verify firewall rules allow connection

### Error: "Authentication failed"
- Double-check the credentials in `inventories/default/host_vars/bastion-zvm.yaml`
- Verify the z/VM user `a3e06001` exists and password is correct
- Check if the user has proper permissions

### Error: "hostvars[item] is undefined"
- Ensure `bastion-zvm.yaml` exists in `inventories/default/host_vars/`
- Check that the node name matches in both `all.yaml` and the filename

## Files Created for Testing

```
inventories/default/
├── group_vars/
│   └── all.yaml                    # Cluster-wide config with node list
├── host_vars/
│   └── bastion-zvm.yaml           # Bastion node with REAL z/VM credentials
└── hosts                           # Ansible inventory

test_zvm_connectivity.sh            # Test script
TEST_CONNECTIVITY.md                # This file
```

## Next Steps After Successful Test

Once the connectivity test passes:

1. **Add more nodes** to test:
   - Edit `inventories/default/group_vars/all.yaml`
   - Add nodes to `zvm_nodes` list
   - Create corresponding `host_vars/{node}.yaml` files

2. **Proceed with implementation**:
   - Phase 3: Develop core roles for VM creation
   - Phase 4: Test actual VM provisioning
   - Phase 5: Complete OCP cluster deployment

## Security Note

⚠️ **Important:** The test files contain real credentials. Consider:
- Using Ansible Vault to encrypt passwords
- Adding `inventories/default/group_vars/all.yaml` to `.gitignore`
- Adding `inventories/default/host_vars/*.yaml` (non-template files) to `.gitignore`

Example with Ansible Vault:
```bash
# Encrypt the password
ansible-vault encrypt_string 'ocp4ever' --name 'zvm_pass'

# Use in bastion-zvm.yaml:
zvm_pass: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted string...
```

## Support

If you encounter issues:
1. Check the error message carefully
2. Verify network connectivity to z/VM
3. Confirm credentials are correct
4. Review tessia-baselib documentation: https://github.com/tessia-project/tessia-baselib

---

Ready to test! Run `./test_zvm_connectivity.sh` to begin. 🚀