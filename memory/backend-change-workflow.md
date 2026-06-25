---
name: backend-change-workflow
description: Workflow for making backend changes — create issue, branch, and PR with closing reference
metadata:
  type: project
  tags: [backend, workflow, github]
---

Whenever making a change to the backend, follow this workflow:

1. **Create a new GitHub issue** using the existing issue template (Task/PBI).
2. **Note the issue number** (e.g., #168).
3. **Create a new branch** named `feature/PBI-<issue_number>-<short-description>` (e.g., `feature/PBI-168-fix-upload-validation`).
4. **When creating the Pull Request**, include `Closes #<issue_number>` in the description so the issue is automatically closed upon merge.

**Why:** Standardizes backend development workflow, ensures traceability from issue to PR, and auto-closes issues on merge.
**How to apply:** Before starting any backend work, create the issue first, then branch from it. Always reference the issue in the PR.
