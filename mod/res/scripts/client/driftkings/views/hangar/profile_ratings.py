# -*- coding: utf-8 -*-
"""Rating colors for the native achievements summary, without replacing values."""
import json

from driftkings.common.utils.colorRatting import getStatisticColor
from driftkings.core.hooks import override
from driftkings.interface_catalog import gameface_spec
from driftkings.logger import get_logger
from driftkings.settings.service import settings_service

FEATURE = 'DriftkingsProfileRatings'
LOG = get_logger('Driftkings.ProfileRatings')


def colors(presenter):
    settings = settings_service.getComponentDict('hangar_preferences')
    dossier = getattr(presenter, '_SummaryView__dossier', None)
    if not settings.get('enabled', True) or not settings.get('profileRatingColors', True) or dossier is None:
        return {}
    stats = dossier.getRandomStats()
    model = presenter.viewModel
    wins = stats.getWinsEfficiency()
    result = {'battles': getStatisticColor('battles', stats.getBattlesCount()),
              'damage': getStatisticColor('avgDamage', stats.getAvgDamage())}
    if wins is not None:
        result['wins'] = getStatisticColor('winrate', wins * 100)
    if model.getBattlesLeftCount() == 0:
        metric = 'wtr' if model.getIsWTREnabled() else 'wgr'
        result['rating'] = getStatisticColor(metric, model.getPersonalScore())
        result['previousRating'] = getStatisticColor(metric, model.getPrevPersonalScore())
    return result


def install():
    from frameworks.wulf import ViewModel
    from gui.impl.pub.view_component import ViewComponent
    from gui.impl.lobby.achievements.achievements_main_view import AchievementMainView
    from gui.impl.lobby.achievements.summary.summary_view import SummaryView
    from driftkings.ui.gameface import attach_assets, resource_id

    layout_id = resource_id(gameface_spec(FEATURE)['resource'])

    class RatingsModel(ViewModel):
        def __init__(self):
            super(RatingsModel, self).__init__(properties=3, commands=0)

        def _initialize(self):
            super(RatingsModel, self)._initialize()
            self._addStringProperty('payload', '{}')
            attach_assets(self, FEATURE)

    class RatingsView(ViewComponent):
        def __init__(self):
            self.presenter = None
            super(RatingsView, self).__init__(layoutID=layout_id, model=RatingsModel)

        def _onLoading(self, *args, **kwargs):
            super(RatingsView, self)._onLoading(*args, **kwargs)
            settings_service.onModSettingsChanged.connect(self.refresh)

        def refresh(self, *args):
            # SummaryView uses slots without weak-reference support. The child
            # retains it only until finalization, where this reference is cleared.
            presenter = self.presenter
            try:
                payload = colors(presenter) if presenter is not None else {}
            except Exception:
                LOG.exception('Could not color native profile statistics')
                payload = {}
            self.getViewModel()._setString(0, json.dumps(payload))

        def _finalize(self):
            settings_service.onModSettingsChanged.disconnect(self.refresh)
            self.presenter = None
            super(RatingsView, self)._finalize()

    @override(SummaryView, '_SummaryView__updatePage')
    def updated(original, presenter, *args, **kwargs):
        result = original(presenter, *args, **kwargs)
        child = presenter.parentView.getChildView(layout_id)
        if child is not None:
            child.presenter = presenter
            child.refresh()
        return result

    @override(AchievementMainView, '_onLoading')
    def loaded(original, view, *args, **kwargs):
        result = original(view, *args, **kwargs)
        child = view.getChildView(layout_id)
        if child is None:
            child = RatingsView()
            view.setChildView(layout_id, child)
        if child is not None and isinstance(view.currentPresenter, SummaryView):
            child.presenter = view.currentPresenter
            child.refresh()
        return result
