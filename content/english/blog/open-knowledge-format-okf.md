---
title: "Open Knowledge Format: A Shared Vocabulary for Agent Knowledge"
meta_title: ""
description: "OKF v0.1 is Google Cloud's proposed open format for AI agent knowledge sharing: YAML-frontmattered Markdown files in a directory tree, no central registry or required runtime."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["AI"]
tags: ["ai-agent", "knowledge-management", "metadata", "open-standard", "okf", "google-cloud", "mcp"]
author: "whackur"
translationKey: "open-knowledge-format-okf"
draft: false
---

When AI agents fail in production, the model is often not the problem. The missing context is. Table schemas, metric definitions, runbooks, join paths between systems, and API deprecation notices are scattered across catalog vendors, internal wikis, code comments, and personal notes. Every agent developer solves the same context assembly problem from scratch.

Open Knowledge Format (OKF) is Google Cloud's response. [Published in June 2026](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/), it is not a new service or platform. It is a minimal interoperability spec: a directory of Markdown files with YAML frontmatter, readable by both humans and agents, with no central schema registry and no required runtime. The [v0.1 draft specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) is on GitHub.

## The context assembly problem

Organizational knowledge typically looks like this in practice:

- table schemas alongside the business meaning of each column
- how a company defines and computes each metric
- incident runbooks and operational playbooks
- join paths between two systems that only one engineer remembers
- API deprecation notices and internal process documentation

Each of these lives in a different system with a different API. Agents either get none of it or get it piecemeal in incompatible formats. OKF proposes making the format itself the shared layer, rather than building yet another service on top.

## Connection to LLM Wiki

Andrej Karpathy's [LLM Wiki idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) argues against RAG-on-demand retrieval in favor of maintaining a steadily-refined Markdown knowledge library alongside an agent. His core observation is that LLMs do not get bored, do not forget to update a cross-reference, and can touch many files in a single pass. That makes them well-suited for the bookkeeping work humans tend to abandon in personal wikis: updating cross-references, merging duplicates, and restructuring directories. OKF tries to formalize that pattern into a spec that works across organizations, tools, and agents.

## OKF v0.1 specification

### Knowledge Bundle

A Knowledge Bundle is a Markdown directory tree, the unit of distribution.

```text
path/to/bundle/
├── index.md        # optional: directory listing for progressive disclosure
├── log.md          # optional: change history
├── <concept>.md    # root concept document
└── <subdirectory>/
    ├── index.md
    └── <concept>.md
```

A Git repository is the recommended storage format, since it gives you history, attribution, diffs, and reviews for free. tarball and zip are acceptable. A bundle can also live as a subdirectory within a larger repo.

### Concept and Concept ID

A concept is one unit of knowledge, expressed as one Markdown file. It can be a tangible asset (table, dataset, API, dashboard) or an abstract concept (metric, process, playbook, reference document).

The **Concept ID is the file path with `.md` removed**. `tables/users.md` has Concept ID `tables/users`. File path is identity, so path design is taxonomy design.

### Frontmatter fields

Every concept document is UTF-8 Markdown with YAML frontmatter at the top:

```yaml
---
type: <Type name>        # the only required field
title: <display name>
description: <one-line summary>
resource: <canonical URI>
tags: [<tag>, <tag>]
timestamp: <ISO 8601 datetime>
---
```

`type` is the only required field, and it is not centrally registered. Producers name it freely: `BigQuery Table`, `Metric`, `API Endpoint`, `Playbook`, `Reference`. Consumers must treat unknown types and unknown extra keys as generic concepts rather than errors.

### Body and cross-linking

The body is plain Markdown. Structured Markdown (headings, lists, tables, fenced code blocks) is preferred over unstructured prose. Conventional sections are `# Schema`, `# Examples`, and `# Citations`.

Relationships between concepts use standard Markdown links. Bundle-root-relative absolute links are preferred: `[customers](/tables/customers.md)`. Relative links are permitted. Broken links are allowed too. They may point to knowledge not yet written.

### Reserved filenames

`index.md` and `log.md` are reserved at any directory level and must not be used as concept documents.

- `index.md`: progressive disclosure file for that directory level. The root `index.md` may include `okf_version: "0.1"`.
- `log.md`: change history file. Uses `## YYYY-MM-DD` headings, newest first. Conventional prefixes: `**Update**`, `**Creation**`, `**Deprecation**`.

### Conformance

