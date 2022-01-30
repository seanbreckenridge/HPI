# 2022-01-30

Renamed some modules to allow for future extension, and less possibilities for conflicts with other related HPI modules under a particular company/service/source

For reference, [here is the current directory structure](https://github.com/seanbreckenridge/HPI/tree/eb425e653918d68eb9d41da29e791fe1ba554dc7/my) as of this commit

In particular, anything with a `gdpr`/`data_export`/`privacy_export` is named to be that, instead of globally squashing the namespace module to the single `modulename.py` file

Converting a single-file module to a namespace module [is always a breaking change](https://github.com/karlicoss/promnesia/pull/225#issuecomment-819773697), and though [one can do hacky traceback introspection](https://github.com/karlicoss/HPI/blob/master/my/reddit/__init__.py) (to possible delay the change from a non-namespace package to a namespace package, but if anyone else is using this code, its likely in the background through promnesia, so most likely situation is that they don't see that till I deprecate it anyways), but its only a temporary solution until the `__init__.py`/`module.py` file is eventually removed -- so better to do them all now instead of waiting till it becomes 'too late'

A user (or me) may want to write their own module with the same name, meaning they can't use both at the same time if mine is just `my.module_name.py`, since that means any other namespace packages installed with have their module before mine (see [reorder_editable](https://github.com/seanbreckenridge/reorder_editable)) for an explanation

The one motivating this change is `apple.py`, since the old `apple.py` was parsing the privacy export, but I wanted to add something to parse [`imessage`](https://github.com/seanbreckenridge/HPI/commit/e361ce8182d8be8b331875078ad17605d3f80a50) files. Someone else may want to add other `apple/file.py` files to parse other parts of apple/mac behaviour, but me having the single `apple.py` either means they have to have their repo before mine on their path (but doing so means they overwrite the current `apple.py` file, so they cant use that to gdpr export, even if they were trying to do something else entirely), or they have to rename their code to something like `my_apple/file.py` to create a new namespace module

Possible 'Exceptions' to this:

- For some files, if the possibility for conflict is low (I can't imagine anyone exporting data from the source in any other way, e.g., `ipython`, `project_euler`) or the name is so specific to the source that its not needed (e.g. `ttt`, `window_watcher`)
- For files where I can't imagine you'd want both mine and your/custom implementation the same time, e.g. if you override `bash`, `zsh` or `imap`, you're probably creating your own solution to parse that source, and don't need mine (If that's not the case, feel free to open an issue)
- For some of my modules, I've renamed them from what they do to their service/project names instead (`albums` to `nextalbums`; `money` to `mint`), so I'm not holding the generic name of some function when I don't really need to
