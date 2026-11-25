# Web Dev Pilot

An AI coding skill for people who want to build a website but may not have a repository, code, domain, or cloud account yet. It can also help maintain an existing site.

## Start from an idea

After installing the skill, say:

> Use `$web-dev-pilot` to help me build a personal homepage. I have no repository and don't know how to code. Ask me only the questions needed, make a working first version, show me a preview, then guide me through publishing it.

The skill helps define the audience, pages, essential features, and visual direction before choosing an implementation. It can then create a project, help set up source control and hosting, and verify the published site. Steps that require the user's own sign-in, identity verification, or purchase are explained clearly.

For an existing project, say:

> Use `$web-dev-pilot` to update my website repository at [path or URL]. Implement [goal], verify it, and show me a preview before publishing.

## Install

Download this repository as a ZIP and place the extracted folder in a skills directory supported by your AI client. See [安装与使用.md](安装与使用.md) for Codex instructions, or run this from the extracted folder:

```powershell
python scripts/install.py --skills-dir "$env:USERPROFILE\.codex\skills"
```

Refresh the skill list or restart the client, then invoke `$web-dev-pilot`. The installer does not overwrite an existing installation.

## Package contents

- `SKILL.md`: workflow and instructions for the AI assistant.
- `references/`: greenfield planning, development, regressions, external services, and releases.
- `scripts/`: read-only project inventory, task checkpoints, HTTP checks, installation, and offline tests.
- `assets/`: project brief, acceptance and handoff templates, and sample content.

Python 3.10+ is required. Scripts use only the Python standard library. Run `python scripts/test_tools.py` for offline checks.