Three conditions make a bundle OKF v0.1 conformant:

1. All non-reserved `.md` files have parseable YAML frontmatter.
2. Every frontmatter block has a non-empty `type` field.
3. `index.md` and `log.md`, when present, follow their structural rules.

Consumers must not reject a bundle for missing optional fields, unknown types, unknown extra keys, broken links, or an absent `index.md`.

## Official repo and examples

The [GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) `okf/` directory has the spec alongside a reference proof-of-concept:

- `SPEC.md`: OKF v0.1 draft specification
- `bundles/`: sample bundles for GA4, Stack Overflow, and Bitcoin public datasets
- `src/enrichment_agent/`: a Google ADK and Gemini-based enrichment agent that generates OKF concept documents from BigQuery metadata
- `viz.html`: a static graph view of a sample bundle

The repo README notes that "format itself is the contribution." The enrichment agent and visualizer are examples of OKF producers and consumers, not requirements.

## Relationship to nearby standards and tools

### AGENTS.md and CLAUDE.md

[AGENTS.md](https://agents.md/) is a "README for agents" convention for code repositories. It is adjacent to OKF but different in scope.

- AGENTS.md: setup, test, and style rules for a coding agent in a specific repo
- OKF: a format for representing an entire organizational knowledge corpus that agents and humans can share

OKF's starting point is the observation that AGENTS.md, CLAUDE.md, index.md, and log.md are already used as LLM Wiki-style files, but their fields, structure, and link semantics vary too much for interoperability. OKF tries to define a minimal common floor.

### Avro, Protobuf, and OpenAPI

The OKF SPEC explicitly lists Avro, Protobuf, and OpenAPI as out of scope. OKF references these formats rather than replacing them.

- OpenAPI: the API contract itself
- Protobuf/Avro: serialization and message schemas
- OKF: the context layer around those schemas: examples, operational knowledge, citations, join paths, and business meaning

### Model Context Protocol

[MCP](https://modelcontextprotocol.io/introduction) is the open protocol for connecting AI applications to external systems, data sources, and tools. OKF and MCP are complementary, not competing.

- MCP: how an agent connects to and calls external tools and data sources
- OKF: what file format the knowledge that agent reads and shares takes

An MCP server could expose an OKF bundle as a resource. An agent could query a data catalog via MCP and organize the results as an OKF bundle.

## When OKF fits, and when it is overkill

OKF fits when:

- multiple agents or tools need to read the same organizational knowledge
- data catalogs, metric definitions, playbooks, and API documentation are scattered across different systems
- knowledge changes should be managed as git diffs and reviewed like code
- sharing a knowledge corpus across teams without binding to a specific vendor API

OKF is overkill for:

- temporary prompt or context files used only within a single application
- cases where the schema is already fully expressed in OpenAPI or Protobuf
- ephemeral context that exists only at runtime in a database

## Caveats

v0.1 is a draft. Optional fields and reserved filename rules may change in future versions. The [PyTorchKR discussion post](https://discuss.pytorch.kr/t/open-knowledge-format-okf-google-ai-feat-llm-wiki/10701) and [Google Cloud blog post](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/) are useful introductions, but for exact rules the authoritative source is the [SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

## Further reading

- [GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf): official repo, spec, sample bundles, enrichment agent
- [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): original LLM Wiki pattern
- [AGENTS.md](https://agents.md/): the README-for-agents convention
- [Model Context Protocol](https://modelcontextprotocol.io/introduction): open protocol for agent-tool connections
- [Google Cloud Blog: OKF](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/): motivation and background from Google Cloud

## References

- [Open Knowledge Format SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md): GoogleCloudPlatform/knowledge-catalog, accessed 2026-06-30
- [GoogleCloudPlatform/knowledge-catalog OKF README](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf): GitHub, accessed 2026-06-30
- [Google Cloud Blog: How the Open Knowledge Format can improve data sharing](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/): Google Cloud, accessed 2026-06-30
- [PyTorchKR: OKF discussion](https://discuss.pytorch.kr/t/open-knowledge-format-okf-google-ai-feat-llm-wiki/10701): discuss.pytorch.kr, accessed 2026-06-30
- [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): Andrej Karpathy, accessed 2026-06-30
- [AGENTS.md](https://agents.md/): agents.md, accessed 2026-06-30
- [Model Context Protocol Introduction](https://modelcontextprotocol.io/introduction): modelcontextprotocol.io, accessed 2026-06-30
