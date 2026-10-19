/* Runtime-independent probe handshake/lifecycle tests, not an in-game test. */
'use strict';
var assert = require('assert'), fs = require('fs'), vm = require('vm'), path = require('path');
var listeners = {}, callbacks = {}, acknowledgements = [], removed = [], errors = [];
var serial = 0, model = null, callbackAdds = 0;
function Element() { this.children = []; this.parentNode = null; this.style = {}; }
Object.defineProperty(Element.prototype, 'firstChild', {get: function () { return this.children[0] || null; }});
Element.prototype.appendChild = function (child) { this.children.push(child); child.parentNode = this; };
Element.prototype.removeChild = function (child) {
    var index = this.children.indexOf(child); assert(index >= 0); this.children.splice(index, 1); child.parentNode = null;
};
var body = new Element(), windowEvents = {};
var win = {subViews: {ids: function () { return model ? [42] : []; }, get: function () { return {model: model}; }},
    addEventListener: function (key, fn) { windowEvents[key] = fn; },
    removeEventListener: function (key, fn) { assert.strictEqual(windowEvents[key], fn); delete windowEvents[key]; }};
var engine = {whenReady: {then: function (fn) { fn(); }},
    on: function (key, fn) { listeners[key] = fn; },
    off: function (key, fn) { assert.strictEqual(listeners[key], fn); delete listeners[key]; }};
var viewEnv = {addDataChangedCallback: function (key, id) {
    assert.strictEqual(key, 'model'); assert.strictEqual(id, 42); callbackAdds++;
    callbacks[++serial] = id; return serial;
}, removeDataChangedCallback: function (callback, id) {
    assert.strictEqual(callbacks[callback], id); delete callbacks[callback]; removed.push(callback);
}};
var data = {enabled: false, protocol: 1, generation: 1, effectiveMode: 'vanilla', available: true,
    acknowledged: false, markerCount: 3, texture: '<img onerror=bad>', bounds: [-1, -1, 1, 1]};
model = {DriftkingsUI: {name: 'DriftkingsTacticalMinimapProbe'}, payload: JSON.stringify(data),
    onProbeReady: function (args) { acknowledgements.push(args); }};
var script = fs.readFileSync(path.join(__dirname,
    '../../mod/res/gui/gameface/mods/Driftkings/TacticalMinimapProbe/probe.js'), 'utf8');
vm.runInNewContext(script, {window: win, document: {body: body, createElement: function () { return new Element(); }},
    engine: engine, viewEnv: viewEnv, console: {error: function () { errors.push(true); }}});
