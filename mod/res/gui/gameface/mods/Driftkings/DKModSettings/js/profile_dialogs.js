/* Profile manager and installed components dialogs of the settings window. */
(function () {
    'use strict';
    var DK = window.DK = window.DK || {};
    var el = DK.dom.el;
    var dialog = null;

    function close() {
        if (dialog) { DK.modal.close(null); if (dialog.root.parentNode) { dialog.root.parentNode.removeChild(dialog.root); } dialog = null; }
    }

    // ctx: {window, labels, state, schema, button(parent, action), send(action, data)}.
    function installed(ctx) {
        close();
        var text = ctx.labels, state = ctx.state, button = ctx.button, root = el('div', 'dk-overlay is-visible', null, ctx.window);
        var panel = el('div', 'dk-dialog dk-profile-dialog', null, root);
        el('div', 'dk-dialog-title', text.installed, panel);
        ctx.schema.mods.forEach(function (mod) {
            var row = el('div', 'dk-installed-row', null, panel), status = state.status[mod.id] || {};
            el('div', 'dk-nav-name', mod.name, row);
            el('div', 'dk-mod-meta', [mod.version, mod.author, status.enabled === false ? text.off : text.on].filter(Boolean).join(' • '), row);
            (mod.dependencies || []).forEach(function (dependency) { if (!dependency.installed) { el('div', 'dk-error', text.dependencyMissing + ': ' + dependency.id, row); } });
        });
        if (state.diagnostics) { var debug = el('textarea', 'dk-text dk-profile-json', null, panel); debug.readOnly = true; debug.value = JSON.stringify(state.diagnostics, null, 2); }
        button(panel, close).textContent = text.close;
        dialog = {root: root};
        DK.modal.bind(panel, {cancel: close});
    }

    function profiles(ctx) {
        if (dialog) { close(); return; }
        var text = ctx.labels, state = ctx.state, button = ctx.button, selection = '';
        var root = el('div', 'dk-overlay is-visible', null, ctx.window);
        var panel = el('div', 'dk-dialog dk-profile-dialog', null, root);
        el('div', 'dk-dialog-title', text.profiles, panel);
        el('div', 'dk-dialog-text', text.profileHelp, panel);
        var selector = DK.controls.create({id: 'profile', type: 'dropdown', label: text.profiles, options: (state.profiles || []).map(function (name) { return {value: name, label: name}; })}, {
            labels: text, commit: function (key, value) { selection = value; name.value = value; }
        });
        panel.appendChild(selector.node);
        selection = (state.profiles || [])[0] || ''; selector.update(selection);
        var name = el('input', 'dk-text', null, panel); name.type = 'text'; name.placeholder = text.profileName; name.value = selection;
        var actions = el('div', 'dk-profile-actions', null, panel);
        function action(operation, extra) { var data = extra || {}; data.operation = operation; ctx.send('profile', data); }
        button(actions, function () { action('create', {name: name.value}); }).textContent = text.profileCreate;
        button(actions, function () { action('load', {name: selection}); close(); }).textContent = text.profileLoad;
        button(actions, function () { action('rename', {name: selection, target: name.value}); close(); }).textContent = text.profileRename;
        var deleting = false, del = button(actions, function () { if (!deleting) { deleting = true; del.textContent = text.confirmDelete; } else { action('delete', {name: selection}); close(); } }); del.textContent = text.profileDelete;
        var area = el('textarea', 'dk-text dk-profile-json', null, panel); area.maxLength = 2000000;
        dialog = {root: root, area: area, exported: ''};
        var bottom = el('div', 'dk-profile-actions', null, panel);
        button(bottom, function () { action('export'); }).textContent = text.profileExport;
        button(bottom, function () { action('import', {text: area.value}); }).textContent = text.profileImport;
        button(bottom, close).textContent = text.close;
        DK.modal.bind(panel, {cancel: close});
    }

    // Shows a newly exported profile in the open profile manager.
    function showExport(profileText) {
        if (dialog && dialog.area && dialog.exported !== profileText) { dialog.area.value = profileText || ''; dialog.exported = profileText; }
    }

    DK.profileDialogs = {installed: installed, profiles: profiles, close: close, showExport: showExport,
                         isOpen: function () { return !!dialog; }};
}());
