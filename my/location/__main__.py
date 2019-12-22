import sys
import logging

from .takeout import get_logger, get_locations, iter_locations, get_groups

from kython.klogging import setup_logzero


# TODO remove this?
def main():
    logger = get_logger()
    setup_logzero(logger, level=logging.DEBUG)


    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        # TODO ok, update cache makes sense just to refresh in case of code changes...
        # TODO don't even need it anymore? cachew handles this..
        if cmd == "update_cache":
            from .takeout import update_cache, get_locations
            update_cache()
        else:
            raise RuntimeError(f"Unknown command {cmd}")
    else:
        for p in get_groups():
            print(p)
            # shit. ok, 4 gigs of ram is def too much for glumov...
            # TODO need datetime!

if __name__ == '__main__':
    main()
