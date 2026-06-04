#!/usr/bin/env bash
set -euo pipefail

if (($# == 0)); then
  exit 0
fi

if ! command -v mjml >/dev/null 2>&1; then
  echo "mjml is required to compile changed email templates. Install it with \`npm install -g mjml\`." >&2
  exit 1
fi

for mjml_file in "$@"; do
  directory="$(dirname "$mjml_file")"
  stem="$(basename "$mjml_file" .mjml)"
  generated_file="$directory/_generated_dont_edit_$stem.html"

  mjml "$mjml_file" -o "$generated_file"

  if ! git ls-files --error-unmatch -- "$generated_file" >/dev/null 2>&1; then
    echo "Generated email template is not staged: $generated_file" >&2
    echo "Run \`git add $generated_file\` and commit again." >&2
    exit 1
  fi
done
