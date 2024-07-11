# First Steps
Depending on, if you are on docker or local, you need to change into the docker container or enable the Virtual Environment for the following functions


## Settings
The Config contains to important Values you should overwrite in a local_config.py file.
First is "SECRET_KEY". This one is used to secure the login cookie. You can change it anytime,
but all users will be logged out by that. More important: "CRYPTOGRAPHY_KEY". This one is used to decode Passwords stored in the Database. If changed, you need to reset all Passwords.
How to set the config see  [here](lcl_config.md)

## Create first User
When you have the Setup Done, you have to create a user to login into the Web interface.

`./cmdbsyncer sys create_user mail@address.org`

The command shows you a password. In case you have forgotten the password, our locked yourself out with the 2FA Function, this command will reset everything.

## Explore the Command line Options
The Command Line offers you access to almost every function. 
It's separated in different areas. So, you can go deeper and deeper into the options.

Example:

![](img/cli_options.png)







