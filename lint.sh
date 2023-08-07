#!/usr/bin/env bash
isort --profile black -l 125 . && black . && ruff . --fix --show-fixes