# Project Guidelines

## Scope
These instructions apply to the entire repository.

## Coding Style
- Follow Python 3.10+ conventions and favor explicit, readable code.
- When adding or modifying functions or classes, include type hints for all parameters and return values unless a third-party API prevents it.
- Prefer `dataclasses` for plain data containers instead of bare dictionaries when practical.
- Keep modules formatted with `black`-compatible 120 character line length and use `isort` ordering for imports.
- Avoid introducing global mutable state; use dependency injection or instance attributes where possible.

## Documentation
- Provide docstrings for any new public function, class, or method that explains its purpose and important parameters.
- Update existing docstrings or comments if behavior changes.

## Testing
- Add or update unit tests alongside functional changes. The canonical test command is `pytest` from the repository root.
- When a change affects gameplay balancing, include a short note in the relevant commit message or docstring summarizing the impact.

## Assets
- Do not add binary assets larger than 1 MB without prior approval. Prefer referencing existing resources or using procedural content where possible.

## Pull Requests
- Summaries should briefly state the player-facing impact and any major internal refactors.
- Include a checklist of updated or new tests in the PR body.

