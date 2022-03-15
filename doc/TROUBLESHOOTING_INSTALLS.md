It seems that sometimes installing from git has weird side effects with upgrading?

If you're having issues -- try doing the following

- Uninstall any package you're using, I'll use [my promnesia modules](https://github.com/seanbreckenridge/promnesia) as an example

```
python3 -m pip uninstall -y promnesia_sean
```

- Make sure its actually uninstalled -- this should error:

```
$ python3 -c "import promnesia_sean"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'promnesia_sean'
```

Clone the repository locally instead, and install it:

```
git clone https://github.com/seanbreckenridge/promnesia ./promnesia_sean
cd ./promnesia_sean
pip install .
```
