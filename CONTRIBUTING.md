# Contributing

Keep each pull request focused on one useful change.

## Report a bug

Search existing issues first. Include the command, a minimal non-sensitive input, expected output, actual output, Python version and operating system. Do not upload credentials, customer data or private configuration.

## Propose a change

1. Create a branch from the latest `main`.
2. Implement a focused improvement and add regression coverage where behaviour changes.
3. Run `python -m unittest discover -s tests -v`.
4. Open a pull request explaining the problem, resulting behaviour and checks run.
5. Wait for all six Python tests jobs to pass before merging. If a run is awaiting maintainer approval, leave the PR open until that approval is available.

Review the diff for accidental files and unnecessary dependencies. State any validation limits. AI-assisted changes should be identified as such; an author's self-review is not independent approval.

## Credit collaborators

Use a `Co-authored-by: Name <email>` commit trailer only for someone who actually contributed to the change, using an email associated with their GitHub account. Do not add uninvolved people to obtain an achievement.

## Questions

Ask questions in issues with a clear explanation and a reproducible example when relevant. If Discussions is enabled later, use its Q&A category for usage questions.
