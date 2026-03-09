# Compiled TypeScript layout: file-structure checks should be skipped

echo "=== compiled-typescript-layout ==="
run_lint "compiled-typescript-layout@test"
assert_output_contains "compiled TS detected" "\[WARN\].*compiled-typescript"
assert_output_contains "file-structure skipped for compiled TS" "\[SKIP\].*file-structure/extension.js"
assert_output_contains "metadata.json skipped for compiled TS" "\[SKIP\].*file-structure/metadata.json"
echo ""
