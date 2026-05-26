# Host and Object Search Syntax

The quick-search box at the top of the Host and Object lists accepts a
small expression language so that you can combine conditions without
opening the full filter sidebar. Every search produces a MongoDB query
under the hood.

## Quick reference

| You type                          | Matches                                                          |
|-----------------------------------|------------------------------------------------------------------|
| `prod`                            | Hosts whose `hostname` contains `prod`, or who carry a label / inventory entry **named exactly** `prod`, or whose label / inventory **value** contains `prod` |
| `prod web`                        | Both terms must match (implicit `AND`)                           |
| `prod AND web`                    | Same as above, explicit                                          |
| `prod OR stage`                   | Either term matches                                              |
| `NOT archived` / `!archived`      | Hosts where no field contains `archived`                         |
| `(prod OR stage) AND NOT test`    | Parentheses group sub-expressions                                |
| `hostname:web`                    | Match only against the `hostname` column                         |
| `env:prod`                        | Look for the value in `labels.env` **or** `inventory.env`        |
| `labels.env:prod`                 | Look only in `labels.env`                                        |
| `inventory.cpu:8`                 | Look only in `inventory.cpu`                                     |
| `hostname:web*`                   | Wildcard — `*` matches anything, `?` matches one character       |
| `hostname:"web 01"`               | Quoted value preserves spaces and disables wildcards             |

## Operators

- `AND`, `OR`, `NOT` — keywords, case-insensitive (`and`, `or`, `not` work
  the same)
- `!` — short form of `NOT`
- `( ... )` — grouping, can be nested
- No operator between two terms means implicit `AND`

Operator precedence is the usual one: `NOT` binds tightest, then `AND`,
then `OR`. Use parentheses if you are unsure.

## Field prefixes

A bare term searches in five places: the `hostname` column (as a
substring), every key in the `labels` and `inventory` dictionaries
(matched **exactly** — `basti_test` does *not* find a label called
`basti_test2`), and every value in those two dictionaries (substring).
Matching against keys is what makes expressions like `NOT basti_test`
return all hosts that do **not** carry a label named `basti_test`. Use
`basti_test*` if you want a prefix match against the key. To restrict
the search, prefix the value with `field:`:

- `hostname:` — only the host name column
- `<key>:` — both `labels.<key>` and `inventory.<key>` (whichever
  contains the key wins)
- `labels.<key>:` — only `labels.<key>`
- `inventory.<key>:` — only `inventory.<key>`

Field names may contain letters, digits, `_`, `-` and `.`.

## Wildcards and quotes

- `*` matches any sequence (including the empty one)
- `?` matches exactly one character
- A value enclosed in double quotes is treated literally: `*`, `?`,
  spaces and other regex characters lose their special meaning. Use
  quotes whenever your value contains spaces.

If a value happens to be invalid as a regular expression, the parser
falls back to a literal match instead of raising an error.

## Errors

Malformed expressions (unbalanced parentheses, a dangling operator, a
field name without a value, an unterminated quote) display an inline
error message above the host list and return an empty result. The
expression itself stays in the search box so you can correct it.
