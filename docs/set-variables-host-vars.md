# Step 3: Set Variables (host_vars)

## Overview
* Similar to the group_vars file, the host_vars files for each LPAR (KVM host) must be filled in. 
* For each KVM host to be acted upon with Ansible, you must have a corresponding host_vars file named `<kvm-hostname>.yaml` (i.e. ocpz1.yaml, ocpz2.yaml, ocpz3.yaml), so you must copy and rename the templates found in the [host_vars folder](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/host_vars) accordingly.
* The variables marked with an `X` are required to be filled in. Many values are pre-filled or are optional. 
* Optional values are commented out; in order to use them, remove the `#` and fill them in.
* Many of the variables in these host_vars files are only required if you are NOT using pre-existing LPARs with RHEL installed. See the `Important Note` below this first section for more details.
* This is the most important step in the process. Take the time to make sure everything here is correct.
* <u>Note on YAML syntax</u>: Only the lowest value in each hierarchicy needs to be filled in. For example, at the top of the variables file networking does not need to be filled in, but the hostname does. There are X's where input is required to help you with this.
* Scroll the table to the right to see examples for each variable.

## 1 - KVM Host
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**networking.hostname** | The hostname of the LPAR with RHEL installed natively (the KVM host). | kvm-host-01
**networking.ip** | The IPv4 address of the LPAR with RHEL installed natively (the KVM host). | 192.168.10.2
**networking.internal_ip** | The internal IPv4 address of the LPAR required when booting the LPAR with HiperSocket card. Currently supports only when bastion is on LPAR or on zVM host. Incase of zVM bastion enable the HiperSocket card prior to the playbook run with vmcp commands on the bastion. Alternative Option would be setting up the bridge port on OSA or RoCE.| 10.42.6.2
**networking.mode** | Type of network card | osa/roce/hipersocket 
**networking.ipv6** | IPv6 address for the bastion if use_ipv6 variable is 'True'. | fd00::3
**networking.subnetmask** | The subnet that the LPAR resides in within your network. | 255.255.255.0
**networking.gateway** | The IPv4 address of the gateway to the network where the KVM host resides. | 192.168.10.0
**networking.ipv6_gateway** | IPv6 of he bastion's gateway server. | fd00::1
**networking.ipv6_prefix** | IPv6 prefix. | 64
**networking.nameserver1** | The IPv4 address from which the KVM host gets its hostname resolved. | 192.168.10.200
**networking.nameserver2** | <b>(Optional)</b> A second IPv4 address from which the KVM host can get its hostname resolved. Used for high availability. | 192.168.10.201
**networking.device1** | The network interface card from Linux's perspective. Usually enc and then a number that comes from the dev_num of the network adapter. | enc100
**networking.device2** | <b>(Optional)</b> Another Linux network interface card. Usually enc and then a number that comes from the dev_num of the second network adapter. | enc1
**storage.pool_path** | The absolute path to a directory on your KVM host that will be used to store qcow2 images for the cluster and other installation artifacts. A sub-directory will be created here that matches your clsuter's metadata name that will act as the cluster's libvirt storage pool directory. Note: all directories present in this path will be made executable for the 'qemu' group, as is required. | /home/kvm_admin/VirtualMachines

## Important Note
* You can skip the rest of the variables on this page IF you are using existing LPAR(s) that has RHEL already installed.
* If you are installing an LPAR based cluster then the information below must be provided and are not optional. You must create a host file corresponding to each lpar node.
    * Since this is how most production deployments on-prem are done on IBM zSystems, these variables have been marked as optional. 
    * With pre-existing LPARs with RHEL installed, you can also skip [1_create_lpar.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/1_create_lpar.yaml) and [2_create_kvm_host.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/2_create_kvm_host.yaml) playbooks. Make sure to still do [0_setup.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/0_setup.yaml) first though, then skip to [3_setup_kvm_host.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml)
    * In the scenario of lpar based installation you can skip [1_create_lpar.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/1_create_lpar.yaml) and [2_create_kvm_host.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/2_create_kvm_host.yaml). You can also optionally skip [3_setup_kvm_host.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml) and [4_create_bastion.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml) unless you are planning on having the bastion on the same host.
    * In case of lpar based installation one is expected to have a tessia live disk accessible by the lpar nodes for network boot. The details of which are to be filled in section #7 below. The steps to create a tessia livedisk can be found [here](https://gitlab.com/tessia-project/tessia-baselib/-/blob/master/doc/users/live_image.md).

