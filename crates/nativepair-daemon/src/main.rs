#![forbid(unsafe_code)]

use nativepair_core::{Capability, DeviceProfile, PhonePlatform};

fn main() {
    // The foundation daemon deliberately does not open Bluetooth sessions yet.
    // M1 protocol feasibility work will introduce the first real adapter.
    let profile = DeviceProfile::new(PhonePlatform::Unknown);
    let messages = profile.availability(Capability::Messages);

    println!("NativePair daemon foundation: messages={messages:?}");
}
