#!/usr/bin/env python3
"""Fix service.rs: remove debug wrapper, keep babe_worker_handle alive."""

with open("/opt/verdis-chain/node/src/service.rs") as f:
    content = f.read()

# Remove the debug wrapper struct (lines 20-49 approximately)
wrapper_start = content.find("/// A wrapper around BabeWorker that logs when poll returns Ready")
wrapper_end = content.find("\n\n", content.find("}", wrapper_start + 100))
if wrapper_start >= 0 and wrapper_end >= 0:
    content = content[:wrapper_start] + content[wrapper_end+2:]
    print("Removed debug wrapper")
else:
    print("WARNING: Could not find debug wrapper")

# Replace the debug spawn with original spawn
old_spawn = """        // Wrap babe future with debug wrapper
        let babe_debug = BabeWorkerDebugWrapper {
            inner: babe,
            poll_count: std::sync::atomic::AtomicU64::new(0),
        };
        task_manager
            .spawn_essential_handle()
            .spawn("babe", Some("block-authoring"), babe_debug);"""

new_spawn = """        task_manager
            .spawn_essential_handle()
            .spawn("babe", Some("block-authoring"), babe);"""

content = content.replace(old_spawn, new_spawn)
print("Replaced debug spawn with normal spawn")

# Add std::mem::forget(babe_worker_handle) before the final Ok(task_manager)
# Find the end of new_full function
old_end = """    Ok(task_manager)
}"""
new_end = """    // Keep the BABE worker handle alive for the lifetime of the node.
    // If this handle is dropped, the babe-worker background task exits,
    // causing an "Essential task failed" shutdown.
    std::mem::forget(babe_worker_handle);

    Ok(task_manager)
}"""

content = content.replace(old_end, new_end, 1)  # Only replace the first occurrence (end of new_full)
print("Added mem::forget(babe_worker_handle)")

with open("/opt/verdis-chain/node/src/service.rs", "w") as f:
    f.write(content)
print("Done")
