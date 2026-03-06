# Architecture Overview: Ansible-OpenShift-Provisioning

## Project Summary

This project provides automated provisioning of Red Hat OpenShift Container Platform (RHOCP) clusters on IBM zSystems/LinuxONE using KVM as the hypervisor. It supports multiple deployment models including standard UPI (User Provisioned Infrastructure), Agent-Based Installer (ABI), and Hosted Control Planes (HCP).

**Version:** v2.3.0  
**Supported OpenShift:** v4.19 and below  
**Target Platform:** IBM zSystems / LinuxONE  
**Hypervisor:** KVM (Kernel Virtual Machine)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ansible Controller                            │
│              (Orchestrates entire deployment)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   LPAR 1     │  │   LPAR 2     │  │   LPAR 3     │
│ (KVM Host)   │  │ (KVM Host)   │  │ (KVM Host)   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
        ┌────────────────┼────────────────────────┐
        │                │                        │
        ▼                ▼                        ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│   Bastion    │  │  Bootstrap   │  │  OpenShift Cluster   │
│   (Helper)   │  │    Node      │  │  - Control Nodes     │
│              │  │              │  │  - Compute Nodes     │
│  - DNS       │  └──────────────┘  │  - Infra Nodes (opt) │
│  - HAProxy   │                    └──────────────────────┘
│  - HTTP      │
└──────────────┘
```

---

## Core Components

### 1. Ansible Controller
- **Role:** Central orchestration point for all automation
- **Location:** Can be local workstation or dedicated server
- **Requirements:** 
  - Ansible installed with required collections
  - SSH access to all target systems
  - Network connectivity to IBM zSystems infrastructure

### 2. LPAR (Logical Partition)
- **Role:** Physical or logical partition on IBM zSystems running Linux
- **Function:** Acts as KVM hypervisor host
- **High Availability:** Supports 1-3 LPARs for HA configurations
- **Responsibilities:**
  - Hosts KVM virtual machines
  - Provides compute resources
  - Network bridging/routing

### 3. Bastion Node (Helper Node)
- **Role:** Infrastructure services host
- **Services Provided:**
  - **DNS:** Name resolution for cluster
  - **HAProxy:** Load balancing for API/Ingress
  - **HTTP Server:** Serves ignition configs, RHCOS images
  - **DHCP (optional):** IP address management
- **Network:** Dual-homed (external + internal cluster network)

### 4. Bootstrap Node
- **Role:** Temporary node for initial cluster bootstrapping
- **Lifecycle:** Created → Used → Destroyed after cluster init
- **Resources:** 120GB disk, 16GB RAM, 4 vCPUs

### 5. Control Plane Nodes
- **Role:** Kubernetes control plane (etcd, API server, controllers)
- **Count:** Typically 3 for HA
- **Resources:** 120GB disk, 16GB RAM, 4 vCPUs per node
- **Function:** Cluster management and orchestration

### 6. Compute Nodes
- **Role:** Application workload execution
- **Count:** 2+ nodes (scalable)
- **Resources:** 120GB disk, 16GB RAM, 4 vCPUs per node
- **Function:** Run containerized applications

### 7. Infra Nodes (Optional)
- **Role:** Infrastructure workloads (monitoring, logging, registry)
- **Purpose:** Separate infrastructure from application workloads

---

## Deployment Models

### 1. Standard UPI (User Provisioned Infrastructure)
**Playbook:** [`site.yaml`](playbooks/site.yaml)

**Workflow:**
1. Setup and prerequisites ([`0_setup.yaml`](playbooks/0_setup.yaml))
2. Create LPAR ([`1_create_lpar.yaml`](playbooks/1_create_lpar.yaml))
3. Create KVM host ([`2_create_kvm_host.yaml`](playbooks/2_create_kvm_host.yaml))
4. Setup KVM host ([`3_setup_kvm_host.yaml`](playbooks/3_setup_kvm_host.yaml))
5. Create bastion ([`4_create_bastion.yaml`](playbooks/4_create_bastion.yaml))
6. Setup bastion ([`5_setup_bastion.yaml`](playbooks/5_setup_bastion.yaml))
7. Create cluster nodes ([`6_create_nodes.yaml`](playbooks/6_create_nodes.yaml))
8. Verify OCP installation ([`7_ocp_verification.yaml`](playbooks/7_ocp_verification.yaml))

**Use Case:** Traditional OpenShift deployment with full control

### 2. Agent-Based Installer (ABI)
**Playbook:** [`master_playbook_for_abi.yaml`](playbooks/master_playbook_for_abi.yaml)

**Workflow:**
1. Setup ([`0_setup.yaml`](playbooks/0_setup.yaml))
2. Setup KVM host ([`3_setup_kvm_host.yaml`](playbooks/3_setup_kvm_host.yaml))
3. Create bastion ([`4_create_bastion.yaml`](playbooks/4_create_bastion.yaml))
4. Setup bastion ([`5_setup_bastion.yaml`](playbooks/5_setup_bastion.yaml))
5. Create ABI cluster ([`create_abi_cluster.yaml`](playbooks/create_abi_cluster.yaml))
6. Monitor installation ([`monitor_create_abi_cluster.yaml`](playbooks/monitor_create_abi_cluster.yaml))

**Features:**
- Simplified installation using ISO or PXE boot
- Declarative configuration
- Supports multi and s390x architectures
- FIPS mode support

**Use Case:** Simplified deployment with reduced manual steps

### 3. Hosted Control Planes (HCP)
**Playbook:** [`hcp.yaml`](playbooks/hcp.yaml)

**Architecture:**
```
┌─────────────────────────────────────────┐
│     Management Cluster (OpenShift)      │
│  ┌───────────────────────────────────┐  │
│  │  MultiCluster Engine (MCE)        │  │
│  │  - Hosted Control Plane Operator  │  │
│  └───────────────────────────────────┘  │
│           │                              │
│           ▼                              │
│  ┌───────────────────────────────────┐  │
│  │  Hosted Control Plane Pods        │  │
│  │  (API, etcd, controllers)         │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        Data Plane (Compute Nodes)       │
│  - KVM guests                           │
│  - zVM guests                           │
│  - LPAR nodes                           │
└─────────────────────────────────────────┘
```

**Workflow:**
1. Create hosted cluster ([`create_hosted_cluster.yaml`](playbooks/create_hosted_cluster.yaml))
2. Create agents and wait for install ([`create_agents_and_wait_for_install_complete.yaml`](playbooks/create_agents_and_wait_for_install_complete.yaml))

**Features:**
- Control plane runs as pods in management cluster
- Reduced resource footprint
- Faster cluster provisioning
- Supports KVM, zVM, and LPAR compute nodes
- Hipersockets support for zVM

**Use Case:** Multi-tenant environments, edge deployments, cost optimization

---

## Network Architecture

### Network Modes
1. **MacVTAP (Default):** Direct VM network access
2. **NAT:** Network Address Translation through jumphost
3. **Bridge:** Traditional Linux bridge networking

### Network Services
- **DNS:** Cluster name resolution (on bastion)
- **Load Balancer:** HAProxy for API (6443) and Ingress (80/443)
- **DHCP (Optional):** Dynamic IP assignment
- **IPv4/IPv6:** Dual-stack support

### Network Topology
```
External Network
       │
       ▼
