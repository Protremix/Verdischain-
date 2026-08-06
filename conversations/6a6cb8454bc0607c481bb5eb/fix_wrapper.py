import sys

with open("/dev/stdin") as f:
    content = f.read()

old_wrapper = """/// A wrapper around BabeWorker that logs when poll returns Ready
struct BabeWorkerDebugWrapper<B: sp_runtime::traits::BlockT> {
    inner: sc_consensus_babe::BabeWorker<B>,
    poll_count: std::sync::atomic::AtomicU64,
}

impl<B: sp_runtime::traits::BlockT> Future for BabeWorkerDebugWrapper<B> {
    type Output = ();

    fn poll(mut self: std::pin::Pin<&mut Self>, cx: &mut std::task::Context) -> std::task::Poll<Self::Output> {
        let count = self.poll_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        if count < 5 {
            eprintln!("BabeWorkerDebugWrapper: poll #{}", count);
        }
        let result = std::pin::Pin::new(&mut self.inner).poll(cx);
        match &result {
            std::task::Poll::Ready(()) => {
                eprintln!("BabeWorkerDebugWrapper: BABE WORKER RETURNED READY after {} polls", count);
                eprintln!("BabeWorkerDebugWrapper: This means the infinite loop exited!");
                std::task::Poll::Ready(())
            }
            std::task::Poll::Pending => {
                if count < 5 {
                    eprintln!("BabeWorkerDebugWrapper: poll returned Pending");
                }
                std::task::Poll::Pending
            }
        }
    }
}"""

new_wrapper = """/// A wrapper around BabeWorker that logs when poll returns Ready
struct BabeWorkerDebugWrapper {
    inner: sc_consensus_babe::BabeWorker<Block>,
    poll_count: std::sync::atomic::AtomicU64,
}

impl std::future::Future for BabeWorkerDebugWrapper {
    type Output = ();

    fn poll(
        mut self: std::pin::Pin<&mut Self>,
        cx: &mut std::task::Context,
    ) -> std::task::Poll<Self::Output> {
        let count = self.poll_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        if count < 5 {
            eprintln!("BabeWorkerDebugWrapper: poll #{}", count);
        }
        let result = std::pin::Pin::new(&mut self.inner).poll(cx);
        match &result {
            std::task::Poll::Ready(()) => {
                eprintln!("BabeWorkerDebugWrapper: BABE WORKER RETURNED READY after {} polls", count);
                eprintln!("BabeWorkerDebugWrapper: This means the infinite loop exited!");
                std::task::Poll::Ready(())
            }
            std::task::Poll::Pending => {
                if count < 5 {
                    eprintln!("BabeWorkerDebugWrapper: poll returned Pending");
                }
                std::task::Poll::Pending
            }
        }
    }
}"""

content = content.replace(old_wrapper, new_wrapper)

with open("/tmp/service_fixed.rs", "w") as f:
    f.write(content)
print("OK")
