(function() {
    'use strict';
    if (window.__dkHangarClock) window.__dkHangarClock.dispose();
    var disposed = false,
        cfg = {},
        timer = null,
        callbackId = null,
        resourceId = null,
        model = null,
        lastPayload = null;

    function pad(n) {
        return n < 10 ? '0' + n : String(n);
    }

    function bounded(v, fallback, min, max) {
        v = Number(v);
        return isFinite(v) ? Math.max(min, Math.min(max, v)) : fallback;
    }
    var custom = null,
        customFields = [],
        policy = null;

    function dateFormat(pattern, now) {
        var names = cfg.calendar || {},
            weekday = (now.getDay() + 6) % 7,
            month = now.getMonth();
        var days = names.days || ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        var shortDays = names.shortDays || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        var months = names.months || ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        var shortMonths = names.shortMonths || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        var h = now.getHours(),
            values = {
                H: pad(h),
                I: pad(h % 12 || 12),
                M: pad(now.getMinutes()),
                S: pad(now.getSeconds()),
                d: pad(now.getDate()),
                m: pad(now.getMonth() + 1),
                Y: String(now.getFullYear()),
                y: pad(now.getFullYear() % 100),
                A: days[weekday],
                a: shortDays[weekday],
                B: months[month],
                b: shortMonths[month],
                p: h < 12 ? 'AM' : 'PM'
            };
        return String(pattern).replace(/%([aAbB][ul]|[HIMSdmYyaAbBp%])/g, function(all, key) {
            if (key === '%') return '%';
            var value = values[key.charAt(0)];
            return key.length === 1 ? value : key.charAt(1) === 'u' ? value.toUpperCase() : value.toLowerCase();
        });
    }

    function formatText(value, now) {
        var macro = /\{\{py:xvm\.formatDate\((['"])(.*?)\1\)\}\}/g;
        // No Python evaluation: only the documented date macro is recognized.
        if (macro.test(value)) {
            macro.lastIndex = 0;
            return value.replace(macro, function(all, q, fmt) {
                return dateFormat(fmt, now);
            });
        }
        return dateFormat(value, now);
    }

    function clockColor(value, fallback) {
        value = String(value || '').replace(/^0x/i, '#');
        return /^#[0-9a-f]{6}$/i.test(value) ? value : fallback;
    }

    function clockImage(src) {
        if (src === 'xvm://res/icons/clock/clockBg.png') return 'coui://gui/maps/driftkings/clock/clockBg.png';
        return /^(?:coui:\/\/)?gui\/[a-zA-Z0-9_./-]+\.(png|dds|webp)$/i.test(src) && src.indexOf('..') < 0 ? src.replace(/^(?!coui:\/\/)/, 'coui://') : '';
    }

    function richClock(parent, html) {
        var stack = [parent],
            current = parent;
        html.split(/(<[^>]*>)/g).forEach(function(part) {
            if (!part) return;
            if (/^<\/(font|textformat|b|i)>$/i.test(part)) {
                if (stack.length > 1) stack.pop();
                current = stack[stack.length - 1];
                return;
            }
            if (/^<br\s*\/?>$/i.test(part)) {
                current.appendChild(document.createElement('br'));
                return;
            }
            if (/^<tab\s*\/?>$/i.test(part)) {
                var tab = document.createElement('span');
                tab.textContent = '\u00a0\u00a0\u00a0\u00a0';
                current.appendChild(tab);
                return;
            }
            var tag = /^<(font|textformat|b|i|img)(\s[^>]*)?>$/i.exec(part);
            if (tag) {
                var attrs = {},
                    match, re = /([a-z]+)\s*=\s*(['"])(.*?)\2/gi;
                while ((match = re.exec(tag[2] || ''))) attrs[match[1].toLowerCase()] = match[3];
                var type = tag[1].toLowerCase(),
                    child = document.createElement(type === 'img' ? 'img' : 'span');
                if (type === 'img') {
                    var src = clockImage(attrs.src || '');
                    if (!src) return;
                    child.src = src;
                    child.alt = '';
                }
                if (attrs.color) child.style.color = clockColor(attrs.color, '#959688');
                if (attrs.size) child.style.fontSize = bounded(attrs.size, 15, 6, 120) + 'px';
                if (attrs.face) child.style.fontFamily = attrs.face === '$FieldFont' ? 'Arial, sans-serif' : attrs.face.replace(/[^a-zA-Z0-9 ,_-]/g, '');
                if (type === 'b') child.style.fontWeight = 'bold';
                if (type === 'i') child.style.fontStyle = 'italic';
                if (type === 'textformat') {
                    child.style.display = 'block';
                    child.style.marginRight = bounded(attrs.rightmargin, 0, -1000, 1000) + 'px';
                    // Flash negative leading cannot be applied as a collapsing CSS margin.
                    child.style.marginBottom = bounded(attrs.leading, 0, 0, 120) + 'px';
                }
                ['width', 'height'].forEach(function(k) {
                    if (attrs[k]) child.style[k] = bounded(attrs[k], 0, 0, 4096) + 'px';
                });
                current.appendChild(child);
                if (type !== 'img') {
                    stack.push(child);
                    current = child;
                }
                return;
            }
            if (part.charAt(0) !== '<') {
                var textNode = document.createElement('span');
                textNode.textContent = part;
                current.appendChild(textNode);
            }
        });
    }

    function shadowStyle(shadow, color) {
        var n = parseInt(color.slice(1), 16);
        var angle = bounded(shadow.angle, 0, 0, 360) * Math.PI / 180;
        var distance = bounded(shadow.distance, 0, 0, 255);
        var rgba = [
            (n >> 16) & 255,
            (n >> 8) & 255,
            n & 255,
            bounded(shadow.alpha, 100, 0, 100) / 100
        ];
        var effect = (distance * Math.cos(angle)) + 'px ' +
            (distance * Math.sin(angle)) + 'px ' +
            bounded(shadow.blur, 4, 0, 255) + 'px rgba(' + rgba.join(',') + ')';
        var copies = [];
        var count = Math.max(1, Math.min(8, Math.round(bounded(shadow.strength, 1, 0, 255))));
        for (var i = 0; i < count; i++) {
            copies.push(effect);
        }
        return copies.join(',');
    }

    function configureCustom() {
        if (custom && custom.parentNode) custom.parentNode.removeChild(custom);
        custom = null;
        customFields = [];
        if (!policy) {
            policy = document.createElement('style');
            document.body.appendChild(policy);
        }
        policy.textContent = cfg.hidePrestige ? '[class*="Information_prestige_"] { display:none; }' : '';
        var source = String(cfg.customClockText || ''),
            formats;
        try {
            var clean = source.replace(/("(?:\\.|[^"\\])*")|\/\/[^\r\n]*|\/\*[\s\S]*?\*\//g, function(all, quoted) {
                return quoted || '';
            });
            var parsed = JSON.parse(clean);
            formats = Array.isArray(parsed) ? parsed : parsed.formats;
            if (!Array.isArray(formats) || formats.length > 32) throw new Error('Invalid clock formats');
        } catch (e) {
            if (/^\s*[\[{]/.test(source)) return;
            formats = [{
                x: cfg.clockX,
                y: cfg.clockY,
                screenHAlign: 'right',
                width: 240,
                height: 100,
                textFormat: {
                    align: 'right'
                },
                format: source
            }];
        }
        custom = document.createElement('div');
        custom.className = 'dk-clock-custom';
        document.body.appendChild(custom);
        formats.forEach(function(def) {
            if (!def || typeof def.format !== 'string') return;
            var field = document.createElement('div');
            field.className = 'dk-clock-custom__field';
            var tf = def.textFormat || {},
                shadow = def.shadow || {},
                color = clockColor(shadow.color, '#000000');
            field.style.color = clockColor(tf.color, '#959688');
            field.style.textAlign = ['left', 'center', 'right'].indexOf(tf.align) >= 0 ? tf.align : 'left';
            field.style.display = 'flex';
            field.style.flexDirection = 'column';
            field.style.justifyContent = tf.valign === 'bottom' ? 'flex-end' : tf.valign === 'center' ? 'center' : 'flex-start';
            if (shadow.enabled) {
                field.style.textShadow = shadowStyle(shadow, color);
            }
            var content = document.createElement('div');
            content.className = 'dk-clock-custom__content';
            content.style.alignSelf = tf.align === 'right' ? 'flex-end' : tf.align === 'center' ? 'center' : 'flex-start';
            if (cfg.clockBackground) content.classList.add('dk-clock-custom__content--background');
            field.appendChild(content);
            custom.appendChild(field);
            customFields.push({
                def: def,
                node: field,
                content: content,
                last: null
            });
        });
    }

    function tickCustom(now) {
        if (!custom) return false;
        var scale = bounded(cfg.clockScale, 100, 50, 200) / 100;
        customFields.forEach(function(entry) {
            var def = entry.def,
                field = entry.node,
                html = formatText(def.format, now);
            if (entry.last !== html) {
                while (entry.content.firstChild) entry.content.removeChild(entry.content.firstChild);
                richClock(entry.content, html);
                entry.last = html;
            }
            var width = bounded(def.width, 0, 0, 4096),
                height = bounded(def.height, 0, 0, 2160),
                x = bounded(def.x, 0, -4096, 4096);
            field.style.width = width ? width + 'px' : 'auto';
            field.style.height = height ? height + 'px' : 'auto';
            field.style.transform = 'scale(' + scale + ')';
            field.style.transformOrigin = 'top left';
            var left = def.screenHAlign === 'right' ?
                window.innerWidth - (width || field.offsetWidth) * scale :
                def.screenHAlign === 'center' ?
                    (window.innerWidth - (width || field.offsetWidth) * scale) / 2 : 0;
            field.style.left = (left + x) + 'px';
            field.style.top = bounded(def.y, 0, -2160, 2160) + 'px';
        });
        return true;
    }

    function tick() {
        if (!disposed && cfg.visible) tickCustom(new Date());
    }

    function release() {
        if (callbackId !== null) viewEnv.removeDataChangedCallback(callbackId, resourceId);
        callbackId = null;
        resourceId = null;
        model = null;
        lastPayload = null;
    }

    function refresh() {
        if (disposed) return;
        var found = null,
            id = null;
        if (window.subViews) {
            var ids = window.subViews.ids();
            for (var i = 0; i < ids.length; i++) {
                var child = window.subViews.get(ids[i]);
                if (child && child.model && child.model.DriftkingsUI && child.model.DriftkingsUI.name === 'DriftkingsHangarClock') {
                    found = child.model;
                    id = ids[i];
                    break;
                }
            }
        }
        if (resourceId !== id) {
            release();
            resourceId = id;
            if (id !== null) callbackId = viewEnv.addDataChangedCallback('model', id, true);
        }
        model = found;
        var payload = found ? found.payload || '{}' : '{}';
        if (custom && lastPayload === payload) return;
        lastPayload = payload;
        try {
            cfg = JSON.parse(payload).config || {};
        } catch (e) {
            cfg = {};
        }
        configureCustom();
        if (custom) custom.style.display = cfg.visible ? 'block' : 'none';
        if (timer !== null) {
            clearInterval(timer);
            timer = null;
        }
        if (cfg.visible) {
            tick();
            timer = setInterval(tick, 1000);
        }
    }

    function changed() {
        if (!model || model.payload !== lastPayload) refresh();
    }

    function dispose() {
        if (disposed) return;
        disposed = true;
        if (timer !== null) {
            clearInterval(timer);
            timer = null;
        }
        engine.off('viewEnv.onDataChanged', changed);
        engine.off('subViews.onAdded', refresh);
        engine.off('subViews.onRemoved', refresh);
        release();
        window.removeEventListener('resize', tick);
        window.removeEventListener('unload', dispose);
        if (custom && custom.parentNode) custom.parentNode.removeChild(custom);
        custom = null;
        customFields = [];
        if (policy && policy.parentNode) policy.parentNode.removeChild(policy);
        policy = null;
    }
    window.__dkHangarClock = {
        dispose: dispose
    };
    engine.whenReady.then(function() {
        if (disposed) return;
        engine.on('viewEnv.onDataChanged', changed);
        engine.on('subViews.onAdded', refresh);
        engine.on('subViews.onRemoved', refresh);
        window.addEventListener('resize', tick);
        window.addEventListener('unload', dispose);
        refresh();
    });
}());