┌──────────────┐
│   Bastion    │
│  (Gateway)   │
└──────┬───────┘
       │
Internal Cluster Network
       │
   ┌───┴────┬─────────┬──────────┐
   ▼        ▼         ▼          ▼
Bootstrap Control  Compute   Infra
  Node     Nodes    Nodes    Nodes
```

---

## Storage Architecture

### Storage Types
1. **QCOW2:** Virtual disk images (default for KVM)
2. **DASD:** Direct Access Storage Device (IBM zSystems native)
3. **FCP:** Fibre Channel Protocol (SAN storage)
4. **NVMe:** Non-Volatile Memory Express (LPAR only)

### Storage Locations
- **KVM Host:** `/var/lib/libvirt/images/` (default pool)
- **Bastion:** Local storage for configs and images
- **Cluster Nodes:** Persistent volumes via CSI drivers

---

## Security Features

### 1. CEX-based LUKS Encryption
- Crypto Express adapter integration
- Full disk encryption for cluster nodes
- Supports DASD, FCP, and virtual devices
- VFIO-AP mediated device support for KVM guests

### 2. FIPS Mode
- Federal Information Processing Standards compliance
- Cryptographic module validation
- Supported in ABI deployments

### 3. Network Security
- IPSec support for encrypted communications
- Firewall configuration (firewalld)
- OpenVPN (deprecated, being removed)

### 4. Access Control
- SSH key-based authentication
- Red Hat subscription management
- Pull secret management for image registries

---

## Disconnected/Air-Gapped Support

**Configuration:** [`disconnected.yaml`](inventories/default/group_vars/disconnected.yaml)

### Components
1. **Mirror Registry:** Private container registry
2. **Mirror Host:** Internet-connected system for mirroring
3. **File Server:** Serves client binaries and RHCOS images

### Mirroring Methods
1. **oc-mirror (v1/v2):** Official OpenShift mirroring tool
2. **Legacy:** Direct image mirroring

### Workflow
1. Mirror images to registry ([`disconnected_mirror_artifacts.yaml`](playbooks/disconnected_mirror_artifacts.yaml))
2. Configure cluster to use mirror
3. Apply operator manifests ([`disconnected_apply_operator_manifests.yaml`](playbooks/disconnected_apply_operator_manifests.yaml))

### Mirrored Content
- OpenShift platform images
- Operator catalogs
- Additional images (UBI, etc.)
- Helm charts

---

## Key Ansible Roles

### Infrastructure Roles
- [`dns`](roles/dns/): DNS server configuration
- [`haproxy`](roles/haproxy/): Load balancer setup
- [`httpd`](roles/httpd/): HTTP server for artifacts
- [`install_packages`](roles/install_packages/): Package management

### Cluster Creation Roles
- [`create_bootstrap`](roles/create_bootstrap/): Bootstrap node creation
- [`create_control_nodes`](roles/create_control_nodes/): Control plane nodes
- [`create_compute_node`](roles/create_compute_node/): Compute node creation
- [`approve_certs`](roles/approve_certs/): CSR approval automation

### HCP-Specific Roles
- [`install_mce_operator`](roles/install_mce_operator/): MultiCluster Engine installation
- [`create_hcp_InfraEnv`](roles/create_hcp_InfraEnv/): Infrastructure environment setup
- [`boot_zvm_nodes_hcp`](roles/boot_zvm_nodes_hcp/): zVM node bootstrapping
- [`create_bastion_hcp`](roles/create_bastion_hcp/): HCP bastion setup

### Disconnected Roles
- [`disconnected_mirror_images`](roles/disconnected_mirror_images/): Image mirroring
- [`disconnected_apply_operator_manifests_to_cluster`](roles/disconnected_apply_operator_manifests_to_cluster/): Operator deployment

### Utility Roles
- [`ssh_agent`](roles/ssh_agent/): SSH key management
- [`check_nodes`](roles/check_nodes/): Node health verification
- [`label_infra_nodes`](roles/label_infra_nodes/): Node labeling

---

## Configuration Management

### Inventory Structure
```
inventories/default/
├── hosts                    # Inventory file
├── group_vars/
│   ├── all.yaml            # Global variables
│   ├── disconnected.yaml   # Disconnected config
│   ├── hcp.yaml            # HCP config
│   └── zvm.yaml            # zVM-specific config
└── host_vars/
    └── KVMhostname*.yaml   # Per-host variables
