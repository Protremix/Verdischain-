#[derive(Clone, PartialEq, Hash)] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:426
/// Flags group `x86`.
pub struct Flags {
    bytes: [u8; 5], // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:429
}
impl Flags {
    /// Create flags x86 settings group.
    #[allow(unused_variables, reason = "generated code")] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:26
    pub fn new(shared: &settings::Flags, builder: &Builder) -> Self {
        let bvec = builder.state_for("x86"); // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:31
        let mut x86 = Self { bytes: [0; 5] }; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:32
        debug_assert_eq!(bvec.len(), 3); // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:38
        x86.bytes[0..3].copy_from_slice(&bvec); // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:43
        // Precompute #17.
        if x86.has_avx() {
            x86.bytes[2] |= 1 << 1; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #18.
        if x86.has_avx() && x86.has_avx2() {
            x86.bytes[2] |= 1 << 2; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #19.
        if x86.has_avx512bitalg() {
            x86.bytes[2] |= 1 << 3; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #20.
        if x86.has_avx512dq() {
            x86.bytes[2] |= 1 << 4; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #21.
        if x86.has_avx512f() {
            x86.bytes[2] |= 1 << 5; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #22.
        if x86.has_avx512vbmi() {
            x86.bytes[2] |= 1 << 6; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #23.
        if x86.has_avx512vl() {
            x86.bytes[2] |= 1 << 7; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #24.
        if x86.has_bmi1() {
            x86.bytes[3] |= 1 << 0; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #25.
        if x86.has_bmi2() {
            x86.bytes[3] |= 1 << 1; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #26.
        if x86.has_cmpxchg16b() {
            x86.bytes[3] |= 1 << 2; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #27.
        if x86.has_avx() && x86.has_fma() {
            x86.bytes[3] |= 1 << 3; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #28.
        if x86.has_lzcnt() {
            x86.bytes[3] |= 1 << 4; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #29.
        if x86.has_popcnt() && x86.has_sse42() {
            x86.bytes[3] |= 1 << 5; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #30.
        if x86.has_sse3() {
            x86.bytes[3] |= 1 << 6; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #31.
        if x86.has_sse41() {
            x86.bytes[3] |= 1 << 7; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #32.
        if x86.has_sse41() && x86.has_sse42() {
            x86.bytes[4] |= 1 << 0; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        // Precompute #33.
        if x86.has_ssse3() {
            x86.bytes[4] |= 1 << 1; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:54
        }
        x86 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:64
    }
}
impl Flags {
    /// Iterates the setting values.
    pub fn iter(&self) -> impl Iterator<Item = Value> + use<> {
        let mut bytes = [0; 3]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:74
        bytes.copy_from_slice(&self.bytes[0..3]); // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:75
        DESCRIPTORS.iter().filter_map(move |d| {
            let values = match &d.detail {
                detail::Detail::Preset => return None, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:78
                detail::Detail::Enum { last, enumerators } => Some(TEMPLATE.enums(*last, *enumerators)), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:79
                _ => None // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:80
            }
            ; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:82
            Some(Value { name: d.name, detail: d.detail, values, value: bytes[d.offset as usize] }) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:83
        }
        ) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:85
    }
}
/// User-defined settings.
#[allow(dead_code, reason = "generated code")] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:209
impl Flags {
    /// Dynamic numbered predicate getter.
    fn numbered_predicate(&self, p: usize) -> bool {
        self.bytes[0 + p / 8] & (1 << (p % 8)) != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:214
    }
    /// Has support for SSE3.
    /// SSE3: CPUID.01H:ECX.SSE3[bit 0]
    pub fn has_sse3(&self) -> bool {
        self.numbered_predicate(0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for SSSE3.
    /// SSSE3: CPUID.01H:ECX.SSSE3[bit 9]
    pub fn has_ssse3(&self) -> bool {
        self.numbered_predicate(1) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for CMPXCHG16b.
    /// CMPXCHG16b: CPUID.01H:ECX.CMPXCHG16B[bit 13]
    pub fn has_cmpxchg16b(&self) -> bool {
        self.numbered_predicate(2) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for SSE4.1.
    /// SSE4.1: CPUID.01H:ECX.SSE4_1[bit 19]
    pub fn has_sse41(&self) -> bool {
        self.numbered_predicate(3) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for SSE4.2.
    /// SSE4.2: CPUID.01H:ECX.SSE4_2[bit 20]
    pub fn has_sse42(&self) -> bool {
        self.numbered_predicate(4) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for AVX.
    /// AVX: CPUID.01H:ECX.AVX[bit 28]
    pub fn has_avx(&self) -> bool {
        self.numbered_predicate(5) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for AVX2.
    /// AVX2: CPUID.07H:EBX.AVX2[bit 5]
    pub fn has_avx2(&self) -> bool {
        self.numbered_predicate(6) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for FMA.
    /// FMA: CPUID.01H:ECX.FMA[bit 12]
    pub fn has_fma(&self) -> bool {
        self.numbered_predicate(7) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for AVX512BITALG.
    /// AVX512BITALG: CPUID.07H:ECX.AVX512BITALG[bit 12]
    pub fn has_avx512bitalg(&self) -> bool {
        self.numbered_predicate(8) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for AVX512DQ.
    /// AVX512DQ: CPUID.07H:EBX.AVX512DQ[bit 17]
    pub fn has_avx512dq(&self) -> bool {
        self.numbered_predicate(9) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for AVX512VL.
    /// AVX512VL: CPUID.07H:EBX.AVX512VL[bit 31]
    pub fn has_avx512vl(&self) -> bool {
        self.numbered_predicate(10) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for AVX512VMBI.
    /// AVX512VBMI: CPUID.07H:ECX.AVX512VBMI[bit 1]
    pub fn has_avx512vbmi(&self) -> bool {
        self.numbered_predicate(11) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for AVX512F.
    /// AVX512F: CPUID.07H:EBX.AVX512F[bit 16]
    pub fn has_avx512f(&self) -> bool {
        self.numbered_predicate(12) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for POPCNT.
    /// POPCNT: CPUID.01H:ECX.POPCNT[bit 23]
    pub fn has_popcnt(&self) -> bool {
        self.numbered_predicate(13) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for BMI1.
    /// BMI1: CPUID.(EAX=07H, ECX=0H):EBX.BMI1[bit 3]
    pub fn has_bmi1(&self) -> bool {
        self.numbered_predicate(14) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for BMI2.
    /// BMI2: CPUID.(EAX=07H, ECX=0H):EBX.BMI2[bit 8]
    pub fn has_bmi2(&self) -> bool {
        self.numbered_predicate(15) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Has support for LZCNT.
    /// LZCNT: CPUID.EAX=80000001H:ECX.LZCNT[bit 5]
    pub fn has_lzcnt(&self) -> bool {
        self.numbered_predicate(16) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
    /// Computed predicate `x86.has_avx()`.
    pub fn use_avx(&self) -> bool {
        self.numbered_predicate(17) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_avx() && x86.has_avx2()`.
    pub fn use_avx2(&self) -> bool {
        self.numbered_predicate(18) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_avx512bitalg()`.
    pub fn use_avx512bitalg(&self) -> bool {
        self.numbered_predicate(19) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_avx512dq()`.
    pub fn use_avx512dq(&self) -> bool {
        self.numbered_predicate(20) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_avx512f()`.
    pub fn use_avx512f(&self) -> bool {
        self.numbered_predicate(21) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_avx512vbmi()`.
    pub fn use_avx512vbmi(&self) -> bool {
        self.numbered_predicate(22) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_avx512vl()`.
    pub fn use_avx512vl(&self) -> bool {
        self.numbered_predicate(23) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_bmi1()`.
    pub fn use_bmi1(&self) -> bool {
        self.numbered_predicate(24) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_bmi2()`.
    pub fn use_bmi2(&self) -> bool {
        self.numbered_predicate(25) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_cmpxchg16b()`.
    pub fn use_cmpxchg16b(&self) -> bool {
        self.numbered_predicate(26) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_avx() && x86.has_fma()`.
    pub fn use_fma(&self) -> bool {
        self.numbered_predicate(27) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_lzcnt()`.
    pub fn use_lzcnt(&self) -> bool {
        self.numbered_predicate(28) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_popcnt() && x86.has_sse42()`.
    pub fn use_popcnt(&self) -> bool {
        self.numbered_predicate(29) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_sse3()`.
    pub fn use_sse3(&self) -> bool {
        self.numbered_predicate(30) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_sse41()`.
    pub fn use_sse41(&self) -> bool {
        self.numbered_predicate(31) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_sse41() && x86.has_sse42()`.
    pub fn use_sse42(&self) -> bool {
        self.numbered_predicate(32) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
    /// Computed predicate `x86.has_ssse3()`.
    pub fn use_ssse3(&self) -> bool {
        self.numbered_predicate(33) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:201
    }
}
static DESCRIPTORS: [detail::Descriptor; 84] = [ // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:253
    detail::Descriptor {
        name: "has_sse3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for SSE3.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 0 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_ssse3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for SSSE3.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 1 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_cmpxchg16b", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for CMPXCHG16b.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 2 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_sse41", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for SSE4.1.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 3 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_sse42", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for SSE4.2.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 4 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_avx", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for AVX.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 5 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_avx2", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for AVX2.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 6 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_fma", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for FMA.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 7 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_avx512bitalg", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for AVX512BITALG.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 0 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_avx512dq", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for AVX512DQ.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 1 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_avx512vl", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for AVX512VL.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 2 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_avx512vbmi", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for AVX512VMBI.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 3 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_avx512f", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for AVX512F.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 4 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_popcnt", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for POPCNT.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 5 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_bmi1", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for BMI1.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 6 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_bmi2", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for BMI2.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 7 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "has_lzcnt", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Has support for LZCNT.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 2, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 0 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "sse3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "SSE3 and earlier.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "ssse3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "SSSE3 and earlier.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 3, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "sse41", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "SSE4.1 and earlier.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 6, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "sse42", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "SSE4.2 and earlier.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 9, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "baseline", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "A baseline preset with no extensions enabled.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 12, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "nocona", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Nocona microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 15, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "core2", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Core 2 microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 18, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "penryn", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Penryn microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 21, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "atom", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Atom microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 24, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "bonnell", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Bonnell microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 27, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "silvermont", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Silvermont microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 30, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "slm", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Silvermont microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 33, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "goldmont", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Goldmont microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 36, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "goldmont-plus", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Goldmont Plus microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 39, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "tremont", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Tremont microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 42, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "alderlake", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Alderlake microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 45, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "sierraforest", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Sierra Forest microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 48, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "grandridge", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Grandridge microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 51, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "nehalem", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Nehalem microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 54, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "corei7", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Core i7 microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 57, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "westmere", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Westmere microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 60, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "sandybridge", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Sandy Bridge microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 63, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "corei7-avx", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Core i7 AVX microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 66, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "ivybridge", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Ivy Bridge microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 69, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "core-avx-i", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Intel Core CPU with 64-bit extensions.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 72, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "haswell", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Haswell microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 75, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "core-avx2", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Intel Core CPU with AVX2 extensions.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 78, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "broadwell", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Broadwell microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 81, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "skylake", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Skylake microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 84, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "knl", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Knights Landing microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 87, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "knm", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Knights Mill microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 90, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "skylake-avx512", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Skylake AVX512 microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 93, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "skx", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Skylake AVX512 microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 96, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "cascadelake", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Cascade Lake microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 99, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "cooperlake", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Cooper Lake microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 102, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "cannonlake", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Canon Lake microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 105, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "icelake-client", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Ice Lake microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 108, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "icelake", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Ice Lake microarchitecture", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 111, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "icelake-server", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Ice Lake (server) microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 114, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "tigerlake", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Tiger Lake microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 117, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "sapphirerapids", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Sapphire Rapids microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 120, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "raptorlake", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Raptor Lake microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 123, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "meteorlake", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Meteor Lake microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 126, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "graniterapids", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Granite Rapids microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 129, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "opteron", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Opteron microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 132, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "k8", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "K8 Hammer microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 135, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "athlon64", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Athlon64 microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 138, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "athlon-fx", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Athlon FX microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 141, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "opteron-sse3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Opteron microarchitecture with support for SSE3 instructions.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 144, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "k8-sse3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "K8 Hammer microarchitecture with support for SSE3 instructions.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 147, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "athlon64-sse3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Athlon 64 microarchitecture with support for SSE3 instructions.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 150, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "barcelona", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Barcelona microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 153, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "amdfam10", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "AMD Family 10h microarchitecture", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 156, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "btver1", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Bobcat microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 159, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "btver2", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Jaguar microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 162, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "bdver1", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Bulldozer microarchitecture", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 165, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "bdver2", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Piledriver microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 168, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "bdver3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Steamroller microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 171, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "bdver4", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Excavator microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 174, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "znver1", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Zen (first generation) microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 177, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "znver2", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Zen (second generation) microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 180, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "znver3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Zen (third generation) microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 183, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "znver4", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Zen (fourth generation) microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 186, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "x86-64", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Generic x86-64 microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 189, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "x86-64-v2", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Generic x86-64 (V2) microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 192, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "x84_64_v3", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Generic x86_64 (V3) microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 195, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
    detail::Descriptor {
        name: "x86_64_v4", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:293
        description: "Generic x86_64 (V4) microarchitecture.", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:294
        offset: 198, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:295
        detail: detail::Detail::Preset, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:296
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:298
]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:304
static ENUMERATORS: [&str; 0] = [ // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:307
]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:313
static HASH_TABLE: [u16; 128] = [ // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:323
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    78, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    77, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    76, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    24, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    79, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    67, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    81, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    23, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    51, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    60, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    15, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    14, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    30, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    42, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    71, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    68, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    5, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    36, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    66, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    6, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    45, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    22, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    65, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    16, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    7, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    48, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    50, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    25, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    63, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    12, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    44, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    39, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    53, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    70, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    4, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    3, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    59, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    11, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    13, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    31, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    80, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    74, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    40, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    29, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    47, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    46, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    9, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    55, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    72, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    10, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    75, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    73, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    2, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    62, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    82, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    34, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    8, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    19, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    20, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    49, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    17, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    54, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    61, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    21, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    69, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    57, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    83, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    27, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    28, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    35, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    37, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    41, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    43, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    33, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    58, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    52, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    18, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    56, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    26, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    38, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:339
static PRESETS: [(u8, u8); 201] = [ // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:342
    // sse3: has_sse3
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // ssse3: has_sse3, has_ssse3
    (0b00000011, 0b00000011), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // sse41: has_sse3, has_ssse3, has_sse41
    (0b00001011, 0b00001011), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // sse42: has_sse3, has_ssse3, has_sse41, has_sse42
    (0b00011011, 0b00011011), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // baseline: 
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // nocona: has_sse3, has_cmpxchg16b
    (0b00000101, 0b00000101), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // core2: has_sse3, has_cmpxchg16b
    (0b00000101, 0b00000101), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // penryn: has_sse3, has_ssse3, has_sse41, has_cmpxchg16b
    (0b00001111, 0b00001111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // atom: has_sse3, has_ssse3, has_cmpxchg16b
    (0b00000111, 0b00000111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // bonnell: has_sse3, has_ssse3, has_cmpxchg16b
    (0b00000111, 0b00000111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // silvermont: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt
    (0b00011111, 0b00011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // slm: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt
    (0b00011111, 0b00011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // goldmont: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt
    (0b00011111, 0b00011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // goldmont-plus: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt
    (0b00011111, 0b00011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // tremont: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt
    (0b00011111, 0b00011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // alderlake: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_bmi1, has_bmi2, has_lzcnt, has_fma
    (0b10011111, 0b10011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // sierraforest: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_bmi1, has_bmi2, has_lzcnt, has_fma
    (0b10011111, 0b10011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // grandridge: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_bmi1, has_bmi2, has_lzcnt, has_fma
    (0b10011111, 0b10011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // nehalem: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b
    (0b00011111, 0b00011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // corei7: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b
    (0b00011111, 0b00011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // westmere: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b
    (0b00011111, 0b00011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // sandybridge: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx
    (0b00111111, 0b00111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // corei7-avx: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx
    (0b00111111, 0b00111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // ivybridge: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx
    (0b00111111, 0b00111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // core-avx-i: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx
    (0b00111111, 0b00111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // haswell: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // core-avx2: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // broadwell: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // skylake: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // knl: has_popcnt, has_avx512f, has_fma, has_bmi1, has_bmi2, has_lzcnt, has_cmpxchg16b
    (0b10000100, 0b10000100), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11110000, 0b11110000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // knm: has_popcnt, has_avx512f, has_fma, has_bmi1, has_bmi2, has_lzcnt, has_cmpxchg16b
    (0b10000100, 0b10000100), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11110000, 0b11110000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // skylake-avx512: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11110110, 0b11110110), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // skx: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11110110, 0b11110110), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // cascadelake: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11110110, 0b11110110), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // cooperlake: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11110110, 0b11110110), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // cannonlake: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl, has_avx512vbmi
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11111110, 0b11111110), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // icelake-client: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl, has_avx512vbmi, has_avx512bitalg
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // icelake: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl, has_avx512vbmi, has_avx512bitalg
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // icelake-server: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl, has_avx512vbmi, has_avx512bitalg
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // tigerlake: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl, has_avx512vbmi, has_avx512bitalg
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // sapphirerapids: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl, has_avx512vbmi, has_avx512bitalg
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // raptorlake: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_bmi1, has_bmi2, has_lzcnt, has_fma
    (0b10011111, 0b10011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // meteorlake: has_sse3, has_ssse3, has_cmpxchg16b, has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_bmi1, has_bmi2, has_lzcnt, has_fma
    (0b10011111, 0b10011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // graniterapids: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_avx, has_avx2, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx512f, has_avx512dq, has_avx512vl, has_avx512vbmi, has_avx512bitalg
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // opteron: 
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // k8: 
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // athlon64: 
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // athlon-fx: 
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // opteron-sse3: has_sse3, has_cmpxchg16b
    (0b00000101, 0b00000101), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // k8-sse3: has_sse3, has_cmpxchg16b
    (0b00000101, 0b00000101), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // athlon64-sse3: has_sse3, has_cmpxchg16b
    (0b00000101, 0b00000101), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // barcelona: has_popcnt, has_lzcnt, has_cmpxchg16b
    (0b00000100, 0b00000100), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // amdfam10: has_popcnt, has_lzcnt, has_cmpxchg16b
    (0b00000100, 0b00000100), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // btver1: has_sse3, has_ssse3, has_lzcnt, has_popcnt, has_cmpxchg16b
    (0b00000111, 0b00000111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // btver2: has_sse3, has_ssse3, has_lzcnt, has_popcnt, has_cmpxchg16b, has_avx, has_bmi1
    (0b00100111, 0b00100111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b01100000, 0b01100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // bdver1: has_lzcnt, has_popcnt, has_sse3, has_ssse3, has_cmpxchg16b
    (0b00000111, 0b00000111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // bdver2: has_lzcnt, has_popcnt, has_sse3, has_ssse3, has_cmpxchg16b, has_bmi1
    (0b00000111, 0b00000111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b01100000, 0b01100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // bdver3: has_lzcnt, has_popcnt, has_sse3, has_ssse3, has_cmpxchg16b, has_bmi1
    (0b00000111, 0b00000111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b01100000, 0b01100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // bdver4: has_lzcnt, has_popcnt, has_sse3, has_ssse3, has_cmpxchg16b, has_bmi1, has_avx2, has_bmi2
    (0b01000111, 0b01000111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // znver1: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_bmi1, has_bmi2, has_lzcnt, has_fma, has_cmpxchg16b
    (0b10011111, 0b10011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // znver2: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_bmi1, has_bmi2, has_lzcnt, has_fma, has_cmpxchg16b
    (0b10011111, 0b10011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // znver3: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_bmi1, has_bmi2, has_lzcnt, has_fma, has_cmpxchg16b
    (0b10011111, 0b10011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // znver4: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_bmi1, has_bmi2, has_lzcnt, has_fma, has_cmpxchg16b, has_avx512bitalg, has_avx512dq, has_avx512f, has_avx512vbmi, has_avx512vl
    (0b10011111, 0b10011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11111111, 0b11111111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // x86-64: 
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // x86-64-v2: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b
    (0b00011111, 0b00011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00100000, 0b00100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000000, 0b00000000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // x84_64_v3: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx2
    (0b11011111, 0b11011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100000, 0b11100000), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    // x86_64_v4: has_sse3, has_ssse3, has_sse41, has_sse42, has_popcnt, has_cmpxchg16b, has_bmi1, has_bmi2, has_fma, has_lzcnt, has_avx2, has_avx512dq, has_avx512vl
    (0b11011111, 0b11011111), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b11100110, 0b11100110), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
    (0b00000001, 0b00000001), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:355
]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:359
static TEMPLATE: detail::Template = detail::Template {
    name: "x86", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:374
    descriptors: &DESCRIPTORS, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:375
    enumerators: &ENUMERATORS, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:376
    hash_table: &HASH_TABLE, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:377
    defaults: &[0x00, 0x00, 0x00], // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:378
    presets: &PRESETS, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:379
}
; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:382
/// Create a `settings::Builder` for the x86 settings group.
pub fn builder() -> Builder {
    Builder::new(&TEMPLATE) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:389
}
impl fmt::Display for Flags {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        writeln!(f, "[x86]")?; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:398
        for d in &DESCRIPTORS {
            if !d.detail.is_preset() {
                write!(f, "{} = ", d.name)?; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:401
                TEMPLATE.format_toml_value(d.detail, self.bytes[d.offset as usize], f)?; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:402
                writeln!(f)?; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:406
            }
        }
        Ok(()) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:409
    }
}
impl Flags {
    /// Get the flag values as raw bytes for hashing.
    pub fn hash_key(&self) -> &[u8] {
        &self.bytes // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:419
    }
}
