# Log

*Append-only, newest at the bottom, one entry per operation. Consistent prefixes keep it greppable:*

```
grep "^## \[" wiki/log.md | tail -5
```

*Prefixes: `ingest`, `interview`, `radar`, `build`, `data`, `query`, `lint`, `fix`, `migrate`,
`research`, `outcome`.*

*🟡 These are the prefixes the SYSTEM writes. Your own entries may use others — nothing checks
your log. What is checked is that this list and the one in `SCHEMA.md` still agree, and that every
operation the schema documents has a prefix here.*
