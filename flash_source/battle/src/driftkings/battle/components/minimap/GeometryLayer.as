package driftkings.battle.components.minimap
{
    import flash.display.DisplayObject;
    import flash.display.DisplayObjectContainer;
    import flash.display.Sprite;
    import flash.utils.Dictionary;

    /** Owned drawing sprites attached to native entries, one per owner. */
    public class GeometryLayer
    {
        public static const NAME:String = "dkMinimapGeometry";
        private var shapes:Dictionary = new Dictionary(true);

        // Returns {shape, key, version}; key/version let callers skip redraws.
        public function overlay(owner:Object, parent:DisplayObjectContainer, index:int = -1):Object
        {
            var stored:Object = shapes[owner];
            if (!stored)
            {
                var shape:Sprite = new Sprite(); shape.mouseEnabled = shape.mouseChildren = false;
                shape.name = NAME;
                if (index >= 0) parent.addChildAt(shape, Math.min(index, parent.numChildren));
                else parent.addChild(shape);
                stored = shapes[owner] = {shape:shape, key:null, version:-1};
            }
            return stored;
        }

        public function removeDetached():void
        {
            for (var key:Object in shapes)
                if (!DisplayObject(key).stage) { detach(shapes[key].shape); delete shapes[key]; }
        }

        public function clear():void
        {
            for each (var stored:Object in shapes) detach(stored.shape);
            shapes = new Dictionary(true);
        }

        private static function detach(shape:Sprite):void
        {
            if (shape.parent) shape.parent.removeChild(shape);
        }
    }
}
