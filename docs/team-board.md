# A board for a team: sign in with GitHub

`tadu board --auth github` serves one workspace's board to a team. People sign in with their GitHub account, and each of them sees only the items of the workspace repositories they can read on GitHub. Nobody needs a printed URL or a token, and a private repository's items never reach someone who cannot read it.

This guide is for whoever runs the board. It covers:

- [How it works](#how-it-works)
- [Before you start](#before-you-start)
- [1. Register a GitHub App](#1-register-a-github-app)
- [2. Prepare the workspace](#2-prepare-the-workspace)
- [3. Run the board](#3-run-the-board)
- [4. Put it behind https](#4-put-it-behind-https)
  - [A subdomain or a domain of its own](#a-subdomain-or-a-domain-of-its-own)
  - [A subfolder of another site](#a-subfolder-of-another-site)
- [Rate limits](#rate-limits)
- [Repository ids: `tadu-workspace.github-ids.json`](#repository-ids-tadu-workspacegithub-idsjson)
- [Sessions: `tadu-workspace.sessions.json`](#sessions-tadu-workspacesessionsjson)
- [What people see](#what-people-see)
- [How much the board asks GitHub](#how-much-the-board-asks-github)
- [Changes are proposals](#changes-are-proposals)
- [Security model](#security-model)
- [Limits](#limits)
- [Troubleshooting](#troubleshooting)

## How it works

- **Items come from the server's checkouts, not from GitHub.** The board reads `TODO.md` (or `todo/`) in the checkouts listed in `tadu-workspace.local.toml`, exactly as `tadu board` always does. GitHub is asked only one question: which of the workspace's repositories can this person read?
- **Each workspace repository is matched to a GitHub repository** by its `remote`, and then by GitHub's numeric repository id, which the board writes down (see [Repository ids](#repository-ids-tadu-workspacegithub-idsjson)).
- **Access is checked with each person's own GitHub token.** Repositories they cannot read are removed before anything is scanned, so their items, names, projects, organizations and problems never reach that person's browser.
- **When in doubt, it hides.** A repository that cannot be checked, whose GitHub identity changed, or whose id cannot be recorded is hidden from everyone until the doubt is resolved.

## Before you start

You need:

- a machine that keeps the checkouts of every workspace repository, and keeps them up to date (the board shows what is checked out, not what is on GitHub; see [Keep the checkouts current](#keep-the-checkouts-current));
- an address the team can reach over https, and a reverse proxy in front of the board (Caddy or nginx). The address can be a subdomain (`https://tadu.example.com`), a domain of its own (`https://example-tadu.com`) or a subfolder of a site you already run (`https://example.com/tadu`); see [4. Put it behind https](#4-put-it-behind-https). The examples below use `https://board.example.com`;
- the right to create a GitHub App, and to install it on the organizations that own the repositories (an organization owner, or someone they allow).

The board needs Python 3.12 and tadu with its `github` extra (`pip install 'tadu[github]'` or `uv tool install 'tadu[github]'`), which brings the libraries that sign people in: [`cryptography`](https://cryptography.io), [`requests`](https://requests.readthedocs.io), [`requests-oauthlib`](https://requests-oauthlib.readthedocs.io) with `oauthlib`, and [Werkzeug](https://werkzeug.palletsprojects.com)'s cookie parser. Only `tadu board --auth github` loads them.

## 1. Register a GitHub App

A GitHub App is the recommended way to sign in. A board that only reads asks for no write access at all; a board started with `--allow write` needs the write permissions listed below, because it opens pull requests and issues for people (see [Changes are proposals](#changes-are-proposals)).

1. Go to the organization's **Settings → Developer settings → GitHub Apps → New GitHub App** (or your own account's settings, for personal repositories).
2. Fill in:
   - **GitHub App name**: anything, such as "Acme tadu board".
   - **Homepage URL**: the board's address, `https://board.example.com`.
   - **Callback URL**: the board's address followed by `/auth/callback`: `https://board.example.com/auth/callback`, or for a board in a subfolder `https://example.com/tadu/auth/callback`. It must be `--public-url` plus `/auth/callback` exactly.
   - **Expire user authorization tokens**: keep it checked. Tokens then last 8 hours, and the board renews them while people use it.
   - **Request user authorization (OAuth) during installation**: leave unchecked.
   - **Webhook**: uncheck **Active**. The board needs no webhook.
   - **Permissions**: for a read-only board, none beyond the default **Repository → Metadata: Read-only**, which GitHub adds by itself; leave every other permission at **No access**. For a board that proposes changes (`--allow write`), also set **Repository → Contents: Read and write**, **Pull requests: Read and write** and **Issues: Read and write**. A token GitHub gives a person holds the intersection of the App's permissions and the person's own rights, so the App never lets anyone do more than they could on GitHub.
   - **Where can this GitHub App be installed?**: **Only on this account** when everyone who signs in is a member of the account that owns the app. Anyone else, such as an outside collaborator, gets GitHub's "Page not found" when signing in, because GitHub lets only the owner's members authorize a private app. For them choose **Any account** (or later **Advanced → Make public**). That lets other accounts install the app on their own repositories, which gives the board nothing: it sees a repository only through the signed-in person's own token, and only when the repository is in the workspace.
3. Create the app, then on its page note the **Client ID** and click **Generate a new client secret**. Keep the secret somewhere safe: GitHub shows it once.
4. **Install App** on the organization (and on every other organization or account that owns workspace repositories). Choose **All repositories**, or select at least every repository the workspace lists.

With a GitHub App, a person sees a repository only when the app is installed on it **and** they can read it. A repository the app is not installed on is hidden from everyone, as if nobody could read it.

### Using an OAuth App instead

An OAuth App (**Settings → Developer settings → OAuth Apps → New OAuth App**, with the same **Authorization callback URL**) works too, but GitHub gives an OAuth App no read-only way to see private repositories. The board therefore asks for the `repo` scope, which also allows writing to every repository the person can write to, and those tokens sit in the board's memory. Prefer the GitHub App. If an organization restricts third-party (OAuth App) access, its private repositories stay hidden until an owner approves the app.

## 2. Prepare the workspace

Every repository the team should see needs a `remote` on `github.com`, in any of the forms `https://github.com/OWNER/NAME`, `git@github.com:OWNER/NAME.git` or `ssh://git@github.com/OWNER/NAME`. A repository without one, or on another forge, is shown to nobody, and the board says so when it starts.

Give each person their GitHub login, so that the person who signs in with it is `me`: My work, Waiting on me and the Needs a person counts are then theirs. A login matches regardless of case, and one login can belong to only one person. Without it, a person still sees the board, but not as anyone in particular.

Optionally pin a repository to its GitHub id with `github_id` (see [Repository ids](#repository-ids-tadu-workspacegithub-idsjson)). `gh api repos/OWNER/NAME --jq .id` prints it.

```toml
# tadu-workspace.toml
version = 1

[[repository]]
key = "shop"
remote = "https://github.com/acme/shop"
github_id = 123456789            # optional

[[repository]]
key = "vault"
remote = "git@github.com:acme/vault.git"

[[person]]
id = "ana"
name = "Ana"
github = "ana-acme"
```

`tadu-workspace.local.toml` on the server says where each checkout is, as usual. Its `me` and `editor_url` are not used by a board that signs people in: `me` comes from the login, and editor links are left out because they would point into the server's disk.

### Keep the checkouts current

The board reads the files of the checkouts as they are on the server, at every page load. To follow GitHub, update them on a schedule, for example with a systemd timer or cron job running `git -C /srv/checkouts/shop pull --ff-only` for each repository. The server's own git credentials (a machine user or deploy keys) need read access to every repository; that does not widen what anyone sees, since the board checks each person's own access.

## 3. Run the board

Put the client ID and secret in the environment, never on the command line, where any user of the machine could read them with `ps`:

```bash
export TADU_GITHUB_CLIENT_ID=Iv23liAbCdEf0123
export TADU_GITHUB_CLIENT_SECRET=...
tadu board --workspace /srv/team-workspace --auth github --port 8123 --public-url https://board.example.com
```

| Option | Meaning |
| --- | --- |
| `--auth github` | Sign people in with GitHub. The default, `token`, is the single-person board. |
| `--public-url URL` | The address people open: `http://` or `https://`, a host, and a path for a board in a subfolder (`https://example.com/tadu`). It gives the callback URL, decides whether cookies are `Secure` and which path they keep to, and its host is accepted in the `Host` header. Default: `http://HOST:PORT`. Only valid with `--auth github`. |
| `--host`, `--port` | Where the board listens; keep the default `127.0.0.1` behind a proxy, and give a fixed `--port`. |
| `--done-days` | How far back done and cancelled items show (default 14). |
| `--sign-in-limit LIMITS` | How often one address may start a sign-in (`/auth/login`), and come back from GitHub (`/auth/callback`), each: `10/minute` by default, as GitLab limits its sign-in paths; any `limits` notation such as `5/minute;50/hour`; `off` turns it off. See [Rate limits](#rate-limits). |
| `--proxy-hops N` | How many proxies in front of the board to trust for the client's address in `X-Forwarded-For` (default `0`: the header is ignored). Behind one reverse proxy, give `1`. |
| `--idle-timeout DURATION` | How long a session lasts without activity (inactivity) before it ends: `14d` by default, or any duration from `10m` to `365d` in days, hours and minutes, such as `8h`, `30m` or `1d12h`. An open page warns 5 minutes before the end. See [Sessions](#sessions-tadu-workspacesessionsjson). |

Every option but `--workspace` can live in the workspace's `tadu-workspace.local.toml` instead, under `[board]`, with `_` for `-`; a flag given on the command line still wins. The server's settings then sit beside its checkout paths, and the command shrinks to `tadu board --workspace /srv/team-workspace`:

```toml
# /srv/team-workspace/tadu-workspace.local.toml
version = 1

[paths]
shop = "/srv/checkouts/shop"
vault = "/srv/checkouts/vault"

[board]
auth = "github"
public_url = "https://board.example.com"   # or https://example.com/tadu
port = 8123
proxy_hops = 1
# sign_in_limit = "10/minute"
# idle_timeout = "8h"
```

Values are checked as the flags are, and a bad one stops the board with the file, table and key named. `--auth token` on the command line turns such a board into the single-person one for that run, dropping the file's `public_url`, `sign_in_limit`, `proxy_hops` and `idle_timeout`. The client ID and secret stay in the environment. A user config file (`~/.config/tadu/config.toml`, or `--config FILE`) takes the same `[board]` table, below the local file; `--no-config` ignores both. See the README's [Config file](https://github.com/syntopica/tadu/blob/main/README.md#config-file) section.

The board prints the public URL (`https://board.example.com/`) and, on standard error, one line per request and any warning (see [Troubleshooting](#troubleshooting)). It refuses to start (exit `2`) when the workspace does not load, when either variable is missing, when `--public-url` is given without `--auth github`, or when `tadu-workspace.github-ids.json` cannot be read.

Run one board process per workspace. Sessions are saved beside the workspace (see [Sessions](#sessions-tadu-workspacesessionsjson)), so restarting or redeploying the board keeps everyone signed in. A second process on the same workspace would not see sessions started after it read the file, so do not put several behind a load balancer.

A systemd unit, with the secret in a file only root and the service can read:

```ini
# /etc/systemd/system/tadu-board.service
[Unit]
Description=tadu board
After=network-online.target

[Service]
User=tadu
EnvironmentFile=/etc/tadu-board.env
ExecStart=/usr/local/bin/tadu board --workspace /srv/team-workspace --auth github --port 8123 --public-url https://board.example.com
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# /etc/tadu-board.env (chmod 600)
TADU_GITHUB_CLIENT_ID=Iv23liAbCdEf0123
TADU_GITHUB_CLIENT_SECRET=...
```

The `tadu` user needs to read the workspace and the checkouts, and to write `tadu-workspace.github-ids.json` and `tadu-workspace.sessions.json` in the workspace directory.

## 4. Put it behind https

The board speaks plain http on `127.0.0.1`; a reverse proxy terminates https and forwards to it. It answers only requests whose `Host` header is the public URL's host (with its port, if the URL has one) or the bound address, and `421` otherwise, so the proxy must forward the `Host` the browser sent: Caddy does by itself, nginx needs `proxy_set_header Host $host;` (`$http_host` when the public URL has a port).

The board can live at three kinds of address; `--public-url` says which.

| Where | `--public-url` | GitHub App callback URL | Cookies |
| --- | --- | --- | --- |
| A subdomain | `https://tadu.example.com` | `https://tadu.example.com/auth/callback` | `__Host-tadu_session`, `Path=/` |
| A domain of its own | `https://example-tadu.com` | `https://example-tadu.com/auth/callback` | `__Host-tadu_session`, `Path=/` |
| A subfolder | `https://example.com/tadu` | `https://example.com/tadu/auth/callback` | `__Secure-tadu_session`, `Path=/tadu/` |

Prefer a subdomain or a domain of its own: a browser keeps apart only different origins (scheme, host and port), and a subfolder shares its origin with every other page of the site (see [A subfolder of another site](#a-subfolder-of-another-site)).

Whichever you choose, run the board with `--proxy-hops 1`: Caddy and nginx both add the client's address to `X-Forwarded-For`, and the board then limits each person's address instead of the proxy's (it warns at start when it looks proxied and `--proxy-hops` is `0`).

### A subdomain or a domain of its own

Point the name's DNS record at the proxy's machine and forward everything to the board.

```bash
tadu board --workspace /srv/team-workspace --auth github --port 8123 --proxy-hops 1 \
    --public-url https://tadu.example.com
```

Caddy, which gets a certificate by itself and forwards the original `Host`:

```
tadu.example.com {
    reverse_proxy 127.0.0.1:8123
}
```

nginx:

```nginx
server {
    listen 443 ssl;
    server_name tadu.example.com;
    # ssl_certificate ...; ssl_certificate_key ...;

    location / {
        proxy_pass http://127.0.0.1:8123;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

A domain of its own is the same with its name (`example-tadu.com`) in place of `tadu.example.com`.

### A subfolder of another site

The board can share a host with other apps under a path of its own, such as `https://example.com/tadu`:

```bash
tadu board --workspace /srv/team-workspace --auth github --port 8123 --proxy-hops 1 \
    --public-url https://example.com/tadu
```

The proxy may forward the board's requests with the subfolder (`/tadu/api/cards`) or without it (`/api/cards`); the board understands both, so either style of configuration works. The page links to its scripts, stylesheet and data relatively, so it works wherever it is served; `https://example.com/tadu` without the slash is sent on to `https://example.com/tadu/`.

Caddy, taking the subfolder away (`handle_path`) next to the site's other routes:

```
example.com {
    redir /tadu /tadu/ 308
    handle_path /tadu/* {
        reverse_proxy 127.0.0.1:8123
    }
    handle {
        # the rest of the site
        reverse_proxy 127.0.0.1:3000
    }
}
```

nginx, taking the subfolder away (the `/` after the port in `proxy_pass` replaces `/tadu/`; nginx itself sends `/tadu` to `/tadu/`):

```nginx
server {
    listen 443 ssl;
    server_name example.com;
    # ssl_certificate ...; ssl_certificate_key ...;

    location /tadu/ {
        proxy_pass http://127.0.0.1:8123/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # location / { ... the rest of the site ... }
}
```

Keeping the subfolder works as well. In Caddy, `handle` instead of `handle_path`, and the board sends `/tadu` on to `/tadu/` itself:

```
example.com {
    @tadu path /tadu /tadu/*
    handle @tadu {
        reverse_proxy 127.0.0.1:8123
    }
    # handle { ... the rest of the site ... }
}
```

In nginx, `proxy_pass http://127.0.0.1:8123;`, with no path after the port.

The path is one or more plain names (letters, digits, `.`, `_`, `~`, `-`). Its first name cannot be `api` or `auth`, nor a file name of the page such as `app.js`: the board could not tell such a prefix from its own routes once a proxy had taken it away.

What a subfolder changes:

- **The cookies keep to the subfolder.** They have `Path=/tadu/`, so the site's other apps do not receive them, and are named `__Secure-tadu_session` and `__Secure-tadu_oauth_state`: browsers accept a `__Secure-` cookie only over https with `Secure`. The stronger `__Host-` prefix requires `Path=/`, which would send the session to every app of the host.
- **The rest of the site is trusted as much as the board.** A cookie's path is not a security boundary: a script on any page of `https://example.com` can fetch `https://example.com/tadu/api/cards`, and the browser sends the session cookie with it and lets the script read the answer, since it is the same origin; it can also set cookies for `/tadu/`. A site with other apps, user content or any script you would not trust with every private repository's items should give the board a subdomain or a domain of its own instead.

### Rate limits

Each address may start a sign-in (`GET /auth/login`) and come back from GitHub (`GET /auth/callback`) only so often: by default 10 times a minute each, the limit GitLab puts on its sign-in paths. A person signing in uses one of each, and sessions last while they are used, so the limit is far above what people need; it is there because every callback makes the board call GitHub's token endpoint, and each sign-in writes the sessions file.

- Beyond the limit the board answers `429 Too Many Requests` with a `Retry-After` header and a plain page: "Too many sign-in attempts from your address. Try again in N seconds." Refused requests are not counted, so waiting is enough.
- The window moves: it counts the requests of the last minute at every moment, so no burst fits at the edge between two minutes. The counting is the [`limits`](https://limits.readthedocs.io) library's, in memory; ended windows are forgotten.
- `--sign-in-limit` changes it, in the `limits` notation: `5/minute`, `20 per hour`, `10/minute;100/hour` (every limit must hold), or `off`. A limit of `0` is refused, since it would keep everyone out.
- The address is the connection's, unless `--proxy-hops N` says how many proxies in front to trust: then it is the N-th address from the right of `X-Forwarded-For`, read the way Werkzeug's ProxyFix reads it. Without it the header is ignored, since anyone can send one; with it, a client cannot choose its address either, since the trusted proxy appends the one it saw. A header with fewer entries, or one that is no address, leaves the connection's address.
- Nothing else is limited: the page, its scripts and `/api/cards` need a session, and signing out is cheap.


## Repository ids: `tadu-workspace.github-ids.json`

A repository's name on GitHub can change hands. When `acme/vault` is renamed to `acme/vault-v2`, GitHub keeps answering the old name with the renamed repository, until someone creates a new `acme/vault`. From then on the old name means the newcomer, and a board that trusted the name would show the private vault's items to everyone who can read the newcomer, which may be everyone.

So the board ties each workspace repository to GitHub's numeric repository id, which never changes and is never reused:

- **Learned once, kept on disk.** The first time someone who can read a repository loads the board, its id is written to `tadu-workspace.github-ids.json` in the workspace directory. The file is read when the board starts, so the tie survives restarts and redeploys as long as the workspace directory does.
- **Checked at every load.** When GitHub gives a repository's remote another id, the repository is hidden from everyone. People see an integrity notice that names nothing, and the board writes a warning to standard error naming the repository and the fix.
- **Renames keep working.** A renamed or transferred repository keeps its id, so it keeps showing under its old remote, and the board warns once that the remote should be updated. Do update it: that closes the window before someone takes the old name.
- **`github_id` overrides.** A `github_id` on the `[[repository]]` is the repository's id while it is set; the learned id is then ignored, and nothing is written for it.

The file looks like this, keys sorted so it reads well in a diff:

```json
{
  "version": 1,
  "github_ids": {
    "shop": 123456789,
    "vault": 987654321
  }
}
```

Keep it where the workspace lives: on the same volume in a container, and ideally committed with `tadu-workspace.toml`, so every machine that runs the board starts with the same ids. Then review changes to it like changes to the workspace file. Deleting it makes the board learn the ids again from the next answers, which reopens the first-sight gap below.

**The first-sight gap.** An id is learned from the first answer the board gets. A board that first sees a repository after its name was already taken over learns the newcomer's id. To rule that out for repositories that matter, set `github_id` on them.

**Resolving a hidden repository.** When the warning says a repository is hidden because its id changed:

1. Check on GitHub that the remote names the repository you mean (`gh api repos/OWNER/NAME --jq '.full_name, .id, .private'`).
2. If the remote is wrong (the repository was renamed and the old name taken), fix `remote` in `tadu-workspace.toml`.
3. If the repository really is new (deleted and created again, or you moved the workspace entry to another repository on purpose), set `github_id` to the id the warning names. It takes effect at the next page load; no restart is needed.

Failures keep repositories hidden. If the file cannot be read or is not in the shape above, `tadu board` refuses to start. If an id cannot be written (a read-only directory, a full disk, another board changing the file at that moment), that repository stays hidden, with a warning, until it can be written or a `github_id` is set. Two boards on the same workspace share the file safely: a board re-reads it before writing and never overwrites a change it did not see, and the first id written for a repository wins.

## Sessions: `tadu-workspace.sessions.json`

People stay signed in the way they do in most apps: a session ends after **14 days of inactivity** (the idle timeout), and every activity pushes that end back. Sessions are saved in `tadu-workspace.sessions.json` in the workspace directory and read when the board starts, so a restart or a redeploy signs nobody out.

**What counts as activity.** Loading the board (opening or reloading the page, or Reload), and acting on an open page: pressing a mouse button or a finger, typing a key, scrolling with a wheel or a finger. An open page reports that at its next check, within 30 seconds, so activity costs no request of its own. Moving the mouse alone is not activity, so a mouse nudged on a shared desk keeps nobody signed in; neither is a page left open, whose checks do not count. The end is pushed back, and the cookie sent again with it, at most once a day, or every tenth of a shorter idle timeout, so a session ends at most that much early, never late.

**A shorter idle timeout.** Where 14 days is too long (shared computers, stricter policies), `--idle-timeout` (or `idle_timeout` under `[board]`) sets it, from `10m` to `365d`: `8h` for a working day, `30m` for a kiosk. When it is shortened, a saved session with longer left to last ends at the restart, and the board says how many did.

**The warning.** 5 minutes before the idle timeout ends a session, an open board shows "You will be signed out in 4:59 for inactivity." counting down, with **Stay signed in** and **Sign out**. Stay signed in, or any activity on the page, answers it at once; activity in another tab of the board makes it go at the next check. Without an answer, the page leaves for the sign-in page when the session ends. A computer that slept past the end finds the sign-in page when it wakes.

**Renewing GitHub tokens.** A GitHub App's user tokens expire after 8 hours. When a request needs GitHub and the person's token expires within 5 minutes, the board renews it with its refresh token and saves the new pair; the person notices nothing. GitHub hands out a new refresh token each time and the old one stops working, so one request per session renews at a time, and the others use what it got. If GitHub cannot be reached to renew, nobody is signed out: the board shows what answers still fresh allow, with the "GitHub could not be reached" notice, and renews at the next load. An OAuth App's tokens never expire and need no renewing.

A session ends when:

- it goes 14 days (or `--idle-timeout`) without activity;
- the person signs out (on the server, every copy of the cookie with it);
- GitHub refuses to renew its token: the person revoked the app's authorization (**Settings → Applications → Authorized GitHub Apps**), or the refresh token expired, which GitHub lets happen after 6 months; a revoked authorization ends every session of that person within 5 minutes;
- the operator signs everyone out: stop the board, delete `tadu-workspace.sessions.json`, start the board. Deleting it while the board runs is not enough: the board still holds the sessions, and warns that it cannot save them.

The file is safe to lose and useless to steal:

- **No cookie.** A session is stored under an id derived from its cookie. The cookie itself (256 random bits) exists only in the person's browser, and the id cannot be turned back into it.
- **No token.** The whole session, with the person's GitHub access and refresh tokens, is encrypted with a key derived from their cookie, so only a request that presents the cookie can open it. The file, a backup of it or a copy of the whole disk holds no token anyone can use, and the board's memory holds none between requests either.
- **No edits.** The encryption is authenticated, and the login and end kept in the clear (so that ended sessions can be dropped without the cookie) must match the sealed ones. A record edited in the file, for instance to make a stolen session last longer, no longer opens.
- **What it does show.** The GitHub logins of the people signed in and when their sessions end.

The cryptography is PyCA's [`cryptography`](https://cryptography.io) library, not tadu's own: HKDF-SHA256 derives the session's id and its key from the cookie, and [Fernet](https://cryptography.io/en/latest/fernet/) (AES-128-CBC with HMAC-SHA256, authenticated) seals the session.

The file is created readable by the board's user only (mode `0600`). Keep it out of version control, next to `tadu-workspace.local.toml` in `.gitignore`; if it is committed by mistake, it gives away no session and no token, only who was signed in.

If the file cannot be read when the board starts, the board warns, starts without sessions (everyone signs in again) and replaces the file at the next sign-in. If it cannot be written, sessions keep working until the next restart, with a warning. The board writes the file only if it still holds what the board last wrote, so a second board on the same workspace never overwrites it.

## What people see

- **The sign-in page** at the board's address, with one button, Sign in with GitHub. GitHub asks them once to authorize the app; after that, signing in is a redirect.
- **The board**, as `tadu board` shows it, cut to the repositories they can read: projects keep only those repositories, organizations of no visible project are left out, and so are saved views that name a hidden project or organization. Cards have no editor link.
- **Their login and Sign out** at the foot of the sidebar (on a phone, under More). Signing out ends the session on the server, not only in the browser, and every other tab of the board in that browser goes to the sign-in page at once.
- **My work** is theirs when their `[[person]]` has their `github` login. Without it, My work asks them to have the login added.
- **Integrity notices** that never name a hidden repository:
  - "GitHub answered HTTP 403, so some repositories are hidden until Reload can check them" (or "GitHub could not be reached, ..."): GitHub rate-limited them, an organization enforces SAML single sign-on, or GitHub is down. Reload after a minute.
  - "a repository is hidden because the board cannot confirm it is still the same repository on GitHub; the board's operator has been told which": see [Repository ids](#repository-ids-tadu-workspacegithub-idsjson).
- **The sign-in page, in place of the board,** as soon as the page learns that the session ended: within 30 seconds on a visible page (it checks), at once when a hidden tab is shown again or when they sign out in another tab of the same browser, and at any load or Reload. A session ends after 14 days (or `--idle-timeout`) of inactivity, when they sign out elsewhere, when GitHub refuses to renew their token, or when the operator signs everyone out. Nothing of the board stays on screen or in the page, which suits a shared computer, and Back does not bring it back; the view they were on opens again after they sign in. Restarting the board does not sign anyone out.
- **"The board cannot be reached", in place of the board,** when two checks in a row (5 seconds apart) get no answer from the board, such as while it restarts or when the network is gone: nothing of it is shown until it answers again, and then the page reloads by itself, back to the board or to the sign-in page.

Anyone with a GitHub account can sign in. Someone who can read none of the workspace's repositories sees an empty board; someone who can read only its public repositories sees only those.

## How much the board asks GitHub

The board asks GitHub only when someone loads the page or clicks Reload; the page's checks every 30 seconds ask GitHub nothing. Each question uses the person's own token, so it counts against their own rate limit (5,000 requests an hour), never a shared one.

- **One list instead of one request per repository.** `GET /user/repos` lists every repository the person reaches as owner, collaborator, or through an organization or team, 100 per page; pages after the first are fetched in parallel. Someone with access to a few hundred repositories costs two or three requests, however many repositories the workspace has.
- **Single checks only for what the list lacks.** A workspace repository missing from the list (typically a public repository of someone else) is asked about on its own with `GET /repos/OWNER/NAME`, 8 at a time. When the first page says the list is longer than 10 pages (1,000 repositories), the rest is not read, and every workspace repository is asked about on its own, which is then cheaper.
- **Nothing unchanged costs anything.** Every request carries the ETag of the previous answer; GitHub answers something unchanged with `304 Not Modified`, which does not count against the rate limit. GitHub sends no ETag with a 404, so "cannot read" answers always cost a request.
- **Answers are reused** per session: every tab of one browser session shares them, a renewed token carries on with them, and loads that arrive together wait for one refresh. Another device or a new sign-in asks again.

| Answer | Trusted for | So |
| --- | --- | --- |
| The repository list, and "can read" | 5 minutes | losing access on GitHub hides a repository within 5 minutes; access given through an organization, team or collaboration shows within 5 minutes |
| "Cannot read", for a repository the list lacks | 1 hour | a public repository that someone may read without being in the list shows within an hour |
| A failure (rate limit, GitHub down) | 1 minute of leaving GitHub alone | what could not be checked stays hidden meanwhile |
| A GitHub App token | 8 hours | renewed when due, one `POST` to GitHub per 8 hours of use |
| A session | 14 days without activity (`--idle-timeout`) | each activity pushes the end back; a warning 5 minutes before; then the person signs in again |

In practice: someone who reaches a 100-repository workspace through their organization costs one or two requests every 5 minutes while they use the board, nearly all of them free 304s. A contractor who can read 5 of those 100 costs about 95 requests an hour, for the "cannot read" answers, which is well under their limit.

## Changes are proposals

A board with `--auth github` never writes the server's checkouts. When a person applies a change (add, mark, close, move and the rest; a Preview is only a dry run and never reaches GitHub), the board:

1. runs the change on a temporary copy of that one repository's backlog files, so the checkout stays byte-identical, and removes the copy afterwards;
2. compares the copy with the original and keeps the files that changed (a change that touches anything but backlog files is refused);
3. with the person's own token, opens a **proposal**: for someone who may push to the repository, one commit on a new branch `tadu/<operation>-<random>` and a pull request against the default branch; the default branch itself is never written (unless the repository sets [`proposals`](#merge-or-commit-at-once-proposals)). For someone who may not push, an **issue** that holds the operation, its arguments and a diff, and no branch.

The answer is `proposed: <url>`, and the card changes on the board only once the pull request is merged (and the checkout pulled) or the issue is handled. GitHub names the person as the author of everything, and holds them to their own rights: if GitHub refuses a step, the person gets a short error and nothing is left half made on the server.

The pull request is built from the repository as GitHub holds it, so **the server's checkout must match the target branch** (the default branch unless the repository sets [`branch`](#several-branches)). Before anything is created, the board compares the blobs of the backlog files on that branch with the checkout's; when they differ it answers HTTP 409 (`the repository changed since the board last read it; refresh and try again`) and creates nothing. Keep the checkouts current (see [Keep the checkouts current](#keep-the-checkouts-current)); a checkout on another branch or with local edits will refuse every proposal. Only repositories with a GitHub remote can receive a proposal.

### Merge or commit at once: `proposals`

A pull request to review is the default, and it is too heavy to move one's own task. Per repository, `tadu-workspace.toml` says how a change by **someone who may push** is applied:

```toml
[[repository]]
key = "shop"
remote = "https://github.com/acme/shop"
proposals = "merge"   # "pr" (default), "merge" or "direct"
```

- `pr`: a branch and a pull request to review, as above.
- `merge`: the same pull request, merged (squashed) at once with the person's token. If GitHub refuses the merge (a required review or check), the pull request stays open for review and the answer says so.
- `direct`: one commit on the default branch, made with the person's token and moved forward only (never forced). If GitHub refuses it (a protected branch), a pull request is opened instead and the answer says so.

Someone who may not push always gets an issue, in every mode, and GitHub's own rules (branch protection, required reviews) still bind the person. The answer starts with `merged: <url>`, `committed: <url>` or `proposed: <url>`. The card changes once the server's checkout is pulled, so in these two modes keep the checkouts very current: until then the next change to that repository answers 409 (the checkout no longer matches the default branch).

### Several branches

Proposals target the repository's GitHub default branch. When the backlog the team works from lives on another branch, such as `dev` in a `dev`/`main` split, the repository names it:

```toml
[[repository]]
key = "shop"
remote = "https://github.com/acme/shop"
branch = "dev"        # proposals, merges and commits target dev, not the default branch
```

- **One target per repository.** Every pull request has `branch` as its base, `merge` merges into it and `direct` commits on it. Feature branches are never targets: a proposal's own `tadu/<operation>-<random>` branch is the only one the board creates.
- **The board reads its checkout.** It shows whatever the server's checkout holds, so check it out on the target branch; a checkout on any other branch answers 409 to every change, because its backlog files differ from the target's.
- **Reaching the other branches is your own merge.** A change that lands on `dev` reaches `main` when you merge `dev` into `main`, as for code; tadu never writes a second branch. Task files merge cleanly, since each task is its own file.
- **The checkout does not pull itself.** In `merge` and `direct` modes the target branch moves on every change, so pull the checkout often (see [Keep the checkouts current](#keep-the-checkouts-current)); until it is pulled, the next change to that repository answers 409 and creates nothing.

## Security model

What is protected:

- A change is only ever proposed with the signed-in person's own token and rights; the board's server holds no credential that can write to a repository, and it writes the default branch only for a repository whose `proposals` is `direct` and a person GitHub lets push there.
- A private repository's items, key, project, organizations and scan problems reach only people who can read it on GitHub. Repositories they cannot read are not even scanned for them.
- A repository whose GitHub identity cannot be confirmed (see [Repository ids](#repository-ids-tadu-workspacegithub-idsjson)) is shown to nobody.
- A workspace that stops loading shows people a message that names nothing; the details go to standard error.
- Someone who can read none of the workspace's repositories (anyone with a GitHub account can sign in) sees an empty board: no repository, project, organization or saved view.
- Only a well-formed `owner/name` on github.com is ever asked about with a person's token; a remote with `..`, an encoded slash or characters GitHub does not allow in a name counts as no GitHub remote.

Sign-in:

- `/auth/login` sends the browser to GitHub with a random `state` and a PKCE challenge (S256), the state and the challenge's verifier kept in a 10-minute cookie; `/auth/callback` accepts only that state, so nobody can sign someone else in to their own account, and trades the code with that verifier, so a code that leaked (a log, the history, a screenshot) is worthless anywhere else. The cookie serves once: every answer of the callback deletes it. GitHub shows its account picker every time (`prompt=select_account`), so on a shared computer the next person does not end up signed in as whoever is still signed in to GitHub in that browser; signing out of the board does not sign out of GitHub, so there, sign out of GitHub too. The callback ignores any other parameter and always sends the person to the board's own page (`/`, or `/tadu/` in a subfolder).
- `requests-oauthlib` builds the authorize URL and its state, trades the code for tokens with the client secret, and renews them; `requests` makes every other call, and the token is traded for the login. The token is kept only sealed with a key that the person's session cookie gives (see [Sessions](#sessions-tadu-workspacesessionsjson)), in memory and on disk alike, and opened for the request that presents the cookie; it never reaches the page or a log. The board keeps no cookie, only a hash of it.
- No request of the board ever reaches a host other than the one it was sent to. GitHub's redirects (a renamed repository) are followed on GitHub's own origin only; a redirect anywhere else (any status, any form of `Location`, another port or scheme) is not followed, nothing is sent there, and the repository stays hidden with a notice. The token requests, whose body holds the client secret and refresh tokens, are held to the same rule. This is enforced in `requests`' own redirect hook and tested against a second server that must receive nothing.
- Credentials in `~/.netrc` are never used: `requests` would put them in place of a person's token (on every request without explicit credentials, and on every redirect), so on a server whose `.netrc` holds the operator's GitHub credentials, everyone would be checked as the operator. The board sends each token as an explicit credential and keeps it across a same-origin redirect.
- `requests-oauthlib` logs token answers at DEBUG level. tadu never turns that on; if you configure Python logging around the board, keep the `requests_oauthlib` and `oauthlib` loggers above DEBUG.

Cookies and sessions:

- The session cookie is a random value, `HttpOnly` and `SameSite=Lax`; behind https it is also `Secure` and named `__Host-tadu_session`, which browsers accept only from the board's own host, so a sibling subdomain cannot plant a session or a sign-in state. In a subfolder it is `__Secure-tadu_session` with the subfolder's path; the other pages of the same host are then as trusted as the board (see [A subfolder of another site](#a-subfolder-of-another-site)).
- Signing out, and signing in again in the same browser, end the previous session on the server and have GitHub revoke its token (`DELETE /applications/{client_id}/token`, as the app), so no copy of the token works anywhere after: this matters most for an OAuth App, whose tokens never expire and can write. A GitHub that cannot be reached does not stop a sign-out. One login holds at most 20 sessions; the oldest ends first.
- A copy of a session cookie works like the original until the session ends: at sign-out, after 14 days (or `--idle-timeout`) without activity, when the operator signs everyone out, or within 5 minutes of the person revoking the app on GitHub. A copy of the sessions file is no such copy: it opens no session. To cut off a stolen cookie, revoke the app on GitHub (**Settings → Applications → Authorized GitHub Apps**): that refuses its token even if the person signs in again meanwhile.

The page and the server:

- Without a session, `/` is the sign-in page and `/api/cards` answers `401`; the per-run token of the single-person board is not accepted. Scripts and the stylesheet hold no data and need no session.
- An open page checks every 30 seconds, while it is visible, that it may still show what it shows: `GET /api/session` answers `200` with the seconds left while the session lives, and `401` once it has ended. The check reads no backlog, asks GitHub nothing and does not push the session's end back, so a page left open does not keep a session alive; after activity on the page the check is a `POST`, which does. Passed checks are not logged.
- The only requests that are not GET are the POSTs that sign out and that report activity; every other method answers `405`.
- Only the board's own page may load the cards, check the session or sign out. `SameSite=Lax` keeps the cookie off requests from other sites, but not from other origins of the same site (a sibling subdomain, another port), so the board also refuses, with `403`, such a request whose `Sec-Fetch-Site` is not `same-origin` or whose `Origin` is not the board's: no sibling page can sign someone out, keep their session alive or make the board ask GitHub. (In a subfolder, the host's other pages are the same origin; see [A subfolder of another site](#a-subfolder-of-another-site).)
- Starting and finishing a sign-in is limited per address (10 a minute each by default, `--sign-in-limit`), so nobody can make the board hammer GitHub's token endpoint or its sessions file; see [Rate limits](#rate-limits).
- The `Host` check, the security headers (a Content-Security-Policy, `frame-ancestors 'none'`, `Cross-Origin-Opener-Policy` and `Cross-Origin-Resource-Policy: same-origin`, `Cache-Control: no-store`) and the escaping of item text are those of `tadu board`; behind https the board also sends `Strict-Transport-Security`. The request log holds the method, the path without its query string and the status, characters that are not printable escaped: never a code, a state or a cookie. A client that drops its connection leaves no traceback in the log.

## Limits

- **github.com only.** GitHub Enterprise Server and GitHub Enterprise Cloud with data residency (`*.ghe.com`) are not supported; their repositories count as having no GitHub remote.
- **A subfolder shares its origin.** A board at `https://example.com/tadu` is only as safe as every other page of `https://example.com`; see [A subfolder of another site](#a-subfolder-of-another-site).
- **One process.** Several processes cannot share the load: each would miss the sessions the others start.
- **Up to 5 minutes late.** Someone who loses access on GitHub can still see the repository's items for up to 5 minutes; someone given access to a public repository outside their list waits up to an hour.
- **Fails closed.** When GitHub is down or rate-limits someone, their repositories disappear from the board once the answers age, until GitHub answers again.
- **Shows the server's checkout.** Items are what the server's checkout holds: possibly behind GitHub until it is pulled, and including changes that are not pushed, visible to everyone who can read the repository.
- **First-sight gap.** A board that first sees a repository after its name was taken over learns the wrong id; set `github_id` for repositories where that matters, and keep the ids file.
- **Rate limits are per address and in memory.** A restart starts them over, and an office behind one address shares one limit (10 sign-ins a minute by default: raise `--sign-in-limit` for a very large one). Behind a proxy they need `--proxy-hops`.
- **Anyone can sign in.** There is no allow-list of people or organizations; a stranger sees only the workspace's public repositories, whose files are public anyway, with their projects and the saved views, and someone who reads none of them sees an empty board.
- **`me` follows the login.** If a login is given up and taken by someone else, the new owner becomes `me` for the person configured with it. That changes only which items are called theirs, never what they may see.
- **The OAuth App scope.** An OAuth App's `repo` scope allows writing; the board never writes to GitHub, and it keeps those tokens only sealed by each person's cookie, but whoever holds a cookie holds that access through the board's GitHub checks.
- **Sessions last while they are used.** Someone who keeps using the board stays signed in until GitHub stops renewing their token (6 months after they authorized the app; never for an OAuth App, whose tokens do not expire); a stolen cookie lasts as long, unless the person signs out or revokes the app. There is no absolute session lifetime.
- **Saved views are per browser.** Saved views, starred and recent scopes are kept in each browser's storage, as on the single-person board.

## Troubleshooting

Messages the board writes to standard error:

| Message | What to do |
| --- | --- |
| `--auth github needs the GitHub app's client ID in TADU_GITHUB_CLIENT_ID and its secret in TADU_GITHUB_CLIENT_SECRET` | Set both variables in the board's environment. |
| `--public-url needs --auth github` | Add `--auth github`, or drop `--public-url` (either may come from `[board]` in a config file: `auth = "github"`). |
| `tadu: …/tadu-workspace.local.toml: [board] KEY: …` | A `[board]` setting is not one the flag would accept, or not a board option; the message says which. |
| `argument --public-url: must be http:// or https://, a host and maybe a path, …` | Give the address people open, such as `https://tadu.example.com` or `https://example.com/tadu`: no query, no `#`, no user name, and a path of plain names whose first is not `api`, `auth` or a file name such as `app.js`. |
| `…/tadu-workspace.github-ids.json: …` (at start) | The ids file is damaged. Restore it from version control or a backup; deleting it makes the board learn the ids again. |
| `warning: repository KEY has no github.com remote, so nobody who signs in sees it` | Give the repository its GitHub `remote`, or ignore it if it should stay hidden. |
| `warning: listening on HOST; only requests whose Host header is … are served` | Expected when `--host` is not `127.0.0.1`; make sure the proxy sends one of those `Host` values. |
| `warning: …/tadu-workspace.sessions.json: …; everyone signs in again` (at start) | The sessions file is damaged, or from a tadu before sessions were renewed (version 1). The board starts without sessions and replaces the file at the next sign-in; nothing else is needed. |
| `warning: cannot save sessions (…); they last until the board restarts` | Let the board's user write to the workspace directory; until then, a restart signs everyone out. The warning comes once per run of failures. |
| `warning: the board looks to be behind a proxy, so every sign-in counts as coming from it and shares one limit: …` | Make the proxy send `X-Forwarded-For` (Caddy does; nginx needs `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`) and give `--proxy-hops 1`. |
| `--sign-in-limit needs --auth github`, `--proxy-hops needs --auth github` | They only concern signing in with GitHub; add `--auth github` or drop them. |
| `warning: --proxy-hops trusts X-Forwarded-For, but the board listens on HOST, …` | Behind a proxy, keep `--host` at `127.0.0.1`: a client that reaches the board directly could name any address in `X-Forwarded-For` and so escape the sign-in limit. |
| `warning: the session cookie travels unencrypted; serve the board over https` | Put the board behind https and give an `https://` `--public-url`. |
| `warning: OWNER/NAME is now OWNER/NEW on GitHub; update the remote of its workspace repository` | Change the repository's `remote` to the new name. |
| `warning: repository KEY: OWNER/NAME on GitHub is repository id N, not M (…); it is hidden from everyone. …` | See [Resolving a hidden repository](#repository-ids-tadu-workspacegithub-idsjson). |
| `warning: repository KEY: cannot record its GitHub id in tadu-workspace.github-ids.json (…); …` | Let the board's user write to the workspace directory, or set the `github_id` the warning names. |
| `tadu board: <a workspace problem>` (while running) | `tadu-workspace.toml` no longer loads; fix it (`tadu doctor --workspace DIR` shows the same problem). |

What people may tell you:

| They see | Why |
| --- | --- |
| "Too many sign-in attempts from your address. Try again in N seconds." | Their address started or finished more sign-ins than `--sign-in-limit` allows; if many people share one address (an office, or a proxy without `--proxy-hops`), raise the limit or set `--proxy-hops`. |
| "Sign-in failed: the sign-in link expired or was opened in another browser." | They waited more than 10 minutes at GitHub, or opened a sign-in link someone sent them. Opening the board again starts over. |
| "Sign-in failed: GitHub did not sign you in." | They declined the authorization at GitHub. |
| "Sign-in failed: GitHub did not confirm who you are. Try again." | The code expired or was used twice, or the client secret or callback URL is wrong: check that `--public-url` plus `/auth/callback` is the app's callback URL. |
| An empty board | The app is not installed on the repositories, they cannot read any of them, or the remotes are missing. |
| A repository missing for one person | They cannot read it on GitHub, the app is not installed on it, or its organization enforces SAML single sign-on and they have no active single sign-on session: they authenticate with the organization on GitHub, then sign in to the board again. |
| "Who are you?" under My work | Their `[[person]]` has no `github` login, or another one. |
