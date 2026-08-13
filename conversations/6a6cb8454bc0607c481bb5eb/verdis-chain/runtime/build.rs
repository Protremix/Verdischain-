fn main() {
    substrate_wasm_builder::WasmBuilder::new()
        .with_current_project()
        .export_heap_base()
        .append_to_rust_flags("-C link-arg=--allow-undefined")
        .build();
}