assert.strictEqual(body.children.length, 0);
assert.strictEqual(acknowledgements.length, 0);
function refresh() { model.payload = JSON.stringify(data); listeners['viewEnv.onDataChanged'](); }
data.enabled = true; refresh();
assert.strictEqual(acknowledgements.length, 1);
assert.strictEqual(acknowledgements[0].generation, 1);
assert.strictEqual(acknowledgements[0].protocol, 1);
assert.strictEqual(body.children.length, 1);
var box = body.children[0];
assert.strictEqual(box.children[3].textContent, 'Textura: <img onerror=bad>');
refresh();
assert.strictEqual(body.children[0], box);
assert.strictEqual(acknowledgements.length, 1);
assert.strictEqual(callbackAdds, 1);
data.acknowledged = true; refresh();
assert.strictEqual(box.children[1].className, 'dk-probe-ready');
data.textureUri = 'img://spaces/01_karelia/mmap.dds'; refresh();
var maps = box.children.filter(function (child) { return child.className === 'dk-probe-cartography'; });
assert.strictEqual(maps.length, 1);
assert.strictEqual(maps[0].children[1].style.backgroundImage, 'url("img://spaces/01_karelia/mmap.dds")');
var originalMap = maps[0];
data.markerCount++; refresh();
assert.strictEqual(box.children.filter(function (child) { return child.className === 'dk-probe-cartography'; })[0], originalMap);
data.textureUri = 'https://example.com/map.png'; refresh();
assert.strictEqual(box.children.filter(function (child) { return child.className === 'dk-probe-cartography'; }).length, 0);
data.calibration = {available: true, x: 800, y: 600, width: 200, height: 200, stageWidth: 1000, stageHeight: 800};
refresh();
var alignment = body.children.filter(function (child) { return child.id === 'dk-tactical-minimap-alignment'; })[0];
assert.strictEqual(alignment.style.left, '80%');
assert.strictEqual(alignment.style.top, '75%');
assert.strictEqual(alignment.style.width, '20%');
assert.strictEqual(alignment.style.height, '25%');
assert.strictEqual(alignment.children.length, 5);
assert.strictEqual(alignment.children[2].style.left, '50%');
data.textureUri = 'img://spaces/01_karelia/mmap.dds';
data.alliedPoint = {x: .25, y: .5}; refresh();
alignment = body.children.filter(function (child) { return child.id === 'dk-tactical-minimap-alignment'; })[0];
assert.strictEqual(alignment.children.length, 5);
var mapImage = box.children.filter(function (child) { return child.className === 'dk-probe-cartography'; })[0].children[1];
assert.strictEqual(mapImage.children.length, 11);
var grid = mapImage.children[0];
assert.strictEqual(grid.children.filter(function (child) { return child.className === 'dk-probe-grid-column'; }).map(function (child) { return child.textContent; }).join(''), '1234567890');
assert.strictEqual(grid.children.filter(function (child) { return child.className === 'dk-probe-grid-row'; }).map(function (child) { return child.textContent; }).join(''), 'ABCDEFGHJK');
var points = mapImage.children[1];
assert.strictEqual(points.children.length, 1);
assert.strictEqual(points.children[0].textContent, 'A');
assert.strictEqual(points.children[0].style.left, '25%');
assert.strictEqual(points.children[0].style.top, '50%');
delete data.alliedPoint; refresh();
assert.strictEqual(points.children.length, 0);
data.alliedPoint = {x: -1, y: .5}; refresh();
assert.strictEqual(points.children.length, 0);
delete data.alliedPoint;
alignment = body.children.filter(function (child) { return child.id === 'dk-tactical-minimap-alignment'; })[0];
assert.strictEqual(alignment.children.length, 5);
data.calibration.width = -1; refresh();
assert.strictEqual(body.children.length, 1);
delete data.calibration; refresh();
var validPayload = model.payload;
['{', 'null', '[]'].forEach(function (bad) {
    model.payload = bad; listeners['viewEnv.onDataChanged'](); assert.strictEqual(body.children.length, 0);
    model.payload = validPayload; listeners['viewEnv.onDataChanged'](); assert.strictEqual(body.children.length, 1);
});
data.generation = 2; data.acknowledged = false; refresh();
assert.strictEqual(acknowledgements.length, 2);
assert.strictEqual(acknowledgements[1].generation, 2);
data.effectiveMode = 'driftkings'; refresh();
assert.strictEqual(body.children.length, 0);
assert.strictEqual(acknowledgements.length, 2);
data.effectiveMode = 'vanilla'; data.enabled = false; refresh();
assert.strictEqual(body.children.length, 0);
model = null; listeners['subViews.onRemoved']();
assert.strictEqual(Object.keys(callbacks).length, 0);
var owner = win.__dkTacticalMinimapProbe;
owner.dispose(); owner.dispose();
assert.strictEqual(Object.keys(listeners).length, 0);
assert.strictEqual(Object.keys(windowEvents).length, 0);
assert.strictEqual(win.__dkTacticalMinimapProbe, undefined);
assert.strictEqual(errors.length, 0);
console.log('PASS: Gameface probe handshake, per-battle generation, safe text, recovery and disposal');

// First run deliberately had no graphics API: basic diagnostics must still work.
assert.strictEqual(acknowledgements[0].svgApi, false);
assert.strictEqual(acknowledgements[0].glyphCount, 0);

