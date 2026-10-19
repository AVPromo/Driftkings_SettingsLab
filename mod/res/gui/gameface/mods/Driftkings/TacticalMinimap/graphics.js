/* Shared synthetic renderer and SVG capability probe; never controls native minimap UI. */
(function (root) {
    'use strict';
    // BEGIN GENERATED TACTICAL ICONS
    var icons = {"AT-SPG": {"nodes": [["defs", {}, [["linearGradient", {"id": "steel", "x1": "0", "x2": ".8", "y1": "0", "y2": "1"}, [["stop", {"offset": "0", "stop-color": "#fff"}, []], ["stop", {"offset": ".53", "stop-color": "#ecf1f5"}, []], ["stop", {"offset": "1", "stop-color": "#b6c1cc"}, []]]]]], ["path", {"d": "M11 15H53L32 52Z", "fill": "url(#steel)", "stroke": "#fff", "stroke-linejoin": "round", "stroke-width": "1.7"}, []], ["path", {"d": "M17 18H47L32 45Z", "fill": "none", "opacity": ".3", "stroke": "#fff", "stroke-width": "1"}, []]], "sha256": "01a4530743e83c8fd4f2073302977c2191d26c96db84aab0c24fc8090ad63fdd", "viewBox": "0 0 64 64"}, "SPG": {"nodes": [["defs", {}, [["linearGradient", {"id": "steel", "x1": "0", "x2": ".8", "y1": "0", "y2": "1"}, [["stop", {"offset": "0", "stop-color": "#fff"}, []], ["stop", {"offset": ".53", "stop-color": "#ecf1f5"}, []], ["stop", {"offset": "1", "stop-color": "#b6c1cc"}, []]]]]], ["rect", {"fill": "url(#steel)", "height": "22", "rx": "2", "stroke": "#fff", "stroke-width": "1.6", "width": "36", "x": "14", "y": "21"}, []], ["path", {"d": "M32 22V42", "stroke": "#343c48", "stroke-width": "3"}, []], ["path", {"d": "M17 24H29M35 24H47", "opacity": ".4", "stroke": "white", "stroke-width": "1.4"}, []]], "sha256": "99468fc42e31b59a0af247c5946d3b4e3d5bf0017661698ce1f567792a97fc61", "viewBox": "0 0 64 64"}, "destroyed": {"nodes": [["defs", {}, [["linearGradient", {"id": "steel", "x1": "0", "x2": ".8", "y1": "0", "y2": "1"}, [["stop", {"offset": "0", "stop-color": "#fff"}, []], ["stop", {"offset": ".53", "stop-color": "#ecf1f5"}, []], ["stop", {"offset": "1", "stop-color": "#b6c1cc"}, []]]]]], ["path", {"d": "M32 10 46 30 32 49 18 30Z", "fill": "#818a93", "opacity": ".6", "stroke": "#f5f7fa", "stroke-width": "2"}, []], ["circle", {"cx": "44", "cy": "44", "fill": "#2a2022", "r": "12.5", "stroke": "#ff6b6b", "stroke-width": "2"}, []], ["path", {"d": "m39 39 10 10m0-10L39 49", "stroke": "#ff7777", "stroke-linecap": "round", "stroke-width": "3.6"}, []]], "sha256": "12be0a91c0fd99ea0f6d0d0d858327cc3cf205fb31f7c86e1772b67fa1087d62", "viewBox": "0 0 64 64"}, "heavyTank": {"nodes": [["defs", {}, [["linearGradient", {"id": "steel", "x1": "0", "x2": ".8", "y1": "0", "y2": "1"}, [["stop", {"offset": "0", "stop-color": "#fff"}, []], ["stop", {"offset": ".53", "stop-color": "#ecf1f5"}, []], ["stop", {"offset": "1", "stop-color": "#b6c1cc"}, []]]]]], ["g", {"transform": "rotate(35 32 32)"}, [["rect", {"fill": "url(#steel)", "height": "42", "rx": "1.2", "stroke": "#fff", "stroke-width": ".8", "width": "7", "x": "16", "y": "11"}, []], ["rect", {"fill": "url(#steel)", "height": "42", "rx": "1.2", "stroke": "#fff", "stroke-width": ".8", "width": "7", "x": "28.5", "y": "11"}, []], ["rect", {"fill": "url(#steel)", "height": "42", "rx": "1.2", "stroke": "#fff", "stroke-width": ".8", "width": "7", "x": "41", "y": "11"}, []]]]], "sha256": "6ffe972b696beb86e16d38fa73b77ce24b05fc85a85d15a6a02d76c86ee6cc3b", "viewBox": "0 0 64 64"}, "lightTank": {"nodes": [["defs", {}, [["linearGradient", {"id": "steel", "x1": "0", "x2": ".8", "y1": "0", "y2": "1"}, [["stop", {"offset": "0", "stop-color": "#fff"}, []], ["stop", {"offset": ".53", "stop-color": "#ecf1f5"}, []], ["stop", {"offset": "1", "stop-color": "#b6c1cc"}, []]]]]], ["path", {"d": "M32 11 47 32 32 53 17 32Z", "fill": "url(#steel)", "stroke": "#fff", "stroke-linejoin": "round", "stroke-width": "1.6"}, []], ["path", {"d": "M32 15 43 32 32 49 21 32Z", "fill": "none", "opacity": ".25", "stroke": "#fff", "stroke-width": "1"}, []]], "sha256": "6566df8f6e34cb21155bd44dc132511402ab0af926895ed6e7126e3459c6a82c", "viewBox": "0 0 64 64"}, "mediumTank": {"nodes": [["defs", {}, [["linearGradient", {"id": "steel", "x1": "0", "x2": ".8", "y1": "0", "y2": "1"}, [["stop", {"offset": "0", "stop-color": "#fff"}, []], ["stop", {"offset": ".53", "stop-color": "#ecf1f5"}, []], ["stop", {"offset": "1", "stop-color": "#b6c1cc"}, []]]]]], ["g", {"transform": "rotate(35 32 32)"}, [["rect", {"fill": "url(#steel)", "height": "42", "rx": "1.5", "stroke": "#fff", "stroke-width": "1", "width": "8", "x": "22", "y": "11"}, []], ["rect", {"fill": "url(#steel)", "height": "42", "rx": "1.5", "stroke": "#fff", "stroke-width": "1", "width": "8", "x": "34", "y": "11"}, []]]]], "sha256": "98ee4edfb4495e39e0ee6b003a11b4eddf594db29d7a493fac1c3f5c4edb686d", "viewBox": "0 0 64 64"}, "player": {"nodes": [["defs", {}, [["linearGradient", {"id": "steel", "x1": "0", "x2": ".8", "y1": "0", "y2": "1"}, [["stop", {"offset": "0", "stop-color": "#fff"}, []], ["stop", {"offset": ".53", "stop-color": "#ecf1f5"}, []], ["stop", {"offset": "1", "stop-color": "#b6c1cc"}, []]]]]], ["path", {"d": "M32 7 52 53 32 43 12 53Z", "fill": "#fff", "stroke": "#d9e9f5", "stroke-linejoin": "round", "stroke-width": "1.7"}, []], ["path", {"d": "M32 12V41", "opacity": ".65", "stroke": "#9daebe", "stroke-width": "1.6"}, []], ["path", {"d": "M32 43 12 53 32 34Z", "fill": "#cbd5df", "opacity": ".3"}, []]], "sha256": "8ede9d301618a4655c08874f7c01bb9ecffed497f8914be2b56169f63d5d6fb0", "viewBox": "0 0 64 64"}};
    // END GENERATED TACTICAL ICONS
    var shapes = {base: 'M7 29 L7 4 L26 4 L21 11 L26 18 L7 18',
        controlPoint: 'M16 3 L29 16 L16 29 L3 16 Z M16 10 L16 22 M10 16 L22 16'};
    var glyphSerial = 0;
    var sides = ['player', 'ally', 'enemy', 'platoon'];
    var classes = ['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG'];
    var defaults = {size: 320, theme: 'dark', opacity: 0.85, iconScale: 1,
        fontSize: 12, showVehicleNames: true, showGrid: true,
        player: '#ffffff', ally: '#67cf69', enemy: '#ee6868', platoon: '#ffc45b'};
    function number(value, fallback, low, high) {
        return typeof value === 'number' && isFinite(value) ? Math.max(low, Math.min(high, value)) : fallback;
    }
    function colour(value, fallback) { return /^#[0-9a-f]{6}$/i.test(value || '') ? value : fallback; }
    function options(value) {
        value = value || {};
        var out = {size: number(value.size, defaults.size, 160, 640),
            opacity: number(value.opacity, defaults.opacity, 0, 1),
            iconScale: number(value.iconScale, 1, 0.5, 3), fontSize: number(value.fontSize, 12, 8, 24),
            theme: /^(dark|military|minimal)$/.test(value.theme || '') ? value.theme : 'dark',
            showVehicleNames: value.showVehicleNames !== false, showGrid: value.showGrid !== false};
        sides.forEach(function (side) { out[side] = colour(value[side], defaults[side]); });
        return out;
    }
    function valid(marker) {
        return marker && typeof marker.id === 'number' && marker.id >= 0 && marker.id % 1 === 0 &&
            marker.visible === true && sides.indexOf(marker.side) !== -1 &&
            classes.indexOf(marker.vehicleClass) !== -1 &&
            (marker.state === 'visible' || marker.state === 'destroyed') &&
            typeof marker.x === 'number' && isFinite(marker.x) && marker.x >= 0 && marker.x <= 1 &&
            typeof marker.y === 'number' && isFinite(marker.y) && marker.y >= 0 && marker.y <= 1;
    }
    function tint(value, color) {
        if (value === 'white') { return color; }
        var match = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(value);
        if (!match) { return value; }
        var hex = match[1];
        if (hex.length === 3) { hex = hex.replace(/./g, function (digit) { return digit + digit; }); }
        var channels = [0, 2, 4].map(function (offset) { return parseInt(hex.substr(offset, 2), 16); });
        if (Math.min.apply(Math, channels) < 145) { return value; }
        return '#' + channels.map(function (channel, index) {
            var result = Math.round(channel * parseInt(color.substr(1 + index * 2, 2), 16) / 255).toString(16);
            return result.length < 2 ? '0' + result : result;
        }).join('');
    }
    function svgElement(doc, definition, color, prefix) {
        var element = doc.createElementNS('http://www.w3.org/2000/svg', definition[0]);
        Object.keys(definition[1]).forEach(function (key) {
            var value = definition[1][key];
            if (key === 'id') { value = prefix + value; }
            else if (value === 'url(#steel)') { value = 'url(#' + prefix + 'steel)'; }
            else if (key === 'fill' || key === 'stroke' || key === 'stop-color') { value = tint(value, color); }
            element.setAttribute(key, value);
        });
        definition[2].forEach(function (child) { element.appendChild(svgElement(doc, child, color, prefix)); });
        return element;
    }
    function updateGlyph(glyph, kind, color) {
        if (glyph.kind === kind && glyph.color === color) { return; }
        glyph.children.forEach(function (child) { glyph.path.removeChild(child); });
        glyph.children = [];
        var definition = icons[kind], doc = glyph.doc;
        glyph.node.setAttribute('viewBox', definition ? definition.viewBox : '0 0 32 32');
        glyph.path.setAttribute('stroke', color);
        glyph.path.setAttribute('data-kind', kind);
        var nodes = definition ? definition.nodes : [['path', {d: shapes[kind], fill: 'none',
            stroke: color, 'stroke-width': '2', 'stroke-linejoin': 'round'}, []]];
        nodes.forEach(function (node) {
            var child = svgElement(doc, node, color, glyph.prefix);
            glyph.path.appendChild(child); glyph.children.push(child);
        });
        glyph.kind = kind; glyph.color = color;
    }
    function createGlyph(doc, kind, color, size) {
        if ((!Object.prototype.hasOwnProperty.call(icons, kind) && !Object.prototype.hasOwnProperty.call(shapes, kind)) ||
                !/^#[0-9a-f]{6}$/i.test(color || '') || typeof size !== 'number' ||
                !isFinite(size) || size < 8 || size > 128) {
            throw new Error('Invalid tactical glyph');
        }
        if (typeof doc.createElementNS !== 'function') { throw new Error('SVG DOM unavailable'); }
        var svg = doc.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', size); svg.setAttribute('height', size);
        var group = doc.createElementNS('http://www.w3.org/2000/svg', 'g'); svg.appendChild(group);
        var glyph = {node: svg, path: group, doc: doc, children: [], prefix: 'dk-glyph-' + (++glyphSerial) + '-'};
        updateGlyph(glyph, kind, color);
        return glyph;
    }
    function Renderer(host) {
        this.host = host;
        this.nodes = {};
        this.config = null;
        this.disposed = false;
        this.grid = host.ownerDocument.createElement('div');
        this.grid.className = 'tm-grid';
        this.grid.textContent = 'A B C D E F G H J K';
        host.appendChild(this.grid);
    }
    Renderer.prototype.render = function (snapshot, config) {
        if (this.disposed) { return; }
        if (!snapshot || snapshot.source !== 'synthetic-preview' || !Array.isArray(snapshot.markers)) {
            this.clear(); return;
        }
        var opts = options(config), doc = this.host.ownerDocument, self = this, seen = {};
        var configKey = JSON.stringify(opts);
        if (this.config !== configKey) {
            this.host.className = 'tm-map tm-' + opts.theme;
            this.host.style.width = opts.size + 'px';
            this.host.style.height = opts.size + 'px';
            this.host.style.backgroundColor = 'rgba(10,22,22,' + opts.opacity + ')';
            this.grid.style.display = opts.showGrid ? '' : 'none';
            this.config = configKey;
        }
        (snapshot.markers || []).forEach(function (marker) {
            if (!valid(marker) || seen[marker.id]) { return; }
            seen[marker.id] = true;
            var key = String(marker.id), record = self.nodes[key];
            var signature = JSON.stringify(marker) + configKey;
            if (record && record.signature === signature) { return; }
            if (!record) {
                var node = doc.createElement('div');
                var glyph = createGlyph(doc, marker.vehicleClass, opts[marker.side], 24);
                var icon = glyph.node, path = glyph.path;
                var label = doc.createElement('span');
                node.className = 'tm-marker';
                node.appendChild(icon); node.appendChild(label); self.host.appendChild(node);
                record = self.nodes[key] = {node: node, icon: icon, path: path, label: label, glyph: glyph};
            }
            record.signature = signature;
            record.node.style.left = (marker.x * 100) + '%';
            record.node.style.top = (marker.y * 100) + '%';
            record.node.style.color = opts[marker.side];
            record.node.style.opacity = marker.state === 'destroyed' ? '0.5' : '1';
            updateGlyph(record.glyph, marker.state === 'destroyed' ? 'destroyed' :
                marker.side === 'player' ? 'player' : marker.vehicleClass, opts[marker.side]);
            record.icon.style.width = (24 * opts.iconScale) + 'px';
            record.icon.style.height = (24 * opts.iconScale) + 'px';
            // Only the player's directional glyph rotates. Class silhouettes stay recognizable.
            var angle = marker.side === 'player' && marker.state !== 'destroyed' ? number(marker.heading, 0, 0, 360) : 0;
            record.icon.style.transform = 'rotate(' + angle + 'deg)';
            record.label.textContent = opts.showVehicleNames && typeof marker.name === 'string' ? marker.name.slice(0, 64) : '';
            record.label.style.fontSize = opts.fontSize + 'px';
        });
        Object.keys(this.nodes).forEach(function (key) {
            if (!seen[key]) { self.host.removeChild(self.nodes[key].node); delete self.nodes[key]; }
        });
    };
    Renderer.prototype.clear = function () {
        var self = this;
        Object.keys(this.nodes).forEach(function (key) { self.host.removeChild(self.nodes[key].node); });
        this.nodes = {};
    };
    Renderer.prototype.dispose = function () {
        if (this.disposed) { return; }
        this.clear(); this.host.removeChild(this.grid); this.disposed = true;
    };
    var iconSourceHashes = {};
    Object.keys(icons).forEach(function (kind) { iconSourceHashes[kind] = icons[kind].sha256; });
    var api = {iconSourceHashes: iconSourceHashes, Renderer: Renderer, options: options, valid: valid, createGlyph: createGlyph};
    if (typeof module !== 'undefined' && module.exports) { module.exports = api; }
    else { root.DKTacticalGraphics = api; }
}(typeof window !== 'undefined' ? window : this));
