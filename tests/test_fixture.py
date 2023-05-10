from typing import Any

pytest_plugins = ["pytester"]


def test_fixture_is_present(pytester: Any) -> None:
    pytester.makepyfile(
        """
        def test_fixture(smtpd):
            assert smtpd
        """)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
