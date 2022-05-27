**TLDR**: I'm using `HPI`(Human Programming Interface) package as a means of unifying, accessing and interacting with all of my personal data.

It's a Python library (named `my`), a collection of modules for:

- social networks: posts, comments, favorites, searches
- shell/program histories (zsh, bash, python, mpv, firefox)
- programming (github/commits)
- instant messaging
- media histories (movies, TV shows, music, video game achievements/history); see <https://sean.fish/feed/>

[_Why?_](https://github.com/karlicoss/HPI#why)

This is built on top of [`karlicoss/HPI`](https://github.com/karlicoss/HPI). It started out as a fork, but has since been converted to my own set of modules. This is installed alongside the upstream repository (meaning _you can use both modules from upstream and here simultaneously_), see [#install](#install)

### My Modules

- `my.zsh` and `my.bash`, access to my shell history w/ timestamps
- `my.mail.imap` and `my.mail.mbox` to parse local IMAP sync's of my mail/mbox files -- see [doc/MAIL_SETUP.md](doc/MAIL_SETUP.md)
- `my.mpv.history_daemon`, accesses movies/music w/ activity/metdata that have played on my machine, facilitated by a [mpv history daemon](https://github.com/seanbreckenridge/mpv-history-daemon)
- `my.discord.data_export`, parses ~1,000,000 messages/events from the discord data export, parser [here](https://github.com/seanbreckenridge/discord_data)
- `my.todotxt.git_history`, to track my to-do list history (using backups of my [`todotxt`](http://todotxt.org/) files in [`git_doc_history`](https://github.com/seanbreckenridge/git_doc_history))
- `my.rss.newsboat`, keeps track of when I added/removed RSS feeds (for [`newsboat`](https://newsboat.org/))
- `my.ipython`, for timestamped python REPL history
- `my.ttt`, to parse shell/system history tracked by [`ttt`](https://github.com/seanbreckenridge/ttt)
- `my.window_watcher`, to parse active window events (what application I'm using/what the window title is) using [`window_watcher`](https://github.com/seanbreckenridge/aw-watcher-window)
- `my.chess.export`, to track my [chess.com](https://www.chess.com)/[lichess.org](https://lichess.org/) games, using [`chess_export`](https://github.com/seanbreckenridge/chess_export)
- `my.trakt.export`, providing me a history/my ratings for Movies/TV Show (episodes) using [`traktexport`](https://github.com/seanbreckenridge/traktexport)
- `my.listenbrainz.export`, exporting my music listening history from [ListenBrainz](https://listenbrainz.org/) (open-source Last.fm) using [`listenbrainz_export`](https://github.com/seanbreckenridge/listenbrainz_export)
- `my.mal.export`, for anime/manga history using [`malexport`](https://github.com/seanbreckenridge/malexport)
- `my.grouvee.export`, for my video game history/backlog using [`grouvee_export`](https://github.com/seanbreckenridge/grouvee_export)
- `my.runelite.screenshots`, parses data from the [automatic runelite screenshots](https://github.com/runelite/runelite/wiki/Screenshot)
- `my.project_euler`, when I solved [Project Euler](https://projecteuler.net/) problems
- `my.linkedin.privacy_export`, to parse the [privacy export](https://www.linkedin.com/help/linkedin/answer/50191/downloading-your-account-data?lang=en) from linkedin

#### 'Historical' Modules

These are modules to parse GDPR exports/data from services I used to use, but don't anymore. They're here to provide more context into the past.

- `my.apple.privacy_export`, parses Game Center and location data from the [apple privacy export](https://privacy.apple.com/)
- `my.facebook.gdpr`, to parse the GDPR export from Facebook
- `my.league.export`, gives League of Legends game history using [`lolexport`](https://github.com/seanbreckenridge/lolexport)
- `my.steam.scraper`, for steam achievement data and game playtime using [`steamscraper`](https://github.com/seanbreckenridge/steamscraper)
- `my.piazza.scraper`, parsing [piazza](https://piazza.com/) (university forum) posts using [`piazza-scraper`](https://github.com/seanbreckenridge/piazza-scraper)
- `my.blizzard.gdpr`, for general battle.net event data [parsed from a GDPR export](https://github.com/seanbreckenridge/blizzard_gdpr_parser)
- `my.skype.gdpr` to parse a couple datetimes from the Skype GDPR export (seems all my data from years ago is long gone)
- `my.spotify.gdpr`, to parse the GDPR export from Spotify, mostly to access songs from my playlists from years ago
- `my.twitch`, merging the [data export](https://www.twitch.tv/p/en/legal/privacy-choices/#user-privacy-requests) and my messages parsed from the [overrustle logs dump](https://github.com/seanbreckenridge/overrustle_parser)

See [here](https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py) for my `HPI` config

[Promnesia `Source`s for these `HPI` modules](https://github.com/seanbreckenridge/promnesia)

I also have some more personal scripts/modules in a separate repo; [`HPI-personal`](https://github.com/seanbreckenridge/HPI-personal)

### In-use from [karlicoss/HPI](https://github.com/karlicoss/HPI)

- `my.browser`, to parse browser history using [`browserexport`](https://github.com/seanbreckenridge/browserexport)
- `my.google.takeout.parser`, parses lots of (~500,000) events (youtube, searches, phone usage, comments, location history) from [google takeouts](https://takeout.google.com/), using [`google_takeout_parser`](https://github.com/seanbreckenridge/google_takeout_parser)
- `my.coding.commits` to track git commits across the system
- `my.github` to track github events/commits and parse the GDPR export, using [`ghexport`](https://github.com/karlicoss/ghexport)
- `my.reddit`, get saved posts, comments. Uses [`rexport`](https://github.com/karlicoss/rexport) to create backups of recent activity periodically, and [`pushshift`](https://github.com/seanbreckenridge/pushshift_comment_export) to get old comments.
- `my.smscalls`, exports call/sms history using [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US)
- `my.stackexchange.stexport`, for stackexchange data using [`stexport`](https://github.com/karlicoss/stexport)

#### Partially in-use/with overrides:

- `my.location`, though since I also have some locations from `apple.privacy_export`, I have a [`my.location.apple`](./my/location/apple.py) which I then merge into `my.location.all` in my overridden [`all.py`](https://github.com/seanbreckenridge/HPI-personal/blob/master/my/location/all.py) file on my personal repo
- similarly, I do use `my.ip` and `my.location.via_ip` from upstream, but I have [overridden `all.py` and module files here](https://github.com/seanbreckenridge/HPI/tree/master/my/ip)

'Overriding' an `all.py` file means replacing the `all.py` from upstream repo (this means it can use my sources here to grab more locations/ips, since those don't exist in the upstream). For more info see [reorder_editable](https://github.com/seanbreckenridge/reorder_editable#editable-namespace-packages), and the [module design](https://github.com/karlicoss/HPI/blob/master/doc/MODULE_DESIGN.org#adding-new-modules) docs for HPI, but you might be able to get the gist by comparing:

- [my.location.all](https://github.com/karlicoss/HPI/blob/master/my/location/all.py) in `karlicoss/HPI`
- [my.location.all](https://github.com/seanbreckenridge/HPI-personal/blob/master/my/location/all.py) in `seanbreckenridge/HPI-personal`

Since I've mangled my `PYTHONPATH` (see [reorder_editable](https://github.com/seanbreckenridge/reorder_editable#editable-namespace-packages)), it imports from my repo instead of `karlicoss/HPI`. `all.py` files tend to pretty small -- so overriding/changing a line to add a source is the whole point.

### Companion Tools/Libraries

Disregarding tools which actively collect data (like [`ttt`](https://github.com/seanbreckenridge/ttt)/[`window_watcher`](https://github.com/seanbreckenridge/aw-watcher-window)) or repositories which have their own exporter/parsers which are used here, there are a couple other tools/libraries I've created for this project:

- [`ipgeocache`](https://github.com/seanbreckenridge/ipgeocache) - for any IPs gathered from data exports, provides geolocation info, so I have partial location info going back to 2013
- [`sqlite_backup`](https://github.com/seanbreckenridge/sqlite_backup) - to safely copy/backup application sqlite databases that may currently be in use
- [`git_doc_history`](https://github.com/seanbreckenridge/git_doc_history) - a bash script to copy/backup files into git history, with a python library to help traverse and create a history/parse diffs between commits
- [`HPI_API`](https://github.com/seanbreckenridge/HPI_API) - automatically creates a JSON API/server for HPI modules
- [`url_metadata`](https://github.com/seanbreckenridge/url_metadata) - caches youtube subtitles, url metadata (title, description, image links), and a html/plaintext summary for any URL

I also use this in [`my_feed`](https://github.com/seanbreckenridge/my_feed), which creates a feed of media/data using `HPI`, live at <https://sean.fish/feed/>

### Ad-hoc and interactive

Some basic examples.

When was I most using reddit?

```python
>>> import collections, my.reddit.all, pprint
>>> pprint.pprint(collections.Counter([c.created.year for c in my.reddit.all.comments()]))
Counter({2016: 3288,
         2017: 801,
         2015: 523,
         2018: 209,
         2019: 65,
         2014: 4,
         2020: 3})
```

Most common shell commands?

```python
>>> import collections, pprint, my.zsh
# lots of these are git-related aliases
>>> pprint.pprint(collections.Counter([c.command for c in my.zsh.history()]).most_common(10))
[('ls', 51059),
 ('gst', 11361),
 ('ranger', 6530),
 ('yst', 4630),
 ('gds', 3919),
 ('ec', 3808),
 ('clear', 3651),
 ('cd', 2111),
 ('yds', 1647),
 ('ga -A', 1333)]
```

What websites do I visit most?

```python
>>> import collections, pprint, my.browser.export, urllib
>>> pprint.pprint(collections.Counter([urllib.parse.urlparse(h.url).netloc for h in my.browser.export.history()]).most_common(5))
[('github.com', 20953),
 ('duckduckgo.com', 10146),
 ('www.youtube.com', 10126),
 ('discord.com', 8425),
 ('stackoverflow.com', 2906)]
```

Song I've listened to most?

```python
>>> import collections, my.mpv.history_daemon
>>> collections.Counter([m.path for m in my.mpv.history_daemon.history()]).most_common(1)[0][0]
'/home/sean/Music/JPEFMAFIA/JPEGMAFIA - LP! - 2021 - V0/JPEGMAFIA - LP! - 05 HAZARD DUTY PAY!.mp3'
```

Movie I've watched most?

```python
>>> import my.trakt, from collections import Counter
>>> Counter(e.media_data.title for e in my.trakt.history()).most_common(1)
[('Up', 92)]  # (the pixar movie)
```

`hpi` also has a JSON query interface, so I can do quick computations using shell tools like:

```bash
# how many calories have I eaten today (from https://github.com/seanbreckenridge/ttally)
$ hpi query ttally.funcs.food --recent 1d -s | jq -r '(.quantity)*(.calories)' | datamash sum 1
2258.5
```

### Install

For the basic setup, I recommend you clone and install both directories as editable installs:

```bash
# clone and install upstream as an editable package
git clone https://github.com/karlicoss/HPI ./HPI-karlicoss
python3 -m pip install --user -e ./HPI-karlicoss

# clone and install my repository as an editable package
git clone https://github.com/seanbreckenridge/HPI ./HPI-seanb
python3 -m pip install --user -e ./HPI-seanb
```

Editable install means any changes to python files reflect immediately, which is very convenient for debugging and developing new modules. To update, you can just `git pull` in those directories.

If you care about [overriding modules](https://github.com/seanbreckenridge/HPI#partially-in-usewith-overrides), to make sure your `easy-install.pth` is ordered correctly:

```bash
python3 -m pip install --user reorder_editable
python3 -m reorder_editable reorder ./HPI-seanb ./HPI-karlicoss
```

Then, you likely need to run `hpi module install` for any modules you plan on using -- this can be done incrementally as you setup new modules. E.g.:

- `hpi module install my.trakt.export` to install dependencies
- Check the [stub config](./tests/my/my/config/__init__.py) or [my config](https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py) and setup the config block in your HPI configuration file
- Run `hpi doctor my.trakt.export` to check for any possible config issues/if your data is being loaded properly

(The [install](./install) script does that for all my modules, but you likely don't want to do that)

Its possible to install both `my` packages because `HPI` is a namespace package. For more information on that, and some of the complications one can run into, see [reorder_editable](https://github.com/seanbreckenridge/reorder_editable#editable-namespace-packages), and the [module design](https://github.com/karlicoss/HPI/blob/master/doc/MODULE_DESIGN.org#adding-new-modules) docs for HPI.

If you're having issues installing/re-installing, check the [TROUBLESHOOTING_INSTALLS.md](doc/TROUBLESHOOTING_INSTALLS.md) file.

If you recently updated and it seems like something has broke, check the [CHANGELOG](CHANGELOG.md) for any possible breaking changes
