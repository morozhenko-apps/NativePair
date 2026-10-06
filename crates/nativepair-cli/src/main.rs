#![forbid(unsafe_code)]

use nativepair_core::{Capability, DeviceProfile, PhonePlatform};

fn main() {
    let profile = DeviceProfile::new(PhonePlatform::Unknown);

    println!(
        "NativePair CLI foundation: contacts={:?}",
        profile.availability(Capability::Contacts)
    );
}
