# takopi

🐙 *he just wants to help-pi*

telegram bridge for codex, claude code, opencode, pi. manage multiple projects and worktrees, stream progress, and resume sessions anywhere.

## features

- projects and worktrees: work on multiple repos/branches simultaneously, branches are git worktrees
- stateless resume: continue in chat or copy the resume line to pick up in terminal
- progress streaming: commands, tools, file changes, elapsed time
- parallel runs across agent sessions, per-agent-session queue
- works with telegram features like voice notes and scheduled messages
- file transfer: send files to the repo or fetch files/dirs back
- group chats and topics: map group topics to repo/branch contexts
- works with existing anthropic and openai subscriptions

## requirements

`uv` for installation (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

python 3.14+ (`uv python install 3.14`)

at least one engine on PATH: `codex`, `claude`, `opencode`, or `pi`

## install

```sh
uv tool install -U takopi
```

## setup

run `takopi` and follow the interactive prompts. it will help you create a bot token (via [@BotFather](https://t.me/BotFather)), capture your `chat_id` from the most recent message you send to the bot, and set a default engine.

to re-run onboarding (and overwrite config), use `takopi --onboard`.

run your agent cli once interactively in the repo to trust the directory.

see [`docs/user-guide.md`](docs/user-guide.md) for detailed configuration and usage.

## config

global config `~/.takopi/takopi.toml`

```toml
default_engine = "codex"
# optional: reload config changes without restarting
watch_config = true

# optional, defaults to "telegram"
transport = "telegram"

[transports.telegram]
bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
chat_id = 123456789
voice_transcription = true

[transports.telegram.files]
enabled = true
auto_put = true
allowed_user_ids = [123456789]

[transports.telegram.topics]
enabled = true

# Matrix transport (alternative to Telegram)
[transports.matrix]
homeserver = "https://matrix.org"
user_id = "@bot:matrix.org"
# Either access_token OR password required
access_token = "syt_..."
# password = "your_password"  # Alternative to access_token
device_id = "TAKOPI"  # Optional: stable device ID
room_ids = ["!roomid:matrix.org"]  # List of allowed room IDs
user_allowlist = ["@user:matrix.org"]  # Optional: restrict to specific users
voice_transcription = false  # Optional: enable voice message transcription
file_download = true  # Optional: enable file attachments
file_download_max_mb = 50  # Optional: max file size in MB
e2ee_enabled = true  # Optional: enable end-to-end encryption (requires matrix-nio[e2e])
crypto_store_path = "~/.takopi/matrix_crypto.db"  # Optional: E2EE key storage

[codex]
# optional: profile from ~/.codex/config.toml
profile = "takopi"
# optional: extra codex CLI args (exec flags are managed by Takopi)
# extra_args = ["-c", "notify=[]"]

[claude]
model = "sonnet"
# optional: defaults to ["Bash", "Read", "Edit", "Write"]
allowed_tools = ["Bash", "Read", "Edit", "Write", "WebSearch"]
dangerously_skip_permissions = false
# uses subscription by default, override to use api billing
use_api_billing = false

[opencode]
model = "claude-sonnet-4-20250514"

[pi]
model = "gpt-4.1"
provider = "openai"
# optional: additional CLI arguments
extra_args = ["--no-color"]
```

note: configs with top-level `bot_token` / `chat_id` are migrated to `[transports.telegram]` on startup.
note: `watch_config` reloads runtime settings (projects, engines, plugins). transport changes still require a restart.

## projects

register the current repo as a project alias:

```sh
takopi init z80
```

`takopi init` writes the repo root to `[projects.<alias>].path`. if you run it inside a git worktree, it resolves the main checkout and records that path instead of the worktree.

example:

```toml
default_project = "z80"

[projects.z80]
path = "~/dev/z80"
worktrees_dir = ".worktrees"
default_engine = "codex"
worktree_base = "master"
chat_id = -123456789
```

set `chat_id` to route messages from that chat to the project automatically.

note: the default `worktrees_dir` lives inside the repo, so `.worktrees/` will
show up as untracked unless you ignore it (add to `.gitignore` or
`.git/info/exclude`), or set `worktrees_dir` to a path outside the repo.

## usage

```sh
cd ~/dev/happy-gadgets
takopi
```

send a message to your bot. prefix with `/codex`, `/claude`, `/opencode`, or `/pi` to pick an engine. reply to continue a thread.

register a project with `takopi init happy-gadgets`, then target it from anywhere with `/happy-gadgets hard reset the timeline`.

mention a branch to run an agent in a dedicated worktree `/happy-gadgets @feat/memory-box freeze artifacts forever`.

see [`docs/user-guide.md`](docs/user-guide.md) for configuration, worktrees, topics, file transfer, and more.

## security

### matrix end-to-end encryption (E2EE)

when `e2ee_enabled = true` (default), takopi automatically trusts all devices in allowed rooms for seamless encrypted messaging. this provides convenience for bot use cases but has security implications:

**auto-trust behavior:**
- all devices in `room_ids` are automatically verified
- enables encrypted file downloads and message decryption
- devices are trusted on first sync, not requiring manual verification

**threat model:**
- **mitigated**: prevents passive eavesdropping by the homeserver
- **not mitigated**: active MITM if attacker adds rogue device to room before first sync

**recommendations:**
- use `user_allowlist` to restrict who can interact with the bot
- limit `room_ids` to rooms you control
- for strict security requirements, disable E2EE (`e2ee_enabled = false`) and use room-level encryption controls
- backup your crypto store (`crypto_store_path`) to preserve device trust across reinstalls

**requirements:**
- install E2EE support: `uv tool install takopi --with 'matrix-nio[e2e]'`
- or with uv: `uv pip install 'matrix-nio[e2e]'` in the takopi environment

## plugins

takopi supports entrypoint-based plugins for engines, transports, and commands.

see [`docs/plugins.md`](docs/plugins.md) and [`docs/public-api.md`](docs/public-api.md).

## development

see [`docs/specification.md`](docs/specification.md) and [`docs/developing.md`](docs/developing.md).

## community

[takopi dev](https://t.me/+jFvQTLE8m183MjBi) telegram group