## 2 - (Optional) CPC & HMC
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**cpc_name** | The name of the IBM zSystems / LinuxONE mainframe that you are creating a Red Hat OpenShift Container Platform cluster on. Can be found under the "Systems Management" tab of the Hardware Management Console (HMC). | SYS1
**hmc.host** | The IPv4 address of the HMC you will be connecting to in order to create a Logical Partition (LPAR) on which will act as the Kernel-based Virtual Machine (KVM) host aftering installing and setting up Red Hat Enterprise Linux (RHEL). | 192.168.10.1
**hmc.user** | The username that the HMC API call will use to connect to the HMC. Must have access to create LPARs, attach storage groups and networking cards. | hmc-user
**hmc.pass** | The password that the HMC API call will use to connect to the HMC. Must have access to create LPARs, attach storage groups and networking cards. | hmcPas$w0rd!

## 3 - (Optional) LPAR
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.name** | The name of the Logical Partition (LPAR) that you would like to create/target for the creation of your cluster. This LPAR will act as the KVM host, with RHEL installed natively. | OCPKVM1
**lpar.description** | A short description of what this LPAR will be used for, will only be displayed in the HMC next to the LPAR name for identification purposes. | KVM host LPAR for RHOCP cluster.
**lpar.access.user** | The username that will be created in RHEL when it is installed on the LPAR (the KVM host). | kvm-admin
**lpar.access.pass** | The password for the user that will be created in RHEL when it is installed on the LPAR (the KVM host). | ch4ngeMe!
**lpar.root_pass** | The root password for RHEL installed on the LPAR (the KVM host). | $ecureP4ass!

## 4 - (Optional) IFL & Memory
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.ifl.count** | Number of Integrated Facilities for Linux (IFL) processors will be assigned to this LPAR. 6 or more recommended. | 6
**lpar.ifl.initial memory** | Initial memory allocation for LPAR to have at start-up (in megabytes). | 55000
**lpar.ifl.max_memory** | The most amount of memory this LPAR can be using at any one time (in megabytes). | 99000
**lpar.ifl.initial_weight** | For LPAR load balancing purposes, the processing weight this LPAR will have at start-up (1-999). | 100
**lpar.ifl.min_weight** | For LPAR load balancing purposes, the minimum weight that this LPAR can have at any one time (1-999). | 50
**lpar.ifl.max_weight** | For LPAR load balancing purposes, the maximum weight that this LPAR can have at any one time (1-999). | 500

## 5 - (Optional) Networking
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.networking.subnet_cidr** | The same value as the above variable but in Classless Inter-Domain Routing (CIDR) notation. | 23
**lpar.networking.nic.osa_card.dev_num** | <b>(Optional) Required only when network mode is HIPERSOCKET</b>The logical device number for the OSA Network Interface Card (NIC). In hex format. |
**lpar.networking.nic.card1.name** | The logical name of the Network Interface Card (NIC) within the HMC. An arbitrary value that is human-readable that points to the NIC. | SYS-NIC-01
**lpar.networking.nic.card1.adapter** | The physical adapter name reference to the logical adapter for the LPAR. | 10Gb-A
**lpar.networking.nic.card1.port** | The port number for the NIC. | 0
**lpar.networking.nic.card1.dev_num** | The logical device number for the NIC. In hex format. | 0x0100
**lpar.networking.nic.card2.name** | <b>(Optional)</b> The logical name of a second Network Interface Card (NIC) within the HMC. An arbitrary value that is human-readable that points to the NIC. | SYS-NIC-02
**lpar.networking.nic.card2.adapter** | <b>(Optional)</b> The physical adapter name of a second NIC. | 10Gb-B
**lpar.networking.nic.card2.port** | <b>(Optional)</b> The port number for a second NIC. | 1
**lpar.networking.nic.card2.dev_num** | <b>(Optional)</b> The logical device number for a second NIC. In hex format. | 0x0001

