'use strict';
var assert = require('assert');
var layout = require('../../mod/res/gui/gameface/mods/driftkings/vehicle_carousel/carousel_layout.js');
var selectors = [], nodes = [];
global.getComputedStyle = function () { return {position:'relative', transform:'none'}; };
var card = {clientWidth:200, clientHeight:100,
    querySelectorAll:function (selector) {
        selectors.push(selector);
        var node = {style:{visibility:'visible', opacity:'1'}};
        nodes.push(node); return [node];
    },
    appendChild:function (node) { node.parentNode=this; },
    insertBefore:function (node) { node.parentNode=this; },
    removeChild:function (node) { node.parentNode=null; }};
var document = {createElement:function () { return {style:{}, appendChild:function () {}}; }};
var fields = {};
['flag','tankIcon','tankName','info','infoImg','rentInfo','crystalsIcon','coreBorder','xp'].forEach(function (key) {
    fields[key]={enabled:false,alpha:100,dx:0,dy:0,scale:1};
});
var cleanup = layout.mount(card,{width:200,height:100,fields:fields,extraFields:[]},document,{});
nodes.forEach(function (node) {
    assert.strictEqual(node.style.visibility,'hidden');
    assert.strictEqual(node.style.opacity,'0','Hidden native parents must also suppress visible descendants');
});
assert(selectors.some(function (s) { return s.indexOf('Overlay_alertText_')!==-1; }));
assert(selectors.some(function (s) { return s.indexOf('Bonuses_rent_')!==-1; }));
assert(selectors.some(function (s) { return s.indexOf('Bonuses_bonus_')!==-1; }));
cleanup();
nodes.forEach(function (node) { assert.strictEqual(node.style.opacity,'1'); assert.strictEqual(node.style.visibility,'visible'); });
delete global.getComputedStyle;
console.log('Native carousel field visibility and restoration: passed');
