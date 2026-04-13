# Interactive Syncer Shell

The Syncer ships with an interactive REPL that lets you run any registered
Flask CLI command without typing `flask ...` every time. It provides tab-completion
for all command groups and subcommands and keeps a persistent history.

## Starting the Shell

```bash
flask cli
```

You will be greeted with a `syncer>` prompt:

```text
CMDB Syncer interactive shell — type 'help' or 'exit'.
syncer>
```

## Usage

Type any syncer command without the leading `flask`. For example:

```text
syncer> rules export_all_rules
syncer> cron list_jobs
syncer> checkmk export_hosts my-account
```

### Built-in Commands

| Command         | Description                                  |
|-----------------|----------------------------------------------|
| `help` / `?`    | Show available top-level commands and groups |
| `exit` / `quit` | Leave the shell (Ctrl-D works as well)       |

### Tab-Completion

Press `Tab` to complete command groups and subcommands. The completer is built
dynamically from the currently registered Click commands, so plugins added via
`application/plugins/` are picked up automatically.

### History

Command history is stored in `~/.cmdbsyncer_shell_history` and persists across
sessions. Use the arrow keys to navigate.

### Error Handling

Usage errors and exceptions from individual commands are caught and printed,
the shell itself keeps running. `Ctrl-C` cancels the current line without
exiting the shell.
