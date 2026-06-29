#!/usr/bin/env python3
import sys
import pytest

if __name__ == "__main__":
    sys.exit(pytest.main([
        #"unit/loginTest.py",
        "test/unit/registrationTest.py",
        #"integration/smokeIT.py",
        #"integration/logoutIT.py",
        "-v",
    ]))
