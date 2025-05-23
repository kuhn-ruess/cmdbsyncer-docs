
# Welcome to the CMDBsyncer

Rule based and modular system to syncronize hosts between Checkmk, Netbox, I-Doit and all others systems with interfaces and APIs.
Main goal is the complete organization of the hosts based on CMDB systems and a full automation of Checkmk.


![Rules](img/index_rules.png)
![Debug Options](img/index_rules_debug.png)


## Main Functions
* Web Interface with Login, 2FA and User management
* All configuration besides Installation in Web Interface
* Simple Plugin API to integrate own Data Sources
* Various Debug Options with the ./cmdbsyncer command
* Rules to control the Synchronization:
	 * Based on Host Attributes
	 * Attribute Rewrites
	 * Filters fur Hosts and Attributes
  * Action Rules for Actions in Ansible, Checkmk, Netbox etc.
* Web Based management for Account Credentials.
* Encryption of Secrets
* Cron Management
* Monitoring Integration
* Jinja Support for Configuration and Rules
* RestAPI
* Ansible Support as Inventory Source

## Modules

* [Checkmk](/checkmk/)
    * Mange full Host Lifecycle (creation, labels, folders, deletion, rules)
    * Tested with more than 140,000 Hosts
    * Sync and Update all possible Host Attributes/ Tags/ Labels
    * Full Support of API Bulk Operations
    * Full management of Checkmk Folders
    * Folder Pool Feature to split big amounts of Hosts automatically between folders (and therefore sites).
    * Creation of Host-, Contact- and Service Groups
    * Create Host Tags and Host Tag Groups
    * Create BI Aggregations
    * Create all types of Setup Rule
    * Integrated options to prevent to many Updates in Checkmk
    * Full Multiprocessing support for Calculations
    * Command to Active Configuration
    * Command to Bake and Sign Agents
    * Management of Checkmk (Fallback) users (Create/ Delete/ Reset Password/ Disable Login)
    * Inventory for Host Attributes (need e.g. for Ansible, like on which site is server on)
    * Inventory of Service Informations, Labels, Tags and HW/SW Inventory possible (can be used e.g. for I-Doit Sync)
    * Create DCD Rules
    * Create and Manage Password Store (Encryption) entries
    * Automatic Detection of the Checkmk Version to use the correct API Payloads

* [Ansible](/ansible/)
    * Rule Based Inventory Source
    * All Functions for Checkmk Agent Management (Installation, TLS Registration, Bakery Registration)
        *  Linux and Windows
    * All functions for Checkmk(OMD) Site Management (Update Sites, Create Sites etc.)
        * Automatic Download of Checkmk Versions if wanted.


* [Netbox](/netbox/)
    * Rulebased Export and Import Devices and VMs to/from Netbox
    * Automatic creation of Categories if wanted.
    *  Export of Sites
    *  Export Interfaces
    *  Export IPAM
    * Export Contacts
    * And more
* PRTG
	* Import Objects from PRTG to sync them to Checkmk

* [I-DOIT](/i-doit/)
    * Rulebased Export and Import Devices to/from I-Doit
    * Template Based

* BMC Remedy
    * Limited import from BMC Remedy

* [Cisco DNA](/ciscodna/)
    * Import devices and their Interface Information

* [CSV](/csv/)
    * Manage Hosts based on CSV File (Import Source)
    * Add Addional Informationen from CSV Files to your Hosts (eg. Overwrite IP Addresses)

* LDAP
    * Import Objects from LDAP Directories

* [RestAPI](/rest_json)
    * Import of Custom Rest APIs

* [JSON](/rest_json/)
    * Import of Json File Structures

* Jira CMDB on Prem and Cloud:
    * Import Objects
    
*  [JDisc](/jdisc/)
	* Import Objects

* Vmware
	* Import Attributes
	* Export Attributes to Vmware VMs
	
* MySQL
    * Import and Inventorize Mysql Database Tables

* Mssql/ FreeDTS/ ODBC
    * Import and Inventorize all kinds of ODBC based Database Connections
