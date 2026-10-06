#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <nativepair.deb>" >&2
  exit 2
fi

PACKAGE_PATH="$(readlink -f "$1")"
if [[ ! -f "$PACKAGE_PATH" ]]; then
  echo "Package not found: $PACKAGE_PATH" >&2
  exit 1
fi

for command in dpkg-deb sha256sum; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

SIDE_CAR="$PACKAGE_PATH.sha256"
if [[ ! -f "$SIDE_CAR" ]]; then
  echo "Checksum sidecar not found: $SIDE_CAR" >&2
  exit 1
fi

(
  cd "$(dirname "$PACKAGE_PATH")"
  sha256sum --check "$(basename "$SIDE_CAR")"
)

assert_field() {
  local field="$1"
  local expected="$2"
  local actual

  actual="$(dpkg-deb --field "$PACKAGE_PATH" "$field")"
  if [[ "$actual" != "$expected" ]]; then
    echo "Unexpected $field: expected '$expected', got '$actual'" >&2
    exit 1
  fi
}

assert_field Package nativepair

version="$(dpkg-deb --field "$PACKAGE_PATH" Version)"
if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then
  echo "Invalid Debian package version: $version" >&2
  exit 1
fi

architecture="$(dpkg-deb --field "$PACKAGE_PATH" Architecture)"
case "$architecture" in
  amd64|arm64)
    ;;
  *)
    echo "Unexpected Debian package architecture: $architecture" >&2
    exit 1
    ;;
esac

depends="$(dpkg-deb --field "$PACKAGE_PATH" Depends)"
dependency_present() {
  local dependency="$1"

  tr ',' '\n' <<<"$depends" |
    sed 's/^[[:space:]]*//' |
    grep -Eq "^$dependency([[:space:](]|$)"
}

for dependency in bluez bluez-obexd; do
  if ! dependency_present "$dependency"; then
    echo "Missing runtime dependency in package metadata: $dependency" >&2
    exit 1
  fi
done

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

dpkg-deb --extract "$PACKAGE_PATH" "$TEMP_DIR"

test -x "$TEMP_DIR/usr/bin/nativepair"
test -x "$TEMP_DIR/usr/libexec/nativepair-daemon"
test -f "$TEMP_DIR/usr/share/doc/nativepair/LICENSE"
test -f "$TEMP_DIR/usr/share/doc/nativepair/NOTICE"
test -f "$TEMP_DIR/usr/share/doc/nativepair/README.md"

"$TEMP_DIR/usr/bin/nativepair" --version
"$TEMP_DIR/usr/libexec/nativepair-daemon" --version

echo "Debian package verification passed: $(basename "$PACKAGE_PATH")"
