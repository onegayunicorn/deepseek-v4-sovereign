"""SOVEREIGN — policy engine.

Evaluates named policies (no-leak, no-destructive-tool, data-residency, ...)
against an event context. Policies are declarative: a predicate name plus
parameters, evaluated by a small registry of check functions.
"""

from __future__ import annotations

from typing import Any, Callable

from sovereign.utils.errors import SovereignError

_PREDICATES: dict[str, Callable[[dict[str, Any], dict[str, Any]], bool]] = {}


def predicate(name: str) -> Callable:
    def deco(fn: Callable[[dict[str, Any], dict[str, Any]], bool]) -> Callable:
        _PREDICATES[name] = fn
        return fn

    return deco


@predicate("allow_tool")
def _allow_tool(event: dict[str, Any], params: dict[str, Any]) -> bool:
    return event.get("tool") in params.get("tools", [])


@predicate("block_tool")
def _block_tool(event: dict[str, Any], params: dict[str, Any]) -> bool:
    return event.get("tool") not in params.get("tools", [])


@predicate("no_external_egress")
def _no_external_egress(event: dict[str, Any], params: dict[str, Any]) -> bool:
    # Sovereignty rule: payloads must not leave the node unless allow-listed.
    return not event.get("egress", False) or event.get("destination") in params.get("allow", [])


@predicate("max_rate")
def _max_rate(event: dict[str, Any], params: dict[str, Any]) -> bool:
    return event.get("rate", 0) <= params.get("max", 1000)


@predicate("role_has")
def _role_has(event: dict[str, Any], params: dict[str, Any]) -> bool:
    return event.get("role") in params.get("roles", [])


class PolicyEngine:
    """Evaluate all policies that apply to an event type."""

    def __init__(self, policies: list[dict[str, Any]] | None = None):
        self.policies = policies or []

    def add(self, policy: dict[str, Any]) -> None:
        self.policies.append(policy)

    def evaluate(self, event_type: str, event: dict[str, Any]) -> list[dict[str, Any]]:
        violations: list[dict[str, Any]] = []
        for policy in self.policies:
            if policy.get("event") not in (None, "*", event_type):
                continue
            for rule in policy.get("rules", []):
                fn = _PREDICATES.get(rule.get("predicate"))
                if fn is None:
                    raise SovereignError(f"unknown policy predicate: {rule.get('predicate')}")
                if not fn(event, rule.get("params", {})):
                    violations.append(
                        {
                            "policy": policy.get("name", "unnamed"),
                            "rule": rule.get("predicate"),
                            "params": rule.get("params", {}),
                        }
                    )
        return violations

    def permits(self, event_type: str, event: dict[str, Any]) -> bool:
        return not self.evaluate(event_type, event)
