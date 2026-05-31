#!/usr/bin/env bash
set -euo pipefail

REPO=${1:-.}
if [[ ! -d "${REPO}" ]]; then
  echo "ERROR: repository directory does not exist: ${REPO}" >&2
  exit 2
fi
REPO=$(cd "${REPO}" && pwd)
cd "${REPO}"

draft_patterns=(
  "NewSection_*.md"
  "NewSection_3.4.md"
  "NewSection_3.4_Revised*.md"
  "NewSection_3.4_*Instructions.md"
)

drafts=()
for pattern in "${draft_patterns[@]}"; do
  for draft in ${pattern}; do
    if [[ -e "${draft}" ]]; then
      drafts+=("${draft}")
    fi
  done
done
if (( ${#drafts[@]} > 0 )); then
  printf 'ERROR: manuscript draft files must not be present in the repository root:\n' >&2
  printf '  %s\n' "${drafts[@]}" >&2
  exit 1
fi

macos_abs_path_pattern="/""Users/"
linux_abs_path_pattern="/""home/"
username_pattern="rostyslav""sipakov"
if git grep -nIF -e "${username_pattern}" -e "${macos_abs_path_pattern}" -e "${linux_abs_path_pattern}" -- .; then
  echo "ERROR: local username or absolute user-home path strings remain in tracked files." >&2
  exit 1
fi

if git ls-files | grep -E '(^|/)copy_section|(^|/)publish_section|(^|/)run_section'; then
  echo "ERROR: maintainer-only copy/publish/run scripts are still tracked." >&2
  exit 1
fi

echo "Privacy cleanup verification passed."
echo "  no manuscript drafts in repository root"
echo "  no local username or absolute user-home path strings in tracked files"
echo "  no maintainer-only copy/publish/run scripts tracked"