// Run the real shared glyph implementation against an SVG-capable DOM stub.
var svgNodesCreated = 0;
Element.prototype.setAttribute = function (key, value) {
    if (!this.attributes) { this.attributes = {}; }
    this.attributes[key] = value;
};
var documentEvents = {}, sampleCommands = [];
var graphicsDoc = {body: body, createElement: function () { return new Element(); },
    addEventListener: function (name, fn, capture) { assert.strictEqual(capture, true); assert(!documentEvents[name]); documentEvents[name] = fn; },
    removeEventListener: function (name, fn, capture) { assert.strictEqual(capture, true); assert.strictEqual(documentEvents[name], fn); delete documentEvents[name]; },
    createElementNS: function (namespace, tag) {
        assert.strictEqual(namespace, 'http://www.w3.org/2000/svg');
        svgNodesCreated++; var element = new Element(); element.tag = tag; return element;
    }};
win.DKTacticalGraphics = require('../../mod/res/gui/gameface/mods/Driftkings/TacticalMinimap/graphics.js');
data = {enabled: true, protocol: 1, generation: 3, effectiveMode: 'vanilla', available: false, acknowledged: false};
model = {DriftkingsUI: {name: 'DriftkingsTacticalMinimapProbe'}, payload: JSON.stringify(data),
    onProbeReady: function (args) { acknowledgements.push(args); },
    onSampleInput: function (args) { sampleCommands.push(args); }};
vm.runInNewContext(script, {window: win, document: graphicsDoc, engine: engine, viewEnv: viewEnv,
    console: {error: function () { errors.push(true); }}});
var report = acknowledgements[acknowledgements.length - 1];
assert.strictEqual(report.svgApi, true);
assert.strictEqual(report.glyphCount, 21);
var sampleNodeCount = svgNodesCreated;
assert(sampleNodeCount > 42); // Complete artwork includes groups, gradients and multiple shapes.
var sample = body.children[0].children.filter(function (child) { return child.className === 'dk-probe-glyphs'; })[0];
assert.strictEqual(sample.children.length, 7);
var medium = sample.children[1];
assert.strictEqual(medium.children[0].textContent, 'MT');
assert.strictEqual(medium.children[1].attributes.width, 16);
assert.strictEqual(medium.children[2].attributes.width, 24);
assert.strictEqual(medium.children[3].attributes.width, 32);
assert.strictEqual(medium.children[1].children[0].attributes.stroke, '#ffc45b');
assert.strictEqual(medium.children[1].attributes.viewBox, '0 0 64 64');
assert.strictEqual(medium.children[1].children[0].attributes['data-kind'], 'mediumTank');
data.acknowledged = true; data.graphics = {svgApi: true, glyphCount: 21}; refresh();
assert.strictEqual(svgNodesCreated, sampleNodeCount); // No graphic rebuild for a metadata change.
assert.strictEqual(body.children[0].children.filter(function (child) { return child.className === 'dk-probe-glyphs'; })[0], sample);
data.textureUri = 'img://spaces/01_karelia/mmap.dds';
['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG'].forEach(function (kind) {
    data.alliedPoint = {x: .25, y: .5, cell: 'E3', vehicleClass: kind, side: 'ally'};
    refresh();
    var image = body.children[0].children.filter(function (child) { return child.className === 'dk-probe-cartography'; })[0].children[1];
    var points = image.children[1], marker = points.children[0];
    assert(marker.className.indexOf('dk-probe-ally-icon') !== -1);
    assert.strictEqual(marker.children[0].children[0].attributes.stroke, '#67cf69');
    assert.strictEqual(marker.children[0].children[0].attributes['data-kind'], kind);
    var count = svgNodesCreated;
    data.alliedPoint.x = .75; refresh();
    assert.strictEqual(points.children[0], marker);
    assert.strictEqual(marker.style.left, '75%');
    assert.strictEqual(svgNodesCreated, count);
});
data.alliedPoint.side = 'platoon'; refresh();
var iconImage = body.children[0].children.filter(function (child) { return child.className === 'dk-probe-cartography'; })[0].children[1];
assert.strictEqual(iconImage.children[1].children[0].children[0].children[0].attributes.stroke, '#ffc45b');
data.alliedPoints = [
    {x: .25, y: .5, vehicleClass: 'mediumTank', side: 'ally'},
    {x: .75, y: .5, vehicleClass: 'heavyTank', side: 'platoon'}];
