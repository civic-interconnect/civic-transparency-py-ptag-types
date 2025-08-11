# tests/test_public_api.py


def test_public_api_surface():
    import ci.transparency.types as t

    expected = {"Meta", "Run", "Scenario", "Series", "ProvenanceTag"}
    # __all__ exists and contains the public names
    assert expected.issubset(set(getattr(t, "__all__", [])))

    # Touch each symbol so the re-export lines count as covered
    for name in expected:
        obj = getattr(t, name)
        assert isinstance(obj, type), f"{name} should be a class"


def test_version_present_and_string():
    from ci.transparency.types import __version__ # type: ignore

    assert isinstance(__version__, str) and __version__
