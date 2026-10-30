# Running the bots on a server

The bots are a git checkout plus a virtualenv, run from cron as an
unprivileged user. Nothing here needs root once it is set up, and the bot user
must not be able to write to the checkout — otherwise a bug in a crawled wiki
can persist code that the next cron run executes.

Paths used below:

| Path | Owner | Purpose |
|---|---|---|
| `/srv/wikibees` | `root:wikidev` | git checkout, read-only to the bot user |
| `/srv/wikibees/.venv` | `root:wikidev` | interpreter, read-only to the bot user |
| `/etc/wikibees/apiary.cfg` | `root:wikibees` `0640` | credentials, outside the checkout |
| `/var/log/wikibees` | `wikibees:adm` `2750` | cron output |
| `/run/wikibees` | `wikibees:wikibees` `0775` | Dead Bee PID lock (tmpfiles) |

## Install order

`contrib/cron.d-wikibees` points at `/etc/wikibees/apiary.cfg` and
`/var/log/wikibees`, so create those first; installing cron first means every
run dies on startup and, with an empty `MAILTO`, silently.

```bash
# 1. runtime state, outside the checkout
sudo install -d -o wikibees -g adm    -m 2750 /var/log/wikibees
sudo install -d -o root     -g wikibees -m 0750 /etc/wikibees
sudo install -o root -g wikibees -m 0640 \
     /srv/wikibees/bumble-bee/apiary.cfg /etc/wikibees/apiary.cfg

# 2. lock directory, recreated at boot
sudo install -o root -g root -m 0644 \
     contrib/tmpfiles-wikibees.conf /etc/tmpfiles.d/wikibees.conf
sudo systemd-tmpfiles --create /etc/tmpfiles.d/wikibees.conf

# 3. code is admin-owned and group-writable, not bot-writable
sudo chown -R root:wikidev /srv/wikibees/{.git,lib,bumble-bee,dead-bee,.venv}
sudo find /srv/wikibees -type d -exec chmod 2775 {} +
sudo find /srv/wikibees -type f -perm -u+x -exec chmod 775 {} +
sudo find /srv/wikibees -type f ! -perm -u+x -exec chmod 664 {} +

# 4. schedule
sudo install -o root -g root -m 0644 contrib/cron.d-wikibees /etc/cron.d/wikibees
```

Deploys are then a plain `git pull` by anyone in `wikidev`: no sudo, because
the checkout and `.git` are group-writable. Only installing cron or touching
`/etc/wikibees` needs root.

## Log rotation

Cron appends forever, so rotate `/var/log/wikibees/*.log` — weekly with
`copytruncate` is enough:

```
/var/log/wikibees/*.log {
    weekly
    rotate 8
    compress
    missingok
    notifempty
    copytruncate
}
```

## Retired

The root `crontab` file in this repository is the old upstream schedule (hourly
segments, `~/wikibots` paths, plus a scratch block of alternatives). Production
has not used it since the move to `scripts`; `contrib/cron.d-wikibees` is the
schedule of record.
