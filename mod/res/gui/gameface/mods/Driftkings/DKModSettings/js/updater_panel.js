/* Updates section of the Driftkings settings page: its buttons and the updater state they show. */
(function () {
    'use strict';
    var DK = window.DK = window.DK || {};
    var el = DK.dom.el;

    // button(parent, action) creates a footer-style button; send(action) talks to Python.
    function build(parent, text, button, send) {
        var panel = {};
        var updates = panel.root = el('div', 'dk-updates', null, parent);
        el('div', 'dk-section', text['updates.title'], updates);
        panel.installed = el('div', 'dk-update-line', null, updates);
        panel.channel = el('div', 'dk-update-line', null, updates);
        panel.lastCheck = el('div', 'dk-update-line', null, updates);
        panel.status = el('div', 'dk-update-line', null, updates);
        panel.blocked = el('div', 'dk-update-blocked', null, updates);
        panel.outcome = el('div', 'dk-update-result', null, updates);
        panel.latest = el('div', 'dk-update-line', null, updates);
        panel.changes = el('div', 'dk-update-changelog', null, updates);
        panel.check = button(updates, function () { send('check_updates'); });
        panel.check.textContent = text['updates.check'];
        panel.download = button(updates, function () { send('download_update'); });
        panel.download.className += ' dk-update-download';
        panel.download.textContent = text['updates.download'];
        panel.manual = button(updates, function () { send('manual_update'); });
        panel.manual.textContent = text['updates.manual'];
        panel.cancel = button(updates, function () { send('cancel_update_download'); });
        panel.cancel.textContent = text['updates.cancelDownload'];
        panel.install = button(updates, function () { send('schedule_update'); });
        panel.install.className += ' dk-update-install';
        panel.install.textContent = text['updates.install'];
        panel.restart = button(updates, function () { send('restart_update'); });
        panel.restart.className += ' dk-update-restart';
        panel.restart.textContent = text.restartNow;
        panel.later = button(updates, function () { send('defer_update'); });
        panel.later.textContent = text['updates.later'];
        panel.cancelInstall = button(updates, function () { send('cancel_update_install'); });
        panel.cancelInstall.textContent = text['updates.cancelInstall'];
        return panel;
    }

    function render(panel, update, strings, unsaved) {
        panel.installed.textContent = strings['updates.installed'] + ': ' + update.installedVersion;
        panel.channel.textContent = strings['updates.channel'] + ': ' + update.channel;
        panel.lastCheck.textContent = strings['updates.lastCheck'] + ': ' + (update.lastCheck === null ? strings['updates.never'] : new Date(update.lastCheck * 1000).toLocaleString());
        panel.status.textContent = strings['updates.' + update.status] || update.status;
        if (update.status === 'IDLE' && update.lastCheck === null) { panel.status.textContent = strings['updates.notChecked']; }
        if (update.error === 'transportUnavailable') { panel.status.textContent = strings['updates.transportUnavailable']; }
        if (update.latestVersion && update.compatible === false) { panel.status.textContent += ' ' + strings['updates.incompatible']; }
        panel.latest.textContent = update.latestVersion ? strings['updates.latest'] + ': ' + update.latestVersion : '';
        panel.changes.textContent = (update.changelog || []).join('\n');
        var busy = ['CHECKING', 'DOWNLOADING', 'VERIFYING', 'INSTALLING', 'RESTART_REQUIRED'].indexOf(update.status) >= 0;
        panel.check.disabled = busy || update.status === 'READY' || !!update.cancellingInstall;
        var downloadable = update.canDownload && update.compatible === true && ['AVAILABLE', 'ERROR'].indexOf(update.status) >= 0;
        panel.download.style.display = downloadable ? '' : 'none';
        panel.download.disabled = !downloadable;
        panel.manual.disabled = ['INSTALLING', 'RESTART_REQUIRED'].indexOf(update.status) >= 0;
        panel.cancel.style.display = update.canCancel ? '' : 'none';
        panel.cancel.disabled = !update.canCancel;
        var installable = update.canInstall && update.compatible === true && ['READY', 'ERROR'].indexOf(update.status) >= 0 && !update.cancellingInstall;
        panel.install.style.display = installable ? '' : 'none';
        panel.install.disabled = !installable;
        var prepared = update.status === 'RESTART_REQUIRED' && update.installScheduled === true && !update.cancellingInstall;
        panel.restart.style.display = prepared ? '' : 'none';
        panel.restart.disabled = !prepared || !update.canRestart || !!unsaved;
        panel.later.style.display = prepared && !update.restartDeferred ? '' : 'none';
        panel.later.disabled = !prepared;
        panel.cancelInstall.style.display = update.status === 'INSTALLING' || update.installScheduled || update.cancellingInstall ? '' : 'none';
        panel.cancelInstall.disabled = !!update.cancellingInstall;
        panel.blocked.textContent = update.installBlocked ? (strings['updates.block.' + update.installBlocked] || strings['updates.installBlocked']) : '';
        if (prepared) { panel.blocked.textContent += ' ' + strings['updates.wgcLimit']; }
        if (update.cancellingInstall) { panel.status.textContent = strings['updates.cancelling']; }
        var outcome = update.lastInstallResult;
        panel.outcome.textContent = outcome ? (strings['updates.result.' + outcome.status] || strings['updates.result.failed']).replace('{version}', outcome.version || '') : '';
        if (update.status === 'DOWNLOADING' && typeof update.downloadPercent === 'number') {
            panel.status.textContent += ' ' + update.downloadPercent + '%';
        }
    }

    DK.updaterPanel = {build: build, render: render};
}());
