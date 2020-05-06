#!/usr/bin/env bash

cd "$(dirname $0)"/..
poetry run covid19pr \
  --config-file config/localhost.toml \
  --output-dir output \
  --bulletin-date 2020-05-03