## 6 - (Optional) Storage
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.storage_group_1.name** | The name of the storage group that will be attached to the LPAR. | OCP-storage-01
**lpar.storage_group_1.type** | Storage type. FCP is the only tested type as of now. | fcp
**lpar.storage_group_1.storage_wwpn** | World-wide port numbers for storage group. Use provided list formatting. | 500708680235c3f0<br />500708680235c3f1<br />500708680235c3f2<br />500708680235c3f3
**lpar.storage_group_1.dev_num** | The logical device number of the Host Bus Adapter (HBA) for the storage group. | C001
**lpar.storage_group_1.lun_name** | The Logical Unit Numbers (LUN) that points to a specific virtual disk behind the WWPN. | 4200569309ahhd240000000000000c001
**lpar.storage_group_2.name** | <b>(Optional)</b> The name of the storage group that will be attached to the LPAR. | OCP-storage-01
**lpar.storage_group_2.auto_config** | <b>(Optional)</b> Attempt to automate the addition of the disk space to the existing logical volume. Check out roles/configure_storage/tasks/main.yaml to ensure this will work properly with your setup. | True
**lpar.storage_group_2.type** | <b>(Optional)</b> Storage type. FCP is the only tested type as of now. | fcp
**lpar.storage_group_2_.storage_wwpn** | <b>(Optional)</b> World-wide port numbers for storage group. Use provided list formatting. | 500708680235c3f0<br />500708680235c3f1<br />500708680235c3f2<br />500708680235c3f3
**lpar.storage_group_2_.dev_num** | <b>(Optional)</b> The logical device number of the Host Bus Adapter (HBA) for the storage group. | C001
**lpar.storage_group_2_.lun_name** | <b>(Optional)</b> The Logical Unit Numbers (LUN) that points to a specific virtual disk behind the WWPN. | 4200569309ahhd240000000000000c001

## 7 - (Optional) Livedisk info
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.livedisk.livedisktype** | <b>(Optional)</b> Storage type. DASD and SCSI are tested types as of now. | dasd/scsi
**lpar.livedisk.lun** | <b>(Required if livedisktype is scsi)</b> The Lunid of the disk when the livedisktype is SCSI. | 4003402b00000000
**lpar.livedisk.wwpn** | <b>(Required if livedisktype is scsi)</b> World-wide port number when livedisktype is SCSI. | 500507630a1b50a4
**lpar.livedisk.devicenr** | <b>(Optional)</b> the device no of the live disk | c6h1
**lpar.livedisk.livedisk_root_pass** | <b>(Optional)</b> root password for the livedisk | p@ssword

## 8 - z/VM Bastion Configuration (bastion-zvm.yaml.template)

### Overview
* This section applies to z/VM-based installations where the bastion runs directly on z/VM instead of as a KVM guest.
* Use the `bastion-zvm.yaml.template` file from the host_vars folder and rename it to `bastion-zvm.yaml`.
* This configuration is used with the `4_create_bastion_zvm.yaml` playbook.
* **Important**: Set `installation_type: zvm` in your `group_vars/all.yaml` file to use this configuration.
* **Note**: Future versions will include similar templates for control nodes, compute nodes, and infra nodes on z/VM.

### 8.1 - General Settings
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**zvm_guest** | The z/VM guest name for the bastion (maximum 8 characters, uppercase). | BASTION1
**host_ip** | The IPv4 address that will be assigned to this bastion node. | 192.168.1.20
**node_user** | The username for logging into the bastion after creation. | root
**node_user_pwd** | The password for the node user. Use Ansible vault for security. | {{ vault_bastion_pwd }}
**create_bastion** | Boolean flag to indicate this node should be created as a bastion. | True

### 8.2 - z/VM Hypervisor and Guest Credentials
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**zvm_host** | The hostname or IP address of the z/VM hypervisor where the guest will be created. | zvm.example.com
**zvm_user** | The z/VM user that owns this guest (typically same as zvm_guest). | BASTION1
**zvm_pass** | The password for the z/VM user. Use Ansible vault for security. | {{ vault_zvm_bastion_pwd }}

