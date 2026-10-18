# -*- coding: utf-8 -*-
"""Read current native crew costs without modifying inventory or training."""
import logging

from Driftkings.core.crew_progression import progression

LOG = logging.getLogger('Driftkings.CrewProgression')


def collect_rows(vehicle, items):
    rows = []
    if vehicle is None:
        return rows
    for slot, tankman in vehicle.crew:
        row = {'slot': slot, 'id': None, 'name': '', 'role': '',
               'state': 'empty', 'remainingXP': None, 'estimatedBattles': None,
               'averageXP': None, 'roleTraining': False}
        if tankman is not None:
            row['state'] = 'unavailable'
            try:
                row.update(id=tankman.invID, name=tankman.getFullUserNameWithSkin(),
                           role=tankman.roleUserName)
                complete = tankman.allSkillsLearned()
                remaining = 0 if complete else tankman.getNextSkillXpCost()
                # Native free XP can exceed the remaining skill cost.
                if remaining is not None and remaining < 0:
                    remaining = 0
                average = None
                if remaining is not None and remaining > 0:
                    dossier = items.getTankmanDossier(tankman.invID)
                    average = dossier.getAvgXP() if dossier is not None and dossier.getBattlesCount() else None
                row.update(progression(remaining, average, complete))
                row['roleTraining'] = not tankman.isMaxRoleLevel
            except Exception:
                LOG.exception('Could not read crew progression for slot %s', slot)
                row.update(state='unavailable')
        rows.append(row)
    return rows
