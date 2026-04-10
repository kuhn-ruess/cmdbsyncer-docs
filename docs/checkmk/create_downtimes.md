# Downtimes

Using Syncer rules and host attributes, you can create flexible scheduled downtimes in Checkmk — managed in your CMDB and applied automatically.

Go to: _Modules → Checkmk → Manage Downtimes_

## Configuration

| Field              | Description                                                                                  |
| :----------------- | :------------------------------------------------------------------------------------------- |
| Start Day          | Select the day for the downtime from a list                                                  |
| Start Day Template | Set the day as a Jinja template using short English names: mon, tue, wed, thu, fri, sat, sun |
| Every              | How often to repeat, e.g. every 2nd occurrence of the start day                              |
| Every Template     | Set repeat frequency as a Jinja template. Results: day, workday, week, 1-5 or 1.-5.          |
| Offset Days        | Number of days offset from the start day                                                     |
| Offset Template    | Offset in days as a Jinja template                                                           |
| Start Time H       | Start hour (Jinja, 24h format)                                                               |
| Start Time M       | Start minutes (Jinja)                                                                        |
| End Time H         | End hour (Jinja, 24h format)                                                                 |
| End Time M         | End minutes (Jinja)                                                                          |
| Downtime Comment   | Comment for the downtime (Jinja supported)                                                   |
| Duration           | Start a flexible downtime with this duration (Jinja)                                         |

## One-Time Downtime for Today

To set a downtime for the current day whenever a condition is met for a host:

- Set **Start Day** to `Today`
- Set **Every** to `once`

This is useful for triggering downtimes based on a CMDB flag or maintenance window attribute.

## Timezones

Downtimes in Checkmk are timezone-aware. The times you enter in the UI use the timezone of the server or Docker container where the Syncer is installed. To override this for the exported downtimes, set the timezone in `local_config.py`:

```python
import datetime

config = {
    'TIMEZONE': datetime.timezone.utc,
}
```

## Command Line

```bash
./cmdbsyncer checkmk export_downtimes ACCOUNTNAME
```
