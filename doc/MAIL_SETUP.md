This is a distillation of the steps described in [this issue](https://github.com/seanbreckenridge/HPI/issues/15)

There are two mail modules here -- `my.mail.imap` and `my.mail.mbox`. An [`mbox` file](https://docs.python.org/3/library/mailbox.html) is just a collection of email messages in a single text file

Remember to first run: `hpi module install my.mail.imap` to install the necessary dependencies

## my.mail.imap

Personally, I use `my.mail.imap`. To sync my mail, I use [`mutt-wizard`](https://github.com/LukeSmithxyz/mutt-wizard/), which uses `mbsync` under the hood to saves a bunch of individual mail files in `~/.local/share/mail` -- updating every 5 minutes. As a visual comparison to any files you may be trying to parse, [this is what one of those files looks like](https://gist.github.com/seanbreckenridge/5a629efacd72e7c28de0930f7e3ed8cf)

There are, of course, hundreds of ways to save your mail locally. Lets take [the ImportTools thunderbird add-on](https://addons.thunderbird.net/en-US/thunderbird/addon/importexporttools-ng/) as an example (since its the one we did troubleshooting on in the [issue](https://github.com/seanbreckenridge/HPI/issues/15)):

To match the format `my.mail.imap` expects, select the folder you want to export, then use `Tools > ImportExportToolsNg > Export all messages in the Folder > Plain Text Format`, and export it to a folder somewhere. Then, in your config file, setup the block to point it at that path:

```python
class mail:
    class imap:
        # path[s]/glob to the the mailboxes/IMAP files
        # you could also just do something like:
        # mailboxes = "~/Documents/mbsync/*@*"
        # to match any files in that directory with '@' in them
        mailboxes = "~/Documents/ExportPlaintext/"
```

To verify its finding your files, you can use `hpi query my.mail.imap.files -s` -- that'll print all the matches files

That may be fine to parse an archive (a backup of some email you don't use anymore), but you need to continuously create new archives/delete old ones.

Recently, ImportToolsExports has added support for periodic backups, but only in MBOX format. So -->

## my.mail.mbox

In `Tools > ImportExportToolsNg > Options > Backup scheduling`, set the `Destination` and `Enable Frequency` to backup once per day, selecting `Just mail files`

You can force a backup with `Tools > ImportExportToolsNg > Backup`

Note: you can set the `Overwrite the mbox files with the same name in the destination directory` to overwrite your backup. Alternatively, since `my.config` is a python script, you can use some custom python in your `my.config` file to parse the timestamp from the exported filepath, only using the latest exports as the input to `mailboxes`. If you're overwriting the `mbox` files while HPI is trying to parse the files, HPI may fail.

Once you've exported, setup your configuration to point at the directory. Note that since this uses `my.mail.imap` to parse the messages, you may have to setup a basic config with no files so that module doesnt fail:

```python
class mail:

    class imap:
        # signifies no files
        mailboxes = ''

    class mbox:

        # paths/glob to the mbox directory -- searches recursively
        mailboxes = "~/Documents/mboxExport"

        # additional extensions to ignore
        exclude_extensions = (".sbd")
```

## Using my.mbox.all

You can also use both of these at the same time -- if you have some exported as individual text files and other accounts, setup a config like above, but specifying paths from both `imap` and `mbox`

Then -- you can just use the `my.mbox.all.mail` or `my.mbox.all.raw_mail` functions -- which return results from both

TODO: create my.mbox.all module

---

If you use a different format and aren't able to figure out how to parse it, [create an issue](https://github.com/seanbreckenridge/HPI/issues/new)
