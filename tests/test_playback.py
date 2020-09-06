def test_playback():
    from my.media.playback import history, Media

    histoire = list(history())
    assert len(histoire) > 1
    play = histoire[0]
    assert isinstance(play, Media)
    # just test an attr
    assert len(play.path) > 0
