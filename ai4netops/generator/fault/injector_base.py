"""Interface for fault injector classes."""

class BaseFaultInjector:
    """Base class for fault injectors."""

    def inject_fault(self, device, fault):
        """Inject a fault on a device."""
        raise NotImplementedError