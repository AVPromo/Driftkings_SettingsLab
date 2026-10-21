/* Building blocks shared by the settings controls: rows, text inputs, value snapping and sliders. */
(function () {
    'use strict';
    var DK = window.DK = window.DK || {};
    var el = DK.dom.el, setClass = DK.dom.setClass, inside = DK.dom.inside, handled = DK.dom.handled;

    function label(ctx, key, fallback) {
        var value = ctx && ctx.labels ? ctx.labels[key] : undefined;
        return value === undefined || value === null ? fallback : value;
    }
    function decimals(step) {
        var text = String(step), dot = text.indexOf('.');
        return dot < 0 ? 0 : text.length - dot - 1;
    }
    function snap(value, def) {
        var steps = Math.round((value - def.min) / def.step);
        var result = def.min + steps * def.step;
        result = Math.max(def.min, Math.min(def.max, result));
        return parseFloat(result.toFixed(decimals(def.step)));
    }

    /* Row layout shared by value controls. */
    function row(def, extraClass) {
        var node = el('div', 'dk-row' + (extraClass ? ' ' + extraClass : ''));
        // Capture focus/blur: Gameface does not need :focus-within support.
        node.addEventListener('focus', function () { setClass(node, 'has-focus', true); }, true);
        node.addEventListener('blur', function (event) {
            setClass(node, 'has-focus', inside(event.relatedTarget, node));
        }, true);
        var labelArea = el('div', 'dk-label-area', null, node);
        el('div', 'dk-label', def.label, labelArea);
        if (def.description) {
            var help = el('div', 'dk-help', '?', labelArea);
            help.tabIndex = 0;
            help.setAttribute('aria-label', def.description);
            help.addEventListener('mouseenter', function () { DK.layer.showTip(help, def.description); });
            help.addEventListener('mouseleave', function () {
                if (document.activeElement !== help) { DK.layer.hideTip(); }
            });
            help.addEventListener('focus', function () { DK.layer.showTip(help, def.description); });
            help.addEventListener('blur', DK.layer.hideTip);
        }
        return {node: node, input: el('div', 'dk-input-area', null, node)};
    }
    function textInput(type, def) {
        var input = document.createElement('input');
        input.type = type; input.className = 'dk-text';
        if (def.maxLength) { input.maxLength = def.maxLength; }
        if (def.placeholder) { input.placeholder = def.placeholder; }
        input.autocomplete = 'off';
        return input;
    }
    function onCommit(input, commit) {
        input.addEventListener('keydown', function (event) {
            if (event.keyCode === 13 && (String(input.tagName).toLowerCase() !== 'textarea' || event.ctrlKey)) { commit(); }
        });
        input.addEventListener('blur', commit);
    }
    function flashInvalid(input) {
        setClass(input, 'is-invalid', true);
        setTimeout(function () { setClass(input, 'is-invalid', false); }, 1200);
    }
    function base(r) {
        var state = {disabled: false};
        return {
            node: r.node, state: state,
            info: function (info) {
                state.disabled = !!info.disabled;
                setClass(r.node, 'is-disabled', state.disabled);
                setClass(r.node, 'is-changed', !!info.changed);
                if (r.node.querySelectorAll) { var inputs = r.node.querySelectorAll('input,textarea,button,[tabindex]'); for (var i = 0; i < inputs.length; i++) { inputs[i].disabled = state.disabled; setClass(inputs[i], 'is-disabled', state.disabled); if (inputs[i]._dkTab === undefined) { inputs[i]._dkTab = inputs[i].tabIndex; } inputs[i].tabIndex = state.disabled ? -1 : inputs[i]._dkTab; } }
            }
        };
    }

    function sliderWidget(parent, def, onInput, onDone) {
        var wrap = el('div', 'dk-slider', null, parent);
        var track = el('div', 'dk-slider-track', null, wrap);
        el('div', 'dk-slider-rail', null, track);
        var fill = el('div', 'dk-slider-fill', null, track), thumb = el('div', 'dk-slider-thumb', null, track);
        var text = el('input', 'dk-slider-value', null, wrap);
        text.type = 'text';
        if (def.unit) { el('span', 'dk-unit', def.unit, wrap); }
        var widget = {track: track, value: def.min, disabled: false, dragging: false};
        widget.render = function () {
            var ratio = (widget.value - def.min) / (def.max - def.min);
            ratio = Math.max(0, Math.min(1, ratio));
            fill.style.width = (ratio * 100) + '%';
            thumb.style.left = (ratio * 100) + '%';
            if (document.activeElement !== text) { text.value = String(widget.value); }
        };
        function commitValue(next) {
            widget.value = snap(next, def);
            text.value = String(widget.value);
            widget.render();
            if (onInput) { onInput(widget.value); }
            onDone(widget.value);
        }
        onCommit(text, function () {
            if (widget.disabled) { return; }
            var raw = String(text.value).trim(), next = Number(raw.replace(',', '.'));
            if (!raw || !isFinite(next) || next < def.min || next > def.max) {
                flashInvalid(text); text.value = String(widget.value); return;
            }
            commitValue(next);
        });
        track.tabIndex = 0;
        function arrowKey(event) {
            var code = event.keyCode || event.which;
            var key = event.key;
            var direction = key === 'ArrowLeft' || key === 'ArrowDown' || code === 37 || code === 40 ? -1 :
                key === 'ArrowRight' || key === 'ArrowUp' || code === 39 || code === 38 ? 1 : 0;
            if (widget.disabled || !direction || event.ctrlKey || event.altKey || event.metaKey) { return; }
            handled(event);
            if (event.preventDefault) { event.preventDefault(); }
            var current = widget.value;
            if (document.activeElement === text) {
                var raw = String(text.value).trim(), typed = Number(raw.replace(',', '.'));
                if (raw && isFinite(typed) && typed >= def.min && typed <= def.max) { current = snap(typed, def); }
            }
            var next = snap(current + direction * def.step, def);
            if (next !== widget.value) { commitValue(next); }
            else { text.value = String(widget.value); }
        }
        function focusedKey(event) {
            if (document.activeElement === track || document.activeElement === text) { arrowKey(event); }
        }
        // A native input reliably owns keyboard focus in Gameface; a div may not.
        document.addEventListener('keydown', focusedKey, true);
        function wheel(event) {
            if (widget.disabled || widget.dragging) { return; }
            var delta = Number(event.deltaY);
            if (!isFinite(delta) || delta === 0) { delta = Number(event.wheelDelta); }
            if (!isFinite(delta) || delta === 0) { return; }
            // Match the client's wheel convention used by the panel scroll wheel.
            var next = snap(widget.value + (delta > 0 ? 1 : -1) * def.step, def);
            if (event.preventDefault) { event.preventDefault(); }
            handled(event);
            if (next !== widget.value) { commitValue(next); }
        }
        wrap.addEventListener('wheel', wheel);
        function fromEvent(event) {
            var rect = track.getBoundingClientRect();
            var ratio = rect.width > 0 ? (event.clientX - rect.left) / rect.width : 0;
            var next = snap(def.min + Math.max(0, Math.min(1, ratio)) * (def.max - def.min), def);
            if (next !== widget.value) { widget.value = next; text.value = String(next); widget.render(); if (onInput) { onInput(next); } }
        }
        function move(event) { fromEvent(event); }
        function cancel() {
            widget.dragging = false;
            document.removeEventListener('mousemove', move);
            document.removeEventListener('mouseup', up);
            DK.layer.removeDrag(cancel);
        }
        widget.dispose = function () {
            cancel();
            document.removeEventListener('keydown', focusedKey, true);
            wrap.removeEventListener('wheel', wheel);
        };
        function up(event) {
            fromEvent(event);
            cancel();
            onDone(widget.value);
        }
        track.addEventListener('mousedown', function (event) {
            if (widget.disabled) { return; }
            if (event.button !== 0) { return; }
            DK.modal.focus(text);
            if (event.preventDefault) { event.preventDefault(); }
            widget.dragging = true;
            DK.layer.addDrag(cancel);
            fromEvent(event);
            document.addEventListener('mousemove', move);
            document.addEventListener('mouseup', up);
        });
        return widget;
    }

    DK.controlKit = {label: label, snap: snap, row: row, base: base, textInput: textInput,
                     onCommit: onCommit, flashInvalid: flashInvalid, sliderWidget: sliderWidget};
}());
