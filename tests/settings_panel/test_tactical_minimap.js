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
    createElementNS: function (namespace, tag) { var node = new Element(doc); node.tag = tag; return node; }};
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
assert.strictEqual(glyph.path.attributes['data-kind'], 'mediumTank');
assert.strictEqual(glyph.path.attributes.stroke, '#ffcc00');
assert.strictEqual(glyph.node.attributes.width, 32);
assert.throws(function () { api.createGlyph(doc, 'lost', '#ffffff', 24); });
assert.throws(function () { api.createGlyph(doc, 'heavyTank', 'url(unsafe)', 24); });
assert.throws(function () { api.createGlyph(doc, 'heavyTank', '#ffffff', Infinity); });
assert.throws(function () { api.createGlyph({}, 'heavyTank', '#ffffff', 24); });

var fs = require('fs'), path = require('path'), crypto = require('crypto');
function descendants(node, tag) {
    var result = node.tag === tag ? [node] : [];
    node.children.forEach(function (child) { result = result.concat(descendants(child, tag)); });
    return result;
}
['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG', 'player', 'destroyed'].forEach(function (kind) {
    var reference = fs.readFileSync(path.join(__dirname, '../../prototypes/tactical_minimap/icons', kind + '.svg'), 'utf8');
    assert.strictEqual(api.iconSourceHashes[kind], crypto.createHash('sha256').update(reference).digest('hex'));
    var built = api.createGlyph(doc, kind, '#ffffff', 24);
    assert.strictEqual(built.node.attributes.viewBox, '0 0 64 64');
    var expected = [], match, paths = /<path d="([^"]+)"/g;
    while ((match = paths.exec(reference))) { expected.push(match[1]); }
    assert.deepStrictEqual(descendants(built.node, 'path').map(function (node) { return node.attributes.d; }), expected);
});
assert.strictEqual(descendants(glyph.node, 'rect').length, 2);
assert.strictEqual(descendants(glyph.node, 'rect')[0].attributes.x, '22');
assert.strictEqual(descendants(glyph.node, 'g')[1].attributes.transform, 'rotate(35 32 32)');
assert.strictEqual(descendants(api.createGlyph(doc, 'heavyTank', '#67cf69', 24).node, 'rect').length, 3);
var green = api.createGlyph(doc, 'lightTank', '#67cf69', 24);
assert.strictEqual(descendants(green.node, 'stop')[0].attributes['stop-color'], '#67cf69');
var gradientID = descendants(green.node, 'linearGradient')[0].attributes.id;
assert.strictEqual(descendants(green.node, 'path')[0].attributes.fill, 'url(#' + gradientID + ')');
assert.notStrictEqual(gradientID, descendants(api.createGlyph(doc, 'lightTank', '#ee6868', 24).node, 'linearGradient')[0].attributes.id);
console.log('PASS: complete SVG paths, rectangles, transforms, unique gradients and team colours');
