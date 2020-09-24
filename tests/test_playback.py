def test_mpv():
    from my.mpv import history, Media

    histoire = list(history())
    assert len(histoire) > 1
    play = histoire[0]
    assert isinstance(play, Media)
    # just test an attr
    assert len(play.path) > 0
