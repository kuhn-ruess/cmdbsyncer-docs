# Checkmk Password Manager

You can use the Syncer to create and update entries for the Checkmk Password Manger.
This feature fully works beginning with 3.9.0. The Passwords you enter inside the Syncer, will be encrypted inside the Database. But the Key to decrypt, is stored in your local_config.py. If you change the key there, you need to Update the Passwords.

The Syncer needs to be able to decrypt the password, before its sent to Checkmk. 


## Setup

You have to configure 1 to 1 all settings you would have to configure in Checkmk. Jinja is not yet supported.