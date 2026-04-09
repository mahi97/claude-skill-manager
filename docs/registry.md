# Registry

The registry is the canonical source of truth for the Claude Skill Manager. It lives in the `registry/` directory as YAML files.

## Structure

```
registry/
  installed.yaml     # Items currently in your stack
  candidates.yaml    # Discovered items pending review
  rejected.yaml      # Items you've explicitly rejected
  sources.yaml       # Configured discovery sources
  policies.yaml      # Automation policy rules
  taxonomy.yaml      # Category taxonomy tree
  proposals/         # Generated change proposals (YAML)
  evaluations/       # Evaluation reports (YAML)
  seeds/             # Seed data for bootstrapping
```

## File Formats

### installed.yaml / candidates.yaml / rejected.yaml

Arrays of RegistryItem objects. See [data-model.md](data-model.md) for the full schema.

### sources.yaml

Array of Source objects. Each source defines:
- Where to look (URL or path)
- What type of connector to use
- Trust tier for items discovered from this source
- Whether scouting is enabled
- Sync interval

### policies.yaml

Array of PolicyRule objects defining automated behavior constraints. Policies are currently informational — the policy engine evaluates them during proposal generation but enforcement is manual.

### taxonomy.yaml

Flat list of TaxonomyNode objects defining the category hierarchy. Currently a single level; hierarchical nesting is a future feature.

## Operations

### Reading

The Registry class in `csm_core/registry.py` handles all YAML I/O. It loads files on demand (no persistent cache), ensuring reads always reflect the latest state.

### Writing

All writes go through Registry methods that serialize Pydantic models to YAML. The registry never partially writes — it serializes the full list atomically.

### Deduplication

Candidates are deduplicated by ID. An item cannot be a candidate if it already exists in installed or rejected.

### Mutations

Direct mutations (install, reject) are performed via Registry methods. These:
1. Load the relevant lists
2. Move the item between lists
3. Save both lists atomically

Proposal-driven mutations (via ApplyAgent) additionally:
1. Create a pre-mutation snapshot
2. Apply each change in the proposal
3. Update the proposal status
