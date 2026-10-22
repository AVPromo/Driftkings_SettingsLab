/* Settings controls built from Python definitions. Text is always set with textContent. */
(function () {
    'use strict';
    var DK = window.DK = window.DK || {};
    var el = DK.dom.el, setClass = DK.dom.setClass, handled = DK.dom.handled, kit = DK.controlKit;
    var label = kit.label, snap = kit.snap, row = kit.row, base = kit.base, textInput = kit.textInput;
    var onCommit = kit.onCommit, flashInvalid = kit.flashInvalid, sliderWidget = kit.sliderWidget;
    var normalizeHex = DK.colors.normalizeColor;

    function toggle(def, ctx, kind) {
        var r = row(def, 'dk-toggle-row'), api = base(r), value = false, root, text;
        if (kind === 'switch') {
            root = el('div', 'dk-switch', null, r.input);
            text = el('div', 'dk-switch-text', null, root);
            el('div', 'dk-switch-knob', null, el('div', 'dk-switch-track', null, root));
        } else {
            root = el('div', 'dk-checkbox', null, r.input);
            el('div', 'dk-checkbox-mark', null, root);
        }
        function render() {
            setClass(root, 'is-on', value);
            if (text) { text.textContent = value ? ctx.labels.on : ctx.labels.off; }
        }
        root.tabIndex = 0;
        root.addEventListener('keydown', function (event) { if (event.keyCode === 13 || event.keyCode === 32) { handled(event); if (!api.state.disabled) { value = !value; render(); ctx.commit(def.id, value); } } });
        root.addEventListener('click', function (event) {
            handled(event);
            if (api.state.disabled) { return; }
            value = !value; render(); ctx.commit(def.id, value);
        });
        api.update = function (next) { value = next === true; render(); };
        return api;
    }

    function dropdown(def, ctx) {
        var r = row(def), api = base(r), value = null;
        var box = el('div', 'dk-dropdown', null, r.input), label = el('span', null, null, box);
        el('div', 'dk-dropdown-arrow', null, box);
        function labelOf(current) {
            for (var i = 0; i < def.options.length; i++) {
                if (def.options[i].value === current) { return def.options[i].label; }
            }
            return String(current);
        }
        box.tabIndex = 0;
        box.addEventListener('keydown', function (event) {
            if (api.state.disabled || [13,27,35,36,38,40].indexOf(event.keyCode) < 0) { return; }
            handled(event);
            if (event.keyCode === 27) { DK.layer.close(); return; }
            if (event.keyCode === 13) { box.click(); return; }
            var index = def.options.map(function (option) { return option.value; }).indexOf(value);
            index = event.keyCode === 36 ? 0 : event.keyCode === 35 ? def.options.length - 1 : Math.max(0, Math.min(def.options.length - 1, index + (event.keyCode === 38 ? -1 : 1)));
            value = def.options[index].value; label.textContent = def.options[index].label; ctx.commit(def.id, value);
        });
        box.addEventListener('click', function (event) {
            handled(event);
            if (api.state.disabled) { return; }
            if (DK.layer.anchor() === box) { DK.layer.close(); return; }
            var list = el('div');
            def.options.forEach(function (option, index) {
                var item = el('button', 'dk-option' + (option.value === value ? ' is-selected' : ''), option.label, list);
                var source = def.preview && def.preview.images && def.preview.images[index];
                if (source) {
                    item.textContent = '';
                    setClass(item, 'dk-image-option', true);
                    var icon = el('img', 'dk-option-image', null, item);
                    icon.src = source;
                    icon.addEventListener('error', function () { icon.style.visibility = 'hidden'; });
                    el('span', null, option.label, item);
                }
                item.addEventListener('keydown', function (event) {
                    if (event.keyCode === 27) { handled(event); DK.layer.close(); return; }
                    if ([35,36,38,40].indexOf(event.keyCode) < 0) { return; }
                    handled(event);
                    var next = event.keyCode === 36 ? 0 : event.keyCode === 35 ? def.options.length-1 : Math.max(0, Math.min(def.options.length-1, index+(event.keyCode === 38 ? -1 : 1)));
                    value = def.options[next].value; label.textContent = def.options[next].label;
                    DK.modal.focus(list.children[next]); ctx.commit(def.id, value);
                });
                item.addEventListener('click', function () {
                    DK.layer.close();
                    if (option.value !== value) {
                        value = option.value; label.textContent = option.label; ctx.commit(def.id, value);
                    }
                });
            });
            DK.layer.open(box, list);
        });
        api.update = function (next) { value = next; label.textContent = labelOf(next); };
        return api;
    }

    function slider(def, ctx) {
        var r = row(def), api = base(r), committed = null;
        var widget = sliderWidget(r.input, def, function (value) { if (ctx.preview) { ctx.preview(def.id, value); } }, function (value) {
            if (value !== committed) { committed = value; ctx.commit(def.id, value); }
        });
        api.dispose = widget.dispose;
        var info = api.info;
        api.info = function (state) { info(state); widget.disabled = api.state.disabled; };
        api.update = function (next) {
            committed = next;
            if (!widget.dragging) { widget.value = next; widget.render(); }
        };
        return api;
    }

    function text(def, ctx) {
        var r = row(def), api = base(r), value = '';
        var input = def.type === 'textarea' ? el('textarea', 'dk-text dk-multiline') : textInput('text', def);
        if(def.type === 'textarea') { input.rows=8; input.maxLength=def.maxLength || 4096; input.style.height='160rem'; input.style.minHeight='160rem'; }
        r.input.appendChild(input);
        onCommit(input, function () {
            if (api.state.disabled) { return; }
            if (input.value !== value) { value = input.value; ctx.commit(def.id, value); }
        });
        api.update = function (next) {
            value = next || '';
            if (document.activeElement !== input) { input.value = value; }
        };
        return api;
    }

    function password(def, ctx) {
        var r = row(def), api = base(r);
        var input = textInput('password', def);
        var clear = el('button', 'dk-btn dk-secret-clear', ctx.labels.clearSecret);
        clear.type = 'button';
        r.input.appendChild(input); r.input.appendChild(clear);
        onCommit(input, function () {
            if (api.state.disabled) { return; }
            // The stored secret is never sent to the view; only a new value is submitted.
            if (input.value !== '') { var next = input.value; input.value = ''; ctx.commit(def.id, next); }
        });
        clear.addEventListener('click', function () { if (!api.state.disabled) { ctx.commit(def.id, ''); } });
        var info = api.info;
        api.info = function (state) {
            info(state);
            input.placeholder = def.placeholder && !state.secretSet ? def.placeholder :
                (state.secretSet ? ctx.labels.secretSet : ctx.labels.secretEmpty);
            clear.style.display = state.secretSet ? 'block' : 'none';
        };
        api.update = function () {};
        return api;
    }

    function stepper(def, ctx) {
        var r=row(def), api=base(r), value=def.min, input=textInput('text',def); r.input.appendChild(input);
        function commit(n){if(api.state.disabled){return;} n=snap(n,def); if(n!==value){value=n;input.value=String(n);ctx.commit(def.id,n);}}
        onCommit(input,function(){var n=Number(input.value);if(String(input.value).trim() && isFinite(n) && n>=def.min && n<=def.max){commit(n);}else{flashInvalid(input);input.value=String(value);}});
        input.addEventListener('keydown',function(e){if(api.state.disabled || [35,36,38,40].indexOf(e.keyCode)<0){return;} handled(e);commit(e.keyCode===36?def.min:e.keyCode===35?def.max:value+(e.keyCode===38?1:-1)*def.step*(e.shiftKey?10:1));});
        [-1,1].forEach(function(direction){el('button','dk-btn dk-step',direction<0?'−':'+',r.input).addEventListener('click',function(){commit(value+direction*def.step);});});
        api.update=function(n){value=n;if(document.activeElement!==input){input.value=String(n);}}; return api;
    }
    function radio(def,ctx){
        var r=row(def),api=base(r),value=null,buttons=[];
        function choose(index){if(api.state.disabled){return;}index=Math.max(0,Math.min(def.options.length-1,index));value=def.options[index].value;render();DK.modal.focus(buttons[index]);ctx.commit(def.id,value);}
        function render(){buttons.forEach(function(b,i){setClass(b,'is-selected',def.options[i].value===value);});}
        def.options.forEach(function(option,i){var b=el('button','dk-btn dk-radio',option.label,r.input);buttons.push(b);b.addEventListener('click',function(){choose(i);});b.addEventListener('keydown',function(e){if([13,32,35,36,37,39].indexOf(e.keyCode)<0 || api.state.disabled){return;}handled(e);choose(e.keyCode===36?0:e.keyCode===35?buttons.length-1:i+(e.keyCode===37?-1:e.keyCode===39?1:0));});});
        api.update=function(n){value=n;render();};return api;
    }

    function hotkey(def, ctx) {
        var r = row(def), api = base(r), values = [], names = {}, capturing = false;
        var box = el('button', 'dk-btn', null, r.input); box.type = 'button';
        var clear = el('button', 'dk-btn dk-secret-clear', ctx.labels.clearSecret, r.input); clear.type = 'button';
        function render() {
            box.textContent = capturing ? ctx.labels.pressKey : values.map(function (group) { return group.map(function (code) { return names[String(code)] || String(code); }).join('/'); }).join(' + ') || ctx.labels.noKey;
        }
        box.addEventListener('click', function () { if (!api.state.disabled) { ctx.capture(def.id); } });
        clear.addEventListener('click', function () { if (!api.state.disabled) { ctx.commit(def.id, []); } });
        var info = api.info;
        api.info = function (state) { info(state); names = state.keyNames || {}; capturing = !!state.capture; render(); };
        api.update = function (next) { values = next || []; render(); };
        return api;
    }
    function multiselect(def, ctx) {
        var r = row(def), api = base(r), values = [], options = [];
        def.options.forEach(function (option) {
            var item = el('div', 'dk-option', option.label, r.input); options.push(item);
            item.addEventListener('click', function () {
                if (api.state.disabled) { return; }
                var index = values.indexOf(option.value); if (index < 0) { values.push(option.value); } else { values.splice(index, 1); }
                ctx.commit(def.id, values.slice());
            });
        });
        api.update = function (next) { values = next.slice(); options.forEach(function (item, index) { setClass(item, 'is-selected', values.indexOf(def.options[index].value) >= 0); }); };
        return api;
    }

    function button(def, ctx) {
        var r = row(def), api = base(r);
        var node = el('button', 'dk-btn', def.text || def.label, r.input);
        node.type = 'button';
        node.addEventListener('click', function () { if (!api.state.disabled) { ctx.action(def.id); } });
        api.update = function () {};
        return api;
    }

    function staticNode(def) {
        var node = def.type === 'section' ? el('div', 'dk-section', def.label) :
            def.type === 'separator' ? el('div', 'dk-separator') : el('div', 'dk-info', def.label);
        return {node: node, state: {}, info: function () {}, update: function () {}};
    }

    var factories = {
        'switch': function (def, ctx) { return toggle(def, ctx, 'switch'); },
        checkbox: function (def, ctx) { return toggle(def, ctx, 'checkbox'); },
        dropdown: dropdown, slider: slider, number: stepper, text: text, password: password,
        color: kit.color, button: button, hotkey: hotkey, multiselect: multiselect, textarea: text, file: text, directory: text
    };

    DK.controls = {
        create: function (def, ctx) {
            var factory = factories[def.type];
            if (def.metadata && def.metadata.sourceType === 'NumericStepper') { factory = stepper; }
            if (def.metadata && def.metadata.sourceType === 'RadioButtonGroup' && def.options.length <= 5) { factory = radio; }
            var api = factory ? factory(def, ctx) : staticNode(def);
            var timing = def.metadata && def.metadata.applyTiming;
            if (['live', 'battle', 'view', 'restart'].indexOf(timing) >= 0) {
                var labels = (ctx && ctx.labels) || {};
                var badge = el('div', 'dk-apply-timing dk-apply-timing--' + timing, null, api.node);
                if (timing === 'restart') { el('span', 'dk-alert-icon', null, badge); }
                el('span', '', (timing === 'restart' ? '' : '• ') + label(ctx, 'timing.' + timing, {live: 'Immediate', battle: 'Next battle', view: 'Next view opening', restart: 'Requires restart'}[timing]), badge);
                badge.title = labels['applyTiming.' + timing] || '';
            }
            if (def.preview && def.preview.kind === 'image') {
                setClass(api.node, 'dk-media-row', true);
                var preview = el('div', 'dk-image-preview', null, api.node);
                var picture = el('img', 'dk-preview-image', null, preview);
                var missing = el('div', 'dk-preview-missing', ctx.labels['image.unavailable'], preview);
                var lastSource = null;
                picture.addEventListener('load', function () {
                    setClass(preview, 'is-empty', !lastSource);
                    picture.style.display = lastSource ? 'block' : 'none';
                    missing.style.display = lastSource ? 'none' : 'block';
                });
                picture.addEventListener('error', function () { setClass(preview, 'is-empty', true); picture.style.display = 'none'; missing.style.display = 'block'; });
                api.previewUpdate = function (source) {
                    if (source === lastSource) { return; }
                    lastSource = source;
                    setClass(preview, 'is-empty', !source);
                    picture.style.display = 'none'; missing.style.display = 'block';
                    picture.src = source || '';
                };
            } else if (def.preview && def.preview.kind === 'audio') {
                setClass(api.node, 'dk-media-row', true);
                setClass(api.node, 'dk-audio-row', true);
                var actions = el('div', 'dk-audio-actions', null, api.node);
                ['play', 'stop'].forEach(function (action) {
                    var button = el('button', 'dk-btn', ctx.labels['sound.' + action], actions);
                    button.type = 'button';
                    // Audition is independent of enabling the sound in battle.
                    // Python validates the preview action against the session.
                    button.addEventListener('click', function () { ctx.action(def.preview[action]); });
                });
            }
            if (ctx && ctx.commit && Object.prototype.hasOwnProperty.call(def, 'default')) {
                var reset = el('button', 'dk-option-reset', null, api.node.firstChild || api.node);
                reset.type = 'button';
                reset.title = label(ctx, 'resetOption', 'Reset this option to default');
                reset.setAttribute('aria-label', reset.title);
                reset.addEventListener('click', function () {
                    if (api.state && api.state.disabled) { return; }
                    DK.layer.close();
                    ctx.commit(def.id, JSON.parse(JSON.stringify(def.default)));
                });
            }
            return api;
        },
        normalizeHex: normalizeHex, snap: snap
    };
}());
