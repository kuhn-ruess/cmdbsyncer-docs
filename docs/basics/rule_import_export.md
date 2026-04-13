# Rule Import and Export

The Syncer can export and import its Syncer Rules. This is useful for backups, for transferring rules between environments (e.g. test → production), or for sharing a rule set with colleagues.

There are two ways to export rules: from the GUI (per rule type) and from the CLI (single type or all types at once).

## GUI Export

Every Syncer Rule list in the web interface supports exporting. To export rules from the GUI:

1. Open the rule list you want to export (e.g. _Modules → Checkmk → Export Rules_).
2. Select the rules you want to export using the checkboxes on the left. Use the header checkbox to select all rules on the current page.
3. Choose _Export → JSON_ from the actions menu above the list.

The browser downloads a file named like `CheckmkRule_202604131530.syncer_json`. The first token before the underscore is the model class name of the exported rule type; the rest is a timestamp.

!!! warning "Do not rename the exported file"
    The import command uses the filename to determine which rule type the file belongs to. It parses the part before the first underscore and matches it against the known rule models. If you rename the file, the import will fail with _"Ruletype not supported"_.

    If you really need to rename a GUI export, keep the model class name as the first token — for example `CheckmkRule_backup.syncer_json` still works, but `my_backup.syncer_json` does not.

## CLI Export

The CLI provides two variants: export of a single rule type and export of all rule types at once.

### Export a Single Rule Type

```bash
./cmdbsyncer rules export_rules <rule_type>
```

The command prints line-delimited JSON to stdout, starting with a header line `{"rule_type": "..."}` followed by one JSON object per rule. Redirect the output to a file to save it:

```bash
./cmdbsyncer rules export_rules cmk_rules > cmk_rules_backup.jsonl
```

Run the command without an argument to list all supported rule types.

### Export All Rules at Once

Since version 3.12.5, you can export **all** Syncer rules of every type into a single file:

```bash
./cmdbsyncer rules export_all_rules
```

Without an argument, the Syncer writes to a timestamped file such as `syncer_rules_export_20260413_145521.jsonl` in the current directory. You can also specify an explicit path:

```bash
./cmdbsyncer rules export_all_rules /path/to/backup.jsonl
```

The output is line-delimited JSON. Each rule type is introduced by a header line `{"rule_type": "..."}`, followed by one JSON object per rule of that type. All known rule types are written into the same file in one pass.

## CLI Import

A single import command handles all export formats — GUI exports, single-type CLI exports, and combined multi-type exports from `export_all_rules`:

```bash
./cmdbsyncer rules import_rules /path/to/file
```

The import auto-detects the format:

- If the file starts with a `{"rule_type": "..."}` header, the import uses that rule type. Multiple header blocks in the same file are supported — the importer switches rule type whenever a new header appears.
- If the file has no header (GUI export), the import falls back to guessing the rule type from the filename, as described above.

Rules that already exist in the database (same `_id`) are skipped with an _"Already existed"_ message, so re-running the import is safe and idempotent.
