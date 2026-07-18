# Graph Report - worktodos  (2026-07-18)

## Corpus Check
- 4 files · ~3,342 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 44 nodes · 70 edges · 6 communities detected
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a3fa979`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 7|Community 7]]

## God Nodes (most connected - your core abstractions)
1. `CategoryRepository` - 12 edges
2. `BaseRepository` - 9 edges
3. `QuickNotesRepository` - 9 edges
4. `index()` - 5 edges
5. `create_todo()` - 5 edges
6. `Todo` - 4 edges
7. `sync_todo_categories()` - 4 edges
8. `get_quick_notes()` - 4 edges
9. `get_available_categories()` - 4 edges
10. `form_context()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Category` --uses--> `CategoryRepository`  [INFERRED]
  app.py → repositories/category_repository.py
- `QuickNotesRepository` --uses--> `QuickNotes`  [INFERRED]
  repositories/quicknotes_repository.py → app.py
- `Todo` --uses--> `CategoryRepository`  [INFERRED]
  app.py → repositories/category_repository.py
- `Todo` --uses--> `QuickNotesRepository`  [INFERRED]
  app.py → repositories/quicknotes_repository.py
- `sync_todo_categories()` --calls--> `CategoryRepository`  [INFERRED]
  app.py → repositories/category_repository.py

## Communities (8 total, 3 thin omitted)

### Community 2 - "Community 2"
Cohesion: 0.47
Nodes (6): create_todo(), edit_todo(), form_context(), parse_due_date(), sync_todo_categories(), Todo

### Community 4 - "Community 4"
Cohesion: 0.4
Nodes (3): BaseRepository, QuickNotesRepository, Category

### Community 5 - "Community 5"
Cohesion: 0.5
Nodes (4): get_available_categories(), get_filter_status(), get_selected_category_ids(), index()

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CategoryRepository` connect `Community 3` to `Community 1`, `Community 2`, `Community 4`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.324) - this node is a cross-community bridge._
- **Why does `BaseRepository` connect `Community 1` to `Community 3`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.255) - this node is a cross-community bridge._
- **Why does `QuickNotesRepository` connect `Community 4` to `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `CategoryRepository` (e.g. with `BaseRepository` and `sync_todo_categories()`) actually correct?**
  _`CategoryRepository` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `BaseRepository` (e.g. with `QuickNotesRepository` and `CategoryRepository`) actually correct?**
  _`BaseRepository` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `QuickNotesRepository` (e.g. with `BaseRepository` and `get_quick_notes()`) actually correct?**
  _`QuickNotesRepository` has 5 INFERRED edges - model-reasoned connections that need verification._