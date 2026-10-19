/* Shared synthetic renderer and SVG capability probe; never controls native minimap UI. */
(function (root) {
    'use strict';
    var shapes = {"lightTank": "M16 3 L27 16 L16 29 L5 16 Z", "mediumTank": "M16 3 L27 16 L16 29 L5 16 Z M10 21 L22 10", "heavyTank": "M16 3 L27 16 L16 29 L5 16 Z M8 18 L19 7 M13 25 L25 13", "AT-SPG": "M16 3 L29 28 L3 28 Z", "SPG": "M16 3 A13 13 0 1 0 16 29 A13 13 0 1 0 16 3 M9 16 L23 16 M16 9 L16 23", "player": "M16 2 L28 28 L16 22 L4 28 Z", "base": "M7 29 L7 4 L26 4 L21 11 L26 18 L7 18", "controlPoint": "M16 3 L29 16 L16 29 L3 16 Z M16 10 L16 22 M10 16 L22 16", "destroyed": "M7 7 L25 25 M25 7 L7 25"};
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
    function createGlyph(doc, kind, color, size) {
        if (!Object.prototype.hasOwnProperty.call(shapes, kind) ||
                !/^#[0-9a-f]{6}$/i.test(color || '') || typeof size !== 'number' ||
                !isFinite(size) || size < 8 || size > 128) {
            throw new Error('Invalid tactical glyph');
        }
        if (typeof doc.createElementNS !== 'function') { throw new Error('SVG DOM unavailable'); }
        var svg = doc.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', '0 0 32 32');
        svg.setAttribute('width', size); svg.setAttribute('height', size);
        var path = doc.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', shapes[kind]);
        path.setAttribute('fill', 'none'); path.setAttribute('stroke', color);
        path.setAttribute('stroke-width', '2'); path.setAttribute('stroke-linejoin', 'round');
        svg.appendChild(path);
        return {node: svg, path: path};
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
                record = self.nodes[key] = {node: node, icon: icon, path: path, label: label};
            }
            record.signature = signature;
            record.node.style.left = (marker.x * 100) + '%';
            record.node.style.top = (marker.y * 100) + '%';
            record.node.style.color = opts[marker.side];
            record.path.setAttribute('stroke', opts[marker.side]);
            record.node.style.opacity = marker.state === 'destroyed' ? '0.5' : '1';
            record.path.setAttribute('d', shapes[marker.state === 'destroyed' ? 'destroyed' :
                marker.side === 'player' ? 'player' : marker.vehicleClass]);
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
    var api = {Renderer: Renderer, options: options, valid: valid, createGlyph: createGlyph};
    if (typeof module !== 'undefined' && module.exports) { module.exports = api; }
    else { root.DKTacticalGraphics = api; }
}(typeof window !== 'undefined' ? window : this));
