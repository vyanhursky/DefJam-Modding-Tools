# Menu exporters with explicit private inputs

The menu exporters formerly under the game's `scripts/` are maintained here.
Install this checkout and run `defjam-tools <command> --help`. They build new local
outputs; they do not install a pack, upload an artifact or approve artwork.

| Command | Private inputs |
|---|---|
| `menu-verify` | `--catalogue` approval ledger and `--art-root` |
| `menu-pack` | `--exports` source-shaped table, `--catalogue`, `--art-root`, `--out` |
| `menu-wide` | `--layers`, `--catalogue`, `--registrations`, `--art-root`, `--mods`, `--out` |
| `menu-branding` | `--catalogue`, `--art-root`, `--faithful`, `--out`; optional `--review` |
| `menu-release` | `--recipe`, `--recipe-root`, `--catalogue`, `--art-root`, `--base-mods`, `--approved-components`, `--out`; optional `--receipt` |

There are no bundled production approval tables. Supply the exact archived JSON
from the matching private project. For old recipes whose registration and wide
paths begin `config/`, `--recipe-root` is the archived root containing that folder.
Do not copy those records into the public tools source tree.

The legacy release builder consumes frozen components and receipts; it is not a
recipe for regenerating the published 1.4 archive from scratch. Preserve that
exact approved archive and its private newer assembly receipt. Native mapping,
private provenance and output hashing remain the author's responsibility.

Optional older neural auditions are `defjam-tools audition` and `defjam-tools swinir`.
The illustrative [texture recipe](../examples/texture-recipe.json) is an early
small runtime batch example, not the accepted full Faithful HD recipe.
