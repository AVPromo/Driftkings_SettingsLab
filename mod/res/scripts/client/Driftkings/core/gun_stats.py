# -*- coding: utf-8 -*-
"""Pure gun statistics (reload and DPM); no game-engine imports, so it is testable off-client."""

# Crew skill/equipment reload multiplier, keyed by (eq2, eq3, eq4) being active.
# Values are the legacy constants previously encoded as an if/elif chain.
CREW_RELOAD_BONUS = {
    (True, True, True): 1.32,
    (True, True, False): 1.27,
    (True, False, True): 1.21,
    (True, False, False): 1.16,
    (False, True, True): 1.27,
    (False, True, False): 1.21,
    (False, False, True): 1.16,
    (False, False, False): 1.10,
}
RAMMER_FACTOR = 0.9


def crew_bonus(eq2=1, eq3=1, eq4=1):
    """Crew reload multiplier; only the value 1 counts as an active slot."""
    return CREW_RELOAD_BONUS[(eq2 == 1, eq3 == 1, eq4 == 1)]


def reload_with_equipment(reload_time, clip_size, eq1=1, eq2=1, eq3=1, eq4=1):
    """Base reload adjusted for rammer (single-shot guns only) and the crew bonus, rounded to 2 decimals."""
    rammer = RAMMER_FACTOR if clip_size == 1 and eq1 == 1 else 1
    return round(reload_time / (0.57 + 0.43 * crew_bonus(eq2, eq3, eq4)) * rammer, 2)


def damage_per_minute(reload_time, clip_size, clip_interval, damage):
    """Full-clip DPM, or None when the cycle time is not positive."""
    cycle = reload_time + (clip_size - 1) * clip_interval
    if cycle <= 0:
        return None
    return int(round(clip_size / cycle * 60 * damage, 0))