refresh();
var livePoints = iconImage.children[1];
data.cameraLine = {x: .5, y: .5, x2: 1, y2: .5}; refresh();
var cameraLayer = iconImage.children[5], cameraLine = cameraLayer.children[0].children[0];
assert.strictEqual(cameraLine.attributes.x1, 50);
assert.strictEqual(cameraLine.attributes.y1, 50);
assert.strictEqual(cameraLine.attributes.x2, 100);
assert.strictEqual(cameraLine.attributes.y2, 50);
data.cameraLine.x2 = .7; refresh();
assert.strictEqual(cameraLayer.children[0].children[0], cameraLine);
assert.strictEqual(cameraLine.attributes.x2, 70);
data.cameraLine = null; refresh();
assert.strictEqual(cameraLayer.children.length, 0);
data.yawLines = [{x: .5, y: .5, x2: .2, y2: 0}, {x: .5, y: .5, x2: .8, y2: 0}]; refresh();
var yawLayer = iconImage.children[6], leftLine = yawLayer.children[0].children[0].children[0];
assert.strictEqual(yawLayer.children.length, 2);
assert.strictEqual(leftLine.attributes.stroke, '#70dfff');
assert.strictEqual(leftLine.attributes.x2, 20);
data.yawLines[0].x2 = .3; refresh();
assert.strictEqual(yawLayer.children[0].children[0].children[0], leftLine);
assert.strictEqual(leftLine.attributes.x2, 30);
data.yawLines = []; refresh();
assert.strictEqual(yawLayer.children.length, 0);
data.strategicPoint = {x: .8, y: .3}; refresh();
var strategicLayer = iconImage.children[7], aimMarker = strategicLayer.children[0];
assert.strictEqual(aimMarker.textContent, '+');
assert.strictEqual(aimMarker.style.left, '80%');
assert.strictEqual(aimMarker.style.top, '30%');
data.strategicArea = [{x: .1, y: .1}, {x: .9, y: .1}, {x: .9, y: .9}, {x: .1, y: .9}]; refresh();
var areaLayer = iconImage.children[8], areaPolygon = areaLayer.children[0].children[0];
assert.strictEqual(areaPolygon.attributes.points, '10,10 90,10 90,90 10,90');
data.strategicArea[0].x = -.1; refresh();
assert.strictEqual(areaLayer.children[0].children[0], areaPolygon);
assert.strictEqual(areaPolygon.attributes.points, '-10,10 90,10 90,90 10,90');
data.strategicPoint.x = .7; refresh();
assert.strictEqual(strategicLayer.children[0], aimMarker);
assert.strictEqual(aimMarker.style.left, '70%');
data.strategicPoint = null; refresh();
assert.strictEqual(strategicLayer.children.length, 0);
assert.strictEqual(areaLayer.children.length, 0);
data.nativeInput = {x: .5, y: .25, button: 0, sizeIndex: 2, sequence: 1}; refresh();
var inputLayer = iconImage.children[9], inputMarker = inputLayer.children[0];
assert.strictEqual(inputMarker.className, 'dk-probe-input-point');
assert.strictEqual(inputMarker.style.left, '50%');
assert.strictEqual(inputMarker.style.top, '25%');
data.nativeInput.x = .8; data.nativeInput.sequence = 2; refresh();
assert.strictEqual(inputLayer.children[0], inputMarker);
assert.strictEqual(inputMarker.style.left, '80%');
data.nativeInput.sizeIndex = 6; refresh();
assert.strictEqual(inputLayer.children.length, 0);
data.nativeInput = null;
data.available = true; data.acknowledged = true;
data.calibration = {available: true, sizeIndex: 2}; data.sampleInputEnabled = true;
iconImage.getBoundingClientRect = function () { return {left: 100, top: 100, width: 200, height: 200}; };
refresh();
assert.strictEqual(iconImage.style.pointerEvents, 'auto');
var prevented = 0, stopped = 0;
function sampleClick(x, y, button) {
    documentEvents.mousedown({clientX: x, clientY: y, button: button, target: iconImage,
        preventDefault: function () { prevented++; }, stopPropagation: function () { stopped++; }});
}
sampleClick(200, 150, 0);
assert.strictEqual(sampleCommands.length, 1);
assert.strictEqual(JSON.stringify(sampleCommands[0]), JSON.stringify({protocol: 1, generation: 3, x: .5, y: .25, button: 0}));
assert.strictEqual(prevented, 1); assert.strictEqual(stopped, 1);
documentEvents.mousedown({clientX: 200, clientY: 150, button: 0, target: body,
    preventDefault: function () { throw new Error('Must not capture foreign elements'); },
    stopPropagation: function () { throw new Error('Must not capture foreign elements'); }});
