#![forbid(unsafe_code)]

use std::{env, process::ExitCode};

use nativepair_core::{Capability, DeviceProfile, PhonePlatform};

const VERSION_LINE: &str = concat!("NativePair daemon ", env!("CARGO_PKG_VERSION"));

fn main() -> ExitCode {
    let mut args = env::args().skip(1);

    match args.next().as_deref() {
        Some("--version" | "-V") if args.next().is_none() => {
            println!("{VERSION_LINE}");
            ExitCode::SUCCESS
        }
        None => {
            // The foundation daemon deliberately does not open Bluetooth sessions yet.
            // M1 protocol feasibility work will introduce the first real adapter.
            let profile = DeviceProfile::new(PhonePlatform::Unknown);
            let messages = profile.availability(Capability::Messages);

            println!("NativePair daemon foundation: messages={messages:?}");
            ExitCode::SUCCESS
        }
        _ => {
            eprintln!("Unsupported arguments. Use --version or start without arguments.");
            ExitCode::from(2)
        }
    }
}
