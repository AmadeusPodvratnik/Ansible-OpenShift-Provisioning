# Ansible-Automated OpenShift Provisioning on KVM on IBM zSystems / LinuxONE
The documentation for this project can be found [here](https://ibm.github.io/Ansible-OpenShift-Provisioning/).

Release v2.4.0 ( 2024/03/17):
This README contains the information for the current release only.
The whole history of the releases can be found [here](https://github.com/IBM/Ansible-OpenShift-Provisioning/releases).
This release was tested with OpenShift v4.19 and below.

## What's new:
* **Added workflows to integrate github actions for PR validations:**
* **Enable CEX based LUKS encryption:**
* **Updated hcp.yaml with CatalogSource image parameter for MCE:**
* **zVM Bastion Provisioning with Tessia:** Complete implementation for provisioning bastion nodes on pre-existing zVM guests using Tessia base library
  - New role: `create_bastion_zvm_tessia` with comprehensive automation
  - New playbook: `4_create_bastion_zvm.yaml` for zVM bastion deployment
  - Support for multiple network modes: vSwitch, OSA, Hipersockets, RoCE
  - Support for multiple storage types: DASD (ECKD) and FCP
  - Automated RHEL installation via kickstart
  - Complete validation and post-install configuration
* **Enhanced Documentation:**
  - New comprehensive guide: `docs/tessia-zvm-bastion-provisioning.md`
  - Architecture overview updated with zVM deployment model
  - Example configuration file: `bastion-zvm.yaml.example`
* **Improved Code Quality:**
  - Better readability with YAML folded scalars for long lines
  - Enhanced variable documentation coverage (100% for zVM bastion)
  - Fixed multiple integration issues for zVM installations

### Bug Fixes
* Fixed LPAR validation errors for zVM installations by adding installation_type checks
* Fixed `nameserver2` undefined errors with conditional logic based on installation_type
* Fixed Red Hat subscription validation NoneType errors with proper null checks
* Fixed DNS template to support both KVM and zVM nameserver configurations
* Add EC build support logic in OCP installer download task (#430)
* Added RoCE interface to the parm file of LPAR while booting (#424)
* DNS entries fix to enabling correct forwarding. (#446)
* Issue 433 - UPI installion not working (#434)
* Jenkins pipeline failure at the mce creation steps (#425)
* Resolved bug for ocmirrorv2 from 4.19 (#412)
* This fix solves the UPI installation for HA (#439), closes (#438)
*    Update to get the by-path value of fcp disk and the pod count of hcp to greater than 20. (#413)
*    Updated InfraEnv template and updated timeouts for image downloads (#418)
*    Updated mirror information for HCP templates (#426)
*    Updated the nameserver of kvm, zvm & LPAR agents - hcp (#417)
*    Updated the nameserver of lpar hipersockets agents (#422)


### New Variables:
* **zVM Bastion Configuration** (28 new variables in `bastion-zvm.yaml`):
  - `zvm.host`: z/VM hypervisor hostname
  - `zvm.user`: z/VM admin username
  - `zvm.password`: z/VM admin password (vault variable)
  - `zvm.guest.name`: Pre-existing guest name
  - `zvm.network_mode`: Network type (vswitch/osa/hipersockets/roce)
  - `zvm.disk_type`: Storage type (dasd/fcp)
  - `zvm.dasd.*`: DASD configuration parameters
  - `zvm.fcp.*`: FCP configuration parameters
  - Additional network, DNS, and service configuration variables

### Deprecated section:

#### Support for openvpn is being deprecated due to issues with RHEL9. It will be removed in one of the upcoming releases. For the time being this feature is disabled by setting setup_openvpn variable to False.
#### Support for RHEL8. RHEL8 support will be removed in one of the upcoming releases.
