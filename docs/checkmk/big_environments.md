# Big Environments
The Syncer is also capable to managing big (>100k hosts) Checkmk Environments. 
For that, config switches exist, which you can enable in case e.g. Checkmk runs in timeouts when the API is queried.

All of them, you can set in you local_config.py



|Variable     | Funtion  |
| --- | --- |
|  CMK_COLLECT_BULK_OPERATIONS   | When Request to Checkmk take too long, <br>the DB Cursor can run in a Timeout.<br> With that switch, DB and CMK Operations<br>will be seperated. Needs more RAM.    |
| CMK_GET_HOST_BY_FOLDER| Query Hosts from Checkmk Folder by Folder <br> That prevents too big a request for hosts <br> which will end in a timeout in CMK. | 



## Limiting objects
It's likely that you have different types of objects in the Syncer Database. In order that the Syncer does not need to calculate on objects not relevant for an operation, it's possible to limit the objects which will be used. That happens directly at Database level, so way faster than just using the normal Filter.

To set this App, switch to the Account for the Operations,  add a Plugin Setting, Select the Operation on which you want to use it, and the objects you would like to use it on.

