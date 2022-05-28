It seems that sometimes installing from git has weird side effects with upgrading?

If you're having issues -- try doing the following

I'll use my promnesia modules (at <https://github.com/seanbreckenridge/promnesia>) as an example.

Note: though the repository is `promnesia`, the module it installs is `promnesia_sean`. In python packages in general, its not necessary for the module name to match the repository (thats just where its hosted). To figure out what the name of the package is, use `python3 -m pip list`. For this HPI repository, it installs as `HPI-seanbreckenridge`, so its possible to differentiate between this and upstream HPI.

These are directions for installing a package as non-editable (into your python `site-packages`), though it covers uninstalling editable packages -- in case your path is misconfigured in some way. If you want to install as editable, see [reorder_editable](https://github.com/seanbreckenridge/reorder_editable) and the [install section](https://github.com/seanbreckenridge/HPI#install) of the README for issues you may run into, or see the [editable](#editable) section of this doc

Whenever there are directions to use `pip` to do something -- its safer to do `python3 -m pip` (unless you know exactly what youre doing with managing multiple python installs on your system). That makes sure the `pip` that is being used is the same version as when you use `python3`

Uninstall the package you're using:

```bash
python3 -m pip uninstall -y promnesia_sean
```

Make sure its actually uninstalled -- this should error:

```bash
$ python3 -c "import promnesia_sean"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'promnesia_sean'
```

Note: For `HPI` in particular (since its a namespace package), if you're trying to uninstall my modules but leaves `karlicoss`'s (the core) modules installed, `import my` won't error. Instead, try something like `import my.trakt.export`, since that would only appear in my modules.

If that still imports, you likely have files leftover in your site packages. To find that directory, you can use:

```bash
$ python3 -m site
sys.path = [
    '/home/sean',
    '/usr/lib/python310.zip',
    '/usr/lib/python3.10',
    '/usr/lib/python3.10/lib-dynload',
    '/home/sean/.local/lib/python3.10/site-packages',
    '/home/sean/Repos/my_feed/src',
    '/home/sean/Repos/albums',
    '/home/sean/Repos/mint/budget',
    '/home/sean/.config/seanb',
    '/home/sean/Repos/HPI-personal',
    '/home/sean/Repos/HPI',
    '/home/sean/Repos/HPI-karlicoss',
    '/home/sean/Repos/promnesia-fork/src',
    '/usr/lib/python3.10/site-packages',
]
USER_BASE: '/home/sean/.local' (exists)
USER_SITE: '/home/sean/.local/lib/python3.10/site-packages' (exists)
ENABLE_USER_SITE: True
```

That should let you which directories python is scanning for imports. Check any of the `site-packages` directories, for files like:

```
promnesia_sean
promnesia_sean-0.0.0.dist-info
```

and remove those (this is essentially a 'manually uninstall' of a broken package)

If you've previously installed this as editable, review your editable installs to make sure its still not there:

```bash
python3 -m pip install reorder_editable
python3 -m reorder_editable locate  # should show you where which editable installs are placing .egg-link files
python3 -m reorder_editable cat
```

Refer to the [reorder_editable](https://github.com/seanbreckenridge/reorder_editable) README for more info on that.

You should now be able to confirm it errors, like:

```bash
$ python3 -c "import promnesia_sean"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'promnesia_sean'
```

Now -- to install it again!

Instead of installing from git (since that can sometimes cache the result and run into other issues), clone it to some local directory:

```bash
git clone https://github.com/seanbreckenridge/promnesia ./promnesia_sean
```

Then, you can install it by pointing it at the directory with includes the `setup.py` file, like: `python3 -m pip install --user ./promnesia_sean`

You should now be able to confirm it imports properly:

```python3
python3 -c "import promnesia_sean"
```

### Editable

Alternatively, since you already have it locally, you can install it as editable:

```bash
python3 -m pip install --user -e ./promnesia_sean
```

That should modify your `sys.path` (run `python3 -m site`; and you'll see that directory appear on your path)

That has the added benefit that whenever you want to update `promnesia_sean`, you can just:

```bash
cd /path/to/promnesia_sean
git pull
```
