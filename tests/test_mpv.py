from my.mpv import history, all_history, Media


def test_mpv():

    hist = list(history())
    all_hist = list(all_history())
    assert len(hist) > 1
    play = hist[0]
    assert isinstance(play, Media)
    # just test an attr
    assert len(play.path) > 0
    assert len(all_hist) > len(hist)
