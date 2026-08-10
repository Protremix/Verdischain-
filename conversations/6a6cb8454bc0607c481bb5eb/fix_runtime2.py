import re

# Fix runtime: map_or not available on &RuntimeCall
with open("/opt/verdis-chain-rust/runtime/src/lib.rs", "r") as f:
    content = f.read()

# The call parameter is Box<RuntimeCall>, not Option<Box<RuntimeCall>>
# call.as_ref() returns &RuntimeCall, not Option<&RuntimeCall>
# Just call Self::contains directly
content = content.replace(
    "call.as_ref().map_or(true, |c| Self::contains(c))",
    "Self::contains(call.as_ref())"
)

with open("/opt/verdis-chain-rust/runtime/src/lib.rs", "w") as f:
    f.write(content)
print("Runtime: scheduler call filter fixed")
