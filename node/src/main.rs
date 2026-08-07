//! Verdis Chain Node

mod chain_spec;
mod cli;
mod command;
mod rpc;
mod service;

fn main() -> sc_cli::Result<()> {
    // Install panic hook to capture BABE worker panics
    let default_hook = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |info| {
        let location = info.location().map(|l| format!("{}:{}", l.file(), l.line())).unwrap_or_default();
        let payload = info.payload().downcast_ref::<&str>().copied()
            .or_else(|| info.payload().downcast_ref::<String>().map(|s| s.as_str()))
            .unwrap_or("<non-string panic payload>");
        eprintln!("=== PANIC CAPTURED ===");
        eprintln!("Location: {}", location);
        eprintln!("Payload: {}", payload);
        eprintln!("Backtrace: {}", std::backtrace::Backtrace::force_capture());
        eprintln!("=== END PANIC ===");
        default_hook(info);
    }));

    command::run()
}
