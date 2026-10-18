/* Feed the native crew tooltip; no nodes above crew portraits. */
(function () {
    'use strict';
    if (window.__dkCrewProgression) { window.__dkCrewProgression.dispose(); }
    var model = null, resourceId = null, callbackId = null, signature = null, data = {}, disposed = false;
    function notify() { window.dispatchEvent(new Event('dk-carousel-config')); }
    function release() {
        if (callbackId !== null) { viewEnv.removeDataChangedCallback(callbackId, resourceId); }
        callbackId = null; resourceId = null; model = null; signature = null; data = {};
    }
    function refresh() {
        if (disposed) { return; }
        var ids = window.subViews ? window.subViews.ids() : [], found = false;
        for (var i = 0; i < ids.length; i++) {
            var child = window.subViews.get(ids[i]), next = child && child.model;
            if (!next || !next.DriftkingsUI || next.DriftkingsUI.name !== 'DriftkingsCrewProgression') { continue; }
            found = true;
            if (resourceId !== ids[i] || model !== next) {
                release(); resourceId = ids[i]; model = next;
                callbackId = viewEnv.addDataChangedCallback('model', resourceId, true);
            }
            if (signature !== model.payload) {
                signature = model.payload;
                try { data = JSON.parse(signature || '{}'); } catch (error) { data = {}; }
                notify();
            }
            break;
        }
        if (!found && model) { release(); notify(); }
    }
    function getRow(id) {
        if (!(data.config || {}).visible) { return null; }
        var rows = data.rows || [];
        for (var i = 0; i < rows.length; i++) { if (rows[i].id === id) { return rows[i]; } }
        return null;
    }
    function dispose() {
        if (disposed) { return; }
        disposed = true;
        engine.off('viewEnv.onDataChanged', refresh); engine.off('subViews.onAdded', refresh); engine.off('subViews.onRemoved', refresh);
        window.removeEventListener('unload', dispose); release();
        if (window.__dkCrewProgression && window.__dkCrewProgression.dispose === dispose) { delete window.__dkCrewProgression; }
        notify();
    }
    window.__dkCrewProgression = {getRow: getRow, dispose: dispose};
    engine.whenReady.then(function () {
        if (disposed) { return; }
        engine.on('viewEnv.onDataChanged', refresh); engine.on('subViews.onAdded', refresh); engine.on('subViews.onRemoved', refresh);
        window.addEventListener('unload', dispose); refresh();
    });
}());
