#!/bin/bash
# Test script for z/VM connectivity validation
# This script tests the z/VM connection without creating any VMs

set -e

echo "=========================================="
echo "z/VM Connectivity Test"
echo "=========================================="
echo ""
echo "Testing connection to z/VM hypervisor: boea3e06"
echo "Testing bastion node: a3e06001"
echo ""

# Check if tessia-baselib is installed
echo "Checking prerequisites..."
if ! python3 -c "import tessia.baselib" 2>/dev/null; then
    echo "❌ tessia-baselib not found. Installing..."
    pip3 install tessia-baselib
    echo "✅ tessia-baselib installed"
else
    echo "✅ tessia-baselib is installed"
fi

# Check if Ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo "❌ Ansible not found. Please install: pip3 install ansible"
    exit 1
else
    echo "✅ Ansible is installed"
fi

echo ""
echo "=========================================="
echo "Running z/VM connectivity test..."
echo "=========================================="
echo ""

# Run only the connectivity validation play
ansible-playbook playbooks/0_setup_zvm.yaml \
    -i inventories/default/hosts \
    -e "inventory_dir=$(pwd)/inventories/default" \
    --tags validate_zvm_connection \
    -vvv

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="

# Made with Bob
