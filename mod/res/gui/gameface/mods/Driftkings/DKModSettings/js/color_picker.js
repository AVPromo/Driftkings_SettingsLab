/* Colour control with a spectrum picker, optional alpha and presets, opened as a modal. */
(function () {
    'use strict';
    var DK = window.DK = window.DK || {};
    var el = DK.dom.el, handled = DK.dom.handled, kit = DK.controlKit;
    var row = kit.row, base = kit.base, textInput = kit.textInput, onCommit = kit.onCommit;
    var flashInvalid = kit.flashInvalid, sliderWidget = kit.sliderWidget, label = kit.label;
    var normalizeHex = DK.colors.normalizeColor;
    var hexToRgb = DK.colors.hexToRgb;

    function color(def, ctx) {
        var r = row(def), api = base(r), value = '#FFFFFF', alpha = 100;
        var meta = def.metadata || {}, hasAlpha = !!(meta.allowAlpha && meta.alphaKey);
        var wrap = el('div', 'dk-color', null, r.input);
        var swatch = el('button', 'dk-color-swatch', null, wrap), input = textInput('text', {maxLength: 8});
        swatch.type = 'button'; wrap.appendChild(input);
        function show() { swatch.style.backgroundColor = value; if (document.activeElement !== input) { input.value = value; } }
        onCommit(input, function () {
            if (api.state.disabled) { return; }
            var hex = normalizeHex(input.value);
            if (!hex) { flashInvalid(input); input.value = value; return; }
            if (hex !== value) { value = hex; show(); ctx.commit(def.id, hex); }
        });
        function open() {
            if (api.state.disabled) { return; }
            var draft = value, draftAlpha = alpha, position = DK.colors.spectrumPosition(value), x = position.x, y = position.y;
            var panel = el('div', 'dk-color-picker'), area = el('div', 'dk-spectrum', null, panel);
            area.tabIndex = 0; area.setAttribute('aria-label', label(ctx, 'color.area', 'Color spectrum'));
            var canvas = el('canvas', 'dk-spectrum-canvas', null, area), cursor = el('div', 'dk-spectrum-cursor', null, area);
            canvas.width = 256; canvas.height = 192;
            try {
                var paint = canvas.getContext && canvas.getContext('2d');
                if (paint) {
                    var pixels = paint.createImageData(256,192);
                    for (var py=0; py<192; py++) { for (var px=0; px<256; px++) {
                        var rgb = hexToRgb(DK.colors.spectrum(px/255,py/191)), offset=(py*256+px)*4;
                        pixels.data[offset]=rgb[0]; pixels.data[offset+1]=rgb[1]; pixels.data[offset+2]=rgb[2]; pixels.data[offset+3]=255;
                    } }
                    paint.putImageData(pixels,0,0);
                } else { canvas.style.display='none'; }
            } catch (ignore) { canvas.style.display='none'; }
            var previews = el('div', 'dk-color-comparison', null, panel);
            function preview(label) {
                var box=el('div', '', null, previews); el('div','dk-color-title',label,box);
                return el('div','dk-color-preview dk-checker',null,box);
            }
            var current=preview(label(ctx, 'color.current', 'Current')), next=preview(label(ctx, 'color.new', 'New'));
            var currentFill=el('div','dk-preview-fill',null,current), nextFill=el('div','dk-preview-fill',null,next);
            currentFill.style.backgroundColor=value; currentFill.style.opacity=alpha/100;
            el('div','dk-color-title','HEX',panel);
            var hexInput=textInput('text',{maxLength:8}); panel.appendChild(hexInput);
            var alphaWidget=null, alphaLabel=null, alphaLine=null;
            function render() {
                cursor.style.left=(x*100)+'%'; cursor.style.top=(y*100)+'%';
                nextFill.style.backgroundColor=draft; nextFill.style.opacity=draftAlpha/100;
                hexInput.value=draft;
                if (alphaLabel) { alphaLabel.textContent=Math.round(draftAlpha)+'%'; }
                if (alphaLine) { alphaLine.style.backgroundImage='linear-gradient(to right, transparent, '+draft+')'; }
            }
            function select(e) {
                var rect=area.getBoundingClientRect(); x=Math.max(0,Math.min(1,(e.clientX-rect.left)/Math.max(1,rect.width)));
                y=Math.max(0,Math.min(1,(e.clientY-rect.top)/Math.max(1,rect.height))); draft=DK.colors.spectrum(x,y); render();
            }
            function stop() { document.removeEventListener('mousemove',select); document.removeEventListener('mouseup',stop); }
            area.addEventListener('mousedown',function(e) { handled(e); DK.modal.focus(area); select(e); document.addEventListener('mousemove',select); document.addEventListener('mouseup',stop); });
            area.addEventListener('keydown',function(e) {
                if ([37,38,39,40].indexOf(e.keyCode)<0) { return; } handled(e);
                var step=e.shiftKey ? 0.05 : 0.005;
                x=Math.max(0,Math.min(1,x+(e.keyCode===37?-step:e.keyCode===39?step:0)));
                y=Math.max(0,Math.min(1,y+(e.keyCode===38?-step:e.keyCode===40?step:0)));
                draft=DK.colors.spectrum(x,y); render();
            });
            function readHex() { var hex=normalizeHex(hexInput.value); if (!hex) { flashInvalid(hexInput); return false; } draft=hex; position=DK.colors.spectrumPosition(draft); x=position.x; y=position.y; render(); return true; }
            onCommit(hexInput,readHex);
            if (hasAlpha) {
                el('div','dk-color-title','Alpha',panel);
                var alphaHost=el('div','dk-alpha dk-checker',null,panel);
                alphaWidget=sliderWidget(alphaHost,{min:0,max:100,step:1},function(n){ draftAlpha=n; render(); },function(){});
                alphaLine=alphaHost.querySelectorAll('.dk-slider-rail')[0];
                alphaWidget.track.setAttribute('aria-label', 'Alpha');
                alphaLabel=el('div','dk-alpha-value',null,panel);
                alphaWidget.value=draftAlpha; alphaWidget.render();
            }
            if (def.presets) {
                var presets=el('div','dk-presets',null,panel);
                def.presets.forEach(function(p) { var btn=el('button','dk-preset',null,presets); btn.style.backgroundColor=p.value; btn.title=p.label;
                    btn.addEventListener('click',function(){ draft=normalizeHex(p.value); position=DK.colors.spectrumPosition(draft); x=position.x; y=position.y; render(); }); });
            }
            var actions=el('div','dk-modal-actions',null,panel);
            el('button','dk-btn',label(ctx, 'cancel', 'Cancel'),actions).addEventListener('click',function(){DK.modal.close(false);});
            el('button','dk-btn dk-primary',label(ctx, 'apply', 'Apply'),actions).addEventListener('click',function(){if(readHex()){DK.modal.close(true);}});
            render(); DK.modal.open(panel,{origin:swatch, cleanup:function(){stop(); if(alphaWidget){alphaWidget.dispose();}}, apply:function(){
                if(draft!==value || draftAlpha!==alpha) {
                    value=draft; alpha=draftAlpha; show();
                    ctx.commit(def.id,draft,hasAlpha ? DK.colors.alphaFromUi(draftAlpha,meta.alphaScale) : undefined);
                }
            }});
        }
        swatch.addEventListener('click',open);
        api.dispose=function(){if(DK.modal.isOpen()){DK.modal.close(false);}};
        api.update=function(next){value=normalizeHex(next)||value; show();};
        var info=api.info;
        api.info=function(state){info(state); if(hasAlpha && state.values){var n=DK.colors.alphaToUi(state.values[meta.alphaKey],meta.alphaScale); alpha=n===null?100:n;}};
        return api;
    }

    DK.controlKit.color = color;
}());
