(function () {
    'use strict';
    if (window.__dkProfileRatings) { window.__dkProfileRatings.dispose(); }
    var bindings = {}, painted = [], pending = null, observer, disposed = false;
    function restore() {
        painted.forEach(function (saved) {
            saved.node.style.color = saved.value;
        });
        painted = [];
    }
    function paint(node, color) {
        if (!node || !/^#[0-9a-f]{6}$/i.test(color || '')) { return; }
        painted.push({node: node, value: node.style.color || ''});
        node.style.color = color;
    }
    function release(id) {
        viewEnv.removeDataChangedCallback(bindings[id].callback);
        delete bindings[id];
    }
    function render() {
        pending = null;
        if (disposed) { return; }
        restore();
        var present = {}, ids = window.subViews ? window.subViews.ids() : [];
        ids.forEach(function (id) {
            var child = window.subViews.get(id), model = child && child.model;
            if (!model || !model.DriftkingsUI || model.DriftkingsUI.name !== 'DriftkingsProfileRatings') { return; }
            present[id] = true;
            if (!bindings[id] || bindings[id].model !== model) {
                if (bindings[id]) { release(id); }
                bindings[id] = {model: model, callback: viewEnv.addDataChangedCallback('model', id, true)};
            }
            var data;
            try { data = JSON.parse(model.payload || '{}'); } catch (error) { return; }
            var root = document.querySelector('[class*="Statistic_base_"]');
            if (!root) { return; }
            // Native order: damage, XP, battles, destroyed, assistance, blocked.
            var cards = root.querySelectorAll('[class*="StatisticItem_base_"]');
            if (cards.length !== 6) { return; }
            paint(cards[0].querySelector('[class*="StatisticItem_caption_"]'), data.damage);
            paint(cards[2].querySelector('[class*="StatisticItem_amount_"]'), data.battles);
            paint(cards[2].querySelector('[class*="StatisticItem_caption_"]'), data.wins);
            var points = root.querySelector('[class*="Points_base_"]');
            paint(points, data.rating);
            if (points) {
                paint(points.querySelector('[class*="Points_prevPoints_"]'), data.previousRating);
                paint(points.querySelector('[class*="Points_newPoints_"]'), data.rating);
            }
        });
        Object.keys(bindings).forEach(function (id) { if (!present[id]) { release(id); } });
    }
    function schedule() { if (!disposed && pending === null) { pending = setTimeout(render, 0); } }
    function dispose() {
        disposed = true;
        if (pending !== null) { clearTimeout(pending); }
        if (observer) { observer.disconnect(); }
        engine.off('viewEnv.onDataChanged', schedule);
        engine.off('subViews.onAdded', schedule);
        engine.off('subViews.onRemoved', schedule);
        window.removeEventListener('unload', dispose);
        restore();
        Object.keys(bindings).forEach(release);
    }
    window.__dkProfileRatings = {dispose: dispose};
    engine.whenReady.then(function () {
        if (disposed) { return; }
        engine.on('viewEnv.onDataChanged', schedule);
        engine.on('subViews.onAdded', schedule);
        engine.on('subViews.onRemoved', schedule);
        window.addEventListener('unload', dispose);
        if (window.MutationObserver) {
            observer = new MutationObserver(schedule);
            observer.observe(document.body, {childList: true, subtree: true, characterData: true});
        }
        schedule();
    });
}());
