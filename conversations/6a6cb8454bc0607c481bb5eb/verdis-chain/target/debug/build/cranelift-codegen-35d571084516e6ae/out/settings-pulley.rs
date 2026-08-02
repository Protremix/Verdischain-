#[derive(Clone, PartialEq, Hash)] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:426
/// Flags group `pulley`.
pub struct Flags {
    bytes: [u8; 2], // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:429
}
impl Flags {
    /// Create flags pulley settings group.
    #[allow(unused_variables, reason = "generated code")] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:26
    pub fn new(shared: &settings::Flags, builder: &Builder) -> Self {
        let bvec = builder.state_for("pulley"); // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:31
        let mut pulley = Self { bytes: [0; 2] }; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:32
        debug_assert_eq!(bvec.len(), 2); // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:38
        pulley.bytes[0..2].copy_from_slice(&bvec); // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:43
        pulley // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:64
    }
}
impl Flags {
    /// Iterates the setting values.
    pub fn iter(&self) -> impl Iterator<Item = Value> + use<> {
        let mut bytes = [0; 2]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:74
        bytes.copy_from_slice(&self.bytes[0..2]); // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:75
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
/// Values for `pulley.pointer_width`.
#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash)] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:147
pub enum PointerWidth {
    /// `pointer32`.
    Pointer32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:151
    /// `pointer64`.
    Pointer64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:151
}
impl PointerWidth {
    /// Returns a slice with all possible [PointerWidth] values. // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:92
    pub fn all() -> &'static [PointerWidth] {
        &[ // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:98
            Self::Pointer32, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:101
            Self::Pointer64, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:101
        ] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:104
    }
}
impl fmt::Display for PointerWidth {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str(match *self {
            Self::Pointer32 => "pointer32", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:116
            Self::Pointer64 => "pointer64", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:116
        }
        ) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:119
    }
}
impl core::str::FromStr for PointerWidth {
    type Err = (); // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:125
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "pointer32" => Ok(Self::Pointer32), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:129
            "pointer64" => Ok(Self::Pointer64), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:129
            _ => Err(()), // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:131
        }
    }
}
/// User-defined settings.
#[allow(dead_code, reason = "generated code")] // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:209
impl Flags {
    /// Dynamic numbered predicate getter.
    fn numbered_predicate(&self, p: usize) -> bool {
        self.bytes[1 + p / 8] & (1 << (p % 8)) != 0 // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:214
    }
    /// The width of pointers for this Pulley target
    /// Supported values:
    /// * 'pointer32'
    /// * 'pointer64'
    pub fn pointer_width(&self) -> PointerWidth {
        match self.bytes[0] {
            0 => {
                PointerWidth::Pointer32
            }
            1 => {
                PointerWidth::Pointer64
            }
            _ => {
                panic!("Invalid enum value")
            }
        }
    }
    /// Whether this is a big-endian target
    /// Whether this is a big-endian target
    pub fn big_endian(&self) -> bool {
        self.numbered_predicate(0) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:171
    }
}
static DESCRIPTORS: [detail::Descriptor; 2] = [ // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:253
    detail::Descriptor {
        name: "pointer_width", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "The width of pointers for this Pulley target", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Enum { last: 1, enumerators: 0 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:274
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
    detail::Descriptor {
        name: "big_endian", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:261
        description: "Whether this is a big-endian target", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:262
        offset: 1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:263
        detail: detail::Detail::Bool { bit: 0 }, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:266
    }
    , // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:288
]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:304
static ENUMERATORS: [&str; 2] = [ // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:307
    "pointer32", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:310
    "pointer64", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:310
]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:313
static HASH_TABLE: [u16; 4] = [ // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:323
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
    0, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    1, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:327
    0xffff, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:335
]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:339
static PRESETS: [(u8, u8); 0] = [ // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:342
]; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:359
static TEMPLATE: detail::Template = detail::Template {
    name: "pulley", // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:374
    descriptors: &DESCRIPTORS, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:375
    enumerators: &ENUMERATORS, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:376
    hash_table: &HASH_TABLE, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:377
    defaults: &[0x00, 0x00], // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:378
    presets: &PRESETS, // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:379
}
; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:382
/// Create a `settings::Builder` for the pulley settings group.
pub fn builder() -> Builder {
    Builder::new(&TEMPLATE) // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:389
}
impl fmt::Display for Flags {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        writeln!(f, "[pulley]")?; // /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/cranelift-codegen-meta-0.123.13/src/gen_settings.rs:398
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
