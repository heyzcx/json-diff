# json-diff

Diff two JSON files by key path — zero-dependency Python CLI.

## Install

Requires Python 3.8+. No dependencies, no install step:

```sh
git clone https://github.com/heyzcx/json-diff.git
cd json-diff
```

## Usage

```sh
python json_diff.py a.json b.json
```

Output lists added (`+`), removed (`-`) and changed (`~`) keys as dotted
paths, plus a summary line:

```
+ extra: 1
- config.debug: true
~ config.timeout: 30 -> 60
~ tags[1]: "b" -> "c"
4 difference(s): 1 added, 1 removed, 2 changed
```

### Options

| Flag | Effect |
| --- | --- |
| `--ignore-order` | Ignore the order of list items |
| `--quiet` | Print nothing, only set the exit code |

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Files are identical |
| 1 | Files differ |
| 2 | Error (missing file or invalid JSON) |

## Examples

```sh
# Compare two config files
python json_diff.py config.prod.json config.staging.json

# Use in a script / CI check
python json_diff.py before.json after.json --quiet || echo "config changed"

# Ignore list ordering (e.g. unordered tag lists)
python json_diff.py a.json b.json --ignore-order
```

## License

MIT
