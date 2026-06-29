#!/usr/bin/env python3
import sys
import pytest

if __name__ == "__main__":
    sys.exit(pytest.main([
        "test/unit/loginTest.py",
        "test/unit/registrationTest.py",
        "test/integration/smokeIT.py",
        "test/integration/logoutIT.py",
        "test/integration/eventsIT.py",
        "-v",
    ]))