assert.strictEqual(sampleCommands.length, 1);
sampleClick(90, 150, 0); sampleClick(NaN, 150, 0); sampleClick(200, 150, 4);
assert.strictEqual(sampleCommands.length, 1);
sampleClick(200, 150, 2);
assert.strictEqual(sampleCommands[1].button, 1); // Browser right -> native right.
sampleClick(200, 150, 1);
assert.strictEqual(sampleCommands[2].button, 2); // Browser middle -> native middle.
data.sampleInputEnabled = false; refresh();
sampleClick(200, 150, 0);
assert.strictEqual(sampleCommands.length, 3);
assert.strictEqual(iconImage.style.pointerEvents, 'none');
data.gamefaceInput = {x: .5, y: .25, button: 0, sizeIndex: 2, sequence: 1, localX: 105, localY: 52.5}; refresh();
var sampleMarker = iconImage.children[10].children[0];
assert.strictEqual(sampleMarker.className, 'dk-probe-gameface-point');
assert.strictEqual(sampleMarker.style.left, '50%');
data.gamefaceInput = null; refresh();
assert.strictEqual(iconImage.children[10].children.length, 0);
assert.strictEqual(livePoints.children.length, 2);
var firstAlly = livePoints.children[0], created = svgNodesCreated;
data.enemyPoints = [{x: .8, y: .2, vehicleClass: 'heavyTank', side: 'enemy', label: '<b>KV-2</b>'}]; refresh();
assert.strictEqual(livePoints.children.length, 3);
var enemyMarker = livePoints.children[2], enemyCount = svgNodesCreated;
var enemyLabel = enemyMarker.children[1];
assert.strictEqual(enemyLabel.textContent, '<b>KV-2</b>'); // Literal text, never HTML.
assert.ok(enemyLabel.className.indexOf('dk-probe-label-left') !== -1);
assert.strictEqual(enemyMarker.children[0].children[0].attributes.stroke, '#ee6868');
assert.strictEqual(enemyMarker.children[0].children[0].attributes['data-kind'], 'heavyTank');
data.enemyPoints[0].x = .6; refresh();
assert.strictEqual(livePoints.children[2], enemyMarker);
assert.strictEqual(enemyMarker.style.left, '60%');
assert.strictEqual(svgNodesCreated, enemyCount);
assert.strictEqual(enemyMarker.children[1], enemyLabel);
assert.strictEqual(enemyLabel.className, 'dk-probe-vehicle-label');
data.enemyPoints[0].label = 'x'.repeat(100); refresh();
assert.strictEqual(enemyLabel.textContent.length, 64);
data.enemyPoints = []; refresh();
assert.strictEqual(livePoints.children.length, 2);
data.destroyedPoints = [{x: .6, y: .2, side: 'enemy', vehicleClass: 'heavyTank', state: 'destroyed'}]; refresh();
assert.strictEqual(livePoints.children.length, 3);
var wreckMarker = livePoints.children[2];
assert.strictEqual(wreckMarker.children[0].children[0].attributes['data-kind'], 'destroyed');
assert.strictEqual(wreckMarker.children[0].children[0].attributes.stroke, '#ee6868');
assert.strictEqual(wreckMarker.style.opacity, .5);
data.destroyedPoints = []; refresh();
assert.strictEqual(livePoints.children.length, 2);
created = svgNodesCreated;
data.alliedPoints[0].x = .3; refresh();
assert.strictEqual(livePoints.children[0], firstAlly);
assert.strictEqual(firstAlly.style.left, '30%');
assert.strictEqual(svgNodesCreated, created);
data.alliedPoints.pop(); refresh();
assert.strictEqual(livePoints.children.length, 1);
data.alliedPoints.push({x: .5, y: .5, vehicleClass: 'mediumTank', side: 'enemy'}); refresh();
assert.strictEqual(livePoints.children.length, 1);
data.alliedPoints = [{x: .5, y: .75, vehicleClass: 'mediumTank', side: 'player', heading: 90}]; refresh();
var ownIcon = livePoints.children[0].children[0].children[0];
assert.strictEqual(ownIcon.attributes.stroke, '#ffffff');
assert.strictEqual(livePoints.children[0].children[0].style.transform, 'rotate(90deg)');
assert.strictEqual(ownIcon.attributes['data-kind'], 'player');
data.objectives = [{kind: 'allyBase', x: .2, y: .1, number: 2, state: 'capturing', progress: 42}, {kind: 'enemyBase', x: .8, y: .9},
    {kind: 'controlPoint', x: .5, y: .5}]; refresh();
