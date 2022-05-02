from .common import Results


def events() -> Results:
    # comment out any sources you're not using
    from .gdpr import events as gdpr_events
    from .overrustle_logs import events as chatlog_events

    yield from chatlog_events()
    yield from gdpr_events()


from my.core import Stats


def stats() -> Stats:
    from my.core import stat

    return {**stat(events)}
