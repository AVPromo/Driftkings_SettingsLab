# -*- coding: utf-8 -*-
"""Format the native Flash statistics and vehicle dossier fields."""
from driftkings.common.utils.colorRatting import getStatisticColor
from driftkings.core.hooks import override
from driftkings.core.profile_ratings import account_wn8
from driftkings.settings.service import settings_service


def enabled():
    settings = settings_service.getComponentDict('hangar_preferences')
    return settings.get('enabled', True) and settings.get('profileRatingColors', True)


def colored(text, metric, value):
    if not enabled() or value is None or value < 0:
        return text
    return u'<font color="{}">{}</font>'.format(getStatisticColor(metric, value), text)


def install():
    from gui.Scaleform.daapi.view.lobby.profile import ProfileUtils as fields
    from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import ProfileAllStatisticsVO
    from gui.Scaleform.daapi.view.lobby.profile.ProfileTechnique import ProfileTechnique
    from gui.Scaleform.daapi.view.lobby.profile.ProfileStatistics import ProfileStatistics
    from driftkings.stats.vehinfo import getVehicleInfoData

    # These native fields use HTML text. Keep all other modes/fields unchanged.
    specifications = (
        ('_BattlesCountField', 'battles', 'getBattlesCount', 1),
        ('_WinsEfficiencyField', 'winrate', 'getWinsEfficiency', 100),
        ('_DamageCoefficientField', 'tdv', 'getDamageEfficiency', 1),
        ('_HitsField', 'hitsRatio', 'getHitsEfficiency', 100),
        ('_AvgDmgField', 'avgDamage', 'getAvgDamage', 1),
        ('_AvgEnemiesSpottedField', 'avgSpotted', 'getAvgEnemiesSpotted', 1),
        ('_AvgDestroyedField', 'avgFrags', 'getAvgFrags', 1),
    )

    def handler(metric, method, scale):
        def build(original, field, stats, current):
            text = original(field, stats, current)
            value = getattr(stats, method)()
            return colored(text, metric, value * scale if value is not None else None)
        return build

    for name, metric, method, scale in specifications:
        override(getattr(fields, name), '_buildData')(handler(metric, method, scale))

    @override(ProfileAllStatisticsVO, '_getHeaderData')
    def header(original, vo, data):
        result = [dict(item) for item in original(vo, data)]
        stats, dossier = data[0], data[1]
        for index, metric, value in ((0, 'battles', stats.getBattlesCount()),
                                      (1, 'winrate', stats.getWinsEfficiency() * 100 if stats.getWinsEfficiency() is not None else None),
                                      (2, 'avgDamage', stats.getAvgDamage())):
            result[index]['text'] = colored(result[index]['text'], metric, value)
        settings = settings_service.getComponentDict('hangar_preferences')
        if settings.get('enabled', True) and settings.get('showProfileWN8', True):
            value = account_wn8(dossier.getRandomStats(), getVehicleInfoData)
            text = colored(str(value), 'wn8', value) if value is not None else '--'
            item = fields.ProfileUtils.packLditItemData(text, 'WN8', '', 'avgPersonalRating40x32.png')
            # Appended after the native mastery badge; no native item is replaced.
            result.append(item)
        return tuple(result)

    @override(ProfileTechnique, '_getTechniqueListVehicles')
    def vehicles(original, view, *args, **kwargs):
        rows = original(view, *args, **kwargs)
        if not enabled():
            return rows
        # vehicleTF is HTML; the numeric columns remain numeric for sorting.
        result = []
        for row in rows:
            item = dict(row)
            item['shortUserName'] = colored(item['shortUserName'], 'winrate', item.get('winsEfficiency'))
            result.append(item)
        return result

    def refresh_view(view):
        if view.isActive():
            view.invokeUpdate()
            if isinstance(view, ProfileTechnique) and view._selectedVehicleIntCD is not None:
                view.requestData(view._selectedVehicleIntCD)

    def changed(view):
        def refresh(*args):
            refresh_view(view)
        return refresh

    def populated(original, view):
        result = original(view)
        view._dkProfileColorsChanged = changed(view)
        settings_service.onModSettingsChanged.connect(view._dkProfileColorsChanged, 'hangar_preferences')
        return result

    def disposed(original, view):
        callback = getattr(view, '_dkProfileColorsChanged', None)
        if callback is not None:
            settings_service.onModSettingsChanged.disconnect(callback)
            del view._dkProfileColorsChanged
        return original(view)

    for target in (ProfileStatistics, ProfileTechnique):
        override(target, '_populate')(populated)
        override(target, '_dispose')(disposed)
