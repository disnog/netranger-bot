# DisNOG V2 Project: netranger-bot

## GitHub Project Fields

| Field | Value |
| --- | --- |
| Project | DisNOG V2 |
| Repository | disnog/netranger-bot |
| Branch | v2dev |
| Track | Discord bot |
| Status | Ready for integration verification |
| Priority | P0 |
| Depends on | disnog/netranger-db v2dev, migrated MariaDB schema, Discord bot intents |
| Enables | Slash-command bot operations and member role restoration |

## Item Summary

Modernize the Discord bot from prefix commands and direct MongoDB access to discord.py 2.x slash commands backed by the shared MariaDB `netranger-db` package.

## Feature Differences From main

| Area | main | v2dev | Documentation |
| --- | --- | --- | --- |
| Command model | Prefix commands such as `$myinfo`, `$accept`, `$role org set` | Slash commands such as `/myinfo`, `/sendkey`, `/orgset` | `README.md`, `MIGRATEDB.md` |
| Join acceptance | Bot challenge question in Discord | Web `/join` flow grants accepted role before/while joining | `README.md`, `MIGRATEDB.md` |
| `!eggs` path | `$accept eggs` persistent role | Removed, no replacement path | `README.md`, `MIGRATEDB.md` |
| Database | Direct MongoDB helper | Shared `netranger-db` MariaDB package | `README.md`, `MIGRATEDB.md` |
| Member sync | Startup overwrites current members from Discord roles | Startup and `/syncdb` replace current members from Discord roles | `README.md`, `MIGRATEDB.md` |
| Returning users | Restores Member/eggs behavior | Restores mapped permanent roles; Member gets number message, periphery/recruiter get welcome-back message | `README.md`, `MIGRATEDB.md` |
| Tests/CI | Minimal/no branch coverage | Unit tests, lint, Docker build workflow | `.github/workflows/ci.yml` |

## Migration Path

1. Complete `netranger-db` migration and verify guild role/channel mappings.
2. Enable Discord Server Members Intent and Message Content Intent.
3. Re-invite or update the bot with `bot applications.commands` scope.
4. Configure `TOKEN`, `GUILD_ID`, `DB_*`, channel names, role names, and optional SMTP/Fernet settings.
5. Deploy `netranger-bot` from `v2dev`.
6. Confirm slash commands sync to the configured guild.
7. Run `/syncdb` once after deployment.
8. Verify `/myinfo`, `/ipcalc`, `/sendkey`, `/orgset`, `/lookup`, and returning-member behavior.

## Acceptance Criteria

- Bot starts, connects to MariaDB, loads cogs, and syncs slash commands.
- Startup sync preserves current Discord role state for current members.
- Returning Member users keep their member number.
- Returning periphery/recruiter users do not get sent back through `/join`.
- Org verification commands are gated to accepted users.
- Docker image builds successfully.
- `pytest` and `ruff check .` pass.

## Audit Notes

- Fixed during audit: Dockerfile now copies package code before `pip install .`.
- Fixed during audit: returning periphery/recruiter users are welcomed back instead of being treated as unaccepted.
- Fixed during audit: startup sync now replaces stored permanent roles for current members to avoid stale role restoration.
