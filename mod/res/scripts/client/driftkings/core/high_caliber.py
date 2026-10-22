# -*- coding: utf-8 -*-
"""Single High Caliber target projection; no engine or presentation dependencies."""


def project(base, competitor, damage, dynamic, friendly, alive, available):
    target = max(base, competitor) if dynamic else base
    remaining = max(0, target - damage)
    eligible = not friendly
    reason = ''
    if friendly:
        reason = 'ineligible'
    elif remaining and not alive:
        reason = 'destroyed'
    elif remaining and available is not None and available < remaining:
        reason = 'insufficient'
    state = 'unavailable' if reason else 'achieved' if remaining == 0 else 'progress'
    return dict(state=state, reason=reason, damage=damage, target=target,
                remaining=remaining, eligible=eligible, dynamic=bool(dynamic),
                progress=max(0.0, min(100.0, 100.0 * damage / target)) if target else 0.0)
