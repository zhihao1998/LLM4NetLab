# This file includes code adapted from the following open-source project:
# https://github.com/microsoft/AIOpsLab
# Licensed under the MIT License.

# Original notice:
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Interface for fault injector classes."""

import time


class BaseFaultInjector:
    def __init__(self):
        pass

    def _inject(self, fault_type: str, *args, **kwargs):
        self._invoke_method("inject", fault_type, *args, **kwargs)
        time.sleep(6)

    def _recover(
        self,
        fault_type: str,
        *args,
        **kwargs,  # Additional parameters for specific fault types
    ):
        self._invoke_method("recover", fault_type, *args, **kwargs)
        time.sleep(6)

    def _invoke_method(self, action_prefix, fault_type, *args, **kwargs):
        """helper: injects/recovers faults based on name"""
        method_name = f"{action_prefix}_{fault_type}"
        method = getattr(self, method_name, None)
        if method:
            method(*args, **kwargs)
        else:
            print(f"Unknown fault type: {fault_type}")


if __name__ == "__main__":
    # Example usage
    injector = BaseFaultInjector()
    injector._inject("packet_loss", "simple_bmv2", "10s")
    injector._recover("packet_loss", "simple_bmv2")
    print("Fault injection and recovery completed.")
