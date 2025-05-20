# This file includes code adapted from the following open-source project:
# https://github.com/microsoft/AIOpsLab
# Licensed under the MIT License.

# Originalt notice:
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Interface for fault injector classes."""

import time


class BaseFaultInjector:
    def __init__(self):
        pass

    def _inject(self, fault_type: str, microservices: list[str] = None, duration: str = None):
        if duration:
            self._invoke_method("inject", fault_type, microservices, duration)
        elif microservices:
            self._invoke_method("inject", fault_type, microservices)
        else:
            self._invoke_method("inject", fault_type)
        time.sleep(6)

    def _recover(
        self,
        fault_type: str,
        microservices: list[str] = None,
    ):
        if microservices and fault_type:
            self._invoke_method("recover", fault_type, microservices)
        elif fault_type:
            self._invoke_method("recover", fault_type)
        time.sleep(6)

    def _invoke_method(self, action_prefix, *args):
        """helper: injects/recovers faults based on name"""
        method_name = f"{action_prefix}_{args[0]}"
        method = getattr(self, method_name, None)
        if method:
            method(*args[1:])
        else:
            print(f"Unknown fault type: {args[0]}")
