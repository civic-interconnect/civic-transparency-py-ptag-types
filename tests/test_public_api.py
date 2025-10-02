# tests/test_public_api.py
def test_public_api_surface():
    import ci.transparency.ptag.types as t

    expected = {"PTag", "PTagSeries", "PTagInterval"}  # Fixed: was {"Series", "PTag"}
    assert expected.issubset(set(getattr(t, "__all__", [])))

    for name in expected:
        obj = getattr(t, name)
        assert obj is not None, f"{name} should exist"

def test_version_present_and_string():
    from ci.transparency.ptag.types import __version__  # type: ignore

    assert isinstance(__version__, str) and __version__
