/* Opt-in glyph/geometry diagnostics and one current allied coordinate sample; native UI unchanged. */
(function () {
    'use strict';
    var OWNER = '__dkTacticalMinimapProbe', FEATURE = 'DriftkingsTacticalMinimapProbe';
    if (window[OWNER]) { window[OWNER].dispose(); }
    var disposed = false, node = null, binding = null, graphics = null, cartography = null, alignment = null;
    var inputListening = false, interaction = null;
    function hide() {
        interaction = null;
        if (node && node.parentNode) { node.parentNode.removeChild(node); }
        node = null; graphics = null; cartography = null;
        clearAlignment();
    }
    function release() {
        interaction = null;
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
    function validAlly(ally) {
        return ally && typeof ally.x === 'number' && isFinite(ally.x) && ally.x >= 0 && ally.x <= 1 &&
            typeof ally.y === 'number' && isFinite(ally.y) && ally.y >= 0 && ally.y <= 1;
    }
    function mapGrid(image) {
        var grid = document.createElement('div'); grid.className = 'dk-probe-map-grid';
        var rows = 'ABCDEFGHJK', columns = '1234567890';
        for (var i = 0; i < 10; i++) {
            var column = document.createElement('div'); column.className = 'dk-probe-grid-column';
            column.textContent = columns.charAt(i); column.style.left = (i * 10 + 5) + '%'; grid.appendChild(column);
            var row = document.createElement('div'); row.className = 'dk-probe-grid-row';
            row.textContent = rows.charAt(i); row.style.top = (i * 10 + 5) + '%'; grid.appendChild(row);
            if (i > 0) {
                var vertical = document.createElement('div'); vertical.className = 'dk-probe-grid-vertical';
                vertical.style.left = (i * 10) + '%'; grid.appendChild(vertical);
                var horizontal = document.createElement('div'); horizontal.className = 'dk-probe-grid-horizontal';
                horizontal.style.top = (i * 10) + '%'; grid.appendChild(horizontal);
            }
        }
        image.appendChild(grid);
        var points = document.createElement('div'); points.className = 'dk-probe-map-points';
        image.appendChild(points);
        return points;
    }
    function allyClass(ally) {
        var names = {lightTank: 'Ligeiro', mediumTank: 'Médio', heavyTank: 'Pesado', 'AT-SPG': 'Caça-tanques', SPG: 'Artilharia'};
        return ally && Object.prototype.hasOwnProperty.call(names, ally.vehicleClass) ? names[ally.vehicleClass] : null;
    }
    function mapPoints(points, allies) {
        var records = points._dkAllies || {}, seen = {};
        if (!Array.isArray(allies)) { allies = []; }
        allies.slice(0, 64).forEach(function (ally, index) {
            if (!validAlly(ally) || (ally.side && ally.side !== 'player' && ally.side !== 'ally' && ally.side !== 'platoon' && ally.side !== 'enemy' && ally.side !== 'training')) { return; }
            var key = 'slot' + index;
            seen[key] = true;
            var color = ally.side === 'player' ? '#ffffff' : ally.side === 'enemy' ? '#ee6868' : ally.side === 'platoon' ? '#ffc45b' : '#67cf69';
            if (ally.side === 'training') { color = ally.goal === true ? '#ffc45b' : '#ff9f5a'; }
            var destroyed = ally.state === 'destroyed';
            var kind = destroyed ? 'destroyed' : ally.side === 'player' ? 'player' : allyClass(ally) ? ally.vehicleClass : null;
            var signature = String(kind) + color, record = records[key];
            if (!record || record.signature !== signature) {
                if (record) { points.removeChild(record.node); }
                var marker = document.createElement('div');
                var glyphNode = null;
                marker.className = 'dk-probe-ally'; marker.textContent = destroyed ? 'X' : ally.side === 'player' ? 'TU' : ally.side === 'enemy' ? 'E' : ally.side === 'training' ? 'T' : 'A';
                if (kind && window.DKTacticalGraphics) {
                    try {
                        var glyph = window.DKTacticalGraphics.createGlyph(document, kind, color, 18);
                        marker.textContent = ''; marker.appendChild(glyph.node);
                        glyphNode = glyph.node;
                        marker.className += ' dk-probe-ally-icon';
                    } catch (error) { /* Keep A when SVG cannot be constructed. */ }
                }
                marker.style.color = color;
                var label = document.createElement('span'); label.className = 'dk-probe-vehicle-label';
                marker.appendChild(label);
                points.appendChild(marker);
                record = records[key] = {node: marker, signature: signature, glyph: glyphNode, label: label};
            }
            record.label.textContent = typeof ally.label === 'string' ? ally.label.replace(/[\x00-\x1f\x7f]/g, '').slice(0, 64) : '';
            record.label.className = 'dk-probe-vehicle-label' + (ally.x > .7 ? ' dk-probe-label-left' : '');
            record.node.style.opacity = destroyed ? .5 : 1;
            var heading = !destroyed && ally.side === 'player' && typeof ally.heading === 'number' && isFinite(ally.heading) ? ally.heading : 0;
            if (record.glyph && record.glyph.style) {
                record.glyph.style.transform = 'rotate(' + heading + 'deg)';
            }
            record.node.style.left = (100 * ally.x) + '%'; record.node.style.top = (100 * ally.y) + '%';
        });
        Object.keys(records).forEach(function (key) {
            if (!seen[key]) { points.removeChild(records[key].node); delete records[key]; }
        });
        points._dkAllies = records;
    }
    function mapObjectives(layer, values) {
        if (!Array.isArray(values)) { values = []; }
        var records = layer._dkObjectives || {}, seen = {};
        values.slice(0, 16).forEach(function (value, index) {
            if (!validAlly(value) || ['allyBase', 'enemyBase', 'controlPoint'].indexOf(value.kind) === -1) { return; }
            var key = 'objective' + index, record = records[key]; seen[key] = true;
            if (!record || record.kind !== value.kind) {
                if (record) { layer.removeChild(record.node); }
                var node = document.createElement('div'); node.className = 'dk-probe-objective';
                var color = value.kind === 'allyBase' ? '#67cf69' : value.kind === 'enemyBase' ? '#ee6868' : '#ffffff';
                node.style.color = color; node.textContent = value.kind === 'controlPoint' ? 'C' : 'B';
                if (window.DKTacticalGraphics) {
                    try {
                        var glyph = window.DKTacticalGraphics.createGlyph(document,
                            value.kind === 'controlPoint' ? 'controlPoint' : 'base', color, 22);
                        node.textContent = ''; node.appendChild(glyph.node);
                    } catch (error) { /* Retain B/C fallback. */ }
                }
                var label = document.createElement('div'); label.className = 'dk-probe-objective-number'; node.appendChild(label);
                var status = document.createElement('div'); status.className = 'dk-probe-objective-status'; node.appendChild(status);
                var bar = document.createElement('div'); bar.className = 'dk-probe-objective-bar';
                var fill = document.createElement('div'); bar.appendChild(fill); node.appendChild(bar);
                layer.appendChild(node); record = records[key] = {node: node, kind: value.kind,
                    label: label, status: status, bar: bar, fill: fill};
            }
            record.label.textContent = typeof value.number === 'number' && value.number > 0 && value.number <= 99 && value.number % 1 === 0 ? String(value.number) : '';
            var state = ['idle', 'capturing', 'blocked', 'captured'].indexOf(value.state) !== -1 ? value.state : 'unknown';
            var progress = typeof value.progress === 'number' && isFinite(value.progress) && value.progress >= 0 && value.progress <= 100 ? value.progress : null;
            record.status.textContent = state === 'captured' ? 'OK' : state === 'blocked' ? 'PAUSA' :
                state === 'capturing' && progress !== null ? Math.floor(progress) + '%' : state === 'unknown' ? '?' : '';
            record.bar.style.display = progress !== null && state !== 'idle' && state !== 'unknown' ? '' : 'none';
            record.fill.style.width = (progress === null ? 0 : progress) + '%';
            record.node.style.left = (100 * value.x) + '%'; record.node.style.top = (100 * value.y) + '%';
        });
        Object.keys(records).forEach(function (key) {
            if (!seen[key]) { layer.removeChild(records[key].node); delete records[key]; }
        });
        layer._dkObjectives = records;
    }
    function mapCircles(layer, values) {
        var records = layer._dkCircles || {}, seen = {};
        if (!Array.isArray(values)) { values = []; }
        values.slice(0, 4).forEach(function (value) {
            if (!validAlly(value) || ['draw', 'view', 'maxView', 'proximity'].indexOf(value.kind) === -1 ||
                    !/^#[0-9a-f]{6}$/i.test(value.color || '') || seen[value.kind] ||
                    !['rx', 'ry', 'alpha'].every(function (key) { return typeof value[key] === 'number' && isFinite(value[key]) && value[key] > 0; }) ||
                    value.rx > 100 || value.ry > 100 || value.alpha > 1) { return; }
            seen[value.kind] = true;
            var circle = records[value.kind];
            if (!circle) {
                circle = document.createElement('div'); circle.className = 'dk-probe-range-circle';
                layer.appendChild(circle); records[value.kind] = circle;
            }
            circle.style.left = (100 * (value.x - value.rx)) + '%';
            circle.style.top = (100 * (value.y - value.ry)) + '%';
            circle.style.width = (200 * value.rx) + '%'; circle.style.height = (200 * value.ry) + '%';
            circle.style.borderColor = value.color; circle.style.opacity = value.alpha;
        });
        Object.keys(records).forEach(function (key) {
            if (!seen[key]) { layer.removeChild(records[key]); delete records[key]; }
        });
        layer._dkCircles = records;
    }
    function mapPings(layer, values) {
        if (!Array.isArray(values)) { values = []; }
        var records = layer._dkPings || {}, seen = {};
        values.slice(0, 32).forEach(function (value, index) {
            if (!validAlly(value) || ['attention', 'going', 'cell', 'artillery', 'artilleryImpact'].indexOf(value.kind) === -1 ||
                    ['attack', 'idle', 'reply'].indexOf(value.state) === -1) { return; }
            var key = 'ping' + index, node = records[key]; seen[key] = true;
            if (!node) { node = records[key] = document.createElement('div'); layer.appendChild(node); }
            node.className = 'dk-probe-ping dk-probe-ping-' + value.kind;
            node.textContent = value.kind === 'cell' ? '' : value.kind === 'attention' ? '!' : '>';
            if (value.kind === 'artillery') { node.textContent = '+'; }
            if (value.kind === 'artilleryImpact') { node.textContent = ''; }
            if (value.state === 'reply') { node.textContent += 'R'; }
            node.style.opacity = value.state === 'idle' ? .65 : 1;
            node.style.left = (100 * value.x) + '%'; node.style.top = (100 * value.y) + '%';
        });
        Object.keys(records).forEach(function (key) {
            if (!seen[key]) { layer.removeChild(records[key]); delete records[key]; }
        });
        layer._dkPings = records;
    }
    function mapCamera(layer, value) {
        var keys = ['x', 'y', 'x2', 'y2'];
        var valid = value && keys.every(function (key) {
            return typeof value[key] === 'number' && isFinite(value[key]) && value[key] >= 0 && value[key] <= 1;
        });
        if (!valid || !document.createElementNS) {
            if (layer.firstChild) { layer.removeChild(layer.firstChild); }
            layer._dkLine = null;
            return;
        }
        if (!layer._dkLine) {
            var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('viewBox', '0 0 100 100'); svg.setAttribute('preserveAspectRatio', 'none');
            svg.style.width = '100%'; svg.style.height = '100%';
            var lineNode = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            lineNode.setAttribute('stroke', '#ffc45b'); lineNode.setAttribute('stroke-width', '.5');
            svg.appendChild(lineNode); layer.appendChild(svg); layer._dkLine = lineNode;
        }
        keys.forEach(function (key, index) {
            layer._dkLine.setAttribute(index === 0 ? 'x1' : index === 1 ? 'y1' : key, 100 * value[key]);
        });
    }
    function mapYawLimits(layer, values) {
        if (!Array.isArray(values) || values.length !== 2) { values = []; }
        while (layer.children.length > values.length) { layer.removeChild(layer.children[layer.children.length - 1]); }
        values.forEach(function (value, index) {
            var child = layer.children[index];
            if (!child) {
                child = document.createElement('div'); child.className = 'dk-probe-camera'; layer.appendChild(child);
            }
            mapCamera(child, value);
            if (child._dkLine) { child._dkLine.setAttribute('stroke', '#70dfff'); }
        });
    }
    function mapStrategic(layer, value) {
        if (!validAlly(value)) {
            if (layer.firstChild) { layer.removeChild(layer.firstChild); }
            return;
        }
        var marker = layer.firstChild;
        if (!marker) {
            marker = document.createElement('div'); marker.className = 'dk-probe-strategic-point';
            marker.textContent = '+'; layer.appendChild(marker);
        }
        marker.style.left = (100 * value.x) + '%'; marker.style.top = (100 * value.y) + '%';
    }
    function mapStrategicArea(layer, values) {
        var valid = Array.isArray(values) && values.length === 4 && values.every(function (point) {
            return point && ['x', 'y'].every(function (key) {
                return typeof point[key] === 'number' && isFinite(point[key]) && point[key] >= -4 && point[key] <= 5;
            });
        });
        if (!valid || !document.createElementNS) {
            if (layer.firstChild) { layer.removeChild(layer.firstChild); }
            layer._dkPolygon = null;
            return;
        }
        if (!layer._dkPolygon) {
            var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('viewBox', '0 0 100 100'); svg.setAttribute('preserveAspectRatio', 'none');
            svg.style.width = '100%'; svg.style.height = '100%';
            var polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            polygon.setAttribute('stroke', '#70dfff'); polygon.setAttribute('stroke-width', '.5');
            polygon.setAttribute('fill', 'none'); svg.appendChild(polygon); layer.appendChild(svg);
            layer._dkPolygon = polygon;
        }
        layer._dkPolygon.setAttribute('points', values.map(function (point) {
            return (100 * point.x) + ',' + (100 * point.y);
        }).join(' '));
    }
    function nativeInput(value) {
        if (!validAlly(value)) { return null; }
        return ['button', 'sizeIndex', 'sequence'].every(function (key) {
            var number = value[key], maximum = key === 'button' ? 4 : key === 'sizeIndex' ? 5 : 2147483647;
            return typeof number === 'number' && isFinite(number) && number >= 0 &&
                number <= maximum && Math.floor(number) === number;
        }) && value.sequence > 0 ? value : null;
    }
    function mapInput(layer, value) {
        value = nativeInput(value);
        mapStrategic(layer, value);
        if (value && layer.firstChild) { layer.firstChild.className = 'dk-probe-input-point'; }
    }
    function sampleInput(event) {
        if (disposed || !interaction || !binding || !cartography || typeof binding.model.onSampleInput !== 'function') { return; }
        var image = cartography.image;
        if (!image || typeof image.getBoundingClientRect !== 'function') { return; }
        var target = event.target, budget = 64;
        while (target && target !== image && --budget > 0) { target = target.parentNode; }
        if (target !== image) { return; }
        var rect = image.getBoundingClientRect(), button = event.button;
        if (!rect || !isFinite(rect.width) || !isFinite(rect.height) || rect.width <= 0 || rect.height <= 0 ||
                typeof event.clientX !== 'number' || typeof event.clientY !== 'number' ||
                !isFinite(event.clientX) || !isFinite(event.clientY) || [0, 1, 2].indexOf(button) === -1) { return; }
        var x = (event.clientX - rect.left) / rect.width, y = (event.clientY - rect.top) / rect.height;
        if (!isFinite(x) || !isFinite(y) || x < 0 || x > 1 || y < 0 || y > 1) { return; }
        event.preventDefault(); event.stopPropagation();
        try {
            if (binding.inputGeneration !== interaction.generation) {
                binding.inputGeneration = interaction.generation; binding.inputSequence = 0;
            }
            binding.inputSequence = Math.max(binding.inputSequence, interaction.request) + 1;
            if (binding.inputSequence > 2147483647) { return; }
            binding.model.onSampleInput({protocol: 1, generation: interaction.generation,
                request: binding.inputSequence, x: x, y: y, button: button === 1 ? 2 : button === 2 ? 1 : 0});
        } catch (error) {
            interaction = null; image.style.pointerEvents = 'none';
            console.error('[Driftkings] Sample input diagnostic failed', error);
        }
    }
    function mapSample(uri, allies, objectives, circles, pings, camera, yawLines, strategicPoint, strategicArea, input, sample) {
        if (typeof uri !== 'string' || uri.length > 262 ||
                !/^img:\/\/(spaces\/[A-Za-z0-9_/-]+\.(dds|png)|gui\/maps\/icons\/map\/[A-Za-z0-9_-]+\.png)$/.test(uri) ||
                uri.indexOf('//', 6) !== -1) { return null; }
        if (cartography && cartography.uri === uri) {
            mapPoints(cartography.points, allies);
            mapObjectives(cartography.objectives, objectives);
            mapCircles(cartography.circles, circles);
            mapPings(cartography.pings, pings);
            mapCamera(cartography.camera, camera);
            mapYawLimits(cartography.yaw, yawLines);
            mapStrategic(cartography.strategic, strategicPoint);
            mapStrategicArea(cartography.area, strategicPoint ? strategicArea : []);
            mapInput(cartography.input, input);
            mapInput(cartography.sample, sample);
            if (cartography.sample.firstChild) { cartography.sample.firstChild.className = 'dk-probe-gameface-point'; }
            return cartography.node;
        }
        var root = document.createElement('div');
        root.className = 'dk-probe-cartography';
        var caption = document.createElement('div');
        caption.textContent = 'Mapa de teste — veículos publicados';
        var image = document.createElement('div');
        image.className = 'dk-probe-map-image';
        image.style.backgroundImage = 'url("' + uri + '")';
        root.appendChild(caption); root.appendChild(image);
        var points = mapGrid(image);
        mapPoints(points, allies);
        var objectiveLayer = document.createElement('div'); objectiveLayer.className = 'dk-probe-objectives';
        image.appendChild(objectiveLayer); mapObjectives(objectiveLayer, objectives);
        var circleLayer = document.createElement('div'); circleLayer.className = 'dk-probe-range-layer';
        image.appendChild(circleLayer); mapCircles(circleLayer, circles);
        var pingLayer = document.createElement('div'); pingLayer.className = 'dk-probe-pings';
        image.appendChild(pingLayer); mapPings(pingLayer, pings);
        var cameraLayer = document.createElement('div'); cameraLayer.className = 'dk-probe-camera';
        image.appendChild(cameraLayer); mapCamera(cameraLayer, camera);
        var yawLayer = document.createElement('div'); yawLayer.className = 'dk-probe-camera';
        image.appendChild(yawLayer); mapYawLimits(yawLayer, yawLines);
        var strategicLayer = document.createElement('div'); strategicLayer.className = 'dk-probe-strategic';
        image.appendChild(strategicLayer); mapStrategic(strategicLayer, strategicPoint);
        var areaLayer = document.createElement('div'); areaLayer.className = 'dk-probe-strategic-area';
        image.appendChild(areaLayer); mapStrategicArea(areaLayer, strategicPoint ? strategicArea : []);
        var inputLayer = document.createElement('div'); inputLayer.className = 'dk-probe-strategic';
        image.appendChild(inputLayer); mapInput(inputLayer, input);
        var sampleLayer = document.createElement('div'); sampleLayer.className = 'dk-probe-strategic';
        image.appendChild(sampleLayer); mapInput(sampleLayer, sample);
        if (sampleLayer.firstChild) { sampleLayer.firstChild.className = 'dk-probe-gameface-point'; }
        cartography = {uri: uri, node: root, image: image, points: points, objectives: objectiveLayer, circles: circleLayer, pings: pingLayer, camera: cameraLayer, yaw: yawLayer, strategic: strategicLayer, area: areaLayer, input: inputLayer, sample: sampleLayer};
        return root;
    }
    function clearAlignment() {
        if (alignment && alignment.parentNode) { alignment.parentNode.removeChild(alignment); }
        alignment = null;
    }
    function alignNativeArea(data) {
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
        line(data.mapContext === 'topography' ? 'Topography — marcadores de treino publicados pelo cliente.' : 'Veículos atuais publicados; sem Lost Contact.');
        line('Seta própria: ' + (data.playerAvailable ? 'publicada' : 'indisponível'));
        line('Marcador aliado no mapa de teste: ' + (data.allyStatus || 'a aguardar'));
        if (validAlly(data.alliedPoint)) {
            line('Referência (primeiro aliado): ' + (allyClass(data.alliedPoint) || 'indisponível (A)') +
                (data.alliedPoint.side === 'player' ? ' | Tu' : data.alliedPoint.side === 'platoon' ? ' | Pelotão' : ' | Aliado'));
            line('Célula nativa: ' + (/^[A-HJK][1-90]$/.test(data.alliedPoint.cell || '') ? data.alliedPoint.cell : 'indisponível'));
            line('Aliado: ' + (100 * data.alliedPoint.x).toFixed(1) + '% horizontal / ' +
                (100 * data.alliedPoint.y).toFixed(1) + '% vertical');
        }
        calibration(data.calibration);
        var sizeIndex = data.calibration && data.calibration.sizeIndex;
        line('Tamanho nativo: ' + (typeof sizeIndex === 'number' && sizeIndex >= 0 && sizeIndex <= 5 && Math.floor(sizeIndex) === sizeIndex ? sizeIndex : 'indisponível'));
        var input = nativeInput(data.nativeInput);
        line(input ? 'Último clique no original #' + input.sequence + ': botão ' + input.button +
            ', escala ' + input.sizeIndex + ' (cruz magenta; apenas diagnóstico)' : 'Cliques nativos: a aguardar no original');
        var sample = nativeInput(data.gamefaceInput);
        var interactive = inputListening && data.sampleInputEnabled === true && data.acknowledged === true &&
            data.available === true && data.calibration && data.calibration.available === true;
        var request = data.sampleInputRequest;
        if (typeof request !== 'number' || !isFinite(request) || request < 0 || request > 2147483647 || Math.floor(request) !== request) { request = 0; }
        interaction = interactive ? {generation: data.generation, request: request} : null;
        line('Input da amostra: ' + (interactive ? 'esquerdo via cliente; restantes botões em diagnóstico' : 'inativo'));
        if (sample && typeof sample.localX === 'number' && isFinite(sample.localX) &&
                typeof sample.localY === 'number' && isFinite(sample.localY)) {
            line('Gameface → Python #' + sample.sequence + ': ' + sample.localX.toFixed(1) + ', ' + sample.localY.toFixed(1) + ' px nativos (cruz turquesa)');
            var statuses = {forwarded: 'entregue ao cliente', 'diagnostic-replay': 'replay: apenas diagnóstico',
                'diagnostic-button': 'botão apenas diagnóstico', 'native-input-unavailable': 'envio nativo indisponível',
                'third-party-owner': 'outro componente controla o minimapa', 'unsupported-mode': 'modo não suportado',
                'modal-view': 'janela modal aberta', 'invalid-input': 'coordenadas inválidas', failed: 'falha nativa; pedido não repetido'};
            line('Clique: ' + (statuses[data.gamefaceInput.dispatch] || 'diagnóstico'));
        }
        alignNativeArea(data.calibration);
        line('Calibração: NO/NE/SO/SE nos cantos; + no centro nativo.');
        var allies = Array.isArray(data.alliedPoints) ? data.alliedPoints : (data.alliedPoint ? [data.alliedPoint] : []);
        allies = allies.filter(function (point) { return point && (!point.side || ['player', 'ally', 'platoon'].indexOf(point.side) !== -1); }).slice(0, 64);
        var enemies = Array.isArray(data.enemyPoints) ? data.enemyPoints.filter(function (point) { return point && point.side === 'enemy'; }).slice(0, 64) : [];
        var wrecks = Array.isArray(data.destroyedPoints) ? data.destroyedPoints.filter(function (point) {
            return point && point.state === 'destroyed' && ['player', 'ally', 'platoon', 'enemy'].indexOf(point.side) !== -1;
        }).slice(0, 64) : [];
        var training = data.mapContext === 'topography' && Array.isArray(data.trainingPoints) ? data.trainingPoints.filter(function (point) {
            return point && point.side === 'training' && ['training', 'destroyed'].indexOf(point.state) !== -1;
        }).slice(0, 64) : [];
        var vehicles = allies.concat(enemies, wrecks, training).slice(0, 64);
        if (data.mapContext === 'topography') { line('Topography: ' + training.length + ' marcadores | laranja: treino; dourado: objetivo atual'); }
        line('Destruídos publicados: ' + wrecks.length + ' (símbolo X)');
        line('Veículos na amostra: ' + vehicles.length + ' | branco: tu; verde: aliado; amarelo: pelotão; vermelho: inimigo avistado');
        line('Bases/objetivos: ' + (Array.isArray(data.objectives) ? data.objectives.length : 0) + ' (captura publicada pelo cliente)');
        line('Círculos nativos: ' + (Array.isArray(data.circles) ? data.circles.length : 0));
        line('Pings nativos: ' + (Array.isArray(data.pings) ? data.pings.length : 0) + ' | quadrado: célula; ! atenção; > destino; + artilharia; ponto vermelho: impacto; R resposta');
        line('Direção da câmara arcade: ' + (data.cameraLine ? 'publicada' : 'indisponível/oculta'));
        line('Limites do canhão: ' + (Array.isArray(data.yawLines) && data.yawLines.length === 2 ? 'publicados (azul)' : 'indisponíveis/ocultos'));
        line('Ponto de mira estratégico: ' + (data.strategicPoint ? 'publicado (mira azul)' : 'indisponível/oculto'));
        line('Contorno estratégico: ' + (Array.isArray(data.strategicArea) && data.strategicArea.length === 4 ? 'publicado' : 'indisponível/oculto'));
        var map = mapSample(data.textureUri, vehicles, data.objectives, data.circles, data.pings, data.cameraLine, data.yawLines, data.strategicPoint, data.strategicArea, input, sample);
        if (cartography) { cartography.image.style.pointerEvents = interactive ? 'auto' : 'none'; }
        if (map) { node.appendChild(map); }
        line('Amostras fixas — 16 / 24 / 32 px; confirmar visualmente.');
        var glyphSample = graphicsSample();
        node.appendChild(glyphSample.node);
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
        if (inputListening) { document.removeEventListener('mousedown', sampleInput, true); inputListening = false; }
        release(); hide();
        if (window[OWNER] && window[OWNER].dispose === dispose) { delete window[OWNER]; }
    }
    window[OWNER] = {dispose: dispose};
    engine.whenReady.then(function () {
        if (disposed) { return; }
        engine.on('viewEnv.onDataChanged', refresh);
        engine.on('subViews.onAdded', refresh); engine.on('subViews.onRemoved', refresh);
        window.addEventListener('unload', dispose);
        if (document.addEventListener && document.removeEventListener) {
            document.addEventListener('mousedown', sampleInput, true); inputListening = true;
        }
        refresh();
    });
}());
