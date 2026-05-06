# Backup Automation & Offloading

This document provides scripts and strategies for automating the W7-Base backup workflow and offloading data to external storage.

## 1. Local Manual Backups
Use the CLI to create timestamped tarballs:
```bash
w7 backup @dev/myapp  # Creates a tarball of myapp's data/ folder
```

## 2. Automated Cron Job (Host-Level)
To automate backups of all `@ops` and `@prod` stacks, add the following to your `crontab`:

```bash
# Every day at 3 AM: Backup all @ops stacks
0 3 * * * cd ~/w7-localbase && . .shared/w7.sh && w7 backup all @ops

# Every Sunday at 4 AM: Full platform backup
0 4 * * 7 cd ~/w7-localbase && . .shared/w7.sh && w7 backup all
```

## 3. Offloading to External Storage (rsync)
After backups are created, use `rsync` to mirror the `./backups` directory to a NAS or external drive.

```bash
#!/bin/bash
# Mirror local backups to an external mount point
BACKUP_DIR="~/w7-localbase/backups"
REMOTE_DEST="/mnt/nas/w7-backups"

rsync -avz --delete "$BACKUP_DIR/" "$REMOTE_DEST/"
```

## 4. Offloading to S3/Cloud (rclone)
If you use `rclone`, you can sync your local backups to encrypted cloud storage.

```bash
#!/bin/bash
# Sync local backups to an S3 bucket
rclone sync ~/w7-localbase/backups s3-remote:my-w7-backups
```

## 5. Pruning Old Backups
To prevent the `./backups` directory from filling up the disk, use a simple `find` command to delete files older than 30 days.

```bash
#!/bin/bash
# Delete backups older than 30 days
find ~/w7-localbase/backups -type f -mtime +30 -name "*.tar.gz" -exec rm {} \;
```

## 6. Verification of Backup Integrity
Always test your backups! Periodically restore a stack tarball to the `@lab` zone to ensure the data is complete and the application boots.

```bash
# Example restoration test
tar -xzf backups/myapp_20260101.tar.gz -C @lab/restore-test/data
cd @lab/restore-test && w7 up
```
