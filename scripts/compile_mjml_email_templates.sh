#!/usr/bin/env bash
set -euo pipefail

staged_mjml_files="$(git diff --cached --name-only --diff-filter=ACMR -- '*.mjml')"

if [[ -z "$staged_mjml_files" ]]; then
  exit 0
fi

if ! command -v mjml >/dev/null 2>&1; then
  echo "mjml is required to compile changed email templates. Install it with \`npm install -g mjml\`." >&2
  exit 1
fi

missing_generated_files=""

while IFS= read -r mjml_file; do
  output_file="$(dirname "$mjml_file")/_generated_dont_edit_$(basename "$mjml_file" .mjml).html"

  mjml "$mjml_file" -o "$output_file"

  if [[ -z "$(git ls-files --cached -- "$output_file")" ]]; then
    missing_generated_files="${missing_generated_files}${output_file}"$'\n'
  fi
done <<< "$staged_mjml_files"

if [[ -n "$missing_generated_files" ]]; then
  echo "Generated email templates are not staged:"
  printf "%s" "$missing_generated_files"
  echo "Run \`git add\` for the generated HTML files and commit again."
  exit 1
fi
