import re

# Fix runtime: Box field access in CallFilter
with open("/opt/verdis-chain-rust/runtime/src/lib.rs", "r") as f:
    content = f.read()

# The Scheduler call parameter is Box<RuntimeCall>, not a tuple
# Fix: use call.as_ref() instead of call.0.as_ref()
content = content.replace(
    "call.0.as_ref().map_or(true, |c| Self::contains(c))",
    "call.as_ref().map_or(true, |c| Self::contains(c))"
)

with open("/opt/verdis-chain-rust/runtime/src/lib.rs", "w") as f:
    f.write(content)
print("Runtime: Box field access fixed")
