target="@dev/test-stack"
if [[ "$target" != @*/* ]]; then
  echo "Error: Must specify zone, e.g. @dev/stack-name"
fi
zone=$(echo "$target" | cut -d'/' -f1)
stack=$(echo "$target" | cut -d'/' -f2)
echo "Zone: $zone, Stack: $stack"
