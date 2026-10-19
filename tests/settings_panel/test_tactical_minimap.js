/* Fake DOM verifies preview contracts; it is not a Gameface runtime test. */
'use strict';
var assert = require('assert');
var api = require('../../mod/res/gui/gameface/mods/Driftkings/TacticalMinimap/graphics.js');
function Element(doc) {
    this.ownerDocument = doc; this.children = []; this.style = {}; this.attributes = {};
}
Element.prototype.appendChild = function (node) { this.children.push(node); node.parentNode = this; };
Element.prototype.removeChild = function (node) {
    var index = this.children.indexOf(node); assert(index >= 0);
    this.children.splice(index, 1); node.parentNode = null;
};
Element.prototype.setAttribute = function (key, value) { this.attributes[key] = value; };
var doc = {createElement: function () { return new Element(doc); },
    createElementNS: function () { return new Element(doc); }};
var host = new Element(doc), renderer = new api.Renderer(host);
var marker = {id: 1, visible: true, state: 'visible', side: 'player', vehicleClass: 'mediumTank',
    x: 0.5, y: 0.25, heading: 90, name: '<script>not html</script>'};
var frame = {source: 'synthetic-preview', markers: [marker]};
renderer.render(frame, {});
assert.strictEqual(host.children.length, 2);
assert.strictEqual(renderer.nodes['1'].node.style.left, '50%');
assert.strictEqual(renderer.nodes['1'].node.style.top, '25%');
assert.strictEqual(renderer.nodes['1'].label.textContent, marker.name);
assert.strictEqual(renderer.nodes['1'].icon.style.transform, 'rotate(90deg)');
var first = renderer.nodes['1'];
renderer.render(frame, {});
assert.strictEqual(renderer.nodes['1'], first);
marker.x = 0.75;
renderer.render(frame, {theme: 'military', enemy: 'url(unsafe)'});
assert.strictEqual(renderer.nodes['1'], first);
assert.strictEqual(first.node.style.left, '75%');
assert.strictEqual(api.options({enemy: 'url(unsafe)'}).enemy, '#ee6868');
assert.strictEqual(api.options({size: Infinity, theme: 'invalid'}).size, 320);
assert.strictEqual(api.options({iconScale: 99}).iconScale, 3);
['lost', 'invisible'].forEach(function (state) {
    marker.state = state;
    renderer.render(frame, {});
    assert.strictEqual(Object.keys(renderer.nodes).length, 0);
});
marker.state = 'visible'; marker.visible = false;
assert.strictEqual(api.valid(marker), false);
marker.visible = true; marker.x = NaN;
assert.strictEqual(api.valid(marker), false);
marker.x = 0.5; marker.vehicleClass = 'player';
assert.strictEqual(api.valid(marker), false);
marker.vehicleClass = 'mediumTank';
renderer.render(frame, {});
assert.strictEqual(Object.keys(renderer.nodes).length, 1);
renderer.render({source: 'native-minimap-audit', markers: [marker]}, {});
assert.strictEqual(Object.keys(renderer.nodes).length, 0);
renderer.render({source: 'battle', markers: [marker]}, {});
assert.strictEqual(Object.keys(renderer.nodes).length, 0);
renderer.render({source: 'synthetic-preview', markers: {}}, {});
assert.strictEqual(Object.keys(renderer.nodes).length, 0);
renderer.render({source: 'synthetic-preview', markers: {}}, {});
assert.strictEqual(Object.keys(renderer.nodes).length, 0);
renderer.render(frame, {});
renderer.dispose(); renderer.dispose(); renderer.render(frame, {});
assert.strictEqual(host.children.length, 0);
console.log('PASS: Tactical Minimap isolated preview, incremental DOM, safe filtering and disposal');

var glyph = api.createGlyph(doc, 'mediumTank', '#ffcc00', 32);
assert(glyph.path.attributes.d.indexOf('M10 21 L22 10') !== -1);
assert.strictEqual(glyph.path.attributes.stroke, '#ffcc00');
assert.strictEqual(glyph.node.attributes.width, 32);
assert.throws(function () { api.createGlyph(doc, 'lost', '#ffffff', 24); });
assert.throws(function () { api.createGlyph(doc, 'heavyTank', 'url(unsafe)', 24); });
assert.throws(function () { api.createGlyph(doc, 'heavyTank', '#ffffff', Infinity); });
assert.throws(function () { api.createGlyph({}, 'heavyTank', '#ffffff', 24); });

var fs = require('fs'), path = require('path');
['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG', 'player', 'destroyed'].forEach(function (kind) {
    var reference = fs.readFileSync(path.join(__dirname, '../../prototypes/tactical_minimap/icons', kind + '.svg'), 'utf8');
    var expectedPath = /<path d="([^"]+)"/.exec(reference)[1];
    assert.strictEqual(api.createGlyph(doc, kind, '#ffffff', 24).path.attributes.d, expectedPath);
});
