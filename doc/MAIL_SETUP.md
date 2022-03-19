This is a distillation of the steps described in [this issue](https://github.com/seanbreckenridge/HPI/issues/15)

There are two mail modules here -- `my.mail.imap` and `my.mail.mbox`. An [`mbox` file](https://docs.python.org/3/library/mailbox.html) is just a collection of email messages in a single text file

Remember to first run: `hpi module install my.mail.imap` to install the necessary dependencies

## my.mail.imap

Personally, I use `my.mail.imap`. To sync my mail, I use [`mutt-wizard`](https://github.com/LukeSmithxyz/mutt-wizard/), which saves to a bunch of individual files in `~/.local/share/mail`. -- updating every 5 minutes. As a visual comparison to any files you may be trying to parse, [this is what one of those files looks like](https://gist.github.com/seanbreckenridge/5a629efacd72e7c28de0930f7e3ed8cf)

There are, of course, hundreds of ways to save your mail locally. Lets take [the ImportTools thunderbird addonn](https://addons.thunderbird.net/en-US/thunderbird/addon/importexporttools-ng/) as an example (since its the one we did troubleshooting on in the [issue](https://github.com/seanbreckenridge/HPI/issues/15)):

To match the format `my.mail.imap` expects, use the `Plain Text Format`, and export it to a folder somewhere. Then, in your config file, setup the block to point it at that path:

```python
class mail:
    class imap:
        # path[s]/glob to the the mailboxes/IMAP files
        mailboxes = "~/Documents/ImportToolsExports/"
```

To verify its finding, your files, you can use `hpi query my.mail.imap.files -s` -- that'll print all the matches files

That may be fine to parse an archive, but you need to continuously create new archives/delete old ones.

Recently, ImportToolsExports has added support for periodic backups, but only in MBOX format. So --

## my.mail.mbox

In `Tools > ImportExportToolsNg > Options > Backup scheduling`, set the `Destination` and `Enable Frequency` to backup once per day, selecting `Just mail files`

You can force a backup with `Tools > ImportExportToolsNg > Backup`

Note: you can set the `Overwrite the mbox files with the same name in the destination directory` to overwrite your backup. Alternatively, since `my.config` is a python script, you can use some python in your `my.config` file to parse the timestamp from the exported filepath, only using the latest exports

---

If you use a different format and aren't able to figure out how to parse it, [create an issue](https://github.com/seanbreckenridge/HPI/issues/new)
