from more_itertools import ilen

from my.spotify import playlists, songs, Playlist, Song


def test_spotify():
    items = list(playlists())
    assert len(items) > 0
    plist = items[0]
    assert isinstance(plist, Playlist)
    songs = plist.songs
    assert len(songs) > 0
    assert isinstance(songs[0], Song)


def test_songs():
    assert ilen(songs()) > 1
