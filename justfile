set shell := ["bash", "-uc"]

source_ref := `grep '^ref:' .loadout.yaml | awk '{print $2}'`
source_url := `grep '^source:' .loadout.yaml | awk '{print $2}'`
loadout := "uvx --from git+" + source_url + "@" + source_ref + " loadout"

default:
    @just --list

# Install npm dependencies from the lockfile
install:
    npm ci

# Run the unit test suite
test:
    npm test

# Same steps GitHub Actions runs
ci: install test

# Register this checkout as an omp plugin
plugin-install:
    omp plugin install .

# Copy the telemetry-probe fixture into the local omp skills dir
install-fixture:
    mkdir -p "{{env_var('HOME')}}/.omp/agent/skills/telemetry-probe"
    cp test/fixtures/telemetry-probe/SKILL.md "{{env_var('HOME')}}/.omp/agent/skills/telemetry-probe/SKILL.md"

# One-shot omp run that loads this plugin from the checkout
probe: install-fixture
    omp --no-extensions -e "$PWD/src/main.ts" -p "read skill://telemetry-probe and follow it"

# Apply the pinned rules and skills to this repo
loadout-sync:
    {{loadout}} sync

# Fail if vendored agent files do not match the lockfile
loadout-check:
    {{loadout}} sync --check

# Bump to the latest release and re-sync
loadout-update:
    {{loadout}} update

# List what the current manifest resolves to
loadout-list:
    {{loadout}} resolve --list
