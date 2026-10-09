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

        profile.set_availability(Capability::Contacts, Availability::TemporarilyUnavailable);

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

#[cfg(test)]
mod exhaustive_contract_tests {
    use super::{Availability, Capability, DeviceProfile, PhonePlatform};

    const PLATFORMS: [PhonePlatform; 3] = [
        PhonePlatform::Android,
        PhonePlatform::Ios,
        PhonePlatform::Unknown,
    ];
    const CAPABILITIES: [Capability; 5] = [
        Capability::Messages,
        Capability::Contacts,
        Capability::Calls,
        Capability::AppNotifications,
        Capability::FileTransfer,
    ];
    const STATES: [Availability; 4] = [
        Availability::Unknown,
        Availability::Unavailable,
        Availability::Available,
        Availability::TemporarilyUnavailable,
    ];

    #[test]
    fn given_each_platform_when_profile_created_then_all_capabilities_unknown() {
        for platform in PLATFORMS {
            // Arrange / Act
            let profile = DeviceProfile::new(platform);
            // Assert
            assert_eq!(profile.platform(), platform);
            for capability in CAPABILITIES {
                assert_eq!(profile.availability(capability), Availability::Unknown);
                assert!(!profile.supports(capability));
            }
        }
    }

    #[test]
    fn given_each_state_when_capability_updated_then_previous_and_new_states_are_exact() {
        for platform in PLATFORMS {
            for capability in CAPABILITIES {
                for old in STATES {
                    for new in STATES {
                        // Arrange
                        let mut profile = DeviceProfile::new(platform);
                        assert_eq!(
                            profile.set_availability(capability, old),
                            Availability::Unknown
                        );
                        // Act
                        let previous = profile.set_availability(capability, new);
                        // Assert
                        assert_eq!(previous, old);
                        assert_eq!(profile.availability(capability), new);
                        assert_eq!(profile.supports(capability), new == Availability::Available);
                        assert_eq!(profile.platform(), platform);
                        assert_eq!(profile.set_availability(capability, new), new);
                        assert_eq!(profile.availability(capability), new);
                    }
                }
            }
        }
    }

    #[test]
    fn given_independent_capabilities_when_one_changes_then_other_states_are_preserved() {
        for platform in PLATFORMS {
            for target in CAPABILITIES {
                for existing in STATES {
                    for replacement in STATES {
                        // Arrange
                        let mut profile = DeviceProfile::new(platform);
                        for capability in CAPABILITIES {
                            profile.set_availability(capability, existing);
                        }
                        let original = profile.clone();
                        // Act
                        profile.set_availability(target, replacement);
                        // Assert
                        for capability in CAPABILITIES {
                            let expected = if capability == target {
                                replacement
                            } else {
                                existing
                            };
                            assert_eq!(profile.availability(capability), expected);
                            assert_eq!(original.availability(capability), existing);
                        }
                    }
                }
            }
        }
    }
}
