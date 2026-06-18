---
name: Good first issue
description: Small, well-scoped task suitable for humans or coding agents
labels: ["good first issue", "agent-assignable"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for helping ClauseKeeper. Good first issues should be narrow, testable, and safe for a coding agent to pick up.

  - type: textarea
    id: goal
    attributes:
      label: Goal
      description: What should be true when this issue is complete?
      placeholder: Example: Add a scanner rule for X and show it in scan results.
    validations:
      required: true

  - type: textarea
    id: files
    attributes:
      label: Files involved
      description: List the likely files or folders to edit.
      placeholder: |
        - app/clause_rules.py
        - tests/test_scanner.py
    validations:
      required: true

  - type: textarea
    id: acceptance
    attributes:
      label: Acceptance criteria
      description: Concrete checklist an assignee/agent can verify before opening a PR.
      placeholder: |
        - [ ] New rule has key/label/category/weight/signals/why/fix
        - [ ] Existing scanner API response shape is unchanged
        - [ ] Tests cover the new behavior
    validations:
      required: true

  - type: input
    id: test-command
    attributes:
      label: Test command
      description: Exact command to run from the repo root.
      value: uv run pytest
    validations:
      required: true

  - type: textarea
    id: constraints
    attributes:
      label: Constraints / guardrails
      description: Anything the assignee must avoid or preserve.
      placeholder: |
        - Do not add an LLM dependency to the core product
        - Preserve the not-legal-advice disclaimer if touching generated docs
        - Keep self-hosted mode working without external keys
    validations:
      required: false
