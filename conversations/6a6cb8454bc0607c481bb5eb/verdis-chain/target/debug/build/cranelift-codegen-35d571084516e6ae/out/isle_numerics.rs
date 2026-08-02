#[macro_export] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:881
#[doc(hidden)] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:882
macro_rules! isle_numerics_methods {
    () => {
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i8> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i8> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i8> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i8> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i8> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i8> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i8> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i8_matches_zero(&mut self, a: i8) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i8_matches_non_zero(&mut self, a: i8) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i8_matches_odd(&mut self, a: i8) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i8_matches_even(&mut self, a: i8) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_checked_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i8> {
            a.checked_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_wrapping_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.wrapping_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i8_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i8 {
            a.checked_neg().unwrap_or_else(|| panic!("negation overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u8> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u8> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u8> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u8> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u8> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u8> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u8> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u8 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u8_matches_zero(&mut self, a: u8) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u8_matches_non_zero(&mut self, a: u8) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u8_matches_odd(&mut self, a: u8) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u8_matches_even(&mut self, a: u8) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u8_is_power_of_two( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a.is_power_of_two() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u8_matches_power_of_two(&mut self, a: u8) -> Option<bool> {
            Some(a.is_power_of_two()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i16> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i16> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i16> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i16> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i16> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i16> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i16> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i16_matches_zero(&mut self, a: i16) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i16_matches_non_zero(&mut self, a: i16) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i16_matches_odd(&mut self, a: i16) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i16_matches_even(&mut self, a: i16) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_checked_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i16> {
            a.checked_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_wrapping_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.wrapping_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i16_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i16 {
            a.checked_neg().unwrap_or_else(|| panic!("negation overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u16> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u16> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u16> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u16> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u16> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u16> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u16> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u16 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u16_matches_zero(&mut self, a: u16) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u16_matches_non_zero(&mut self, a: u16) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u16_matches_odd(&mut self, a: u16) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u16_matches_even(&mut self, a: u16) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u16_is_power_of_two( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a.is_power_of_two() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u16_matches_power_of_two(&mut self, a: u16) -> Option<bool> {
            Some(a.is_power_of_two()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i32> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i32> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i32> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i32> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i32> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i32> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i32> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i32_matches_zero(&mut self, a: i32) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i32_matches_non_zero(&mut self, a: i32) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i32_matches_odd(&mut self, a: i32) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i32_matches_even(&mut self, a: i32) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_checked_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i32> {
            a.checked_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_wrapping_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.wrapping_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i32_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i32 {
            a.checked_neg().unwrap_or_else(|| panic!("negation overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u32_matches_zero(&mut self, a: u32) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u32_matches_non_zero(&mut self, a: u32) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u32_matches_odd(&mut self, a: u32) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u32_matches_even(&mut self, a: u32) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u32_is_power_of_two( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a.is_power_of_two() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u32_matches_power_of_two(&mut self, a: u32) -> Option<bool> {
            Some(a.is_power_of_two()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i64> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i64> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i64> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i64> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i64> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i64> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i64> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i64_matches_zero(&mut self, a: i64) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i64_matches_non_zero(&mut self, a: i64) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i64_matches_odd(&mut self, a: i64) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i64_matches_even(&mut self, a: i64) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_checked_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i64> {
            a.checked_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_wrapping_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.wrapping_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i64_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i64 {
            a.checked_neg().unwrap_or_else(|| panic!("negation overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u64> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u64> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u64> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u64> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u64> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u64> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u64> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u64 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u64_matches_zero(&mut self, a: u64) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u64_matches_non_zero(&mut self, a: u64) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u64_matches_odd(&mut self, a: u64) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u64_matches_even(&mut self, a: u64) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u64_is_power_of_two( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a.is_power_of_two() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u64_matches_power_of_two(&mut self, a: u64) -> Option<bool> {
            Some(a.is_power_of_two()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i128> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i128> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i128> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i128> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i128> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i128> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i128> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i128_matches_zero(&mut self, a: i128) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i128_matches_non_zero(&mut self, a: i128) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i128_matches_odd(&mut self, a: i128) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn i128_matches_even(&mut self, a: i128) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_checked_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<i128> {
            a.checked_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_wrapping_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.wrapping_neg() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn i128_neg( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: i128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> i128 {
            a.checked_neg().unwrap_or_else(|| panic!("negation overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_ne( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_lt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a < b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_lt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a <= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_gt( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a > b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_gt_eq( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a >= b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_checked_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u128> {
            a.checked_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_wrapping_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.wrapping_add(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_add( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.checked_add(b).unwrap_or_else(|| panic!("addition overflow: {a} + {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_checked_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u128> {
            a.checked_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_wrapping_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.wrapping_sub(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_sub( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.checked_sub(b).unwrap_or_else(|| panic!("subtraction overflow: {a} - {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_checked_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u128> {
            a.checked_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_wrapping_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.wrapping_mul(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_mul( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.checked_mul(b).unwrap_or_else(|| panic!("multiplication overflow: {a} * {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_checked_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u128> {
            a.checked_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_wrapping_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.wrapping_div(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_div( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.checked_div(b).unwrap_or_else(|| panic!("div failure: {a} / {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_checked_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u128> {
            a.checked_rem(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_rem( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.checked_rem(b).unwrap_or_else(|| panic!("rem failure: {a} % {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_and( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a & b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_or( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a | b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_xor( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a ^ b // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_not( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            !a // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_checked_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u128> {
            a.checked_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_wrapping_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.wrapping_shl(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_shl( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.checked_shl(b).unwrap_or_else(|| panic!("shl overflow: {a} << {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_checked_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u128> {
            a.checked_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_wrapping_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.wrapping_shr(b) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_shr( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
            b: u32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u128 {
            a.checked_shr(b).unwrap_or_else(|| panic!("shr overflow: {a} >> {b}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_is_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u128_matches_zero(&mut self, a: u128) -> Option<bool> {
            Some(a == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_is_non_zero( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u128_matches_non_zero(&mut self, a: u128) -> Option<bool> {
            Some(a != 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_is_odd( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 1 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u128_matches_odd(&mut self, a: u128) -> Option<bool> {
            Some(a & 1 == 1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_is_even( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a & 1 == 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u128_matches_even(&mut self, a: u128) -> Option<bool> {
            Some(a & 1 == 0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_checked_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> Option<u32> {
            a.checked_ilog2() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_ilog2( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.checked_ilog2().unwrap_or_else(|| panic!("ilog2 overflow: {a}")) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_trailing_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_trailing_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.trailing_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_leading_zeros( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_zeros() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_leading_ones( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> u32 {
            a.leading_ones() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:909
        fn u128_is_power_of_two( // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:910
            &mut self, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:912
            a: u128, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:914
        ) -> bool {
            a.is_power_of_two() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:919
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:949
        fn u128_matches_power_of_two(&mut self, a: u128) -> Option<bool> {
            Some(a.is_power_of_two()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:955
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i8_try_into_u8(&mut self, x: i8) -> Option<u8> {
            u8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i8_unwrap_into_u8(&mut self, x: i8) -> u8 {
            u8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn i8_cast_unsigned(&mut self, x: i8) -> u8 {
            x as u8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i8_from_u8(&mut self, x: i8) -> Option<u8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i8_into_i16(&mut self, x: i8) -> i16 {
            i16::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i8_from_i16(&mut self, x: i8) -> Option<i16> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i8_try_into_u16(&mut self, x: i8) -> Option<u16> {
            u16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i8_unwrap_into_u16(&mut self, x: i8) -> u16 {
            u16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i8_from_u16(&mut self, x: i8) -> Option<u16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i8_into_i32(&mut self, x: i8) -> i32 {
            i32::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i8_from_i32(&mut self, x: i8) -> Option<i32> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i8_try_into_u32(&mut self, x: i8) -> Option<u32> {
            u32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i8_unwrap_into_u32(&mut self, x: i8) -> u32 {
            u32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i8_from_u32(&mut self, x: i8) -> Option<u32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i8_into_i64(&mut self, x: i8) -> i64 {
            i64::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i8_from_i64(&mut self, x: i8) -> Option<i64> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i8_try_into_u64(&mut self, x: i8) -> Option<u64> {
            u64::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i8_unwrap_into_u64(&mut self, x: i8) -> u64 {
            u64::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i8_from_u64(&mut self, x: i8) -> Option<u64> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i8_into_i128(&mut self, x: i8) -> i128 {
            i128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i8_from_i128(&mut self, x: i8) -> Option<i128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i8_try_into_u128(&mut self, x: i8) -> Option<u128> {
            u128::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i8_unwrap_into_u128(&mut self, x: i8) -> u128 {
            u128::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i8_from_u128(&mut self, x: i8) -> Option<u128> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u8_try_into_i8(&mut self, x: u8) -> Option<i8> {
            i8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u8_unwrap_into_i8(&mut self, x: u8) -> i8 {
            i8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn u8_cast_signed(&mut self, x: u8) -> i8 {
            x as i8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u8_from_i8(&mut self, x: u8) -> Option<i8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u8_into_i16(&mut self, x: u8) -> i16 {
            i16::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u8_from_i16(&mut self, x: u8) -> Option<i16> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u8_into_u16(&mut self, x: u8) -> u16 {
            u16::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u8_from_u16(&mut self, x: u8) -> Option<u16> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u8_into_i32(&mut self, x: u8) -> i32 {
            i32::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u8_from_i32(&mut self, x: u8) -> Option<i32> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u8_into_u32(&mut self, x: u8) -> u32 {
            u32::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u8_from_u32(&mut self, x: u8) -> Option<u32> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u8_into_i64(&mut self, x: u8) -> i64 {
            i64::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u8_from_i64(&mut self, x: u8) -> Option<i64> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u8_into_u64(&mut self, x: u8) -> u64 {
            u64::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u8_from_u64(&mut self, x: u8) -> Option<u64> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u8_into_i128(&mut self, x: u8) -> i128 {
            i128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u8_from_i128(&mut self, x: u8) -> Option<i128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u8_into_u128(&mut self, x: u8) -> u128 {
            u128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u8_from_u128(&mut self, x: u8) -> Option<u128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i16_try_into_i8(&mut self, x: i16) -> Option<i8> {
            i8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i16_unwrap_into_i8(&mut self, x: i16) -> i8 {
            i8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i16_truncate_into_i8(&mut self, x: i16) -> i8 {
            x as i8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i16_from_i8(&mut self, x: i16) -> Option<i8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i16_try_into_u8(&mut self, x: i16) -> Option<u8> {
            u8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i16_unwrap_into_u8(&mut self, x: i16) -> u8 {
            u8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i16_from_u8(&mut self, x: i16) -> Option<u8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i16_try_into_u16(&mut self, x: i16) -> Option<u16> {
            u16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i16_unwrap_into_u16(&mut self, x: i16) -> u16 {
            u16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn i16_cast_unsigned(&mut self, x: i16) -> u16 {
            x as u16 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i16_from_u16(&mut self, x: i16) -> Option<u16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i16_into_i32(&mut self, x: i16) -> i32 {
            i32::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i16_from_i32(&mut self, x: i16) -> Option<i32> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i16_try_into_u32(&mut self, x: i16) -> Option<u32> {
            u32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i16_unwrap_into_u32(&mut self, x: i16) -> u32 {
            u32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i16_from_u32(&mut self, x: i16) -> Option<u32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i16_into_i64(&mut self, x: i16) -> i64 {
            i64::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i16_from_i64(&mut self, x: i16) -> Option<i64> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i16_try_into_u64(&mut self, x: i16) -> Option<u64> {
            u64::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i16_unwrap_into_u64(&mut self, x: i16) -> u64 {
            u64::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i16_from_u64(&mut self, x: i16) -> Option<u64> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i16_into_i128(&mut self, x: i16) -> i128 {
            i128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i16_from_i128(&mut self, x: i16) -> Option<i128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i16_try_into_u128(&mut self, x: i16) -> Option<u128> {
            u128::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i16_unwrap_into_u128(&mut self, x: i16) -> u128 {
            u128::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i16_from_u128(&mut self, x: i16) -> Option<u128> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u16_try_into_i8(&mut self, x: u16) -> Option<i8> {
            i8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u16_unwrap_into_i8(&mut self, x: u16) -> i8 {
            i8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u16_from_i8(&mut self, x: u16) -> Option<i8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u16_try_into_u8(&mut self, x: u16) -> Option<u8> {
            u8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u16_unwrap_into_u8(&mut self, x: u16) -> u8 {
            u8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u16_truncate_into_u8(&mut self, x: u16) -> u8 {
            x as u8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u16_from_u8(&mut self, x: u16) -> Option<u8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u16_try_into_i16(&mut self, x: u16) -> Option<i16> {
            i16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u16_unwrap_into_i16(&mut self, x: u16) -> i16 {
            i16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn u16_cast_signed(&mut self, x: u16) -> i16 {
            x as i16 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u16_from_i16(&mut self, x: u16) -> Option<i16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u16_into_i32(&mut self, x: u16) -> i32 {
            i32::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u16_from_i32(&mut self, x: u16) -> Option<i32> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u16_into_u32(&mut self, x: u16) -> u32 {
            u32::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u16_from_u32(&mut self, x: u16) -> Option<u32> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u16_into_i64(&mut self, x: u16) -> i64 {
            i64::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u16_from_i64(&mut self, x: u16) -> Option<i64> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u16_into_u64(&mut self, x: u16) -> u64 {
            u64::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u16_from_u64(&mut self, x: u16) -> Option<u64> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u16_into_i128(&mut self, x: u16) -> i128 {
            i128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u16_from_i128(&mut self, x: u16) -> Option<i128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u16_into_u128(&mut self, x: u16) -> u128 {
            u128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u16_from_u128(&mut self, x: u16) -> Option<u128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i32_try_into_i8(&mut self, x: i32) -> Option<i8> {
            i8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i32_unwrap_into_i8(&mut self, x: i32) -> i8 {
            i8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i32_truncate_into_i8(&mut self, x: i32) -> i8 {
            x as i8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i32_from_i8(&mut self, x: i32) -> Option<i8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i32_try_into_u8(&mut self, x: i32) -> Option<u8> {
            u8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i32_unwrap_into_u8(&mut self, x: i32) -> u8 {
            u8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i32_from_u8(&mut self, x: i32) -> Option<u8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i32_try_into_i16(&mut self, x: i32) -> Option<i16> {
            i16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i32_unwrap_into_i16(&mut self, x: i32) -> i16 {
            i16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i32_truncate_into_i16(&mut self, x: i32) -> i16 {
            x as i16 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i32_from_i16(&mut self, x: i32) -> Option<i16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i32_try_into_u16(&mut self, x: i32) -> Option<u16> {
            u16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i32_unwrap_into_u16(&mut self, x: i32) -> u16 {
            u16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i32_from_u16(&mut self, x: i32) -> Option<u16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i32_try_into_u32(&mut self, x: i32) -> Option<u32> {
            u32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i32_unwrap_into_u32(&mut self, x: i32) -> u32 {
            u32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn i32_cast_unsigned(&mut self, x: i32) -> u32 {
            x as u32 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i32_from_u32(&mut self, x: i32) -> Option<u32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i32_into_i64(&mut self, x: i32) -> i64 {
            i64::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i32_from_i64(&mut self, x: i32) -> Option<i64> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i32_try_into_u64(&mut self, x: i32) -> Option<u64> {
            u64::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i32_unwrap_into_u64(&mut self, x: i32) -> u64 {
            u64::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i32_from_u64(&mut self, x: i32) -> Option<u64> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i32_into_i128(&mut self, x: i32) -> i128 {
            i128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i32_from_i128(&mut self, x: i32) -> Option<i128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i32_try_into_u128(&mut self, x: i32) -> Option<u128> {
            u128::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i32_unwrap_into_u128(&mut self, x: i32) -> u128 {
            u128::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i32_from_u128(&mut self, x: i32) -> Option<u128> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u32_try_into_i8(&mut self, x: u32) -> Option<i8> {
            i8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u32_unwrap_into_i8(&mut self, x: u32) -> i8 {
            i8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u32_from_i8(&mut self, x: u32) -> Option<i8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u32_try_into_u8(&mut self, x: u32) -> Option<u8> {
            u8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u32_unwrap_into_u8(&mut self, x: u32) -> u8 {
            u8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u32_truncate_into_u8(&mut self, x: u32) -> u8 {
            x as u8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u32_from_u8(&mut self, x: u32) -> Option<u8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u32_try_into_i16(&mut self, x: u32) -> Option<i16> {
            i16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u32_unwrap_into_i16(&mut self, x: u32) -> i16 {
            i16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u32_from_i16(&mut self, x: u32) -> Option<i16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u32_try_into_u16(&mut self, x: u32) -> Option<u16> {
            u16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u32_unwrap_into_u16(&mut self, x: u32) -> u16 {
            u16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u32_truncate_into_u16(&mut self, x: u32) -> u16 {
            x as u16 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u32_from_u16(&mut self, x: u32) -> Option<u16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u32_try_into_i32(&mut self, x: u32) -> Option<i32> {
            i32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u32_unwrap_into_i32(&mut self, x: u32) -> i32 {
            i32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn u32_cast_signed(&mut self, x: u32) -> i32 {
            x as i32 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u32_from_i32(&mut self, x: u32) -> Option<i32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u32_into_i64(&mut self, x: u32) -> i64 {
            i64::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u32_from_i64(&mut self, x: u32) -> Option<i64> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u32_into_u64(&mut self, x: u32) -> u64 {
            u64::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u32_from_u64(&mut self, x: u32) -> Option<u64> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u32_into_i128(&mut self, x: u32) -> i128 {
            i128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u32_from_i128(&mut self, x: u32) -> Option<i128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u32_into_u128(&mut self, x: u32) -> u128 {
            u128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u32_from_u128(&mut self, x: u32) -> Option<u128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i64_try_into_i8(&mut self, x: i64) -> Option<i8> {
            i8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i64_unwrap_into_i8(&mut self, x: i64) -> i8 {
            i8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i64_truncate_into_i8(&mut self, x: i64) -> i8 {
            x as i8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i64_from_i8(&mut self, x: i64) -> Option<i8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i64_try_into_u8(&mut self, x: i64) -> Option<u8> {
            u8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i64_unwrap_into_u8(&mut self, x: i64) -> u8 {
            u8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i64_from_u8(&mut self, x: i64) -> Option<u8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i64_try_into_i16(&mut self, x: i64) -> Option<i16> {
            i16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i64_unwrap_into_i16(&mut self, x: i64) -> i16 {
            i16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i64_truncate_into_i16(&mut self, x: i64) -> i16 {
            x as i16 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i64_from_i16(&mut self, x: i64) -> Option<i16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i64_try_into_u16(&mut self, x: i64) -> Option<u16> {
            u16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i64_unwrap_into_u16(&mut self, x: i64) -> u16 {
            u16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i64_from_u16(&mut self, x: i64) -> Option<u16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i64_try_into_i32(&mut self, x: i64) -> Option<i32> {
            i32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i64_unwrap_into_i32(&mut self, x: i64) -> i32 {
            i32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i64_truncate_into_i32(&mut self, x: i64) -> i32 {
            x as i32 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i64_from_i32(&mut self, x: i64) -> Option<i32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i64_try_into_u32(&mut self, x: i64) -> Option<u32> {
            u32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i64_unwrap_into_u32(&mut self, x: i64) -> u32 {
            u32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i64_from_u32(&mut self, x: i64) -> Option<u32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i64_try_into_u64(&mut self, x: i64) -> Option<u64> {
            u64::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i64_unwrap_into_u64(&mut self, x: i64) -> u64 {
            u64::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn i64_cast_unsigned(&mut self, x: i64) -> u64 {
            x as u64 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i64_from_u64(&mut self, x: i64) -> Option<u64> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i64_into_i128(&mut self, x: i64) -> i128 {
            i128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i64_from_i128(&mut self, x: i64) -> Option<i128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i64_try_into_u128(&mut self, x: i64) -> Option<u128> {
            u128::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i64_unwrap_into_u128(&mut self, x: i64) -> u128 {
            u128::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i64_from_u128(&mut self, x: i64) -> Option<u128> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u64_try_into_i8(&mut self, x: u64) -> Option<i8> {
            i8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u64_unwrap_into_i8(&mut self, x: u64) -> i8 {
            i8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u64_from_i8(&mut self, x: u64) -> Option<i8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u64_try_into_u8(&mut self, x: u64) -> Option<u8> {
            u8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u64_unwrap_into_u8(&mut self, x: u64) -> u8 {
            u8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u64_truncate_into_u8(&mut self, x: u64) -> u8 {
            x as u8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u64_from_u8(&mut self, x: u64) -> Option<u8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u64_try_into_i16(&mut self, x: u64) -> Option<i16> {
            i16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u64_unwrap_into_i16(&mut self, x: u64) -> i16 {
            i16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u64_from_i16(&mut self, x: u64) -> Option<i16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u64_try_into_u16(&mut self, x: u64) -> Option<u16> {
            u16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u64_unwrap_into_u16(&mut self, x: u64) -> u16 {
            u16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u64_truncate_into_u16(&mut self, x: u64) -> u16 {
            x as u16 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u64_from_u16(&mut self, x: u64) -> Option<u16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u64_try_into_i32(&mut self, x: u64) -> Option<i32> {
            i32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u64_unwrap_into_i32(&mut self, x: u64) -> i32 {
            i32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u64_from_i32(&mut self, x: u64) -> Option<i32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u64_try_into_u32(&mut self, x: u64) -> Option<u32> {
            u32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u64_unwrap_into_u32(&mut self, x: u64) -> u32 {
            u32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u64_truncate_into_u32(&mut self, x: u64) -> u32 {
            x as u32 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u64_from_u32(&mut self, x: u64) -> Option<u32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u64_try_into_i64(&mut self, x: u64) -> Option<i64> {
            i64::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u64_unwrap_into_i64(&mut self, x: u64) -> i64 {
            i64::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn u64_cast_signed(&mut self, x: u64) -> i64 {
            x as i64 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u64_from_i64(&mut self, x: u64) -> Option<i64> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u64_into_i128(&mut self, x: u64) -> i128 {
            i128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u64_from_i128(&mut self, x: u64) -> Option<i128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u64_into_u128(&mut self, x: u64) -> u128 {
            u128::from(x) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1062
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u64_from_u128(&mut self, x: u64) -> Option<u128> {
            Some(x.into()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1156
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i128_try_into_i8(&mut self, x: i128) -> Option<i8> {
            i8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i128_unwrap_into_i8(&mut self, x: i128) -> i8 {
            i8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i128_truncate_into_i8(&mut self, x: i128) -> i8 {
            x as i8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i128_from_i8(&mut self, x: i128) -> Option<i8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i128_try_into_u8(&mut self, x: i128) -> Option<u8> {
            u8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i128_unwrap_into_u8(&mut self, x: i128) -> u8 {
            u8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i128_from_u8(&mut self, x: i128) -> Option<u8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i128_try_into_i16(&mut self, x: i128) -> Option<i16> {
            i16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i128_unwrap_into_i16(&mut self, x: i128) -> i16 {
            i16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i128_truncate_into_i16(&mut self, x: i128) -> i16 {
            x as i16 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i128_from_i16(&mut self, x: i128) -> Option<i16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i128_try_into_u16(&mut self, x: i128) -> Option<u16> {
            u16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i128_unwrap_into_u16(&mut self, x: i128) -> u16 {
            u16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i128_from_u16(&mut self, x: i128) -> Option<u16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i128_try_into_i32(&mut self, x: i128) -> Option<i32> {
            i32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i128_unwrap_into_i32(&mut self, x: i128) -> i32 {
            i32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i128_truncate_into_i32(&mut self, x: i128) -> i32 {
            x as i32 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i128_from_i32(&mut self, x: i128) -> Option<i32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i128_try_into_u32(&mut self, x: i128) -> Option<u32> {
            u32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i128_unwrap_into_u32(&mut self, x: i128) -> u32 {
            u32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i128_from_u32(&mut self, x: i128) -> Option<u32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i128_try_into_i64(&mut self, x: i128) -> Option<i64> {
            i64::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i128_unwrap_into_i64(&mut self, x: i128) -> i64 {
            i64::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn i128_truncate_into_i64(&mut self, x: i128) -> i64 {
            x as i64 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i128_from_i64(&mut self, x: i128) -> Option<i64> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i128_try_into_u64(&mut self, x: i128) -> Option<u64> {
            u64::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i128_unwrap_into_u64(&mut self, x: i128) -> u64 {
            u64::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i128_from_u64(&mut self, x: i128) -> Option<u64> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn i128_try_into_u128(&mut self, x: i128) -> Option<u128> {
            u128::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn i128_unwrap_into_u128(&mut self, x: i128) -> u128 {
            u128::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn i128_cast_unsigned(&mut self, x: i128) -> u128 {
            x as u128 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn i128_from_u128(&mut self, x: i128) -> Option<u128> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u128_try_into_i8(&mut self, x: u128) -> Option<i8> {
            i8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u128_unwrap_into_i8(&mut self, x: u128) -> i8 {
            i8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u128_from_i8(&mut self, x: u128) -> Option<i8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u128_try_into_u8(&mut self, x: u128) -> Option<u8> {
            u8::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u128_unwrap_into_u8(&mut self, x: u128) -> u8 {
            u8::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u128_truncate_into_u8(&mut self, x: u128) -> u8 {
            x as u8 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u128_from_u8(&mut self, x: u128) -> Option<u8> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u128_try_into_i16(&mut self, x: u128) -> Option<i16> {
            i16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u128_unwrap_into_i16(&mut self, x: u128) -> i16 {
            i16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u128_from_i16(&mut self, x: u128) -> Option<i16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u128_try_into_u16(&mut self, x: u128) -> Option<u16> {
            u16::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u128_unwrap_into_u16(&mut self, x: u128) -> u16 {
            u16::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u128_truncate_into_u16(&mut self, x: u128) -> u16 {
            x as u16 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u128_from_u16(&mut self, x: u128) -> Option<u16> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u128_try_into_i32(&mut self, x: u128) -> Option<i32> {
            i32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u128_unwrap_into_i32(&mut self, x: u128) -> i32 {
            i32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u128_from_i32(&mut self, x: u128) -> Option<i32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u128_try_into_u32(&mut self, x: u128) -> Option<u32> {
            u32::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u128_unwrap_into_u32(&mut self, x: u128) -> u32 {
            u32::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u128_truncate_into_u32(&mut self, x: u128) -> u32 {
            x as u32 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u128_from_u32(&mut self, x: u128) -> Option<u32> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u128_try_into_i64(&mut self, x: u128) -> Option<i64> {
            i64::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u128_unwrap_into_i64(&mut self, x: u128) -> i64 {
            i64::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u128_from_i64(&mut self, x: u128) -> Option<i64> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u128_try_into_u64(&mut self, x: u128) -> Option<u64> {
            u64::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u128_unwrap_into_u64(&mut self, x: u128) -> u64 {
            u64::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1098
        fn u128_truncate_into_u64(&mut self, x: u128) -> u64 {
            x as u64 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1104
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u128_from_u64(&mut self, x: u128) -> Option<u64> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1053
        fn u128_try_into_i128(&mut self, x: u128) -> Option<i128> {
            i128::try_from(x).ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1060
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1077
        fn u128_unwrap_into_i128(&mut self, x: u128) -> i128 {
            i128::try_from(x).unwrap() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1083
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1125
        fn u128_cast_signed(&mut self, x: u128) -> i128 {
            x as i128 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1133
        }
        #[inline] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1147
        fn u128_from_i128(&mut self, x: u128) -> Option<i128> {
            x.try_into().ok() // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_isle.rs:1154
        }

    }
}
