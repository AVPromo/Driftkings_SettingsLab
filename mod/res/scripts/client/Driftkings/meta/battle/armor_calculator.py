# -*- coding: utf-8 -*-
from Driftkings.meta.battle.base import CrosshairMeta


class ArmorCalculatorMeta(CrosshairMeta):
    FLASH_CLASS = 'driftkings.battle.components.armor_calculator.ArmorCalculatorUI'

    def as_armorCalculatorS(self, text):
        if self._isDAAPIInited():
            return self.flashObject.as_armorCalculator(text)
