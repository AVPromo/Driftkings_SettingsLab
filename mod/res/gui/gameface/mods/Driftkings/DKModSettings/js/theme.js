/* Settings window theme: accent shades and the generated stylesheet. */
(function () {
    'use strict';
    var DK = window.DK = window.DK || {};
    var lastAccent = null;

    function shade(hex, amount) {
        var value = parseInt(hex.slice(1), 16), channels = [(value >> 16) & 255, (value >> 8) & 255, value & 255];
        return 'rgb(' + channels.map(function (channel) {
            return Math.round(amount >= 0 ? channel + (255 - channel) * amount : channel * (1 + amount));
        }).join(',') + ')';
    }
    function themeCss(accent) {
        var light = shade(accent, 0.25), dark = shade(accent, -0.35);
        return [
            '.dk-nav-item.is-selected{border-left-color:' + accent + '}',
            '.dk-nav-badge,.dk-nav-dot,.dk-row.is-changed:before,.dk-slider-fill{background:' + accent + '}',
            '.dk-unsaved,.dk-section,.dk-option.is-selected{color:' + accent + '}',
            '.dk-btn.is-primary{background:' + accent + ';border-color:' + light + '}',
            '.dk-btn.is-primary:hover{background:' + light + ';color:#000}',
            '.dk-switch.is-on .dk-switch-track{background:' + dark + ';border-color:' + accent + '}',
            '.dk-switch.is-on .dk-switch-text{color:' + accent + '}',
            '.dk-checkbox.is-on{background:' + accent + ';border-color:' + light + '}',
            '.dk-text:focus,.dk-dropdown:focus{border-color:' + accent + '}',
            '.dk-btn:focus,.dk-switch:focus,.dk-checkbox:focus,.dk-nav-item:focus,.dk-dropdown:focus,.dk-text:focus,.dk-slider-track:focus,.dk-toast:focus{outline:2px solid ' + accent + ';outline-offset:2px;box-shadow:none}',
            '.dk-slider-thumb{border-color:' + dark + '}',
            '.dk-window{border-color:' + shade(accent, -0.6) + '}'
        ].join('\n');
    }
    function apply(values) {
        var signature = JSON.stringify(values);
        if (signature === lastAccent) { return; }
        lastAccent = signature;
        var accent = DK.controls.normalizeHex(values.accent) || '#D98219';
        var bg = DK.controls.normalizeHex(values.background) || '#101113';
        var n = parseInt(bg.slice(1), 16);
        var rgba = 'rgba(' + [(n >> 16) & 255, (n >> 8) & 255, n & 255, (values.opacity || 96) / 100].join(',') + ')';
        var css = '.dk-label,.dk-text,.dk-dropdown{font-size:' + (values.fontSize || 15) + 'rem}' + themeCss(accent) + '.dk-window{background:' + rgba + ';color:' + (values.textColor || '#E8E4DA') + ';font-size:' + (values.fontSize || 15) + 'rem}';
        css += '.dk-section{font-size:' + (values.sectionFontSize || 18) + 'rem}.dk-sidebar{background:rgba(0,0,0,' + (Number(values.sidebarOpacity === undefined ? 35 : values.sidebarOpacity) / 100) + ')}';
        css += '.dk-label,.dk-text{color:' + (values.textColor || '#E8E4DA') + '}.dk-window{border-color:' + (values.border || '#4A463E') + '}.dk-nav-item:hover{background:' + (values.hover || '#39352B') + '}';
        if (values.secondary) {
            css += '.dk-mod-description,.dk-mod-meta,.dk-nav-status,.dk-apply-timing{color:' + values.secondary + '}';
        }
        document.getElementById('dk-theme').textContent = css;
    }

    DK.theme = {apply: apply, css: themeCss};
}());
