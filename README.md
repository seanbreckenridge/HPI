**TLDR**: I'm using `HPI`(Human Programming Interface) package as a means of unifying, accessing and interacting with all of my personal data.

It's a Python library (named `my`), a collection of modules for:

- social networks: posts, comments, favorites, searches
- shell/program histories (zsh, bash, python, mpv, firefox)
- reading: e-books and pdfs
- programming (github/commits)
- todos and notes
- instant messaging
- bank account history/transactions
- media histories (movies, tv shows, albums, video game achievements/history)

[_Why?_](https://github.com/karlicoss/HPI#why)

This is built on top of [`karlicoss/HPI`](https://github.com/karlicoss/HPI). It started out as a fork, but has since been converted to my own set of modules. This is installed alongside the upstream repository, see [#install](#install)

### My Modules

- `my.browser.export`, using [`browserexport`](https://github.com/seanbreckenridge/browserexport) to backup/parse firefox/chrome/safari history
- `my.zsh` and `my.bash`, access to my shell history w/ timestamps
- `my.mail.imap` to parse local IMAP sync's of my email
- `my.google_takeout`, parses lots of (~500,000) events (youtube, searches, phone usage, comments, location history) from [google takeouts](https://takeout.google.com/), using [`google_takeout_parser`](https://github.com/seanbreckenridge/google_takeout_parser)
- `my.mpv.history_daemon`, accesses movies/music w/ activity/metdata that have played on my machine, facilitated by a [mpv history daemon](https://github.com/seanbreckenridge/mpv-history-daemon)
- `my.discord.data_export`, parses ~1,000,000 messages/events from the discord data export, parser [here](https://github.com/seanbreckenridge/discord_data)
- `my.mint`, bank account transactions/balance history from [my personal budget tool](https://github.com/seanbreckenridge/mint)
- `my.todotxt`, to track my to-do list history (using backups of my [`todotxt`](http://todotxt.org/) files)
- `my.rss.newsboat`, keeps track of when I added/removed RSS feeds (for [`newsboat`](https://newsboat.org/))
- `my.ipython`, for timestamped python REPL history
- `my.ttt`, to parse shell/system history tracked by [`ttt`](https://github.com/seanbreckenridge/ttt)
- `my.window_watcher`, to parse active window events (what application I'm using/what the window title is) using [`window_watcher`](https://github.com/seanbreckenridge/aw-watcher-window)
- `my.location`, merges data from [`gpslogger`](https://github.com/mendhak/gpslogger), `apple`, `google`, `discord`, `blizzard`, and `facebook` to provide location data (goes back ~10 years)
- `my.chess.export`, to track my [chess.com](https://www.chess.com)/[lichess.org](https://lichess.org/) games, using [`chess_export`](https://github.com/seanbreckenridge/chess_export)
- `my.trakt.export`, providing me a history/my ratings for Movies/TV Show (episodes) using [`traktexport`](https://github.com/seanbreckenridge/traktexport)
- `my.listenbrainz.export`, exporting my music scrobbling history from [ListenBrainz](https://listenbrainz.org/) (open-source Last.fm) using [`listenbrainz_export`](https://github.com/seanbreckenridge/listenbrainz_export)
- `my.mal.export`, for anime/manga history using [`malexport`](https://github.com/seanbreckenridge/malexport)
- `my.grouvee.export`, for my video game history/backlog using [`grouvee_export`](https://github.com/seanbreckenridge/grouvee_export)
- `my.runelite.screenshots`, parses data from the [automatic runelite screenshots](https://github.com/runelite/runelite/wiki/Screenshot)
- `my.project_euler`, when I solved [Project Euler](https://projecteuler.net/) problems
- `my.nextalbums`, grabbing when I listened to music albums/my ratings using my [giant spreadsheet](https://sean.fish/s/albums). Handled by [`nextalbums export`](https://github.com/seanbreckenridge/albums)

#### 'Historical' Modules

These are modules to parse GDPR exports/data from services I used to use, but don't anymore. They're here to provide more context into the past.

- `my.apple.privacy_export`, parses Game Center and location data from the apple GDPR export
- `my.facebook.gdpr`, to parse the GDPR export from Facebook
- `my.league.export`, gives League of Legends game history using [`lolexport`](https://github.com/seanbreckenridge/lolexport)
- `my.steam.scraper`, for steam achievement data and game playtime using [`steamscraper`](https://github.com/seanbreckenridge/steamscraper)
- `my.blizzard.gdpr`, for general battle.net event data [parsed from a GDPR export](https://github.com/seanbreckenridge/blizzard_gdpr_parser)
- `my.old_forums`, parses random forum posts and achievements from sites I used to use in the past, see [`old_forums`](https://github.com/seanbreckenridge/old_forums)
- `my.skype.gdpr` to parse a couple datetimes from the Skype GDPR export (seems all my data from years ago is long gone)
- `my.spotify.gdpr`, to parse the GDPR export from Spotify, mostly to access songs from my playlists from years ago
- `my.twitch`, merging the [data export](https://www.twitch.tv/p/en/legal/privacy-choices/#user-privacy-requests) and my messages parsed from the [overrustle logs dump](https://github.com/seanbreckenridge/overrustle_parser)

See [here](https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py) for my `HPI` config

[Promnesia `Source`s for these `HPI` modules](https://github.com/seanbreckenridge/promnesia)

### In-use from [karlicoss/HPI](https://github.com/karlicoss/HPI)

- `my.coding.commits` to track git commits across the system
- `my.github` to track github events/commits and parse the GDPR export, using [`ghexport`](https://github.com/karlicoss/ghexport)
- `my.reddit`, get saved posts, comments. Uses [`rexport`](https://github.com/karlicoss/rexport) to create backups of recent activity periodically, and [`pushshift`](https://github.com/seanbreckenridge/pushshift_comment_export) to get old comments.
- `my.smscalls`, exports call/sms history using [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US)

### Companion Libraries

Disregarding tools which actively collect data (like [`ttt`](https://github.com/seanbreckenridge/ttt)/[`window_watcher`](https://github.com/seanbreckenridge/aw-watcher-window)), I have some other libraries I've created for this project, to provide more context to some of the data.

- [`ipgeocache`](https://github.com/seanbreckenridge/ipgeocache) - for any IPs gathered from data exports, provides geolocation info, so I have partial location info going back to 2013
- [`url_metadata`](https://github.com/seanbreckenridge/url_metadata) - caches youtube subtitles, url metadata (title, description, image links), and a html/plaintext summary for any URL
- [`HPI_API`](https://github.com/seanbreckenridge/HPI_API) - automatically creates a JSON API for HPI modules

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

The [`install` script here](./scripts/install) first installs the upstream repo ([`karlicoss/HPI`](https://github.com/karlicoss/HPI)) as a editable package, then sets up this repository along side it -- this is possible because `HPI` is a namespace package.

For more information on that, and some of the complications one can run into, see [reorder_editable](https://github.com/seanbreckenridge/reorder_editable#editable-namespace-packages), and the [module design](https://github.com/karlicoss/HPI/blob/master/doc/MODULE_DESIGN.org#adding-new-modules) docs for HPI.

Disregarding setting up all the dependencies for individual (e.g. `my.ipython`) modules (which is why the [`install`](./scripts/install) script exists), this is setup by doing:

```bash
# clone and install upstream as an editable package
git clone https://github.com/karlicoss/HPI ./HPI-fork
python3 -m pip install -e ./HPI-fork

# clone and install my repository as an editable package
git clone https://github.com/seanbreckenridge/HPI ./HPI
python3 -m pip install -e ./HPI

# make sure my easy-install.pth is ordered correctly
python3 -m pip install reorder_editable
python3 -m reorder_editable reorder ./HPI ./HPI-fork
```

Those directories are editable installs, meaning any changes I make to them get applied immediately, which is very convenient for debugging and developing new modules.

If you have issues installing, check the [CHANGELOG](CHANGELOG.md) for any possible breaking changes

[`scripts/jobs`](./scripts/jobs) contains anacron-like jobs that are run periodically, using [`bgproc`](https://github.com/seanbreckenridge/bgproc) and [`evry`](https://github.com/seanbreckenridge/evry). In other words, those are the scripts that back up the data, and the python here parses it.

I run the jobs in the background using [supervisor](https://github.com/Supervisor/supervisor), see [here](https://github.com/seanbreckenridge/dotfiles/tree/master/.local/scripts/supervisor) for my configuration, and/or [`run_jobs`](https://github.com/seanbreckenridge/dotfiles/blob/master/.local/scripts/supervisor/run_jobs) for the `bgproc` wrapper. They likely won't work out of the box for you, as they depend on tokens/environment variables that are set on my system - In particular the `HPIDATA` environment variable, which for me is `~/data` -- they're here as examples if you're having issues setting up cron/scripts to backup the data

### TODO:

- [ ] configure `my.stackexchange` API tokens: https://github.com/karlicoss/stexport
- [ ] google [now playing history](https://dfir.pubpub.org/pub/xbvsrjt5/release/1)
