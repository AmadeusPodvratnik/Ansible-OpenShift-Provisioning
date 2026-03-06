# z/VM UPI Implementation Progress

**Last Updated**: 2026-03-06  
**Status**: Phase 1 Complete - Foundation Files Created  
**Branch**: Current working branch

---

## Project Overview

Adding full User Provisioned Infrastructure (UPI) support for IBM Z z/VM-based OpenShift Container Platform clusters to the Ansible-OpenShift-Provisioning repository.

**Goal**: Create a complete z/VM UPI deployment path similar to the existing KVM-based `site.yaml` workflow.

**Reference Documents**:
- [Implementation Plan](zvm-upi-implementation-plan.md) - Complete architectural design and implementation strategy
- [Architecture Overview](ARCHITECTURE.md) - Repository architecture

---

## Key Design Decisions

### 1. Configuration Structure
- **Individual Node Files**: Each z/VM node has its own configuration file in `host_vars/`
- **Cluster-Wide Settings**: Global z/VM and cluster settings in `group_vars/all_zvm.yaml`
- **Base Template**: All node configurations based on existing `node.yaml.template`

### 2. Variable Naming Convention
After discussion and refinement:
- `ocp_nodename`: OpenShift/DNS hostname (e.g., `bastion.ocp.example.com`)
- `zvm_guest`: z/VM guest name (max 8 characters, uppercase, e.g., `BASTION`)
- `zvm_user`: z/VM user that owns the guest (same value as `zvm_guest`)
- `zvm_pass`: z/VM user password (mandatory, use vault)
- `zvm_host`: z/VM hypervisor hostname/IP

**Rationale**: Clear distinction between OpenShift naming and z/VM naming conventions.

### 3. z/VM User Model
- In z/VM, the guest name and the z/VM user that owns/runs that guest are the same
- Each node requires its own z/VM user credentials
- z/VM hypervisor admin credentials are in `group_vars` for guest creation

### 4. Node Roles
Determined by file usage and explicit `node_role` field:
- `bastion`: Infrastructure services (DNS, HAProxy, HTTP)
- `bootstrap`: Temporary bootstrap node
- `control`: Control plane nodes (3x)
- `compute`: Worker nodes (2+)

---

## Phase 1: Foundation Files ✅ COMPLETE

### Files Created

#### 1. Master Playbook
**File**: `playbooks/site_zvm.yaml`
```yaml
- import_playbook: 0_setup_zvm.yaml
- import_playbook: 1_create_zvm_bastion.yaml
- import_playbook: 2_setup_zvm_bastion.yaml
- import_playbook: disconnected_mirror_artifacts.yaml (conditional)
- import_playbook: 3_prepare_zvm_guests.yaml
- import_playbook: 4_create_zvm_nodes.yaml
- import_playbook: 5_verify_zvm_cluster.yaml
- import_playbook: disconnected_apply_operator_manifests.yaml (conditional)
```

#### 2. Group Variables
**File**: `inventories/default/group_vars/all_zvm.yaml.template`

**Contains**:
- `installation_type: zvm`
- z/VM hypervisor configuration (`env.zvm_host`)
- File server details
- Red Hat credentials
- Cluster networking (metadata_name, base_domain)
- Global z/VM settings (network_mode, disk_type, vcpus, memory)
- OCP version and download URLs
- Optional: CEX encryption, disconnected mode, proxy

**Does NOT contain**: Individual node configurations (those are in host_vars)

#### 3. Host Variables Templates

**File**: `inventories/default/host_vars/bastion-zvm.yaml.template`
- Role: Infrastructure services host
- Resources: 4 vCPU, 8GB RAM, 30GB disk
- Services: DNS, HAProxy, HTTP, firewalld
- User: `root`

**File**: `inventories/default/host_vars/bootstrap-zvm.yaml.template`
- Role: Temporary bootstrap node
- Resources: 4 vCPU, 16GB RAM, 120GB disk
- `node_role: bootstrap`, `ignition_type: bootstrap`
- User: `core` (RHCOS default)

**File**: `inventories/default/host_vars/control-1-zvm.yaml.template`
- Role: Control plane node
- Resources: 4 vCPU, 16GB RAM, 120GB disk
- `node_role: control`, `ignition_type: master`
- User: `core`
- Note: Users create control-2 and control-3 similarly

