/* Runtime-independent probe handshake/lifecycle tests, not an in-game test. */
'use strict';
var assert = require('assert'), fs = require('fs'), vm = require('vm'), path = require('path');
var listeners = {}, callbacks = {}, acknowledgements = [], removed = [], errors = [];
var serial = 0, model = null, callbackAdds = 0;
function Element() { this.children = []; this.parentNode = null; }
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
