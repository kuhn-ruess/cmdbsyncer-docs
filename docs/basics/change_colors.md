# Changing the GUI Colors

In environments with multiple instances — such as a production and a test system — it is helpful to visually distinguish the Syncer interfaces from each other.

You can configure the following settings in [local_config.py](lcl_config.md):

| Setting                      | Description                                                              |
| :--------------------------- | :----------------------------------------------------------------------- |
| `STYLE_NAV_BACKGROUND_COLOR` | HTML color for the navigation bar background (default: `#000`)           |
| `STYLE_NAV_LINK_COLOR`       | HTML color for the navigation links (default: `#fff`)                    |
| `HEADER_HINT`                | Free text shown in the header bar, e.g. the environment name             |

## Example

```python
config = {
    'STYLE_NAV_BACKGROUND_COLOR': '#8b0000',
    'STYLE_NAV_LINK_COLOR': '#ffffff',
    'HEADER_HINT': 'PRODUCTION — handle with care',
}
```

This makes the navigation bar dark red and adds a warning text in the header, making it immediately clear which instance you are working on.
