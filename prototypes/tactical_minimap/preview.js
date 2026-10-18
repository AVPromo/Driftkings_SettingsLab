(function () {
    'use strict';
    var renderer = new window.DKTacticalPreview.Renderer(document.getElementById('map'));
    var names = ['theme', 'size', 'opacity', 'iconScale', 'ally', 'enemy', 'platoon', 'names', 'grid'];
    var sample = {source: 'synthetic-preview', markers: [
        {id: 1, visible: true, state: 'visible', side: 'player', vehicleClass: 'mediumTank', x: 0.5, y: 0.7, heading: 45, name: 'Jogador'},
        {id: 2, visible: true, state: 'visible', side: 'enemy', vehicleClass: 'heavyTank', x: 0.3, y: 0.2, name: 'HT'},
        {id: 3, visible: true, state: 'visible', side: 'ally', vehicleClass: 'lightTank', x: 0.7, y: 0.5, name: 'LT'},
        {id: 4, visible: true, state: 'visible', side: 'platoon', vehicleClass: 'AT-SPG', x: 0.2, y: 0.6, name: 'TD'},
        {id: 5, visible: true, state: 'visible', side: 'ally', vehicleClass: 'SPG', x: 0.8, y: 0.85, name: 'SPG'},
        {id: 6, visible: true, state: 'destroyed', side: 'enemy', vehicleClass: 'mediumTank', x: 0.8, y: 0.2, name: 'Destruído'}
    ]};
    function render() {
        function value(id) { return document.getElementById(id).value; }
        renderer.render(sample, {theme: value('theme'), size: Number(value('size')),
            opacity: Number(value('opacity')) / 100, iconScale: Number(value('iconScale')) / 100,
            ally: value('ally'), enemy: value('enemy'), platoon: value('platoon'),
            showVehicleNames: document.getElementById('names').checked,
            showGrid: document.getElementById('grid').checked});
    }
    names.forEach(function (id) { document.getElementById(id).onchange = render; });
    window.onunload = function () {
        names.forEach(function (id) { document.getElementById(id).onchange = null; });
        renderer.dispose();
    };
    render();
}());
