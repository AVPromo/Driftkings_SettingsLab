package driftkings.battle.components.minimap
{
    import flash.display.DisplayObject;
    import flash.geom.Rectangle;
    import flash.text.TextField;
    import flash.utils.Dictionary;
    import net.wg.gui.battle.views.minimap.components.entries.vehicle.VehicleMinimapEntry;

    /** Owned vehicle captions replacing the native names, with overlap avoidance. */
    public class VehicleLabels
    {
        private var styles:NativeStyles;
        private var labels:Dictionary = new Dictionary(true);
        private var visible:Array = [];

        public function VehicleLabels(styles:NativeStyles)
        {
            this.styles = styles;
        }

        public function begin():void
        {
            visible = [];
        }

        public function update(entry:VehicleMinimapEntry, data:Object, options:Object):void
        {
            var owned:VehicleLabel = labels[entry] as VehicleLabel;
            if (!owned) { owned = new VehicleLabel(); labels[entry] = owned; entry.addChild(owned); }
            var native:TextField = entry.vehicleNameTextFieldAlt.visible ? entry.vehicleNameTextFieldAlt : entry.vehicleNameTextFieldClassic;
            styles.remember(entry.vehicleNameTextFieldAlt); styles.remember(entry.vehicleNameTextFieldClassic);
            entry.vehicleNameTextFieldAlt.alpha = entry.vehicleNameTextFieldClassic.alpha = 0;
            owned.update(data, options, native);
            if (entry.visible && owned.caption.visible) visible.push(owned);
        }

        public function resolveOverlaps(options:Object, space:DisplayObject):void
        {
            if (!options.labels.avoidOverlap || options.alternative) return;
            visible.sortOn("priority", Array.DESCENDING | Array.NUMERIC);
            var occupied:Array = [];
            for each (var label:VehicleLabel in visible)
            {
                var bounds:Rectangle = label.caption.getBounds(space);
                var collision:Boolean = intersects(bounds, occupied);
                if (collision) { label.compact(true); bounds = label.caption.getBounds(space); }
                if (collision && intersects(bounds, occupied)) label.caption.visible = false;
                else occupied.push(bounds);
            }
        }

        public function removeDetached():void
        {
            for (var key:Object in labels)
                if (!DisplayObject(key).stage) { VehicleLabel(labels[key]).dispose(); delete labels[key]; }
        }

        public function clear():void
        {
            for each (var label:VehicleLabel in labels) label.dispose();
            labels = new Dictionary(true);
            visible = [];
        }

        private static function intersects(bounds:Rectangle, occupied:Array):Boolean
        {
            for each (var rect:Rectangle in occupied) if (bounds.intersects(rect)) return true;
            return false;
        }
    }
}
