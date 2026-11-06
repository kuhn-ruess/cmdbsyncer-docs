# Rules in Git

<span class="since">Since 4.5</span>

Rules in Git moves rules from one Syncer to another through a Git repository, typically from a test instance to production. The test instance pushes the rule types you select into the repository, production pulls them from there, by hand, on the command line or with a cronjob.

Go to: _Modules → Syncer Rules → Rules in Git_

Every rule type is one file `<path>/<rule_type>.json` in the repository, a JSON list of its rules sorted by id. The Git history therefore shows which rule was added, changed or removed, and when. A merge request on the branch can serve as the approval step before production pulls.

!!! note "What is not transferred"
    Hosts and objects (`host_objects`), accounts, users and the [Secret Store](secret_store.md) belong to each instance and can not be selected. Accounts point at each instance's own systems, and the Secret Store is encrypted with each instance's own key.

    Rules keep their id when they are transferred. A rule which refers to an account, for example a Checkmk site, still needs an account with the same id on the target. Rules referring to each other, for example Ansible rules and their project, work when both types are transferred.

The page is available to global admins only, read only users can not push or pull.

## Set up the Repository Account

Create an empty repository on your Git server (GitLab, GitHub, Gitea, Bitbucket, …) and an access token for it. Then create an account in the Syncer on both instances:

| Field    | Value                                                                              |
| :------- | :--------------------------------------------------------------------------------- |
| Type     | Git Repository                                                                     |
| Address  | HTTPS URL of the repository, e.g. `https://git.example.com/group/syncer-rules.git` |
| Username | Git user. For a GitLab access token any name works, e.g. `oauth2`                  |
| Password | Access token with read access (pull) or write access (push)                        |

The account type _Git Repository_ is not tied to rules, other features can use the same kind of account. It offers these custom fields:

| Custom field  | Default | Description                                                                   |
| :------------ | :------ | :---------------------------------------------------------------------------- |
| `branch`      | `main`  | Branch the rules are pushed to and pulled from. The first push creates it     |
| `path`        | empty   | Folder inside the repository with one file per rule type. Empty uses the root |
| `verify_cert` | `True`  | `False` accepts a self signed certificate of the Git server                   |

The token is sent as an HTTP header. It is neither stored in a Git configuration on disk nor visible in the process list.

The rule files and their folder must not be symbolic links: push and pull stop with an error then, and neither write nor read anything.

## Push to Git

1. Select the repository account.
1. Select the rule types to push. _Select all_ and _Select none_ help with long lists.
1. Optionally enter a commit message. Without one the message lists the pushed rule types.
1. Click _Push_.

The commit is written with your user name and email address as author. Files of rule types you did not select stay in the repository as they are, so different teams can push different rule types. If nothing changed since the last push, no commit is created.

## Pull from Git

1. Select the repository account.
1. Select the rule types to load. Without a selection every rule type found in the repository is loaded.
1. Optionally check _Delete rules which are not in the repository_.
1. Click _Pull_.

A rule from the repository replaces the rule with the same id or the same name. Rules which are not in the repository stay untouched, unless _Delete rules which are not in the repository_ is checked: then the loaded rule types match the repository exactly afterwards, and a rule deleted on the test instance is deleted on production as well. Rule types without a file in the repository are listed and left untouched.

The result shows the commit which was loaded and, per rule type, how many rules were imported and deleted. Every push and pull is written to the [log](logging.md) with the source `rules_git`.

## Command Line

```bash
./cmdbsyncer rules git_push <account> --type cmk_rules --type cmk_filter --message "New filter for the web servers"
./cmdbsyncer rules git_pull <account> --type cmk_rules --delete-missing
./cmdbsyncer rules git_pull <account>
```

| Option               | Description                                                                    |
| :------------------- | :----------------------------------------------------------------------------- |
| `--type <rule_type>` | Rule type to push or pull, repeat for several types. Required for `git_push`   |
| `--message <text>`   | `git_push` only: the commit message                                            |
| `--delete-missing`   | `git_pull` only: delete rules of a pulled type which are not in the repository |

Without `--type`, `git_pull` loads every rule type found in the repository.

## Cronjob

To let production pull on its own, add the job _Syncer: Pull Rules from Git_ to a [cron group](cron.md) and select the repository account. The job reads two more custom fields of the account, add them when you need them:

| Custom field     | Description                                                                                  |
| :--------------- | :------------------------------------------------------------------------------------------- |
| `rule_types`     | Comma separated rule types to pull. Missing or empty pulls every type in the repository      |
| `delete_missing` | `True` deletes rules of a pulled type which are not in the repository. Missing means `False` |

There is no cronjob for pushing: what goes to production is decided on the test instance.
