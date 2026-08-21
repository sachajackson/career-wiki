# Log

*Append-only, newest at the bottom, one entry per operation. Consistent prefixes keep it greppable:*

```
grep "^## \[" wiki/log.md | tail -5
```

*Prefixes: `ingest`, `interview`, `radar`, `build`, `data`, `query`, `lint`, `fix`.*
