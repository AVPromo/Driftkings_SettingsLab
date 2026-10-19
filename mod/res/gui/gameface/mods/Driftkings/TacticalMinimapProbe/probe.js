/* Opt-in glyph/geometry diagnostics and one current allied coordinate sample; native UI unchanged. */
(function () {
    'use strict';
    var OWNER = '__dkTacticalMinimapProbe', FEATURE = 'DriftkingsTacticalMinimapProbe';
    if (window[OWNER]) { window[OWNER].dispose(); }
    var disposed = false, node = null, binding = null, graphics = null, cartography = null, alignment = null;
    function hide() {
        if (node && node.parentNode) { node.parentNode.removeChild(node); }
        node = null; graphics = null; cartography = null;
        clearAlignment();
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
    function graphicsSample() {
        if (graphics) { return graphics; }
        var root = document.createElement('div');
        root.className = 'dk-probe-glyphs';
        graphics = {node: root, report: {svgApi: false, glyphCount: 0}};
        var definitions = [
            ['lightTank', 'LT', '#67cf69'], ['mediumTank', 'MT', '#ffc45b'],
            ['heavyTank', 'HT', '#ee6868'], ['AT-SPG', 'TD', '#67cf69'],
            ['SPG', 'SPG', '#ee6868'], ['player', 'TU', '#ffffff'], ['destroyed', 'X', '#8c8c7e']
        ];
        try {
            if (!window.DKTacticalGraphics || typeof window.DKTacticalGraphics.createGlyph !== 'function') {
                throw new Error('Tactical glyph library unavailable');
            }
            definitions.forEach(function (definition) {
                var column = document.createElement('div'); column.className = 'dk-probe-glyph-column';
                var title = document.createElement('div'); title.textContent = definition[1]; column.appendChild(title);
                [16, 24, 32].forEach(function (size) {
                    column.appendChild(window.DKTacticalGraphics.createGlyph(
                        document, definition[0], definition[2], size).node);
                    graphics.report.glyphCount++;
                });
                root.appendChild(column);
            });
            graphics.report.svgApi = true;
        } catch (error) {
            while (root.firstChild) { root.removeChild(root.firstChild); }
            root.textContent = 'SVG DOM indisponível: teste gráfico omitido.';
        }
        return graphics;
    }
    function mapSample(uri) {
        if (typeof uri !== 'string' || uri.length > 262 ||
                !/^img:\/\/(spaces\/[A-Za-z0-9_/-]+\.(dds|png)|gui\/maps\/icons\/map\/[A-Za-z0-9_-]+\.png)$/.test(uri) ||
                uri.indexOf('//', 6) !== -1) { return null; }
        if (cartography && cartography.uri === uri) { return cartography.node; }
        var root = document.createElement('div');
        root.className = 'dk-probe-cartography';
        var caption = document.createElement('div');
        caption.textContent = 'Amostra da textura — confirmar visualmente';
        var image = document.createElement('div');
        image.className = 'dk-probe-map-image';
        image.style.backgroundImage = 'url("' + uri + '")';
        root.appendChild(caption); root.appendChild(image);
        cartography = {uri: uri, node: root};
        return root;
    }
    function clearAlignment() {
        if (alignment && alignment.parentNode) { alignment.parentNode.removeChild(alignment); }
        alignment = null;
    }
    function alignNativeArea(data, ally) {
        clearAlignment();
        if (!data || data.available !== true) { return; }
        var keys = ['x', 'y', 'width', 'height', 'stageWidth', 'stageHeight'];
        if (!keys.every(function (key) { return typeof data[key] === 'number' && isFinite(data[key]); }) ||
                data.stageWidth <= 0 || data.stageHeight <= 0 || data.width <= 0 || data.height <= 0 ||
                data.width > data.stageWidth * 4 || data.height > data.stageHeight * 4 ||
                Math.abs(data.x) > data.stageWidth * 4 || Math.abs(data.y) > data.stageHeight * 4) { return; }
        alignment = document.createElement('div');
        alignment.id = 'dk-tactical-minimap-alignment';
        alignment.style.left = (100 * data.x / data.stageWidth) + '%';
        alignment.style.top = (100 * data.y / data.stageHeight) + '%';
        alignment.style.width = (100 * data.width / data.stageWidth) + '%';
        alignment.style.height = (100 * data.height / data.stageHeight) + '%';
        [[0, 0, 'NO'], [100, 0, 'NE'], [50, 50, '+'], [0, 100, 'SO'], [100, 100, 'SE']].forEach(function (point) {
            var mark = document.createElement('div');
            mark.className = 'dk-probe-anchor';
            mark.style.left = point[0] + '%'; mark.style.top = point[1] + '%';
            mark.textContent = point[2]; alignment.appendChild(mark);
        });
        if (ally && typeof ally.x === 'number' && isFinite(ally.x) && ally.x >= 0 && ally.x <= 1 &&
                typeof ally.y === 'number' && isFinite(ally.y) && ally.y >= 0 && ally.y <= 1) {
            var marker = document.createElement('div');
            marker.className = 'dk-probe-ally'; marker.textContent = 'A';
            marker.style.left = (100 * ally.x) + '%'; marker.style.top = (100 * ally.y) + '%';
            alignment.appendChild(marker);
        }
        document.body.appendChild(alignment);
    }
    function calibration(data) {
        if (!data || data.available !== true) {
            line('Geometria Flash: ' + (data && data.reason || 'a aguardar'));
            return;
        }
        var keys = ['x', 'y', 'width', 'height', 'stageWidth', 'stageHeight'];
        if (!keys.every(function (key) { return typeof data[key] === 'number' && isFinite(data[key]); })) { return; }
        line('Área Flash: ' + data.x + ', ' + data.y + ' | ' + data.width + ' × ' + data.height +
            ' | palco ' + data.stageWidth + ' × ' + data.stageHeight);
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
        line('Um aliado para calibração; sem inimigos ou Lost Contact.');
        calibration(data.calibration);
        alignNativeArea(data.calibration, data.alliedPoint);
        line('Calibração: NO/NE/SO/SE nos cantos; + no centro nativo.');
        var map = mapSample(data.textureUri);
        if (map) { node.appendChild(map); }
        line('Amostras fixas — 16 / 24 / 32 px; confirmar visualmente.');
        var sample = graphicsSample();
        node.appendChild(sample.node);
        if (data.graphics) {
            line('SVG DOM: ' + (data.graphics.svgApi ? 'disponível' : 'indisponível') +
                ' | nós construídos: ' + data.graphics.glyphCount + '/21');
        }
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
                try {
                    var report = graphicsSample().report;
                    model.onProbeReady({protocol: 1, generation: data.generation,
                        svgApi: report.svgApi, glyphCount: report.glyphCount});
                }
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
