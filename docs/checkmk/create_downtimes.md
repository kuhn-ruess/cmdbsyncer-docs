# Downtimes
Using the known Syncer Rules and the Hosts Attributes, you can create Flexible Downtimes, which can be manged in your CMDB, but then created in Checkmk by the CMDB Syncer.

## How to configure
_Rules → Checkmk → Checkmk Downtimes_


| Field | Description |
| :--------|:------------|
| Start Day| Select the Day for the Downtime in the List |
| Start Day Template| Set the day, by Jinja Template. English, short <br> mon, tue, wed, thu, fri, sat, sun |
| Every| Select how often to repeat, eg. every 2nd Start Day |
| Every Template | Set repeat by Jinja Template. Results: <br> day, workday, week, 1-5 or 1.-5.  |
| Offset Days | Offset in Days from the Startday |
| Offset Template | Offset in Days from Jinja Template |
| Start Time H| Start Hour (Jinja, 24h)  |
| Start Time M| End Minutes (Jinja) |
| End Time H| End Hour (Jinja 24h) |
| End Time M| End Minutes (Jinja) |
| Downtime Comment| Comment for Downtime (Jina) |
| Duration | Start Flexible Downtime (Jinja) |


## Timezones
Downtimes in Checkmk need to be Timezone aware.
The Downtimes you enter in the gui, will have the Timezone of the Server/ Docker Container where you installed the syncer.
But for the Downtime used in Checkmk, you need to overwrite maybe with the local_config.py.

Example local_config.py:
```
import datetime
config = {
    'TIMEZONE': datetime.timezone.utc,
}
```