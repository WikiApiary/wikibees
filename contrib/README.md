# Running the bots on a server

The bots are a git checkout plus a virtualenv, run from cron as an
unprivileged user. Nothing here needs root once it is set up, and the bot user
must not be able to write to the checkout — otherwise a bug in a crawled wiki
can persist code that the next cron run executes.

Paths used below:

|Path                      |Owner                     |Purpose                                |
|--------------------------|--------------------------|---------------------------------------|
|`/srv/wikibees`           |`root:wikidev`            |git checkout, read-only to the bot user|
|`/srv/wikibees/.venv`     |`root:wikidev`            |interpreter, read-only to the bot user |
|`/etc/wikibees/apiary.cfg`|`root:wikibees` `0640`    |credentials, outside the checkout      |
|`/var/log/wikibees`       |`wikibees:adm` `2750`     |cron output                            |
|`/run/wikibees`           |`wikibees:wikibees` `0775`|Dead Bee PID lock (tmpfiles)           |

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

# 3. code is admin-owned and group-writable, not bot-writable.
#    Run this ONLY after step 1: it makes every file in the checkout
#    world-readable, so the tree-local apiary.cfg must be gone first.
sudo rm /srv/wikibees/bumble-bee/apiary.cfg
sudo chown -R root:wikidev /srv/wikibees
sudo find /srv/wikibees -type d -exec chmod 2775 {} +
sudo find /srv/wikibees -type f -perm -u+x -exec chmod 775 {} +
sudo find /srv/wikibees -type f ! -perm -u+x -exec chmod 664 {} +

# 4. schedule
sudo install -o root -g root -m 0644 contrib/cron.d-wikibees /etc/cron.d/wikibees

# 5. log rotation (cron appends forever)
sudo install -o root -g root -m 0644 \
     contrib/logrotate-wikibees /etc/logrotate.d/wikibees
sudo /usr/sbin/logrotate --debug /etc/logrotate.d/wikibees
```

> **If you already ran step 3 with the tree-local config still present**, it is
> now `root:wikidev 0664` — world-readable credentials. Delete it:
>
> ```bash
> sudo rm /srv/wikibees/bumble-bee/apiary.cfg
> ```
>
> The password should also be rotated, since it sat readable for the window
> between the two steps.

After step 1 the config of record is `/etc/wikibees/apiary.cfg`, so manual
runs need `--config /etc/wikibees/apiary.cfg` — the cron entries already pass
it, and a manual run without it now fails loudly instead of silently reading a
stale tree-local copy.

Deploys are then a plain `git pull` by anyone in `wikidev`: no sudo, because
the checkout and `.git` are group-writable. Only installing cron or touching
`/etc/wikibees` needs root.

## Log rotation

`contrib/logrotate-wikibees` is the stanza of record, installed in step 5.
It must keep `copytruncate`: cron appends as `wikibees`, and without it
logrotate would rename the live log and create a root-owned replacement that
cron cannot write to. Verify a fresh install with a forced rotation of a
scratch file — the truncated file should stay zero bytes and stay
`wikibees:adm`:

```bash
cat <<'EOF' | sudo tee /tmp/lot.conf >/dev/null
/var/log/wikibees/rotatetest.log {
    weekly
    rotate 8
    compress
    missingok
    notifempty
    copytruncate
}
EOF
sudo -u wikibees sh -c 'head -c 200000 /dev/urandom | base64 > /var/log/wikibees/rotatetest.log'
sudo /usr/sbin/logrotate --force /tmp/lot.conf
sudo ls -l /var/log/wikibees/rotatetest.log*
sudo rm /var/log/wikibees/rotatetest.log*
```

A pre-existing `/etc/logrotate.d/wikibees` left over from the old
`/srv/wikibees/log` layout should be replaced wholesale rather than appended
to; an orphaned stanza without `missingok` makes the nightly run report
`stat` errors once the old directory is removed.

## Retired

The root `crontab` file in this repository is the old upstream schedule (hourly
segments, `~/wikibots` paths, plus a scratch block of alternatives). Production
has not used it since the move to `scripts`; `contrib/cron.d-wikibees` is the
schedule of record.
