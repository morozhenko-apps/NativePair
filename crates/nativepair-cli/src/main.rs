#![forbid(unsafe_code)]

use std::{env, process::ExitCode};

use nativepair_core::{Capability, DeviceProfile, PhonePlatform};

const VERSION_LINE: &str = concat!("NativePair ", env!("CARGO_PKG_VERSION"));
const HELP: &str = concat!(
    "NativePair ",
    env!("CARGO_PKG_VERSION"),
    "\n\n",
    "Usage:\n",
    "  nativepair [--help]\n",
    "  nativepair --version\n\n",
    "The protocol-facing CLI will be added after M1 feasibility results are recorded.\n"
);

fn main() -> ExitCode {
    let mut args = env::args().skip(1);

    match args.next().as_deref() {
        Some("--version" | "-V") if args.next().is_none() => {
            println!("{VERSION_LINE}");
            ExitCode::SUCCESS
        }
        Some("--help" | "-h") if args.next().is_none() => {
            print!("{HELP}");
            ExitCode::SUCCESS
        }
        None => {
            let profile = DeviceProfile::new(PhonePlatform::Unknown);
            println!(
                "NativePair CLI foundation: contacts={:?}",
                profile.availability(Capability::Contacts)
            );
            ExitCode::SUCCESS
        }
        _ => {
            eprintln!("Unsupported arguments. Run 'nativepair --help'.");
            ExitCode::from(2)
        }
    }
}
