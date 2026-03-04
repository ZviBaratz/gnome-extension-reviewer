# Field test #10: prototype-override deduplication (closes #28)

# --- proto-override-dedup (each prototype warned only once) ---
echo "=== proto-override-dedup ==="
run_lint "proto-override-dedup@test"
assert_output_contains "prototype override detected" "\[WARN\].*lifecycle/prototype-override.*BackgroundMenu.prototype.open"
assert_output_contains "search prototype override detected" "\[WARN\].*lifecycle/prototype-override.*SearchController.prototype.startSearch"
echo ""