```

### Variable Hierarchy
1. **Group Variables:** Shared across node groups
2. **Host Variables:** Specific to individual hosts
3. **Playbook Variables:** Runtime overrides

### Key Configuration Sections
1. **Ansible Controller:** Credentials and paths
2. **LPAR Configuration:** Host details and HA settings
3. **File Server:** ISO and artifact storage
4. **Red Hat Credentials:** Subscription and pull secrets
5. **Bastion Configuration:** Network and services
6. **Cluster Networking:** IP ranges and DNS
7. **Node Specifications:** Resources per node type
8. **OCP Settings:** Version and download URLs
9. **ABI Settings:** Agent-based installer config
10. **HCP Settings:** Hosted control plane config
11. **CEX Settings:** Encryption configuration
12. **Disconnected Settings:** Mirror registry config

---

## Day 2 Operations

### Supported Operations
1. **Add Compute Node:** [`create_compute_node.yaml`](playbooks/create_compute_node.yaml)
2. **Delete Compute Node:** [`delete_compute_node.yaml`](playbooks/delete_compute_node.yaml)
3. **Reinstall Cluster:** [`reinstall_cluster.yaml`](playbooks/reinstall_cluster.yaml)
4. **Destroy ABI Cluster:** [`destroy_abi_cluster.yaml`](playbooks/destroy_abi_cluster.yaml)
5. **Destroy HCP Cluster:** [`destroy_cluster_hcp.yaml`](playbooks/destroy_cluster_hcp.yaml)

### Scaling
- Horizontal: Add/remove compute nodes
- Vertical: Modify VM resources (requires recreation)

---

## Technology Stack

### Core Technologies
- **Ansible:** 2.9+ (automation framework)
- **OpenShift:** 4.x (container platform)
- **KVM/QEMU:** Virtualization
- **RHEL:** 9.x (base OS, RHEL 8 being deprecated)
- **Python:** 3.x (Ansible runtime)

### Ansible Collections
- [`ansible.posix`](collections/ansible/posix/)
- [`community.crypto`](collections/community/crypto/)
- [`community.general`](collections/community/general/)
- [`community.libvirt`](collections/community/libvirt/)
- [`ibm.ibm_zhmc`](collections/ibm/ibm_zhmc/)

### External Roles
- [`robertdebock.epel`](roles/robertdebock.epel/): EPEL repository setup
- [`robertdebock.openvpn`](roles/robertdebock.openvpn/): VPN configuration (deprecated)

---

## Installation Types

### 1. KVM-based Installation
- Standard deployment on KVM hypervisor
- Full control over virtual infrastructure
- Supports all features

### 2. zVM-based Installation
- IBM z/VM as hypervisor
- Native zSystems virtualization
- Hipersockets support
- Network modes: vSwitch, OSA, RoCE, Hipersockets

### 3. LPAR-based Installation
- Direct LPAR provisioning
- No hypervisor layer
- Maximum performance
- Supports DPM (Dynamic Partition Manager)

---

## Project Structure

```
Ansible-OpenShift-Provisioning/
├── ansible.cfg                 # Ansible configuration
├── playbooks/                  # Automation playbooks
│   ├── site.yaml              # Master playbook (UPI)
│   ├── master_playbook_for_abi.yaml  # Master playbook (ABI)
│   ├── hcp.yaml               # Master playbook (HCP)
│   └── [0-7]_*.yaml           # Sequential playbooks
├── roles/                      # Ansible roles
│   ├── dns/                   # DNS configuration
│   ├── haproxy/               # Load balancer
│   ├── create_*/              # Node creation roles
│   └── install_*/             # Installation roles
├── inventories/                # Inventory and variables
│   └── default/
│       ├── hosts              # Inventory file
│       ├── group_vars/        # Group variables
│       └── host_vars/         # Host variables
├── collections/                # Ansible collections
├── docs/                       # Documentation
└── README.md                   # Project overview
```

---

## References

- **Documentation:** https://ibm.github.io/Ansible-OpenShift-Provisioning/
- **GitHub Repository:** https://github.com/IBM/Ansible-OpenShift-Provisioning
- **OpenShift Documentation:** https://docs.openshift.com/
- **IBM zSystems:** https://www.ibm.com/z

---

## Contact

For assistance, contact: jacob.emery@ibm.com

---

*This architecture overview is based on version 2.3.0 of the Ansible-OpenShift-Provisioning project.*