var objectiveLayer = iconImage.children[2];
assert.strictEqual(objectiveLayer.children.length, 3);
assert.strictEqual(objectiveLayer.children[0].children[0].children[0].attributes.stroke, '#67cf69');
assert.strictEqual(objectiveLayer.children[1].children[0].children[0].attributes.stroke, '#ee6868');
assert.strictEqual(objectiveLayer.children[2].children[0].children[0].attributes.stroke, '#ffffff');
assert.strictEqual(objectiveLayer.children[0].children[1].textContent, '2');
assert.strictEqual(objectiveLayer.children[0].children[2].textContent, '42%');
assert.strictEqual(objectiveLayer.children[0].children[3].children[0].style.width, '42%');
data.objectives[0].state = 'blocked'; refresh();
assert.strictEqual(objectiveLayer.children[0].children[2].textContent, 'PAUSA');
data.objectives[0].state = 'captured'; data.objectives[0].progress = 100; refresh();
assert.strictEqual(objectiveLayer.children[0].children[2].textContent, 'OK');
data.objectives[0].state = 'idle'; data.objectives[0].progress = 0; refresh();
assert.strictEqual(objectiveLayer.children[0].children[2].textContent, '');
assert.strictEqual(objectiveLayer.children[0].children[3].style.display, 'none');
var base = objectiveLayer.children[0], objectiveCount = svgNodesCreated;
data.objectives[0].x = .3; refresh();
assert.strictEqual(objectiveLayer.children[0], base);
assert.strictEqual(base.style.left, '30%');
assert.strictEqual(svgNodesCreated, objectiveCount);
data.objectives = []; refresh();
assert.strictEqual(objectiveLayer.children.length, 0);
data.circles = [{kind: 'view', x: .5, y: .5, rx: .25, ry: .125, alpha: .5, color: '#ffffff'}]; refresh();
var ranges = iconImage.children[3], range = ranges.children[0];
assert.strictEqual(range.style.left, '25%');
assert.strictEqual(range.style.top, '37.5%');
assert.strictEqual(range.style.width, '50%');
assert.strictEqual(range.style.height, '25%');
data.circles[0].rx = .3; refresh();
assert.strictEqual(ranges.children[0], range);
assert.strictEqual(range.style.width, '60%');
data.circles = []; refresh();
assert.strictEqual(ranges.children.length, 0);
data.pings = [{kind: 'attention', state: 'attack', x: .25, y: .75},
    {kind: 'going', state: 'reply', x: .5, y: .5}]; refresh();
