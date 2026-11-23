# EnvCheck

by Dr. Brent Allen Jensen

Compare a `.env` file against its `.env.example` template and report
what is missing, extra, empty, or duplicated — **key names only, never
values** — so the report is safe to paste into an issue, a chat, or CI
logs.

## Quickstart

```bash
python3 envcheck.py .env.example .env
python3 envcheck.py --dir ./myproject    # compares .env.example and .env inside it
python3 envcheck.py .env.example .env --json
```

## What it reports

- **Missing keys** — in the template, absent from the actual file
- **Extra keys** — in the actual file, not in the template
- **Empty values** — key present, value empty
- **Duplicate keys** — the same key defined twice in either file

Exit code is 0 when there are no missing and no empty keys, 1
otherwise — ready to use as a setup check or CI step.

Parsing handles `export KEY=value`, single- and double-quoted values,
comments, and blank lines.

## The one rule

EnvCheck never prints a value. Not in text mode, not in JSON mode, not
in an error message. Only key names ever leave the parser.

## Requirements

- Python 3.10+, standard library only

## Support this work

If this tool saved you time or taught you something, donations keep the work going:

- BTC: 15McijPo79Zx58NGyEf2PvaPtGqGmpztWn
- ETH: 0x8C25164E9234E6A30b8E44485B79c5cE8419cF2B

## License

MIT — see [LICENSE](LICENSE).