### 8.3 - Hardware Settings
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**attach_network** | Boolean to attach network devices to the guest. | True
**attach_disk** | Boolean to attach storage devices to the guest. | True
**cpu** | Number of virtual CPUs to assign to the bastion. | 4
**memory** | Amount of memory in MB to assign to the bastion. | 8192
**zfcp_allow_lun_scan** | Enable (1) or disable (0) FCP LUN scanning. Disabled by default for security. | 0

### 8.4 - Storage Configuration
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**zrd_dasd** | List of DASD device numbers for ECKD storage. Use `#X` as placeholder if not using DASD. | - 0.0.0100<br />- 0.0.0101
**zrd_fcp** | List of FCP devices in format: adapter,wwpn,lun. Leave empty `[]` if using DASD. | - 0.0.8001,0x500507630400d1e3,0x4000404500000000<br />- 0.0.8101,0x500507630400d1e3,0x4000404500000000
**install_disk** | The disk device name for installation. Use `mpatha` for multipath FCP, `sda` for single-path FCP, or `dasda` for DASD. | mpatha

### 8.5 - Network Configuration
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**zrd_network_mode** | Network mode for z/VM. | osa
**zrd_znet** | List of network device subchannels for OSA/vSwitch/Hipersockets in qeth format. | - qeth,0.0.1000,0.0.1001,0.0.1002,layer2=1
**network[].ip** | IPv4 address for the network interface. Supports multiple interfaces. | 192.168.1.20
**network[].ipv6** | IPv6 address for the network interface. Use `#X` if not using IPv6. | fd00::20
**network[].gateway** | IPv4 gateway address. | 192.168.1.1
**network[].gatewayv6** | IPv6 gateway address. Use `#X` if not using IPv6. | fd00::1
**network[].netmask** | IPv4 subnet mask. | 255.255.255.0
**network[].netmaskv6** | IPv6 prefix length. Use `#X` if not using IPv6. | 64
**network[].device** | Network device name as seen by Linux (e.g., enc followed by first subchannel). | enc1000

### 8.6 - DNS Configuration
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**nameserver** | List of DNS server IP addresses. At least one is required. | - 8.8.8.8<br />- 8.8.4.4

### 8.7 - Bastion Services
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**bastion_services.dns** | Enable DNS server (bind) on the bastion. | True
**bastion_services.haproxy** | Enable HAProxy load balancer on the bastion. | True
**bastion_services.httpd** | Enable HTTP server for serving ignition files and RHCOS images. | True
**bastion_services.firewalld** | Enable and configure firewall on the bastion. | True

### 8.8 - Additional Boot Parameters
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**additonal_params** | Additional kernel parameters to pass during boot. | rd.neednet=1 rd.luks.options=discard cio_ignore=all,!condev

### Important Notes for z/VM Bastion
* **Tessia Base Library**: The z/VM bastion provisioning uses Tessia base library for guest management. Ensure it's installed on the Ansible controller. If running on MacOS there might be an issue with Tessia base libary so it make sense to run the ansible controller on a Linux machine. The Tessia base library can be installed using the following command: `pip install tessia-base`. You can install it in a virtual environment if needed but make sure to run the playbooks after activating the virtual environment.
* **Pre-existing Guest**: The z/VM guest must already exist and be accessible before running the playbook.
* **Storage Choice**: Choose either DASD or FCP storage, not both. Set unused storage type to `#X` or `[]`.
* **Network Devices**: The `zrd_znet` format must match your z/VM network configuration (OSA, vSwitch, or Hipersockets).
* **Multipath**: For FCP storage with multiple paths, use `mpatha` as the install_disk. The playbook automatically configures multipath.
* **File Server**: Ensure the file server specified in `group_vars/all.yaml` is accessible and has the RHEL ISO mounted.

### Future Enhancements
* **Control Node Templates**: Templates for z/VM control nodes will be added in upcoming versions.
* **Compute Node Templates**: Templates for z/VM compute nodes will be added in upcoming versions.
* **Infra Node Templates**: Templates for z/VM infrastructure nodes will be added in upcoming versions.
* **Day 2 Operations**: Additional playbooks for scaling and managing z/VM-based clusters.

<!-- Assisted by Bob -->