var pingLayer = iconImage.children[4], ping = pingLayer.children[0];
assert.strictEqual(pingLayer.children.length, 2);
assert.strictEqual(ping.textContent, '!');
assert.strictEqual(ping.style.left, '25%');
assert.strictEqual(pingLayer.children[1].textContent, '>R');
data.pings[0].state = 'idle'; refresh();
assert.strictEqual(pingLayer.children[0], ping);
assert.strictEqual(ping.style.opacity, .65);
data.pings = [{kind: 'artillery', state: 'attack', x: .4, y: .6}]; refresh();
assert.strictEqual(pingLayer.children.length, 1);
assert.strictEqual(pingLayer.children[0].textContent, '+');
assert.ok(pingLayer.children[0].className.indexOf('dk-probe-ping-artillery') >= 0);
assert.strictEqual(pingLayer.children[0].style.left, '40%');
assert.strictEqual(pingLayer.children[0].style.top, '60%');
data.pings = [{kind: 'artilleryImpact', state: 'attack', x: .7, y: .2}]; refresh();
assert.strictEqual(pingLayer.children.length, 1);
assert.strictEqual(pingLayer.children[0].textContent, '');
assert.ok(pingLayer.children[0].className.indexOf('dk-probe-ping-artilleryImpact') >= 0);
assert.strictEqual(pingLayer.children[0].style.left, '70%');
assert.strictEqual(pingLayer.children[0].style.top, '20%');
data.pings = [{kind: 'cell', state: 'attack', x: .25, y: .75}]; refresh();
assert.strictEqual(pingLayer.children.length, 1);
assert.ok(pingLayer.children[0].className.indexOf('dk-probe-ping-cell') >= 0);
assert.strictEqual(pingLayer.children[0].textContent, '');
assert.strictEqual(pingLayer.children[0].style.left, '25%');
assert.strictEqual(pingLayer.children[0].style.top, '75%');
data.pings = []; refresh();
assert.strictEqual(pingLayer.children.length, 0);
data.alliedPoints = []; refresh();
assert.strictEqual(livePoints.children.length, 0); // Empty frame overrides the legacy reference.
delete data.alliedPoints;
delete data.alliedPoint; refresh();
assert.strictEqual(iconImage.children[1].children.length, 0);
win.__dkTacticalMinimapProbe.dispose();
assert.strictEqual(body.children.length, 0);
assert.strictEqual(Object.keys(callbacks).length, 0);
assert.strictEqual(Object.keys(documentEvents).length, 0);
assert.strictEqual(Object.keys(listeners).length, 0);
console.log('PASS: shared SVG glyphs, three scales, missing-API fallback and cached graphic samples');

// A DOM method may exist but reject SVG: contain this failure inside the probe.
graphicsDoc.createElementNS = function () { throw new Error('SVG namespace unsupported'); };
data.generation = 4; data.acknowledged = false;
data.alliedPoint = {x: .25, y: .5, vehicleClass: 'mediumTank', side: 'ally'};
model.payload = JSON.stringify(data);
vm.runInNewContext(script, {window: win, document: graphicsDoc, engine: engine, viewEnv: viewEnv,
    console: {error: function () { errors.push(true); }}});
report = acknowledgements[acknowledgements.length - 1];
assert.strictEqual(report.svgApi, false);
assert.strictEqual(report.glyphCount, 0);
assert.strictEqual(body.children[0].children.filter(function (child) { return child.className === 'dk-probe-cartography'; })[0].children[1].children[1].children[0].textContent, 'A');
assert.strictEqual(body.children.length, 1);
assert.strictEqual(errors.length, 0);
win.__dkTacticalMinimapProbe.dispose();
assert.strictEqual(body.children.length, 0);
assert.strictEqual(Object.keys(callbacks).length, 0);
