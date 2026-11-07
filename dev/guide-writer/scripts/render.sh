#!/usr/bin/env bash
# render.sh — render a /write-guide guide (spec write-guide, REQ-19–21).
#
#   render.sh <guide.html> <output-name>
#
# Writes <output-name>.pdf (WeasyPrint) and <output-name>.docx (pandoc, for
# copying prompts) beside the HTML, and contact sheets of the PDF's pages under
# ${TMPDIR:-/tmp}/write-guide-qa/<output-name>/ for the page-by-page check.
# Refuses an HTML file inside this repository: guides hold personal details.
set -euo pipefail

die() { echo "render.sh: $*" >&2; exit 2; }

[ $# -eq 2 ] || die "usage: render.sh <guide.html> <output-name>"
html=$1
name=$2
[ -f "$html" ] || die "no such file: $html"
case "$name" in
  ""|*/*|.*) die "output name must be a plain file name without a path: '$name'" ;;
esac

# REQ-20: never inside the repository this script belongs to.
script_dir=$(cd "$(dirname "$0")" && pwd -P)
repo=$(git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null || true)
out_dir=$(cd "$(dirname "$html")" && pwd -P)
if [ -n "$repo" ]; then
  repo=$(cd "$repo" && pwd -P)
  case "$out_dir/" in
    "$repo"/*) die "refusing to write inside the repository ($out_dir): guides hold personal details. Save the guide outside it, e.g. ~/Downloads/BodhiKit-<name>-guide/" ;;
  esac
fi

# REQ-21: name every missing tool at once.
missing=""
for tool in weasyprint pandoc pdftoppm magick; do
  command -v "$tool" >/dev/null 2>&1 || missing="$missing $tool"
done
if [ -n "$missing" ]; then
  die "missing tool(s):$missing. On a Mac: brew install weasyprint pandoc poppler imagemagick"
fi

pdf="$out_dir/$name.pdf"
docx="$out_dir/$name.docx"

weasyprint "$html" "$pdf"
pandoc "$html" --from html --to docx --output "$docx"

qa="${TMPDIR:-/tmp}"
qa="${qa%/}/write-guide-qa/$name"
mkdir -p "$qa"
find "$qa" -maxdepth 1 -type f \( -name 'p-*.png' -o -name 'sheet-*.png' \) -delete
pdftoppm -r 50 -png "$pdf" "$qa/p"
magick montage "$qa"/p-*.png -tile 7x2 -geometry +4+4 "$qa/sheet-%02d.png"

pages=$(pdfinfo "$pdf" 2>/dev/null | awk '/^Pages:/ {print $2}')
echo "PDF:  $pdf (${pages:-?} pages)"
echo "DOCX: $docx"
echo "Contact sheets: $qa/sheet-*.png (14 pages each). Read every one; for a closer look: pdftoppm -r 80 -png -f N -l N \"$pdf\" <prefix>"
