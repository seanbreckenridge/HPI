"""
Config file used for testing in CI; so that config is defined
"""


import tempfile
from pathlib import Path
from typing import Optional, List, Sequence, Callable

from os import environ, path

from my.core.common import PathIsh, Paths


class core:
    cache_dir: PathIsh = path.join(environ["HOME"], ".cache", "cachew")
    tmp_dir: PathIsh = path.join(tempfile.gettempdir(), "HPI-tempdir")
    enabled_modules: Sequence[str] = []
    disabled_modules: Sequence[str] = []


class mail:
    class imap:
        mailboxes: Paths = ""
        # filter function which filters the input paths
        filter_path: Optional[Callable[[Path], bool]] = None

    class mbox:
        mailboxes: Paths = ""
        exclude_extensions = ()


class zsh:
    export_path: Paths = ""
    live_file: Optional[PathIsh] = ""


class bash:
    export_path: Paths = ""


class todotxt:
    class git_history:
        export_path: Paths = ""


class rss:
    class newsboat:
        class git_history:
            export_path: Paths = ""


class mpv:
    class history_daemon:
        export_path: Paths = ""


class league:
    class export:
        export_path: Paths = ""
        username = ""


class chess:
    class export:
        export_path: Paths = ""


class listenbrainz:
    class export:
        export_path: Paths = ""


class trakt:
    class export:
        export_path: Paths = ""


class mal:
    class export:
        export_path: PathIsh = ""


class grouvee:
    class export:
        export_path: Paths = ""


class nextalbums:
    export_path: Paths = ""


class steam:
    class scraper:
        export_path: Paths = ""


class piazza:
    class scraper:
        export_path: Paths = ""


class blizzard:
    class gdpr:
        export_path: Paths = ""


class project_euler:
    export_path: Paths = ""


class skype:
    class gdpr:
        export_path: Paths = ""


class facebook:
    class gdpr:
        gdpr_dir: PathIsh = ""


class spotify:
    class gdpr:
        gdpr_dir: PathIsh = ""


class twitch:
    class overrustle:
        export_path: Paths = ""

    class gdpr:
        gdpr_dir: PathIsh = ""


class ipython:
    export_path: Paths = ""


class ttt:
    export_path: Paths = ""


class window_watcher:
    export_path: Paths = ""
    force_individual: Optional[List[str]] = None


class apple:
    class privacy_export:
        gdpr_dir: PathIsh = ""


class linkedin:
    class privacy_export:
        gdpr_dir: PathIsh = ""


class discord:
    class data_export:
        export_path: Paths = ""


class runelite:
    class screenshots:
        export_path: Paths = ""


class minecraft:
    class advancements:
        export_path: Paths = ""


class time:
    class tz:
        policy = "convert"
