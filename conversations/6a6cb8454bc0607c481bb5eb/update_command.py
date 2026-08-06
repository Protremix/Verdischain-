#!/usr/bin/env python3
"""Update command.rs to handle BenchmarkCmd."""

with open("/opt/verdis-chain/node/src/command.rs") as f:
    content = f.read()

# Add benchmark handling before the None => case
old_none = """        None => {"""
new_bench = """        Some(Subcommand::Benchmark(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| {
                let PartialComponents { client, backend, .. } = service::new_partial(&config)?;
                let db = backend.expose_db();
                let storage = backend.expose_storage();

                match cmd {
                    frame_benchmarking_cli::BenchmarkCmd::Pallet(cmd) => {
                        cmd.run_with_storage_provider(
                            &*client,
                            db.unwrap(),
                            storage.unwrap(),
                            &config,
                        )
                    }
                    _ => Err(sc_cli::Error::Input("Unsupported benchmark command".into())),
                }
            })
        }
        None => {"""

if "Subcommand::Benchmark" not in content:
    content = content.replace(old_none, new_bench)
    with open("/opt/verdis-chain/node/src/command.rs", "w") as f:
        f.write(content)
    print("Updated command.rs with Benchmark handling")
else:
    print("Already has benchmark handling")
