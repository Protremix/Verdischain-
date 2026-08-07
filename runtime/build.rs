use substrate_wasm_builder::WasmBuilder;

fn main() {
    WasmBuilder::new()
        .with_current_project()
        .export_heap_base()
        .append_to_rust_flags("-C link-arg=--allow-undefined")
        .append_to_rust_flags("--cfg getrandom_backend=\"custom\"")
        .build();
}
