/* Driftkings-owned loader: catalog assets, ordered scripts and explicit disposal. */
(function () {
    'use strict';
    if (window.__dkUIBridge) { return; }
    var active = {}, retiring = {}, disposed = false;
    /* GENERATED CATALOG START */
    var features = {
        "DriftkingsBattleEfficiency": {
            "owner": "__dkBattleEfficiency",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/shared/flash_text.js",
                "coui://gui/gameface/mods/Driftkings/BattleEfficiency/results.js"
            ],
            "styles": [
                "coui://gui/gameface/mods/Driftkings/BattleEfficiency/results.css"
            ]
        },
        "DriftkingsCarouselStats": {
            "owner": "__dkCarouselStats",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/CarouselStats/carousel_native.js",
                "coui://gui/gameface/mods/Driftkings/CarouselStats/carousel_layout.js",
                "coui://gui/gameface/mods/Driftkings/CarouselStats/carousel.js"
            ],
            "styles": [
                "coui://gui/gameface/mods/Driftkings/CarouselStats/carousel.css"
            ]
        },
        "DriftkingsCrewDetails": {
            "owner": "__dkCrewDetails",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/CrewDetails/details.js"
            ],
            "styles": [
                "coui://gui/gameface/mods/Driftkings/CrewDetails/details.css"
            ]
        },
        "DriftkingsCrewProgression": {
            "owner": "__dkCrewProgression",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/CrewProgression/crew.js"
            ],
            "styles": []
        },
        "DriftkingsHangarClock": {
            "owner": "__dkHangarClock",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/HangarClock/clock.js"
            ],
            "styles": [
                "coui://gui/gameface/mods/Driftkings/HangarClock/clock.css"
            ]
        },
        "DriftkingsHangarHeaderOptions": {
            "owner": "__dkHangarHeaderOptions",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/HangarHeaderOptions/header_options.js"
            ],
            "styles": []
        },
        "DriftkingsMainGun": {
            "owner": "__dkMainGun",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/shared/marks_panel.js",
                "coui://gui/gameface/mods/Driftkings/MainGun/main_gun.js"
            ],
            "styles": [
                "coui://gui/gameface/mods/Driftkings/MainGun/main_gun.css"
            ]
        },
        "DriftkingsMarksOnGunBattle": {
            "owner": "__dkBattleMarks",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/shared/marks_panel.js",
                "coui://gui/gameface/mods/Driftkings/MarksOnGunBattle/marks.js"
            ],
            "styles": [
                "coui://gui/gameface/mods/Driftkings/shared/marks_panel.css",
                "coui://gui/gameface/mods/Driftkings/MarksOnGunBattle/marks.css"
            ]
        },
        "DriftkingsMarksOnGunHangar": {
            "owner": "__dkHangarMarks",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/shared/marks_panel.js",
                "coui://gui/gameface/mods/Driftkings/MarksOnGunHangar/marks.js"
            ],
            "styles": [
                "coui://gui/gameface/mods/Driftkings/shared/marks_panel.css",
                "coui://gui/gameface/mods/Driftkings/MarksOnGunHangar/marks.css"
            ]
        },
        "DriftkingsMarksOnGunTechTree": {
            "owner": "__dkTechMarks",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/MarksOnGunTechTree/marks.js"
            ],
            "styles": [
                "coui://gui/gameface/mods/Driftkings/shared/marks_tokens.css",
                "coui://gui/gameface/mods/Driftkings/MarksOnGunTechTree/marks.css"
            ]
        },
        "DriftkingsRatingPlayers": {
            "owner": "__dkPlayerRatings",
            "scripts": [
                "coui://gui/gameface/mods/Driftkings/RatingPlayers/rating_text.js",
                "coui://gui/gameface/mods/Driftkings/RatingPlayers/rating_rows.js",
                "coui://gui/gameface/mods/Driftkings/RatingPlayers/ratings.js"
            ],
            "styles": []
        }
    };
    /* GENERATED CATALOG END */

    function remove(node) {
        node.onload = node.onerror = null;
        if (node.parentNode) { node.parentNode.removeChild(node); }
    }
    function disposeOwner(name) {
        var key = features[name].owner, owner = window[key];
        try {
            if (owner && typeof owner.dispose === 'function') { owner.dispose(); }
        } catch (error) {
            console.error('[Driftkings] Cannot dispose UI owner: ' + name, error);
        } finally {
            if (window[key] === owner) { delete window[key]; }
        }
    }
    function unload(name) {
        var entry = active[name];
        if (!entry) { return; }
        entry.cancelled = true;
        delete active[name];
        // Let an in-flight script finish before loading another generation.
        // It may still execute after its view disappeared and create an owner.
        if (entry.pending) { retiring[name] = entry; }
        disposeOwner(name);
        entry.nodes.forEach(function (node) {
            if (node !== entry.pending) { remove(node); }
        });
    }
    function retired(name, entry, node) {
        disposeOwner(name);
        remove(node);
        if (retiring[name] === entry) { delete retiring[name]; }
        if (!disposed) { refresh(); }
    }
    function load(name) {
        if (disposed || active[name] || retiring[name] || !features[name]) { return; }
        var spec = features[name];
        var entry = active[name] = {nodes: [], pending: null, cancelled: false};
        spec.styles.forEach(function (url) {
            var node = document.createElement('link');
            node.rel = 'stylesheet'; node.href = url;
            node.onerror = function () {
                if (active[name] === entry) { unload(name); }
            };
            entry.nodes.push(node); document.head.appendChild(node);
        });
        function next(index) {
            if (disposed || entry.cancelled || index >= spec.scripts.length) { return; }
            var node = document.createElement('script');
            node.async = false; node.src = spec.scripts[index];
            node.onload = function () {
                entry.pending = null;
                node.onload = node.onerror = null;
                if (entry.cancelled) { retired(name, entry, node); return; }
                next(index + 1);
            };
            node.onerror = function () {
                entry.pending = null;
                console.error('[Driftkings] Cannot load UI asset: ' + node.src);
                if (entry.cancelled) { retired(name, entry, node); return; }
                unload(name);
            };
            entry.pending = node;
            entry.nodes.push(node); document.head.appendChild(node);
        }
        next(0);
    }
    function refresh() {
        if (disposed || !window.subViews) { return; }
        var present = {};
        window.subViews.ids().forEach(function (id) {
            var child = window.subViews.get(id);
            var meta = child && child.model && child.model.DriftkingsUI;
            if (meta && features[meta.name]) { present[meta.name] = true; load(meta.name); }
        });
        Object.keys(active).forEach(function (name) { if (!present[name]) { unload(name); } });
    }
    function dispose() {
        if (disposed) { return; }
        disposed = true;
        engine.off('subViews.onAdded', refresh);
        engine.off('subViews.onRemoved', refresh);
        Object.keys(active).forEach(unload);
        window.removeEventListener('unload', dispose);
        if (window.__dkUIBridge === bridge) { delete window.__dkUIBridge; }
    }
    var bridge = window.__dkUIBridge = {dispose: dispose};
    engine.whenReady.then(function () {
        if (disposed) { return; }
        engine.on('subViews.onAdded', refresh);
        engine.on('subViews.onRemoved', refresh);
        window.addEventListener('unload', dispose);
        refresh();
    });
}());
