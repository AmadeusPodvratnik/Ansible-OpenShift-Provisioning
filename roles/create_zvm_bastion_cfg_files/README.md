# Ansible Role: template_zvm_parm_file

This role templates out an s390x boot parameter file for RHEL installation on z/VM guests. It reads configuration from a bastion host_vars file and generates a properly formatted parm file with all network and storage devices configured.

## Requirements

- Ansible 2.9 or higher
- Access to file server configuration in `group_vars/all.yaml`
- Valid bastion configuration file in `host_vars/`

## Role Variables

### Required Variables

- `bastion_config_file`: Path to the bastion configuration YAML file (e.g., `inventories/default/host_vars/bastion-zvm.yaml`)
- `env.file_server.ip`: File server IP address (from group_vars)
- `env.file_server.cfgs_dir`: Configuration directory on file server (from group_vars)

### Optional Variables

- `parm_file_output_path`: Output path for generated parm file (default: `/tmp/<zvm_guest>-boot.parm`)
- `zfcp_allow_lun_scan`: Enable/disable ZFCP LUN scanning (default: `0`)
- `hostname`: Hostname for the system (default: derived from `zvm_guest`)

### Variables from Bastion Config File

The role expects the following variables in the bastion configuration file:

#### Network Configuration
- `network`: List of network interfaces with:
  - `ip`: IPv4 address
  - `gateway`: IPv4 gateway
  - `netmask`: IPv4 netmask
  - `device`: Network device name
  - `ipv6`: (optional) IPv6 address
  - `netmaskv6`: (optional) IPv6 prefix length
- `nameserver`: List of DNS servers
- `zrd_znet`: List of network device subchannels (e.g., `0.0.1000,0.0.1001,0.0.1002`)

#### Storage Configuration
- `zrd_dasd`: List of DASD devices (e.g., `0.0.0100`)
- `zrd_fcp`: List of FCP devices (e.g., `0.0.1a00,0x500507630040710b,0x4000404600000000`)

#### Other Configuration
- `zvm_guest`: z/VM guest name
- `host_ip`: IP address of the bastion

## Dependencies

None

## Example Playbook

```yaml
---
- name: Generate s390x boot parm file for bastion
  hosts: localhost
  gather_facts: true
  vars_files:
    - "{{ inventory_dir }}/group_vars/all.yaml"
  
  tasks:
    - name: Template parm file for bastion
      ansible.builtin.include_role:
        name: template_zvm_parm_file
      vars:
        bastion_config_file: "{{ inventory_dir }}/host_vars/bastion-zvm.yaml"
        parm_file_output_path: "/tmp/bastion-boot.parm"
```

## Example Usage

### Basic Usage

```bash
ansible-playbook -i inventories/default/hosts playbooks/generate_parm_file.yaml
```

### With Custom Output Path

```yaml
- name: Generate parm file with custom path
  ansible.builtin.include_role:
    name: template_zvm_parm_file
  vars:
    bastion_config_file: "inventories/default/host_vars/bastion-zvm.yaml"
    parm_file_output_path: "/var/www/html/pub/bastion-boot.parm"
```

## Generated Parm File Format

The role generates a single-line parm file with the following parameters:

```
inst.ks=http://<file_server_ip>:<port>/<cfgs_dir>/rhel9-bastion-ks.cfg
inst.repo=http://<file_server_ip>:<port>/<iso_mount_dir>
coreos.live.rootfs_url=http://<file_server_ip>:<port>/<cfgs_dir>/rootfs.img
ip=<ip>::<gateway>:<netmask>:<hostname>:<device>:none
nameserver=<ns1> nameserver=<ns2>
rd.znet=qeth,<subchannels>
rd.dasd=<dasd_device>
rd.zfcp=<fcp_device>
zfcp.allow_lun_scan=<0|1>
console=ttysclp0 console=tty0
```

### Example Output

```
inst.ks=http://172.23.236.156:80/pub/rhel9-bastion-ks.cfg inst.repo=http://172.23.236.156:80/RHEL-9.6.0 coreos.live.rootfs_url=http://172.23.236.156:80/pub/rootfs.img ip=172.23.236.255::172.23.236.1:255.255.255.0:bastion:enc1000:none nameserver=172.23.236.1 rd.znet=qeth,0.0.1000,0.0.1001,0.0.1002 rd.dasd=0.0.0100 console=ttysclp0 console=tty0
```

## Network Configuration Details

### DASD Storage
For DASD-based storage, the role adds:
```
rd.dasd=0.0.0100
```

### FCP Storage
For FCP-based storage, the role adds:
```
rd.zfcp=0.0.1a00,0x500507630040710b,0x4000404600000000
zfcp.allow_lun_scan=0
```

### Network Devices
For OSA/vSwitch/Hipersockets, the role adds:
```
rd.znet=qeth,0.0.1000,0.0.1001,0.0.1002
```

### IPv6 Support
If IPv6 is configured, the role adds:
```
ipv6=fd00::20/64
```

## File Server Configuration

The role uses the following from `group_vars/all.yaml`:

```yaml
env:
  file_server:
    ip: 172.23.236.156
    port: 80
    cfgs_dir: /pub
    iso_mount_dir: RHEL-9.6.0
```

## Kickstart File Location

The parm file references the kickstart file at:
```
http://<file_server_ip>:<port>/<cfgs_dir>/rhel9-bastion-ks.cfg
```

Ensure this file exists on the file server before booting the guest.

## Rootfs Location

The CoreOS live rootfs image is referenced at:
```
coreos.live.rootfs_url=http://<file_server_ip>:<port>/<cfgs_dir>/rootfs.img
```

The installation repository is referenced at:
```
inst.repo=http://<file_server_ip>:<port>/<iso_mount_dir>
```

Ensure both the `rootfs.img` file exists in the `cfgs_dir` and the ISO is mounted at `iso_mount_dir` on the file server.

## Validation

The role performs the following validations:

1. Required variables are defined
2. Bastion configuration file exists and is valid
3. Network configuration is complete
4. At least one storage device (DASD or FCP) is configured

## Troubleshooting

### Error: "Required variables are not defined"
Ensure `bastion_config_file` and `env.file_server.cfgs_dir` are set.

### Error: "Network configuration is incomplete"
Check that the bastion config file has complete network settings:
- `network[0].ip`
- `network[0].gateway`
- `network[0].netmask`
- `network[0].device`

### Error: "At least one storage device must be configured"
Ensure either `zrd_dasd` or `zrd_fcp` is defined with at least one device.

## License

Apache License 2.0

## Author Information

Created for IBM Z OpenShift provisioning automation.