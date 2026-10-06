#![forbid(unsafe_code)]

//! Platform-neutral domain types for NativePair.
//!
//! This crate intentionally has no dependency on BlueZ, D-Bus, GTK, or other
//! transport/UI implementations.

use std::collections::BTreeMap;

/// Phone operating-system family.
///
/// Platform is descriptive metadata. It must never be treated as proof that a
/// capability is available on a particular device.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum PhonePlatform {
    Android,
    Ios,
    Unknown,
}

/// A user-visible feature that may be exposed by one or more protocol adapters.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Capability {
    Messages,
    Contacts,
    Calls,
    AppNotifications,
    FileTransfer,
}

/// Runtime availability of a capability on a particular device.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Availability {
    /// The capability has not been probed yet.
    Unknown,
    /// The capability was probed and is not available for this device/session.
    Unavailable,
    /// The capability is currently usable.
    Available,
    /// The capability is known but cannot currently be used.
    TemporarilyUnavailable,
}

/// Runtime capability profile for one paired device.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DeviceProfile {
    platform: PhonePlatform,
    capabilities: BTreeMap<Capability, Availability>,
}

impl DeviceProfile {
    #[must_use]
    pub fn new(platform: PhonePlatform) -> Self {
        Self {
            platform,
            capabilities: BTreeMap::new(),
        }
    }

    #[must_use]
    pub const fn platform(&self) -> PhonePlatform {
        self.platform
    }

    #[must_use]
    pub fn availability(&self, capability: Capability) -> Availability {
        self.capabilities
            .get(&capability)
            .copied()
            .unwrap_or(Availability::Unknown)
    }

    pub fn set_availability(
        &mut self,
        capability: Capability,
        availability: Availability,
    ) -> Availability {
        self.capabilities
            .insert(capability, availability)
            .unwrap_or(Availability::Unknown)
    }

    #[must_use]
    pub fn supports(&self, capability: Capability) -> bool {
        self.availability(capability) == Availability::Available
    }
}

#[cfg(test)]
mod tests {
    use super::{Availability, Capability, DeviceProfile, PhonePlatform};

    #[test]
    fn new_profile_reports_unprobed_capabilities_as_unknown() {
        let profile = DeviceProfile::new(PhonePlatform::Android);

        assert_eq!(
            profile.availability(Capability::Messages),
            Availability::Unknown
        );
        assert!(!profile.supports(Capability::Messages));
    }

    #[test]
    fn platform_does_not_imply_capability_support() {
        for platform in [
            PhonePlatform::Android,
            PhonePlatform::Ios,
            PhonePlatform::Unknown,
        ] {
            let profile = DeviceProfile::new(platform);

            assert!(!profile.supports(Capability::Messages));
            assert!(!profile.supports(Capability::Contacts));
            assert!(!profile.supports(Capability::Calls));
            assert!(!profile.supports(Capability::AppNotifications));
        }
    }

    #[test]
    fn available_capability_is_reported_as_supported() {
        let mut profile = DeviceProfile::new(PhonePlatform::Ios);

        let previous =
            profile.set_availability(Capability::AppNotifications, Availability::Available);

        assert_eq!(previous, Availability::Unknown);
        assert!(profile.supports(Capability::AppNotifications));
    }

    #[test]
    fn temporarily_unavailable_capability_is_not_reported_as_supported() {
        let mut profile = DeviceProfile::new(PhonePlatform::Android);

        profile.set_availability(
            Capability::Contacts,
            Availability::TemporarilyUnavailable,
        );

        assert_eq!(
            profile.availability(Capability::Contacts),
            Availability::TemporarilyUnavailable
        );
        assert!(!profile.supports(Capability::Contacts));
    }

    #[test]
    fn updating_capability_returns_previous_state() {
        let mut profile = DeviceProfile::new(PhonePlatform::Android);

        assert_eq!(
            profile.set_availability(Capability::Messages, Availability::Unavailable),
            Availability::Unknown
        );
        assert_eq!(
            profile.set_availability(Capability::Messages, Availability::Available),
            Availability::Unavailable
        );
        assert!(profile.supports(Capability::Messages));
    }
}