**File**: `inventories/default/host_vars/compute-1-zvm.yaml.template`
- Role: Compute/worker node
- Resources: 4 vCPU, 16GB RAM, 120GB disk
- `node_role: compute`, `ignition_type: worker`
- User: `core`
- Note: Users create compute-2, compute-3, etc. similarly

### Common Structure in All Node Templates

```yaml
# General Settings
ocp_nodename: <hostname>
zvm_guest: <GUESTNAME>
host_ip: <ip_address>
node_user: <user>
node_user_pwd: "{{ vault_password }}"

# z/VM Configuration
zvm_host: <hypervisor>
zvm_user: <GUESTNAME>  # Same as zvm_guest
zvm_pass: <password>

# Hardware
cpu: <number>
memory: <MB>
attach_network: True
attach_disk: True

# Storage (DASD or FCP)
zrd_dasd: [<device>]
zrd_fcp: []

# Network
zrd_znet: [<subchannels>]
network:
  - ip: <ip>
    gateway: <gateway>
    netmask: <netmask>
    device: <device>

# DNS
nameserver: [<dns_servers>]
```

---

## Phase 2: Sequential Playbooks (NEXT)

### Playbooks to Create

1. **`playbooks/0_setup_zvm.yaml`**
   - SSH key generation
   - z/VM connectivity validation
   - Prerequisites installation
   - Inventory validation

2. **`playbooks/1_create_zvm_bastion.yaml`**
   - Create bastion guest on z/VM
   - Attach storage and network
   - Boot with RHEL
   - Enable SSH access

3. **`playbooks/2_setup_zvm_bastion.yaml`**
   - Install packages (bind, haproxy, httpd)
   - Configure DNS server
   - Setup HAProxy load balancer
   - Configure HTTP server
   - Setup firewall

4. **`playbooks/3_prepare_zvm_guests.yaml`**
   - Download RHCOS artifacts
   - Generate install-config.yaml
   - Create ignition configs
   - Upload to bastion HTTP server
   - Generate parm files

5. **`playbooks/4_create_zvm_nodes.yaml`**
   - Create and boot bootstrap
   - Create and boot control nodes
   - Wait for bootstrap completion
   - Destroy bootstrap
   - Create and boot compute nodes
   - Approve CSRs

6. **`playbooks/5_verify_zvm_cluster.yaml`**
   - Check node status
   - Verify cluster operators
   - Test connectivity
   - Generate access info

---

## Phase 3: Ansible Roles (FUTURE)

### Roles to Develop

#### Bastion Roles
- `create_zvm_bastion` - Provision bastion guest
- `setup_zvm_bastion` - Configure services

#### Node Creation Roles
- `create_zvm_bootstrap` - Bootstrap node
- `create_zvm_control_nodes` - Control plane nodes
- `create_zvm_compute_nodes` - Compute nodes

#### Boot and Configuration Roles
- `boot_zvm_node_upi` - Boot guest with ignition
- `attach_zvm_storage` - DASD/FCP attachment
- `configure_zvm_network` - Network configuration
- `prepare_zvm_ignition` - Ignition generation

---

## Implementation Phases

### ✅ Phase 1: Foundation (COMPLETE)
- [x] Master playbook created
- [x] Group variables template created
- [x] Individual node templates created
- [x] Variable naming finalized
- [x] Configuration structure validated

### 🔄 Phase 2: Sequential Playbooks (IN PROGRESS)
- [ ] 0_setup_zvm.yaml
- [ ] 1_create_zvm_bastion.yaml
- [ ] 2_setup_zvm_bastion.yaml
- [ ] 3_prepare_zvm_guests.yaml
- [ ] 4_create_zvm_nodes.yaml
- [ ] 5_verify_zvm_cluster.yaml

### ⏳ Phase 3: Core Roles (PENDING)
- [ ] Bastion roles
- [ ] Node creation roles
- [ ] Boot and configuration roles

### ⏳ Phase 4: Templates and Scripts (PENDING)
- [ ] Ignition templates
- [ ] Parm file templates
- [ ] Python boot scripts

