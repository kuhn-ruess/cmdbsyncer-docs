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

## Per-User Themes

Each logged-in user can pick their own colour scheme under
**Account → Theme**. Administrators can override the choice for any
user from **Settings → Users → Preferences → Theme**.

The following themes ship with cmdbsyncer:

| Slug            | Description                                |
| :-------------- | :----------------------------------------- |
| `default`       | The classic light look — uses the `STYLE_NAV_*` config above. |
| `gruvbox-dark`  | Warm earthy dark theme.                    |
| `gruvbox-light` | Warm earthy light theme.                   |
| `nord`          | Cool blue dark theme.                      |
| `dracula`       | High-contrast dark theme with purple/pink accents. |

A user theme only affects that user's browser; it never changes what
other users see.

### Adding Your Own Themes

Drop a `.css` file into `plugins/themes/` next to the cmdbsyncer
installation and restart the application — the new theme appears in
the picker automatically. The filename (without `.css`) becomes the
slug; the human-readable label is taken from a header comment, or
falls back to a title-cased slug (`solarized-dark.css` →
"Solarized Dark").

A minimal theme file:

```css
/* @name: My Theme */
:root {
    --nav-bg: #112233;
    --nav-link: #eeeeee;
}
body { background-color: #112233; color: #eeeeee; }
/* ...overrides for tables, cards, dropdowns, forms, modals... */
```

The shipped themes under `application/themes/` (in particular
`gruvbox-dark.css` and `nord.css`) are the most complete templates to
copy from — they cover every Bootstrap component the admin UI uses
(tables, dropdowns, modals, pagination, filter chips, the changelog
widget, etc.).

Shipped themes win on slug collision, so pick a different filename if
you want to ship something next to a built-in look.
