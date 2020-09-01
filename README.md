### Modified from [`karlicoss/HPI`](https://github.com/karlicoss/HPI) to more fit my life

- A lot of the documentation remains unchanged from the original.
- *For now*, I don't expect anyone else to use this directly, the code is up here as reference.

---

### Currently in-use modules/scripts


- `my.github`, with [`jobs/ghexport.job`](jobs/ghexport.job) to download github actions periodically.
- `my.reddit`, corresponding [job](./jobs/rexport.job)
- `my.zsh`, [example usage](https://gist.github.com/seanbreckenridge/921b49da3fadf09e45a23bb5a06b030e)
- `my.body.weight` to track weight (w/ TUI to add to log)
- `my.coding` to track git commits across the system
- `my.todotxt`, to track my to-do list history
- `my.browsing`, using my [`ffexport`](https://github.com/seanbreckenridge/ffexport) tool to backup/parse firefox history

See [here](https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py) for config.

---

### TODO:

- [x] backup/parse zsh history and create corresponding DAL
- [x] add tests for zsh history
- [x] setup script to track weight
- [x] backup todo lists (todotxt)
- [x] create DAL for todotxt (use <https://github.com/bram85/topydo> to read todo file)
- [x] backup newsboat `rss` feeds
- [ ] daemon to capture i3/x-window tree structure (instead of rescuetime)
- [ ] mpv-socket-daemon, use sockets/`socat` to capture what Im currently watching/listening to
- [ ] patch in rifle/ranger history?
- [x] configure `my.coding`
- [x] save browser history (look at promnesia scripts?)
- [ ] configure `my.media` (youtube history)
- [ ] configure google takeout/mounted google drive
- [ ] polar? some other reading system? formalize documents/configure `my.pdfs`
- [ ] backup sms/phone calls
- [x] configure `my.reddit`/`rexport`
- [ ] food/tracking caloric intake?
- [ ] android app to track my location?
- [ ] discord backups - can request [exports](https://support.discord.com/hc/en-us/articles/360004027692) once a month, write a DAL once I have access
- [ ] backup MAL (ugh)
- [ ] backup trakt? (have API access)
- [ ] better [exobrain](https://github.com/seanbreckenridge/exobrain) for notes...? want:
  - private/public notes
  - filter by category/tag (more than just the directory)
  - generate an RSS feed (if only so I can periodically `curl` it to track my own posts)
  - be able to connect/reference whatever reading tool I end up using
  - [maybe] let the inverted index connect related info automatically?
  - `org` mode may solve most of these, but I have to learn org mode

### delayed todos
- [ ] configure `my.stackexchange` (isnt really documented/able to use in HPI without modifications [wait for repo](https://github.com/karlicoss/ghexport/issues/3#issuecomment-680732889))
- [ ] reddit: maybe manually export comments past the last 1000? would be nice to see them in context for lifelogging. could be done manually by scrolling back and parsing HTML
- [ ] rss - rss is continually backed up. once a good sample has been accrued, write a DAL to show when feeds were added/removed

---

### Structural Changes

- collection of [`bootstrap`](./bootstrap) scripts to setup things on my computer
- [`jobs`](./jobs) contains anacron-like jobs that are run periodically, using [`bgproc`](https://github.com/seanbreckenridge/bgproc) and [`evry`](https://github.com/seanbreckenridge/evry). So, this repo has both the [DAL](https://beepb00p.xyz/exports.html#dal) and the scripts to backup the data.

---

Last referenced commit hash: [`07dd61ca6ae2b6de20d6954ca1584accede8b762`](https://github.com/karlicoss/HPI/commit/07dd61ca6ae2b6de20d6954ca1584accede8b762)

---

**TLDR**: I'm using [HPI](https://github.com/karlicoss/HPI) (Human
Programming Interface) package as a means of unifying, accessing and
interacting with all of my personal data.

It's a Python library (named `my`), a collection of modules for:

-   social networks: posts, comments, favorites
-   reading: e-books and pdfs
-   annotations: highlights and comments
-   todos and notes
-   health data: sleep, exercise, weight, heart rate, and other body
    metrics
-   location
-   photos & videos
-   browser history
-   instant messaging

The package hides the [gory
details](https://beepb00p.xyz/sad-infra.html#exports_are_hard) of
locating data, parsing, error handling and caching. You simply
'import' your data and get to work with familiar Python types and data
structures.

-   Here's a short example to give you an idea: \"which subreddits I
    find the most interesting?\"

    ``` {.python}
    import my.reddit
    from collections import Counter
    return Counter(s.subreddit for s in my.reddit.saved()).most_common(4)
    ```

      ---------------- ----
      orgmode          62
      emacs            60
      selfhosted       51
      QuantifiedSelf   46
      ---------------- ----

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

```{=org}
#+toc: headlines 2
```
::: {.RESULTS .drawer}
**Table of contents:**

-   Why?
-   How does a Python package help?
    -   Why don't you just put everything in a massive database?
-   What's inside?
-   How do you use it?
-   Ad-hoc and interactive
    -   What were my music listening stats for 2018?
    -   What are the most interesting Slate Star Codex posts I've read?
    -   Accessing exercise data
    -   Book reading progress
    -   Messenger stats
    -   Querying Roam Reasearch database
-   How does it get input data?
-   Q & A
    -   Why Python?
    -   Can anyone use it?
    -   How easy is it to use?
    -   What about privacy?
    -   But *should* I use it?
    -   Would it suit *me*?
    -   What it isn't?
-   Related links
-   --
:::

Why?
====

The main reason that led me to develop this is the dissatisfaction of
the current situation:

-   Our personal data is siloed and trapped across cloud services and
    various devices

    Even when it's possible to access it via the API, it's hardly
    useful, unless you're an experienced programmer, willing to invest
    your time and infrastructure.

-   We have insane amounts of data scattered across the cloud, yet
    we're left at the mercy of those who collect it to provide
    something useful based on it

    Integrations of data across silo boundaries are almost non-existent.
    There is so much potential and it's all wasted.

-   I'm not willing to wait till some vaporwave project reinvents the
    whole computing model from scratch

    As a programmer, I am in capacity to do something **right now**,
    even though it's not necessarily perfect and consistent.

I've written a lot about it
[here](https://beepb00p.xyz/sad-infra.html#why), so allow me to simply
quote:

::: {.RESULTS .drawer}
> -   search and information access
>     -   Why can't I search over all of my personal chat history with
>         a friend, whether it's ICQ logs from 2005 or Whatsapp logs
>         from 2019?
>     -   Why can't I have incremental search over my tweets? Or
>         browser bookmarks? Or over everything I've ever typed/read on
>         the Internet?
>     -   Why can't I search across my watched youtube videos, even
>         though most of them have subtitles hence allowing for full
>         text search?
>     -   Why can't I see the places my friends recommended me on
>         Google maps (or any other maps app)?
> -   productivity
>     -   Why can't my Google Home add shopping list items to Google
>         Keep? Let alone other todo-list apps.
>     -   Why can't I create a task in my todo list or calendar from a
>         conversation on Facebook Messenger/Whatsapp/VK.com/Telegram?
> -   journaling and history
>     -   Why do I have to lose all my browser history if I decide to
>         switch browsers?
>     -   Why can't I see all the places I traveled to on a single map
>         and photos alongside?
>     -   Why can't I see what my heart rate (i.e. excitement) and
>         speed were side by side with the video I recorded on GoPro
>         while skiing?
>     -   Why can't I easily transfer all my books and metadata if I
>         decide to switch from Kindle to PocketBook or vice versa?
> -   consuming digital content
>     -   Why can't I see stuff I highlighted on Instapaper as an
>         overlay on top of web page?
>     -   Why can't I have single 'read it later' list, unifying all
>         things saved on Reddit/Hackernews/Pocket?
>     -   Why can't I use my todo app instead of 'Watch later'
>         playlist on youtube?
>     -   Why can't I 'follow' some user on Hackernews?
>     -   Why can't I see if I've run across a Youtube video because
>         my friend sent me a link months ago?
>     -   Why can't I have uniform music listening stats based on my
>         Last.fm/iTunes/Bandcamp/Spotify/Youtube?
>     -   Why am I forced to use Spotify's music recommendation
>         algorithm and don't have an option to try something else?
>     -   Why can't I easily see what were the books/music/art
>         recommended by my friends or some specific
>         Twitter/Reddit/Hackernews users?
>     -   Why my otherwise perfect hackernews [app for
>         Android](https://play.google.com/store/apps/details?id=io.github.hidroh.materialistic)
>         doesn't share saved posts/comments with the website?
> -   health and body maintenance
>     -   Why can't I tell if I was more sedentary than usual during
>         the past week and whether I need to compensate by doing a bit
>         more exercise?
>     -   Why can't I see what's the impact of aerobic exercise on my
>         resting HR?
>     -   Why can't I have a dashboard for all of my health: food,
>         exercise and sleep to see baselines and trends?
>     -   Why can't I see the impact of temperature or CO2
>         concentration in room on my sleep?
>     -   Why can't I see how holidays (as in, not going to work)
>         impact my stress levels?
>     -   Why can't I take my Headspace app data and see how/if
>         meditation impacts my sleep?
>     -   Why can't I run a short snippet of code and check some random
>         health advice on the Internet against **my** health data.
> -   personal finance
>     -   Why am I forced to manually copy transactions from different
>         banking apps into a spreadsheet?
>     -   Why can't I easily match my Amazon/Ebay orders with my bank
>         transactions?
> -   why I can't do anything when I'm offline or have a wonky
>     connection?
> -   tools for thinking and learning
>     -   Why when something like ['mind
>         palace'](https://en.wikipedia.org/wiki/Method_of_loci) is
>         **literally possible** with VR technology, we don't see any
>         in use?
>     -   Why can't I easily convert select Instapaper highlights or
>         new foreign words I encountered on my Kindle into Anki
>         flashcards?
> -   mediocre interfaces
>     -   Why do I have to suffer from poor management and design
>         decisions in UI changes, even if the interface is not the main
>         reason I'm using the product?
>     -   Why can't I leave priorities and notes on my saved
>         Reddit/Hackernews items?
>     -   Why can't I leave private notes on Deliveroo
>         restaurants/dishes, so I'd remember what to order/not to
>         order next time?
>     -   Why do people have to suffer from Google Inbox shutdown?
> -   communication and collaboration
>     -   Why can't I easily share my web or book highlights with a
>         friend? Or just make highlights in select books public?
>     -   Why can't I easily find out other person's expertise without
>         interrogating them, just by looking what they read instead?
> -   backups
>     -   Why do I have to think about it and actively invest time and
>         effort?
:::

-   I'm tired of having to use multiple different messengers and social
    networks

-   I'm tired of shitty bloated interfaces

    Why do we have to be at mercy of their developers, designers and
    product managers? If we had our data at hand, we could fine-tune
    interfaces for our needs.

-   I'm tired of mediocre search experience

    Text search is something computers do **exceptionally** well. Yet,
    often it's not available offline, it's not incremental, everyone
    reinvents their own query language, and so on.

-   I'm frustrated by poor information exploring and processing
    experience

    While for many people, services like Reddit or Twitter are simply
    time killers (and I don't judge), some want to use them
    efficiently, as a source of information/research. Modern bookmarking
    experience makes it far from perfect.

You can dismiss this as a list of first-world problems, and you would be
right, they are. But the major reason I want to solve these problems is
to be better at learning and working with knowledge, so I could be
better at solving the real problems.

How does a Python package help?
===============================

When I started solving some of these problems for myself, I've noticed
a common pattern: the [hardest
bit](https://beepb00p.xyz/sad-infra.html#exports_are_hard) is actually
getting your data in the first place. It's inherently error-prone and
frustrating.

But once you have the data in a convenient representation, working with
it is pleasant -- you get to **explore and build instead of fighting
with yet another stupid REST API**.

This package knows how to find data on your filesystem, deserialize it
and normalize it to a convenient representation. You have the full power
of the programming language to transform the data and do whatever comes
to your mind.

Why don't you just put everything in a massive database?
---------------------------------------------------------

Glad you've asked! I wrote a whole
[post](https://beepb00p.xyz/unnecessary-db.html) about it.

In short: while databases are efficient and easy to read from, often
they aren't flexible enough to fit your data. You're probably going to
end up writing code anyway.

While working with your data, you'll inevitably notice common patterns
and code repetition, which you'll probably want to extract somewhere.
That's where a Python package comes in.

What's inside?
===============

Here's the (incomplete) list of the modules:

::: {.RESULTS .drawer}
  ------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------
  [my.bluemaestro](https://github.com/karlicoss/my/tree/master/my/bluemaestro)                      [Bluemaestro](https://bluemaestro.com/products/product-details/bluetooth-environmental-monitor-and-logger) temperature/humidity/pressure monitor
  [my.body.blood](https://github.com/karlicoss/my/tree/master/my/body/blood.py)                     Blood tracking
  [my.body.weight](https://github.com/karlicoss/my/tree/master/my/body/weight.py)                   Weight data (manually logged)
  [my.books.kobo](https://github.com/karlicoss/my/tree/master/my/books/kobo.py)                     [Kobo](https://uk.kobobooks.com/products/kobo-aura-one) e-ink reader: annotations and reading stats
  [my.calendar.holidays](https://github.com/karlicoss/my/tree/master/my/calendar/holidays.py)       Public holidays (automatic) and days off work (manual inputs)
  [my.coding.commits](https://github.com/karlicoss/my/tree/master/my/coding/commits.py)             Git commits data for repositories on your filesystem
  [my.coding.github](https://github.com/karlicoss/my/tree/master/my/coding/github.py)               Github events and their metadata: comments/issues/pull requests
  [my.emfit](https://github.com/karlicoss/my/tree/master/my/emfit)                                  [Emfit QS](https://shop-eu.emfit.com/products/emfit-qs) sleep tracker
  [my.fbmessenger](https://github.com/karlicoss/my/tree/master/my/fbmessenger.py)                   Facebook Messenger messages
  [my.feedbin](https://github.com/karlicoss/my/tree/master/my/feedbin.py)                           Feedbin RSS reader
  [my.feedly](https://github.com/karlicoss/my/tree/master/my/feedly.py)                             Feedly RSS reader
  [my.foursquare](https://github.com/karlicoss/my/tree/master/my/foursquare.py)                     Foursquare/Swarm checkins
  [my.google.takeout.html](https://github.com/karlicoss/my/tree/master/my/google/takeout/html.py)   Google Takeout exports: browsing history, search/youtube/google play activity
  [my.hypothesis](https://github.com/karlicoss/my/tree/master/my/hypothesis.py)                     [Hypothes.is](https://hypothes.is) highlights and annotations
  [my.instapaper](https://github.com/karlicoss/my/tree/master/my/instapaper.py)                     Instapaper bookmarks, highlights and annotations
  [my.lastfm](https://github.com/karlicoss/my/tree/master/my/lastfm)                                Last.fm scrobbles
  [my.location.takeout](https://github.com/karlicoss/my/tree/master/my/location/takeout.py)         Location data from Google Takeout
  [my.materialistic](https://github.com/karlicoss/my/tree/master/my/materialistic.py)               [Materialistic](https://play.google.com/store/apps/details?id=io.github.hidroh.materialistic) app for Hackernews
  [my.notes.orgmode](https://github.com/karlicoss/my/tree/master/my/notes/orgmode.py)               Programmatic access and queries to org-mode files on the filesystem
  [my.pdfs](https://github.com/karlicoss/my/tree/master/my/pdfs.py)                                 PDF documents and annotations on your filesystem
  [my.photos](https://github.com/karlicoss/my/tree/master/my/photos)                                Photos and videos on your filesystem, their GPS and timestamps
  [my.pinboard](https://github.com/karlicoss/my/tree/master/my/pinboard.py)                         [Pinboard](https://pinboard.in) bookmarks
  [my.reading.polar](https://github.com/karlicoss/my/tree/master/my/reading/polar.py)               [Polar](https://github.com/burtonator/polar-books) articles and highlights
  [my.reddit](https://github.com/karlicoss/my/tree/master/my/reddit.py)                             Reddit data: saved items/comments/upvotes/etc.
  [my.rescuetime](https://github.com/karlicoss/my/tree/master/my/rescuetime.py)                     Rescuetime (activity tracking) data
  [my.roamresearch](https://github.com/karlicoss/my/tree/master/my/roamresearch.py)                 [Roam](https://roamresearch.com) data
  [my.rtm](https://github.com/karlicoss/my/tree/master/my/rtm.py)                                   [Remember The Milk](https://rememberthemilk.com) tasks and notes
  [my.smscalls](https://github.com/karlicoss/my/tree/master/my/smscalls.py)                         Phone calls and SMS messages
  [my.stackexchange](https://github.com/karlicoss/my/tree/master/my/stackexchange.py)               Stackexchange data
  [my.twitter.all](https://github.com/karlicoss/my/tree/master/my/twitter/all.py)                   Unified Twitter data (merged from the archive and periodic updates)
  [my.twitter.archive](https://github.com/karlicoss/my/tree/master/my/twitter/archive.py)           Twitter data (uses [official twitter archive export](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive))
  [my.twitter.twint](https://github.com/karlicoss/my/tree/master/my/twitter/twint.py)               Twitter data (tweets and favorites). Uses [Twint](https://github.com/twintproject/twint) data export.
  ------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------
:::

Some modules are private, and need a bit of cleanup before merging:

  ----------------- --------------------------------------------------------------------------------
  my.workouts       Exercise activity, from Endomondo and manual logs
  my.sleep.manual   Subjective sleep data, manually logged
  my.nutrition      Food and drink consumption data, logged manually from different sources
  my.money          Expenses and shopping data
  my.webhistory     Browsing history (part of [promnesia](https://github.com/karlicoss/promnesia))
  ----------------- --------------------------------------------------------------------------------

```{=html}
<div id="usecases"></div>
```
How do you use it?
==================

Mainly I use it as a data provider for my scripts, tools, and
dashboards.

Also, check out [my infrastructure
map](https://beepb00p.xyz/myinfra.html#mypkg). It's a draft at the
moment, but it might be helpful for understanding what's my vision on
HPI.

Instant search
--------------

Typical search interfaces make me unhappy as they are **siloed, slow,
awkward to use and don't work offline**. So I built my own ways around
it! I write about it in detail
[here](https://beepb00p.xyz/pkm-search.html#personal_information).

In essence, I'm mirroring most of my online data like chat logs,
comments, etc., as plaintext. I can overview it in any text editor, and
incrementally search over **all of it** in a single keypress.

orger
-----

[orger](https://github.com/karlicoss/orger) is a tool that helps you
generate an org-mode representation of your data.

It lets you benefit from the existing tooling and infrastructure around
org-mode, the most famous being Emacs.

I'm using it for:

-   searching, overviewing and navigating the data
-   creating tasks straight from the apps (e.g. Reddit/Telegram)
-   spaced repetition via
    [org-drill](https://orgmode.org/worg/org-contrib/org-drill.html)

Orger comes with some existing
[modules](https://github.com/orger/tree/master/modules), but it should
be easy to adapt your own data source if you need something else.

I write about it in detail [here](https://beepb00p.xyz/orger.html) and
[here](https://beepb00p.xyz/orger-todos.html).

promnesia
---------

[promnesia](https://github.com/karlicoss/promnesia#demo) is a browser
extension I'm working on to escape silos by **unifying annotations and
browsing history** from different data sources.

I've been using it for more than a year now and working on final
touches to properly release it for other people.

dashboard
---------

As a big fan of
[\#quantified-self](https://beepb00p.xyz/tags.html#quantified-self),
I'm working on personal health, sleep and exercise dashboard, built
from various data sources.

I'm working on making it public, you can see some screenshots
[here](https://www.reddit.com/r/QuantifiedSelf/comments/cokt4f/what_do_you_all_do_with_your_data/ewmucgk).

timeline
--------

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

Ad-hoc and interactive
======================

What were my music listening stats for 2018?
--------------------------------------------

Single import away from getting tracks you listened to:

``` {.python}
from my.lastfm import get_scrobbles
scrobbles = get_scrobbles()
scrobbles[200: 205]
```

``` {.example}
[Scrobble(raw={'album': 'Nevermind', 'artist': 'Nirvana', 'date': '1282488504', 'name': 'Drain You'}),
 Scrobble(raw={'album': 'Dirt', 'artist': 'Alice in Chains', 'date': '1282489764', 'name': 'Would?'}),
 Scrobble(raw={'album': 'Bob Dylan: The Collection', 'artist': 'Bob Dylan', 'date': '1282493517', 'name': 'Like a Rolling Stone'}),
 Scrobble(raw={'album': 'Dark Passion Play', 'artist': 'Nightwish', 'date': '1282493819', 'name': 'Amaranth'}),
 Scrobble(raw={'album': 'Rolled Gold +', 'artist': 'The Rolling Stones', 'date': '1282494161', 'name': "You Can't Always Get What You Want"})]
```

Or, as a pandas frame to make it pretty:

``` {.python}
import pandas as pd
df = pd.DataFrame([{
    'dt': s.dt,
    'track': s.track,
} for s in scrobbles])
cdf = df.set_index('dt')
cdf[200: 205]
```

``` {.example}
                                                                       track
dt                                                                          
2010-08-22 14:48:24+00:00                                Nirvana — Drain You
2010-08-22 15:09:24+00:00                           Alice in Chains — Would?
2010-08-22 16:11:57+00:00                   Bob Dylan — Like a Rolling Stone
2010-08-22 16:16:59+00:00                               Nightwish — Amaranth
2010-08-22 16:22:41+00:00  The Rolling Stones — You Can't Always Get What...
```

We can use [calmap](https://github.com/martijnvermaat/calmap) library to
plot a github-style music listening activity heatmap:

``` {.python}
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 2.3))

import calmap
cdf = cdf.set_index(cdf.index.tz_localize(None)) # calmap expects tz-unaware dates
calmap.yearplot(cdf['track'], how='count', year=2018)

plt.tight_layout()
plt.title('My music listening activity for 2018')
plot_file = 'lastfm_2018.png'
plt.savefig(plot_file)
plot_file
```

![](https://beepb00p.xyz/lastfm_2018.png)

This isn't necessarily very insightful data, but fun to look at now and
then!

What are the most interesting Slate Star Codex posts I've read?
----------------------------------------------------------------

My friend asked me if I could recommend them posts I found interesting
on [Slate Star Codex](https://slatestarcodex.com). With few lines of
Python I can quickly recommend them posts I engaged most with, i.e. the
ones I annotated most on [Hypothesis](https://hypothes.is).

``` {.python}
from my.hypothesis import get_pages
from collections import Counter
cc = Counter({(p.title + ' ' + p.url): len(p.highlights) for p in get_pages() if 'slatestarcodex' in p.url})
return cc.most_common(10)
```

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ----
  The Anti-Reactionary FAQ <http://slatestarcodex.com/2013/10/20/the-anti-reactionary-faq/>                                                                                               32
  Reactionary Philosophy In An Enormous, Planet-Sized Nutshell <https://slatestarcodex.com/2013/03/03/reactionary-philosophy-in-an-enormous-planet-sized-nutshell/>                       17
  The Toxoplasma Of Rage <http://slatestarcodex.com/2014/12/17/the-toxoplasma-of-rage/>                                                                                                   16
  What Universal Human Experiences Are You Missing Without Realizing It? <https://slatestarcodex.com/2014/03/17/what-universal-human-experiences-are-you-missing-without-realizing-it/>   16
  Meditations On Moloch <http://slatestarcodex.com/2014/07/30/meditations-on-moloch/>                                                                                                     12
  Universal Love, Said The Cactus Person <http://slatestarcodex.com/2015/04/21/universal-love-said-the-cactus-person/>                                                                    11
  Untitled <http://slatestarcodex.com/2015/01/01/untitled/>                                                                                                                               11
  Considerations On Cost Disease <https://slatestarcodex.com/2017/02/09/considerations-on-cost-disease/>                                                                                  10
  In Defense of Psych Treatment for Attempted Suicide <http://slatestarcodex.com/2013/04/25/in-defense-of-psych-treatment-for-attempted-suicide/>                                         9
  I Can Tolerate Anything Except The Outgroup <https://slatestarcodex.com/2014/09/30/i-can-tolerate-anything-except-the-outgroup/>                                                        9
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ----

Accessing exercise data
-----------------------

E.g. see use of `my.workouts`
[here](https://beepb00p.xyz/./heartbeats_vs_kcals.html).

Book reading progress
---------------------

I publish my reading stats on
[Goodreads](https://www.goodreads.com/user/show/22191391-dima-gerasimov)
so other people can see what I'm reading/have read, but Kobo [lacks
integration](https://beepb00p.xyz/ideas.html#kobo2goodreads) with
Goodreads. I'm using [kobuddy](https://github.com/karlicoss/kobuddy) to
access my my Kobo data, and I've got a regular task that reminds me to
sync my progress once a month.

The task looks like this:

``` {.org}
* TODO [#C] sync [[https://goodreads.com][reading progress]] with kobo
  DEADLINE: <2019-11-24 Sun .+4w -0d>
[[eshell: with_my python3 -c 'import my.books.kobo as kobo; kobo.print_progress()']]
```

With a single Enter keypress on the inlined `eshell:` command I can
print the progress and fill in the completed books on Goodreads, e.g.:

``` {.example}
A_Mathematician's_Apology by G. H. Hardy
Started : 21 Aug 2018 11:44
Finished: 22 Aug 2018 12:32

Fear and Loathing in Las Vegas: A Savage Journey to the Heart of the American Dream (Vintage) by Thompson, Hunter S.
Started : 06 Sep 2018 05:54
Finished: 09 Sep 2018 12:21

Sapiens: A Brief History of Humankind by Yuval Noah Harari
Started : 09 Sep 2018 12:22
Finished: 16 Sep 2018 07:25

Inadequate Equilibria: Where and How Civilizations Get Stuck by Eliezer Yudkowsky
Started : 31 Jul 2018 22:54
Finished: 16 Sep 2018 07:25

Albion Dreaming by Andy Roberts
Started : 20 Aug 2018 21:16
Finished: 16 Sep 2018 07:26
```

Messenger stats
---------------

How much do I chat on Facebook Messenger?

``` {.python}
from my.fbmessenger import messages

import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({'dt': m.dt, 'messages': 1} for m in messages())
df.set_index('dt', inplace=True)

df = df.resample('M').sum() # by month
df = df.loc['2016-01-01':'2019-01-01'] # past subset for determinism

fig, ax = plt.subplots(figsize=(15, 5))
df.plot(kind='bar', ax=ax)

# todo wonder if that vvv can be less verbose...
x_labels = df.index.strftime('%Y %b')
ax.set_xticklabels(x_labels)

plot_file = 'messenger_2016_to_2019.png'
plt.tight_layout()
plt.savefig(plot_file)
return plot_file
```

![](https://beepb00p.xyz/messenger_2016_to_2019.png)

Querying Roam Reasearch database
--------------------------------

I've got some code examples
[here](https://beepb00p.xyz/myinfra-roam.html#interactive).

How does it get input data?
===========================

If you're curious about any specific data sources I'm using, I've
written it up [in detail](https://beepb00p.xyz/my-data.html).

Also see [\"Data flow\"](doc/SETUP.org::#data-flow) documentation with
some nice diagrams explaining on specific examples.

In short:

-   The data is [periodically
    synchronized](https://beepb00p.xyz/myinfra.html#exports) from the
    services (cloud or not) locally, on the filesystem

    As a result, you get
    [JSONs/sqlite](https://beepb00p.xyz/myinfra.html#fs) (or other
    formats, depending on the service) on your disk.

    Once you have it, it's trivial to back it up and synchronize to
    other computers/phones, if necessary.

    To schedule periodic sync, I'm using
    [cron](https://beepb00p.xyz/scheduler.html#cron).

-   `my.` package only accesses the data on the filesystem

    That makes it extremely fast, reliable, and fully offline capable.

As you can see, in such a setup, the data is lagging behind the
'realtime'. I consider it a necessary sacrifice to make everything
fast and resilient.

In theory, it's possible to make the system almost realtime by having a
service that sucks in data continuously (rather than periodically), but
it's harder as well.

Q & A
=====

Why Python?
-----------

I don't consider Python unique as a language suitable for such a
project. It just happens to be the one I'm most comfortable with. I do
have some reasons that I think make it *specifically* good, but
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

Can anyone use it?
------------------

Yes!

-   you can plug in **your own data**

-   most modules are isolated, so you can only use the ones that you
    want to

-   everything is easily **extensible**

    Starting from simply adding new modules to any dynamic hackery you
    can possibly imagine within Python.

How easy is it to use?
----------------------

The whole setup requires some basic programmer literacy:

-   installing/running and potentially modifying Python code
-   using symlinks
-   potentially running Cron jobs

If you have any ideas on making the setup simpler, please let me know!

What about privacy?
-------------------

The modules contain **no data, only code** to operate on the data.

Everything is [**local first**](https://beepb00p.xyz/tags.html#offline),
the input data is on your filesystem. If you're truly paranoid, you can
even wrap it in a Docker container.

There is still a question of whether you trust yourself at even keeping
all the data on your disk, but it is out of the scope of this post.

If you'd rather keep some code private too, it's also trivial to
achieve with a private subpackage.

But *should* I use it?
----------------------

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

Would it suit *me*?
-------------------

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

What it isn't?
---------------

-   It's not vaporwave

    The project is a little crude, but it's real and working. I've
    been using it for a long time now, and find it fairly sustainable to
    keep using for the foreseeable future.

-   It's not going to be another silo

    While I don't have anything against commercial use (and I believe
    any work in this area will benefit all of us), I'm not planning to
    build a product out of it.

    I really hope it can grow into or inspire some mature open source
    system.

    Please take my ideas and code and build something cool from it!

Related links
=============

Similar projects:

-   [Memacs](https://github.com/novoid/Memacs) by Karl Voit

-   [Me API - turn yourself into an open API
    (HN)](https://news.ycombinator.com/item?id=9615901)

-   [QS ledger](https://github.com/markwk/qs_ledger) from Mark Koester

-   [tehmantra/my](https://github.com/tehmantra/my): directly inspired
    by this package

-   [bcongdon/bolero](https://github.com/bcongdon/bolero)

-   [Solid
    project](https://en.wikipedia.org/wiki/Solid_(web_decentralization_project)#Design):
    personal data pod, which websites pull data from

Other links:

-   NetOpWibby: [A Personal API
    (HN)](https://news.ycombinator.com/item?id=21684949)
-   [The sad state of personal data and
    infrastructure](https://beepb00p.xyz/sad-infra.html): here I am
    going into motivation and difficulties arising in the implementation

---

Open to any feedback and thoughts!

Also, don't hesitate to raise an issue, or reach me personally if you
want to try using it, and find the instructions confusing. Your
questions would help me to make it simpler!

In some near future I will write more about:

-   specific technical decisions and patterns
-   challenges I had so solve
-   more use-cases and demos -- it's impossible to fit everything in
    one post!

, but happy to answer any questions on these topics now!