### ⏳ Phase 5: Integration (PENDING)
- [ ] Update common role
- [ ] Update existing roles for z/VM

### ⏳ Phase 6: Documentation (PENDING)
- [ ] Deployment guide
- [ ] Variable reference
- [ ] Troubleshooting guide

---

## Validation Checkpoints

### Checkpoint 1: Foundation Files ✅
**Status**: Awaiting validation

**Items to Validate**:
1. File structure and locations
2. Variable naming (`ocp_nodename`, `zvm_guest`, `zvm_user`, `zvm_pass`)
3. Configuration separation (group_vars vs host_vars)
4. Template completeness
5. Comments and examples

### Checkpoint 2: Sequential Playbooks (NEXT)
**Items to Validate**:
- Playbook structure and flow
- Role integration
- Error handling
- Task logic

### Checkpoint 3: End-to-End (FUTURE)
**Items to Validate**:
- Complete deployment workflow
- All roles working together
- Documentation accuracy

---

## Technical Notes

### z/VM Guest Naming
- Maximum 8 characters
- Uppercase recommended
- Examples: `BASTION`, `BOOTSTRP`, `CONTROL1`, `COMPUTE1`

### Storage Options
- **DASD**: Direct Access Storage Device (native z/VM)
- **FCP**: Fibre Channel Protocol (SAN storage)
- Configured per node in host_vars

### Network Modes
- **vSwitch**: Virtual switch
- **OSA**: Open Systems Adapter
- **RoCE**: RDMA over Converged Ethernet
- **Hipersockets**: High-speed memory-to-memory

### Resource Requirements
- **Bastion**: 4 vCPU, 8GB RAM, 30GB disk
- **Bootstrap**: 4 vCPU, 16GB RAM, 120GB disk
- **Control**: 4 vCPU, 16GB RAM, 120GB disk (per node)
- **Compute**: 4 vCPU, 16GB RAM, 120GB disk (per node, adjustable)

---

## Questions and Decisions Log

### Q1: Where should z/VM hypervisor credentials be stored?
**A**: In `group_vars/all_zvm.yaml` under `env.zvm_host` for cluster-wide access.

### Q2: Should node configurations be in one file or separate files?
**A**: Separate files per node for better organization and management.

### Q3: What should the variable names be?
**A**: 
- `ocp_nodename` for OpenShift/DNS hostname
- `zvm_guest` for z/VM guest name
- `zvm_user` for z/VM user (same as guest)
- `zvm_pass` for z/VM user password

### Q4: Are z/VM user credentials optional?
**A**: No, they are mandatory. Each node needs its own z/VM user credentials.

### Q5: What is the relationship between zvm_user and zvm_guest?
**A**: They are the same value. In z/VM, the guest name and the user that owns it are identical.

---

## Next Steps

1. **Validate Phase 1 files** with team
2. **Begin Phase 2**: Create sequential playbooks
3. **Test playbook syntax** with `ansible-playbook --syntax-check`
4. **Develop core roles** for bastion and node creation
5. **Create Python boot scripts** using tessia-baselib
6. **Write documentation** for deployment process

---

## Team Collaboration

### To Continue This Work

1. **Review this document** for context and decisions
2. **Check the implementation plan**: `docs/zvm-upi-implementation-plan.md`
3. **Review created files**:
   - `playbooks/site_zvm.yaml`
   - `inventories/default/group_vars/all_zvm.yaml.template`
   - `inventories/default/host_vars/*-zvm.yaml.template`
4. **Validate Phase 1** before proceeding to Phase 2
5. **Follow the phase sequence** outlined above

### Key Files to Reference
- **Architecture**: `docs/ARCHITECTURE.md`
- **Implementation Plan**: `docs/zvm-upi-implementation-plan.md`
- **Progress**: `docs/zvm-upi-progress.md` (this file)
- **Existing z/VM Support**: 
  - `playbooks/create_abi_cluster.yaml`
  - `roles/boot_zvm_nodes/`
  - `inventories/default/group_vars/zvm.yaml`
  - `inventories/default/host_vars/node.yaml.template`

---

## Contact and Support

For questions or clarifications on design decisions, refer to:
- This progress document
- The implementation plan
- Git commit messages for rationale

---

*This document should be updated as implementation progresses through each phase.*