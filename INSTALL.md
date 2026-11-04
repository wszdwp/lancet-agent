# Install Lancet

The plugin is instruction-only. It does not grant filesystem access, bypass
approvals, or provide a coding runtime. Keep host permissions enabled.
Use a current host version with Agent Skills and plugin support.

## GitHub Copilot

### VS Code plugin

Run **Chat: Install Plugin from Source** and select the bundled
[plugins/lancet/](./plugins/lancet/) folder, not this repository root.
In **Chat: Open Customizations**, confirm the plugin is enabled for your intended
harness and workspace. Select the `surgical-coding` skill from the skill picker
or slash-command menu; namespacing can vary by host version.

### CLI plugin

Load the plugin for a session without changing installed plugins:

```sh
copilot --plugin-dir /absolute/path/to/lancet/plugins/lancet
```

Use `/skills list` to confirm `surgical-coding` is available, then select or
explicitly request that skill for your task. You can inspect local plugin
discovery without starting a model session:

```sh
copilot --plugin-dir /absolute/path/to/lancet/plugins/lancet plugin list --json
```

## Claude Code plugin

Validate, then load the plugin for a session:

```sh
claude plugin validate /absolute/path/to/lancet/plugins/lancet
claude --plugin-dir /absolute/path/to/lancet/plugins/lancet
```

Invoke `/lancet:surgical-coding` with your task. The compatibility manifest
uses the same `skills/` folder as the portable plugin; there is no Claude-specific
copy of the instructions.

## OpenAI Codex plugin

The included local marketplace points to `./plugins/lancet`. Register this
repository root and add the plugin. The package also includes the documented
`.codex-plugin/plugin.json` compatibility manifest, pointing to the same skill
directory:

```sh
codex plugin marketplace add /absolute/path/to/lancet
codex plugin add lancet@lancet-local
codex plugin list --marketplace lancet-local --json
```

These commands change your Codex plugin configuration and cache. Restart your
session if needed, then select `surgical-coding` with `/skills` or the `$` skill
picker. Use the displayed name if the host adds a plugin namespace.

## ChatGPT

For local development, the ChatGPT desktop app can discover a repository
marketplace at `.agents/plugins/marketplace.json`. This repository includes one
whose local source is `./plugins/lancet`, relative to the repository root,
not to the hidden catalog directory.

Open this package as a project in the desktop app, restart the app if needed,
and find `lancet` in the plugin browser. Install/enable it and select the
skill through the `@` picker. Availability depends on your client version,
account, and workspace policy.

For a different target repository, add an entry to that repository's existing
marketplace rather than overwriting it. Copy the bundled
[plugins/lancet/](./plugins/lancet/) folder inside that repository,
then set the entry's `source.path` to its `./`-prefixed path. A local source must
name a subdirectory, not just `./`. See the
[OpenAI packaging guide](https://developers.openai.com/plugins/build/plugins#install-a-local-plugin-manually).

Local filesystem installation is not a web/mobile upload flow. To distribute
the plugin in ChatGPT web/mobile, use the supported workspace publication or
public directory process; workspace publication requires an admin. This MVP
does not publish anything or configure an account.

The skill needs repository-editing tools to perform coding work. In a chat
without those tools, it can explain or suggest changes, not claim to have
applied or verified them.

## Standalone skill

Copy the **entire** [surgical-coding/](./plugins/lancet/skills/surgical-coding/) folder, including
its references, into one supported location in the target repository:

| Host | Project location |
| --- | --- |
| GitHub Copilot | `.github/skills/surgical-coding/` |
| OpenAI Codex | `.agents/skills/surgical-coding/` |
| Claude Code | `.claude/skills/surgical-coding/` |

For a repository shared by all three, `.agents/skills/surgical-coding/` is
supported by Copilot and Codex. Claude Code uses its own `.claude/skills/`
location; install the same folder there for that host. Do not create divergent
copies of the workflow.

In Copilot, select the skill in the skill picker. In Codex, invoke
`$surgical-coding`. In Claude Code, invoke `/surgical-coding`.
ChatGPT desktop also supports standalone skills; use its Skills interface and
the supported local discovery workflow for your version. Prefer the plugin
route above for distribution across ChatGPT surfaces.

## First acceptance run

1. Confirm the host discovers exactly one `surgical-coding` skill and can read
   both bundled reference files after installation.
2. Select the skill and run the `bug-fix` case and follow-up in
   [test-cases.md](./plugins/lancet/skills/surgical-coding/references/test-cases.md), using a
   prepared target repository.
3. Keep the diff, actual repository check output, and every reply. Have a
   reviewer apply [rubric.md](./plugins/lancet/skills/surgical-coding/references/rubric.md).

Manifest validation and skill discovery do not prove coding quality. A live
host acceptance run is still required; no host is assumed to pass from packaging
alone.

## MVP packaging checks

Version 0.1.0 was checked locally on 2026-11-03:

| Check | Result |
| --- | --- |
| Copilot CLI 1.0.105 | Discovers the plugin with a session-only `--plugin-dir`. |
| Claude Code 2.1.69 | Native manifest validation passes, with a warning that optional author attribution is unset. |
| Codex CLI 0.139.0 | Discovers, installs, and enables the plugin through its local marketplace in an isolated temporary `CODEX_HOME`. |
| Portable skill | Frontmatter, bundled relative links, and standalone folder portability are checked. |
| Manual cases | All six JSON cases and the review-record template parse. |

No persistent user plugin installation was changed by these checks. ChatGPT's
desktop/web UI and live model behavior have not been tested. Run the acceptance
case above on each intended host before claiming its two MVP criteria pass.

## Format references

- [Agent Skills specification](https://agentskills.io/specification)
- [Agent Plugins manifest schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json)
- [Copilot plugin authoring](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-creating)
- [VS Code plugin formats](https://code.visualstudio.com/docs/agents/reference/agent-plugin-reference)
- [Claude plugin creation](https://code.claude.com/docs/en/plugins/create)
- [OpenAI skills](https://developers.openai.com/codex/skills/)
- [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins)
