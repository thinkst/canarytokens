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

while IFS= read -r mjml_file; do
  output_file="$(dirname "$mjml_file")/_generated_dont_edit_$(basename "$mjml_file" .mjml).html"

  mjml "$mjml_file" -o "$output_file"

  if [[ -z "$(git ls-files --cached -- "$output_file")" ]]; then
    echo "Generated email template is not staged: $output_file" >&2
    echo "Run \`git add $output_file\` and commit again." >&2
    exit 1
  fi
done <<< "$staged_mjml_files"
