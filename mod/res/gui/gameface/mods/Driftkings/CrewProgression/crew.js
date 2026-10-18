(function () {
    'use strict';
    if (window.__dkCrewProgression) { window.__dkCrewProgression.dispose(); }
    var FEATURE = 'DriftkingsCrewProgression', disposed = false, pending = null, observer = null;
    var model = null, resourceId = null, callbackId = null, lastPayload = null, data = {}, mounted = [];
    var SLOT = '[data-dk-crew-slot][data-dk-crew-id]';
    function owned(node) { return !!(node && node.classList && node.classList.contains('dk-crew-progress')); }
    function clear() {
        mounted.forEach(function (entry) {
            if (entry.badge.parentNode) { entry.badge.parentNode.removeChild(entry.badge); }
            entry.host.classList.remove('dk-crew-progress-host');
        });
        mounted = [];
    }
    function release() {
        if (callbackId !== null) { viewEnv.removeDataChangedCallback(callbackId, resourceId); }
        model = null; resourceId = null; callbackId = null; lastPayload = null; data = {};
    }
    function readModel() {
        var ids = window.subViews ? window.subViews.ids() : [];
        for (var i = 0; i < ids.length; i++) {
            var child = window.subViews.get(ids[i]), next = child && child.model;
            if (!next || !next.DriftkingsUI || next.DriftkingsUI.name !== FEATURE) { continue; }
            if (resourceId !== ids[i] || model !== next) {
                release(); resourceId = ids[i]; model = next;
                callbackId = viewEnv.addDataChangedCallback('model', resourceId, true);
            }
            if (lastPayload !== model.payload) {
                lastPayload = model.payload;
                try { data = JSON.parse(model.payload || '{}'); } catch (error) { data = {}; }
            }
            return;
        }
        release();
    }
    function render() {
        pending = null;
        if (disposed) { return; }
        readModel(); clear();
        if (!(data.config || {}).visible) { return; }
        var rows = data.rows || [], slots = document.querySelectorAll(SLOT);
        for (var i = 0; i < slots.length; i++) {
            var slot = slots[i], id = Number(slot.getAttribute('data-dk-crew-id'));
            var index = Number(slot.getAttribute('data-dk-crew-slot')), row = null;
            for (var j = 0; j < rows.length; j++) {
                if (rows[j].id === id && rows[j].slot === index) { row = rows[j]; break; }
            }
            if (!row || !slot.parentNode) { continue; }
            var host = slot.parentNode, badge = document.createElement('div');
            badge.className = 'dk-crew-progress';
            (row.lines || []).forEach(function (value) {
                var line = document.createElement('div'); line.className = 'dk-crew-progress__line';
                line.textContent = value; badge.appendChild(line);
            });
            host.classList.add('dk-crew-progress-host'); host.appendChild(badge);
            mounted.push({host: host, badge: badge});
        }
    }
    function schedule() { if (!disposed && pending === null) { pending = setTimeout(render, 0); } }
    function changed() { if (!observer || !model || model.payload !== lastPayload) { schedule(); } }
    function mutations(records) {
        for (var i = 0; i < records.length; i++) {
            var record = records[i];
            if (record.type === 'attributes') { schedule(); return; }
            if (owned(record.target) || owned(record.target.parentNode)) { continue; }
            var nodes = Array.prototype.slice.call(record.addedNodes).concat(Array.prototype.slice.call(record.removedNodes));
            for (var j = 0; j < nodes.length; j++) {
                if (!owned(nodes[j])) { schedule(); return; }
            }
        }
    }
    function dispose() {
        if (disposed) { return; }
        disposed = true;
        if (pending !== null) { clearTimeout(pending); pending = null; }
        if (observer) { observer.disconnect(); observer = null; }
        engine.off('viewEnv.onDataChanged', changed); engine.off('subViews.onAdded', schedule); engine.off('subViews.onRemoved', schedule);
        window.removeEventListener('unload', dispose);
        clear(); release();
        if (window.__dkCrewProgression && window.__dkCrewProgression.dispose === dispose) { delete window.__dkCrewProgression; }
    }
    window.__dkCrewProgression = {dispose: dispose};
    engine.whenReady.then(function () {
        if (disposed) { return; }
        engine.on('viewEnv.onDataChanged', changed); engine.on('subViews.onAdded', schedule); engine.on('subViews.onRemoved', schedule);
        window.addEventListener('unload', dispose);
        if (window.MutationObserver) {
            observer = new MutationObserver(mutations);
            observer.observe(document.body, {childList: true, subtree: true, attributes: true,
                attributeFilter: ['data-dk-crew-slot', 'data-dk-crew-id']});
        }
        schedule();
    });
}());
