/* Presentation only: Python supplies damage, target, state and progress. */
(function () {
    'use strict';
    var K = window.__dkMarksKit;
    var root = K.node('div', 'dk-main-gun', document.body);
    var content = K.node('div', 'dk-main-gun__content', root);
    var medal = K.node('img', 'dk-main-gun__medal', content);
    medal.src = 'coui://gui/maps/icons/achievement/32x32/mainGun.png';
    medal.alt = '';
    var info = K.node('div', 'dk-main-gun__info', content);
    var primary = K.node('div', 'dk-main-gun__value', info);
    var secondary = K.node('div', 'dk-main-gun__secondary', info);
    var footer = K.node('div', 'dk-main-gun__footer', content);
    var track = K.node('div', 'dk-main-gun__track', footer);
    var fill = K.node('div', 'dk-main-gun__fill', track);
    var percentage = K.node('span', 'dk-main-gun__percentage', footer);

    function render(data) {
        var cfg = data.config || {};
        var interactive = cfg.draggable === true && cfg.locked === false;
        var accent = K.theme(root, cfg, true, 290);
        var color = data.state === 'unavailable' ? '#D77D7D' :
            data.state === 'achieved' ? '#7DCEA0' : accent;
        K.style(root, 'borderColor', 'rgba(218,170,88,0.65)');
        K.style(root, 'pointerEvents', interactive ? 'auto' : 'none');
        K.style(content, 'cursor', interactive ? 'move' : 'default');
        K.style(primary, 'color', data.state === 'unavailable' ? color : '#F2F0EB');
        K.style(primary, 'fontSize', data.state === 'unavailable' ? '17rem' : '25rem');
        K.text(primary, data.primaryText);
        K.text(secondary, data.secondaryText);
        secondary.title = data.secondaryText || '';
        K.show(secondary, cfg.showSecondary !== false);
        K.show(track, cfg.showProgress !== false);
        K.show(percentage, cfg.showPercentage !== false);
        K.show(footer, cfg.showProgress !== false || cfg.showPercentage !== false);
        K.style(fill, 'backgroundColor', color);
        K.style(fill, 'width', K.number(data.progress, 0) + '%');
        K.text(percentage, data.progressText);
        track.title = data.progressLabel || '';
    }

    K.connect('DriftkingsMainGun', '__dkMainGun', root, render, K.position, K.savedPosition);
}());
