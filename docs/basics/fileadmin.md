# Fileadmin

If you work, for example, with a lot of CSV Files in your Setup, but you don't want to access the Shell all the time, you can enable a simple Fileadmin Panel. This will appear as:
__Filemanager__  in the Panel

To enable it, just create a folder `/srv/cmdbsyncer-files` and make sure the Syncer can write to it.
This will enable the Fileadmin. You can, of course, overwrite this path by setting `FILEADMIN_PATH` in your [local config](lcl_config.md). This is recommended when using Docker with a mounted volume.

The Fileadmin shows the full path of each file, so you can easily copy the path into account configurations without needing shell access.





