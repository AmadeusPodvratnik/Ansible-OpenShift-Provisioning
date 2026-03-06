# Role: create_zvm_bastion

## Purpose

Creates a bastion VM on z/VM hypervisor using tessia-baselib. This role provisions the z/VM guest with specified CPU, memory, storage, and network resources.

## Requirements

- tessia-baselib Python library installed
- z/VM hypervisor access credentials
- Network connectivity to z/VM hypervisor

## Role Variables

### Required Variables (from host_vars)

- `zvm_host`: z/VM hypervisor hostname or IP
- `zvm_user`: z/VM user for guest management
- `zvm_pass`: z/VM user password
- `zvm_guest`: z/VM guest name (max 8 characters, uppercase)
- `cpu`: Number of vCPUs for the guest
- `memory`: Memory in MB for the guest
- `host_ip`: IP address to assign to the bastion
- `ocp_nodename`: OpenShift node name

### Optional Variables

- `zrd_dasd`: List of DASD devices to attach
- `zrd_fcp`: List of FCP devices to attach
- `zrd_znet`: List of network device subchannels

### Default Variables

- `default_cpu`: 4
- `default_memory`: 8192
- `skip_if_exists`: true

## Dependencies

None

## Example Playbook

```yaml
- name: Create bastion on z/VM
  hosts: localhost
  vars_files:
    - inventories/default/group_vars/all.yaml
    - inventories/default/host_vars/bastion-zvm.yaml
  roles:
    - create_zvm_bastion
```

## What This Role Does

1. **Validates Configuration**: Checks that all required variables are present
2. **Connects to z/VM**: Uses tessia-baselib to connect to the z/VM hypervisor
3. **Creates Guest**: Defines a new z/VM guest with specified resources
4. **Attaches Storage**: Attaches DASD or FCP storage devices
5. **Attaches Network**: Configures network devices
6. **Verifies Creation**: Checks that the guest was created successfully

## Important Notes

- This role creates the z/VM guest but does NOT install the operating system
- After running this role, you need to manually install RHEL on the guest
- The guest will be created but not started (not IPL'd)
- Use z/VM console to access the guest and begin OS installation

## Next Steps After Running This Role

1. Access z/VM console
2. Start the guest: `XAUTOLOG <guest_name>`
3. Install RHEL from ISO
4. Configure network and SSH
5. Run `2_setup_zvm_bastion.yaml` to configure bastion services

## Troubleshooting

### Guest Already Exists

If the guest already exists, the role will skip creation (if `skip_if_exists: true`).

### Connection Failed

- Verify z/VM hypervisor is accessible
- Check credentials in host_vars
- Ensure tessia-baselib is installed

### Storage/Network Attachment Failed

- Verify device numbers are correct
- Check that devices are available in z/VM
- Ensure proper permissions for the z/VM user

## License

Same as parent project

## Author

Created for z/VM UPI OpenShift deployment automation