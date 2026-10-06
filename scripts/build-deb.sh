#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

for command in cargo dpkg dpkg-deb python3 sha256sum; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

VERSION="${NATIVEPAIR_VERSION:-}"
if [[ -z "$VERSION" ]]; then
  VERSION="$(
    cargo metadata --locked --no-deps --format-version 1 |
      python3 -c 'import json, sys; data = json.load(sys.stdin); print(next(p["version"] for p in data["packages"] if p["name"] == "nativepair-core"))'
  )"
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then
  echo "Invalid package version: $VERSION" >&2
  exit 1
fi

ARCH="${DEB_ARCH:-$(dpkg --print-architecture)}"
case "$ARCH" in
  amd64|arm64)
    ;;
  *)
    echo "Unsupported Debian architecture: $ARCH" >&2
    exit 1
    ;;
esac

ARTIFACTS_DIR="${NATIVEPAIR_ARTIFACTS_DIR:-$ROOT_DIR/artifacts}"
BUILD_ROOT="${NATIVEPAIR_PACKAGE_BUILD_DIR:-$ROOT_DIR/target/package/nativepair}"
PACKAGE_ROOT="$BUILD_ROOT/root"
PACKAGE_NAME="nativepair_${VERSION}_${ARCH}.deb"
PACKAGE_PATH="$ARTIFACTS_DIR/$PACKAGE_NAME"

rm -rf "$BUILD_ROOT"
mkdir -p "$PACKAGE_ROOT/DEBIAN" "$ARTIFACTS_DIR"

cargo build --release --locked -p nativepair-cli -p nativepair-daemon

install -Dm755 "$ROOT_DIR/target/release/nativepair"   "$PACKAGE_ROOT/usr/bin/nativepair"
install -Dm755 "$ROOT_DIR/target/release/nativepair-daemon"   "$PACKAGE_ROOT/usr/libexec/nativepair-daemon"

install -Dm644 "$ROOT_DIR/LICENSE"   "$PACKAGE_ROOT/usr/share/doc/nativepair/LICENSE"
install -Dm644 "$ROOT_DIR/NOTICE"   "$PACKAGE_ROOT/usr/share/doc/nativepair/NOTICE"
install -Dm644 "$ROOT_DIR/README.md"   "$PACKAGE_ROOT/usr/share/doc/nativepair/README.md"

sed   -e "s/@VERSION@/$VERSION/g"   -e "s/@ARCH@/$ARCH/g"   "$ROOT_DIR/packaging/debian/control.in"   > "$PACKAGE_ROOT/DEBIAN/control"

installed_size="$(du -sk "$PACKAGE_ROOT/usr" | awk '{print $1}')"
printf 'Installed-Size: %s\n' "$installed_size" >> "$PACKAGE_ROOT/DEBIAN/control"

if [[ -z "${SOURCE_DATE_EPOCH:-}" ]] && command -v git >/dev/null 2>&1; then
  SOURCE_DATE_EPOCH="$(git log -1 --format=%ct 2>/dev/null || true)"
fi
if [[ -n "${SOURCE_DATE_EPOCH:-}" ]]; then
  export SOURCE_DATE_EPOCH
  while IFS= read -r -d '' path; do
    touch -h -d "@$SOURCE_DATE_EPOCH" "$path"
  done < <(find "$PACKAGE_ROOT" -print0)
fi

rm -f "$PACKAGE_PATH" "$PACKAGE_PATH.sha256"
dpkg-deb --root-owner-group --build "$PACKAGE_ROOT" "$PACKAGE_PATH" >/dev/null

(
  cd "$ARTIFACTS_DIR"
  sha256sum "$PACKAGE_NAME" > "$PACKAGE_NAME.sha256"
)

printf '%s\n' "$PACKAGE_PATH"
