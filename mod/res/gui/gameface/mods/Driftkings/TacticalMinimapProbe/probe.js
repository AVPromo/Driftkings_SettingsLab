/* Diagnostic text only. Never renders markers or manipulates native minimap UI. */
(function () {
    'use strict';
    var OWNER = '__dkTacticalMinimapProbe', FEATURE = 'DriftkingsTacticalMinimapProbe';
    if (window[OWNER]) { window[OWNER].dispose(); }
    var disposed = false, node = null, binding = null;
    function hide() {
        if (node && node.parentNode) { node.parentNode.removeChild(node); }
        node = null;
    }
    function release() {
        if (binding && binding.callback !== null) { viewEnv.removeDataChangedCallback(binding.callback, binding.id); }
        binding = null;
    }
    function line(text, className) {
        var child = document.createElement('div');
        child.className = className || '';
        child.textContent = text;
        node.appendChild(child);
    }
    function render(data) {
        if (!data || data.enabled !== true || data.protocol !== 1 || data.effectiveMode !== 'vanilla') {
            hide(); return;
        }
        if (!node) {
            node = document.createElement('div'); node.id = 'dk-tactical-minimap-probe';
            document.body.appendChild(node);
        }
        while (node.firstChild) { node.removeChild(node.firstChild); }
        line('Tactical Minimap — diagnóstico | Vanilla preservado', 'dk-probe-title');
        line(data.acknowledged ? 'Gameface: ligação confirmada' : 'Gameface: a confirmar ligação',
            data.acknowledged ? 'dk-probe-ready' : 'dk-probe-pending');
        if (data.available) {
            line('Entradas nativas em AoI: ' + data.markerCount + ' (leitura parcial)');
            line('Textura: ' + data.texture);
            line('Limites: ' + (data.bounds || []).join(', '));
        } else {
            line('Fonte nativa: ' + (data.reason || 'indisponível'), 'dk-probe-pending');
        }
        line('Sem substituição do minimapa, posições ou Lost Contact.');
    }
    function update() {
        if (disposed || !window.subViews) { return; }
        var ids = window.subViews.ids(), found = false;
        for (var i = 0; i < ids.length; i++) {
            var child = window.subViews.get(ids[i]), model = child && child.model;
            if (!model || !model.DriftkingsUI || model.DriftkingsUI.name !== FEATURE) { continue; }
            found = true;
            if (!binding || binding.id !== ids[i] || binding.model !== model) {
                release();
                binding = {id: ids[i], model: model, callback: null, signature: null, sentGeneration: null};
                binding.callback = viewEnv.addDataChangedCallback('model', ids[i], true);
            }
            var data = {};
            try { data = JSON.parse(model.payload || '{}'); }
            catch (error) { binding.signature = null; hide(); return; }
            if (!data || typeof data !== 'object' || Array.isArray(data)) {
                binding.signature = null; hide(); return;
            }
            if (binding.signature !== model.payload) {
                binding.signature = model.payload;
                render(data);
            }
            if (data.enabled === true && data.protocol === 1 && data.effectiveMode === 'vanilla' &&
                    typeof data.generation === 'number' && binding.sentGeneration !== data.generation && typeof model.onProbeReady === 'function') {
                binding.sentGeneration = data.generation;
                try { model.onProbeReady({protocol: 1, generation: data.generation}); }
                catch (error) { binding.sentGeneration = null; console.error('[Driftkings] Diagnostic handshake failed', error); }
            }
            break;
        }
        if (!found) { release(); hide(); }
    }
    function refresh() {
        try { update(); }
        catch (error) { hide(); console.error('[Driftkings] Diagnostic update failed; Vanilla unchanged', error); }
    }
    function dispose() {
        if (disposed) { return; }
        disposed = true;
        engine.off('viewEnv.onDataChanged', refresh);
        engine.off('subViews.onAdded', refresh); engine.off('subViews.onRemoved', refresh);
        window.removeEventListener('unload', dispose);
        release(); hide();
        if (window[OWNER] && window[OWNER].dispose === dispose) { delete window[OWNER]; }
    }
    window[OWNER] = {dispose: dispose};
    engine.whenReady.then(function () {
        if (disposed) { return; }
        engine.on('viewEnv.onDataChanged', refresh);
        engine.on('subViews.onAdded', refresh); engine.on('subViews.onRemoved', refresh);
        window.addEventListener('unload', dispose);
        refresh();
    });
}());
