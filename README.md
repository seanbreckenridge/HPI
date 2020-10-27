**TLDR**: I'm using [HPI](https://github.com/seanbreckenridge/HPI) (Human
Programming Interface) package as a means of unifying, accessing and
interacting with all of my personal data.

It's a Python library (named `my`), a collection of modules for:

- social networks: posts, comments, favorites, searches
- shell/program histories (zsh, python, mpv, firefox)
- reading: e-books and pdfs
- programming (github/commits)
- todos and notes
- instant messaging
- bank account history/transactions
- some video game achievements/history

[_Why?_](https://github.com/seanbreckenridge/HPI#why)

---

This is modified from [`karlicoss/HPI`](https://github.com/karlicoss/HPI) to more fit my life.

- A lot of the documentation remains unchanged from the original.
- _For now_, I don't expect anyone else to use this directly, the code is up here as reference.

---

## Currently in-use modules

- `my.github`, get all github actions (comments, issues, etc.)
- `my.reddit`, get saved posts, comments. Uses [`rexport`](https://github.com/karlicoss/rexport) to create backups of recent activity periodically, and [`pushshift`](https://github.com/seanbreckenridge/pushshift_comment_export) to get old comments.
- `my.browsing`, using my [`ffexport`](https://github.com/seanbreckenridge/ffexport) tool to backup/parse firefox history
- `my.zsh`, access to my shell history w/ timestamps
- `my.google`, parses lots of (~250,000) events (youtube, searches, phone usage, comments, location history) from [google takeouts](https://takeout.google.com/)
- `my.food`, tracks calorie/water intake; imports from [`calories`](https://github.com/zupzup/calories). I use [this](https://github.com/seanbreckenridge/calories-fzf/) interface most of the time to add food I eat.
- `my.body` to track body functionality (e.g. weight) (with a TUI using [`autotui`](https://github.com/seanbreckenridge/autotui))
- `my.coding` to track git commits across the system
- `my.mpv`, accesses movies/music w/ activity/metdata that have played on my machine, facilitated by a [mpv history daemon](https://github.com/seanbreckenridge/mpv-sockets/blob/master/DAEMON.md)
- `my.discord`, parses ~1,000,000 messages/events from the discord GDPR export, parser [here](https://github.com/seanbreckenridge/discord_data)
- `my.money`, bank account transactions/balance history from [my budget tool](https://github.com/seanbreckenridge/mint)
- `my.smscalls`, exports call/sms history using [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US)
- `my.todotxt`, to track my to-do list history (using backups of my [`todotxt`](http://todotxt.org/) files)
- `my.rss`, keeps track of when I added/removed RSS feeds (for [`newsboat`](https://newsboat.org/))
- `my.ipython`, for timestamped python REPL history
- `my.ttt`, to parse shell/system history tracked by [`ttt`](https://github.com/seanbreckenridge/ttt)
- `my.window_watcher`, to parse active window events using [`window_watcher`](https://github.com/seanbreckenridge/aw-watcher-window)
- `my.location`, merges data from `apple`, `google`, `games.blizzard`, and `facebook` to provide location data (goes back ~10 years)

### 'Historical' Modules

These are modules to parse GDPR exports/data from services I used to use, but don't anymore. They're here to provide more context into the past.

- `my.apple`, parses game center and location data from the apple GDPR export
- `my.facebook`, to parse the GDPR export I downloaded from facebook before deleting my account
- `my.games.league`, gives league of legends game history using [`lolexport`](https://github.com/seanbreckenridge/lolexport)
- `my.games.steam`, for steam achievement data and game playtime using [`steamscraper`](https://github.com/seanbreckenridge/steamscraper)
- `my.games.blizzard`, for general battle.net event data [parsed from a gdpr export](https://github.com/seanbreckenridge/blizzard_gdpr_parser)
- `my.old_forums`, random posts from forums I used to use in the past, see [`forum_parser`](https://github.com/seanbreckenridge/forum_parser)
- `my.skype` to parse a couple datetimes from the skype GDPR export
- `my.spotify`, to parse the GDPR export from spotify, mostly for songs from my playlists from years ago

See [here](https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py) for config.

### Companion Libraries

Disregarding tools which actively collect data (like [`ttt`](https://github.com/seanbreckenridge/ttt)/[`window_watcher`](https://github.com/seanbreckenridge/aw-watcher-window)), I have some other libraries I've created for this project, to provide more context to some of the data.

- [`ipgeocache`](https://github.com/seanbreckenridge/ipgeocache) - for any IPs gathered from data exports, provides geolocation info, so I have location info going back to 2013 (thanks facebook)
- [`url_metadata`](https://github.com/seanbreckenridge/url_metadata) - caches youtube subtitles, url metadata (title, description, image links), and a html/plaintext summary for any URL

### Ad-hoc and interactive

Some basic examples.

When was I most using reddit?

```python
>>> import collections, my.reddit, pprint
>>> pprint.pprint(collections.Counter([c.created.year for c in my.reddit.comments()]))
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
>>> import collections, pprint, my.browsing, urllib
>>> pprint.pprint(collections.Counter([urllib.parse.urlparse(h.url).netloc for h in my.browsing.history()]).most_common(5))
[('github.com', 20953),
 ('duckduckgo.com', 10146),
 ('www.youtube.com', 10126),
 ('discord.com', 8425),
 ('stackoverflow.com', 2906)]
```

Song I've listened to most?

```python
>>> import collections, my.mpv
>>> collections.Counter([m.path for m in my.mpv.history()]).most_common(1)[0]
('/home/sean/Music/Toby Fox/Toby Fox - UNDERTALE Soundtrack (2015) [V0]/085 - Fallen Down (Reprise).mp3', 8)
```

---

### TODO:

- [ ] [gpslogger](https://github.com/mendhak/gpslogger) module

historical GDPR exports

create 'export modules' which keep these up to date:

- [ ] backup trakt? (have API access)
- [ ] backup MAL (ugh)

Need to do more research/figure out

- [ ] android app to track my location?
- [ ] polar? some other reading system? formalize documents/configure `my.pdfs`
- [ ] email?

### delayed todos

- [ ] configure `my.stackexchange` (isnt really documented/able to use in HPI without modifications [wait for repo](https://github.com/karlicoss/ghexport/issues/3#issuecomment-680732889))
- [ ] exif data from photos; I don't really take lots of photos, so perhaps this isn't as useful as of right now

---

### Structural Changes

- collection of [`bootstrap`](./bootstrap) scripts to setup things on my computer
- [`jobs`](./jobs) contains anacron-like jobs that are run periodically, using [`bgproc`](https://github.com/seanbreckenridge/bgproc) and [`evry`](https://github.com/seanbreckenridge/evry). So, this repo has both the [DAL](https://beepb00p.xyz/exports.html#dal) and the scripts to backup the data.
- `HPI_LOGS` controls the `kython` logging verbosity across the entire package mostly for running `HPI_LOGS=debug hpi doctor`
- Modified lots of the tests that run with pytest. A lot of them just do basic tests to check if data exists on the system, it doesnt mock unit test data. Is just to run after making changes to make sure I didn't break anything that was already working. The `./lint` script wraps `mypy`, `pytest` and `flake8`, to check for typing, tests, and syntax/formatting errors. It also wraps `shellcheck` and `shfmt` to check shell scripts for syntax errors; autoformats if there are no errors. I use [`black`](https://black.readthedocs.io/en/stable/) to autoformat python

---

Last referenced commit hash on [karicoss/HPI](https://github.com/karlicoss/HPI): a946e23dd3351bebd57f7f06ef0fad57886b523d

---

The package hides the [gory
details](https://beepb00p.xyz/sad-infra.html#exports_are_hard) of
locating data, parsing, error handling and caching. You simply
'import' your data and get to work with familiar Python types and data
structures.

- Here's a short example to give you an idea: \"which subreddits I
  find the most interesting?\"

  ```python
  >>> import my.reddit
  >>> from collections import Counter
  >>> return Counter(s.subreddit for s in my.reddit.saved()).most_common(4)
  orgmode 62
  emacs 60
  selfhosted 51
  QuantifiedSelf 46
  ```

I consider my digital trace an important part of my identity.
([\#extendedmind](https://beepb00p.xyz/tags.html#extendedmind)) The fact
that the data is siloed, and accessing it is inconvenient and borderline
frustrating feels very wrong.

Once the data is available as Python objects, I can easily plug it into
existing tools, libraries and frameworks. It makes building new tools
considerably easier and allows creating new ways of interacting with the
data.

I tried different things over the years and I think I'm getting to the
point where other people can also benefit from my code by 'just'
plugging in their data, and that's why I'm sharing this.

Imagine if all your life was reflected digitally and available at your
fingertips. This library is my attempt to achieve this vision.

---

# Why?

The main reason that led me to develop this is the dissatisfaction of
the current situation:

- Our personal data is siloed and trapped across cloud services and
  various devices

  Even when it's possible to access it via the API, it's hardly
  useful, unless you're an experienced programmer, willing to invest
  your time and infrastructure.

- We have insane amounts of data scattered across the cloud, yet
  we're left at the mercy of those who collect it to provide
  something useful based on it

  Integrations of data across silo boundaries are almost non-existent.
  There is so much potential and it's all wasted.

- I'm not willing to wait till some vaporwave project reinvents the
  whole computing model from scratch

  As a programmer, I am in capacity to do something **right now**,
  even though it's not necessarily perfect and consistent.

I've written a lot about it
[here](https://beepb00p.xyz/sad-infra.html#why), so allow me to simply
quote:

> - search and information access
>   - Why can't I search over all of my personal chat history with
>     a friend, whether it's ICQ logs from 2005 or Whatsapp logs
>     from 2019?
>   - Why can't I have incremental search over my tweets? Or
>     browser bookmarks? Or over everything I've ever typed/read on
>     the Internet?
>   - Why can't I search across my watched youtube videos, even
>     though most of them have subtitles hence allowing for full
>     text search?
>   - Why can't I see the places my friends recommended me on
>     Google maps (or any other maps app)?
> - productivity
>   - Why can't my Google Home add shopping list items to Google
>     Keep? Let alone other todo-list apps.
>   - Why can't I create a task in my todo list or calendar from a
>     conversation on Facebook Messenger/Whatsapp/VK.com/Telegram?
> - journaling and history
>   - Why do I have to lose all my browser history if I decide to
>     switch browsers?
>   - Why can't I see all the places I traveled to on a single map
>     and photos alongside?
>   - Why can't I see what my heart rate (i.e. excitement) and
>     speed were side by side with the video I recorded on GoPro
>     while skiing?
>   - Why can't I easily transfer all my books and metadata if I
>     decide to switch from Kindle to PocketBook or vice versa?
> - consuming digital content
>   - Why can't I see stuff I highlighted on Instapaper as an
>     overlay on top of web page?
>   - Why can't I have single 'read it later' list, unifying all
>     things saved on Reddit/Hackernews/Pocket?
>   - Why can't I use my todo app instead of 'Watch later'
>     playlist on youtube?
>   - Why can't I 'follow' some user on Hackernews?
>   - Why can't I see if I've run across a Youtube video because
>     my friend sent me a link months ago?
>   - Why can't I have uniform music listening stats based on my
>     Last.fm/iTunes/Bandcamp/Spotify/Youtube?
>   - Why am I forced to use Spotify's music recommendation
>     algorithm and don't have an option to try something else?
>   - Why can't I easily see what were the books/music/art
>     recommended by my friends or some specific
>     Twitter/Reddit/Hackernews users?
>   - Why my otherwise perfect hackernews [app for
>     Android](https://play.google.com/store/apps/details?id=io.github.hidroh.materialistic)
>     doesn't share saved posts/comments with the website?
> - health and body maintenance
>   - Why can't I tell if I was more sedentary than usual during
>     the past week and whether I need to compensate by doing a bit
>     more exercise?
>   - Why can't I see what's the impact of aerobic exercise on my
>     resting HR?
>   - Why can't I have a dashboard for all of my health: food,
>     exercise and sleep to see baselines and trends?
>   - Why can't I see the impact of temperature or CO2
>     concentration in room on my sleep?
>   - Why can't I see how holidays (as in, not going to work)
>     impact my stress levels?
>   - Why can't I take my Headspace app data and see how/if
>     meditation impacts my sleep?
>   - Why can't I run a short snippet of code and check some random
>     health advice on the Internet against **my** health data.
> - personal finance
>   - Why am I forced to manually copy transactions from different
>     banking apps into a spreadsheet?
>   - Why can't I easily match my Amazon/Ebay orders with my bank
>     transactions?
> - why I can't do anything when I'm offline or have a wonky
>   connection?
> - tools for thinking and learning
>   - Why when something like ['mind
>     palace'](https://en.wikipedia.org/wiki/Method_of_loci) is
>     **literally possible** with VR technology, we don't see any
>     in use?
>   - Why can't I easily convert select Instapaper highlights or
>     new foreign words I encountered on my Kindle into Anki
>     flashcards?
> - mediocre interfaces
>   - Why do I have to suffer from poor management and design
>     decisions in UI changes, even if the interface is not the main
>     reason I'm using the product?
>   - Why can't I leave priorities and notes on my saved
>     Reddit/Hackernews items?
>   - Why can't I leave private notes on Deliveroo
>     restaurants/dishes, so I'd remember what to order/not to
>     order next time?
>   - Why do people have to suffer from Google Inbox shutdown?
> - communication and collaboration
>   - Why can't I easily share my web or book highlights with a
>     friend? Or just make highlights in select books public?
>   - Why can't I easily find out other person's expertise without
>     interrogating them, just by looking what they read instead?
> - backups - Why do I have to think about it and actively invest time and
>   effort?
>   :::

- I'm tired of having to use multiple different messengers and social
  networks

- I'm tired of shitty bloated interfaces

  Why do we have to be at mercy of their developers, designers and
  product managers? If we had our data at hand, we could fine-tune
  interfaces for our needs.

- I'm tired of mediocre search experience

  Text search is something computers do **exceptionally** well. Yet,
  often it's not available offline, it's not incremental, everyone
  reinvents their own query language, and so on.

- I'm frustrated by poor information exploring and processing
  experience

  While for many people, services like Reddit or Twitter are simply
  time killers (and I don't judge), some want to use them
  efficiently, as a source of information/research. Modern bookmarking
  experience makes it far from perfect.

You can dismiss this as a list of first-world problems, and you would be
right, they are. But the major reason I want to solve these problems is
to be better at learning and working with knowledge, so I could be
better at solving the real problems.

# How does a Python package help?

When I started solving some of these problems for myself, I've noticed
a common pattern: the [hardest bit](https://beepb00p.xyz/sad-infra.html#exports_are_hard) is actually
getting your data in the first place. It's inherently error-prone and
frustrating.

But once you have the data in a convenient representation, working with
it is pleasant -- you get to **explore and build instead of fighting
with yet another stupid REST API**.

This package knows how to find data on your filesystem, deserialize it
and normalize it to a convenient representation. You have the full power
of the programming language to transform the data and do whatever comes
to your mind.

## Why don't you just put everything in a massive database?

Glad you've asked! I wrote a whole
[post](https://beepb00p.xyz/unnecessary-db.html) about it.

In short: while databases are efficient and easy to read from, often
they aren't flexible enough to fit your data. You're probably going to
end up writing code anyway.

While working with your data, you'll inevitably notice common patterns
and code repetition, which you'll probably want to extract somewhere.
That's where a Python package comes in.

# How do you use it?

Mainly I use it as a data provider for my scripts, tools, and
dashboards.

## Instant search

Typical search interfaces make me unhappy as they are **siloed, slow,
awkward to use and don't work offline**. So I built my own ways around
it! I write about it in detail
[here](https://beepb00p.xyz/pkm-search.html#personal_information).

In essence, I'm mirroring most of my online data like chat logs,
comments, etc., as plaintext. I can overview it in any text editor, and
incrementally search over **all of it** in a single keypress.

## dashboard

As a big fan of
[\#quantified-self](https://beepb00p.xyz/tags.html#quantified-self),
I'm working on personal health, sleep and exercise dashboard, built
from various data sources.

I'm working on making it public, you can see some screenshots
[here](https://www.reddit.com/r/QuantifiedSelf/comments/cokt4f/what_do_you_all_do_with_your_data/ewmucgk).

## timeline

Timeline is a
[\#lifelogging](https://beepb00p.xyz/tags.html#lifelogging) project I'm
working on.

I want to see all my digital history, search in it, filter, easily jump
at a specific point in time and see the context when it happened. That
way it works as a sort of external memory.

Ideally, it would look similar to Andrew Louis's
[Memex](https://hyfen.net/memex), or might even reuse his interface if
he open sources it. I highly recommend watching his talk for
inspiration.

# How does it get input data?

If you're curious about any specific data sources I'm using, I've
written it up [in detail](https://beepb00p.xyz/my-data.html).

Also see [\"Data flow\"](doc/SETUP.org::#data-flow) documentation with
some nice diagrams explaining on specific examples.

In short:

- The data is [periodically
  synchronized](https://beepb00p.xyz/myinfra.html#exports) from the
  services (cloud or not) locally, on the filesystem

  As a result, you get
  [JSONs/sqlite](https://beepb00p.xyz/myinfra.html#fs) (or other
  formats, depending on the service) on your disk.

  Once you have it, it's trivial to back it up and synchronize to
  other computers/phones, if necessary.

  To schedule periodic sync, I'm using
  [cron](https://beepb00p.xyz/scheduler.html#cron).

- `my.` package only accesses the data on the filesystem

  That makes it extremely fast, reliable, and fully offline capable.

As you can see, in such a setup, the data is lagging behind the
'realtime'. I consider it a necessary sacrifice to make everything
fast and resilient.

In theory, it's possible to make the system almost realtime by having a
service that sucks in data continuously (rather than periodically), but
it's harder as well.

# Q & A

## Why Python?

I don't consider Python unique as a language suitable for such a
project. It just happens to be the one I'm most comfortable with. I do
have some reasons that I think make it _specifically_ good, but
explaining them is out of this post's scope.

In addition, Python offers a [very rich
ecosystem](https://github.com/karlicoss/awesome-python#data-analysis)
for data analysis, which we can use to our benefit.

That said, I've never seen anything similar in other programming
languages, and I would be really interested in, so please send me links
if you know some. I've heard LISPs are great for data? ;)

Overall, I wish
[FFIs](https://en.wikipedia.org/wiki/Foreign_function_interface) were a
bit more mature, so we didn't have to think about specific programming
languages at all.

## Can anyone use it?

Yes!

- you can plug in **your own data**

- most modules are isolated, so you can only use the ones that you
  want to

- everything is easily **extensible**

  Starting from simply adding new modules to any dynamic hackery you
  can possibly imagine within Python.

## How easy is it to use?

The whole setup requires some basic programmer literacy:

- installing/running and potentially modifying Python code
- using symlinks
- potentially running Cron jobs

If you have any ideas on making the setup simpler, please let me know!

## What about privacy?

The modules contain **no data, only code** to operate on the data.

Everything is [**local first**](https://beepb00p.xyz/tags.html#offline),
the input data is on your filesystem. If you're truly paranoid, you can
even wrap it in a Docker container.

There is still a question of whether you trust yourself at even keeping
all the data on your disk, but it is out of the scope of this post.

If you'd rather keep some code private too, it's also trivial to
achieve with a private subpackage.

## But _should_ I use it?

> Sure, maybe you can achieve a perfect system where you can instantly
> find and recall anything that you've done. Do you really want it?
> Wouldn't that, like, make you less human?

I'm not a gatekeeper of what it means to be human, but I don't think
that the shortcomings of the human brain are what makes us such.

So I can't answer that for you. I certainly want it though. I'm [quite
open](https://beepb00p.xyz/tags.html#pkm) about my goals -- I'd happily
get merged/augmented with a computer to enhance my thinking and
analytical abilities.

While at the moment [we don't even remotely
understand](https://en.wikipedia.org/wiki/Hard_problem_of_consciousness)
what would such merging or \"mind uploading\" entail exactly, I can
clearly delegate some tasks, like long term memory, information lookup,
and data processing to a computer. They can already handle it really
well.

> What about these people who have perfect recall and wish they hadn't.

Sure, maybe it sucks. At the moment though, I don't anything close to
it and this only annoys me. I want to have a choice at least, and
digital tools give me this choice.

## Would it suit _me_?

Probably, at least to some extent.

First, our lives are different, so our APIs might be different too. This
is more of a demonstration of what's I'm using, although I did spend
effort towards making it as modular and extensible as possible, so other
people could use it too. It's easy to modify code, add extra methods
and modules. You can even keep all your modifications private.

But after all, we've all sharing many similar activities and using the
same products, so there is a huge overlap. I'm not sure how far we can
stretch it and keep modules generic enough to be used by multiple
people. But let's give it a try perhaps? :)

Second, interacting with your data through the code is the central idea
of the project. That kind of cuts off people without technical skills,
and even many people capable of coding, who dislike the idea of writing
code outside of work.

It might be possible to expose some
[no-code](https://en.wikipedia.org/wiki/No-code_development_platform)
interfaces, but I still feel that wouldn't be enough.

I'm not sure whether it's a solvable problem at this point, but happy
to hear any suggestions!

## What it isn't?

- It's not vaporwave

  The project is a little crude, but it's real and working. I've
  been using it for a long time now, and find it fairly sustainable to
  keep using for the foreseeable future.

- It's not going to be another silo

  While I don't have anything against commercial use (and I believe
  any work in this area will benefit all of us), I'm not planning to
  build a product out of it.

  I really hope it can grow into or inspire some mature open source
  system.

  Please take my ideas and code and build something cool from it!

# Related links

Similar projects:

- [Memacs](https://github.com/novoid/Memacs) by Karl Voit

- [Me API - turn yourself into an open API
  (HN)](https://news.ycombinator.com/item?id=9615901)

- [QS ledger](https://github.com/markwk/qs_ledger) from Mark Koester

- [tehmantra/my](https://github.com/tehmantra/my): directly inspired
  by this package

- [bcongdon/bolero](https://github.com/bcongdon/bolero)

- [Solid
  project](<https://en.wikipedia.org/wiki/Solid_(web_decentralization_project)#Design>):
  personal data pod, which websites pull data from

Other links:

- NetOpWibby: [A Personal API
  (HN)](https://news.ycombinator.com/item?id=21684949)
- [The sad state of personal data and
  infrastructure](https://beepb00p.xyz/sad-infra.html): here I am
  going into motivation and difficulties arising in the implementation

---

Open to any feedback and thoughts!

Also, don't hesitate to raise an issue, or reach me personally if you
want to try using it, and find the instructions confusing. Your
questions would help me to make it simpler!

In some near future I will write more about:

- specific technical decisions and patterns
- challenges I had so solve
- more use-cases and demos -- it's impossible to fit everything in
  one post!

, but happy to answer any questions on these topics now!
