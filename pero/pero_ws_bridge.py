"""Bridge PERO frames into the main orchestrator WebSocket bus."""

from __future__ import annotations

from typing import Awaitable, Callable

from .live_ingest import LaserFrame

BroadcastFn = Callable[[dict], Awaitable[None]]


def attach_pero_to_orchestrator_ws(broadcast_fn: BroadcastFn) -> Callable[[LaserFrame], Awaitable[None]]:
    async def listener(frame: LaserFrame) -> None:
        await broadcast_fn(
            {
                "type": "pero",
                "data": {
                    "t": frame.t,
                    "crystal": frame.crystal,
                    "wavelength_nm": frame.wavelength_nm,
                    "power_mw": frame.power_mw,
                    "temperature_c": frame.temperature_c,
                    "splitting_efficiency": frame.splitting_efficiency,
                    "spatial_coherence": frame.spatial_coherence,
                    "bell_fidelity": frame.bell_fidelity,
                    "pairs_this_frame": frame.pairs_this_frame,
                },
            }
        )

    return listener
