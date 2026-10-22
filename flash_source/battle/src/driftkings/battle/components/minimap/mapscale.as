package driftkings.battle.components.minimap
{
    import flash.display.DisplayObject;
    import flash.geom.Matrix;

    /** Arena ranges from Python and the conversion from metres to minimap units. */
    public class mapscale
    {
        // Native circles entry: its local space spans 210 units per map width.
        public static const UNITS:Number = 210;
        public var reference:DisplayObject;
        public var ranges:Object;
        public var version:int = 0;
        public var mapWidth:Number = 0;

        public function setRanges(value:Object):void
        {
            ranges = value;
            ++version;
        }

        public function get width():Number
        {
            return ranges && Number(ranges.width) > 0 ? Number(ranges.width) : mapWidth;
        }

        public static function scaleOf(target:DisplayObject):Number
        {
            var m:Matrix = target.transform.concatenatedMatrix;
            return Math.sqrt(m.a * m.a + m.b * m.b);
        }

        // Map metres to target-local units. Entries are counter-scaled per minimap
        // size, so measure against the circles entry rather than assume its space.
        public function metres(target:DisplayObject, value:Number):Number
        {
            if (!(width > 0)) return 0;
            var units:Number = value * UNITS / width;
            if (reference && reference.stage && target.stage)
            {
                var own:Number = scaleOf(target), native:Number = scaleOf(reference);
                if (own > 0 && native > 0) units *= native / own;
            }
            return units;
        }
    }
}
