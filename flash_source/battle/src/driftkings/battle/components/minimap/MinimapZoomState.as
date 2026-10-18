package driftkings.battle.components.minimap
{
    import net.wg.gui.battle.views.minimap.BaseMinimap;

    /** Native state captured once on entering the alternative zoom mode. */
    internal class MinimapZoomState
    {
        public var x:Number;
        public var y:Number;
        public var sx:Number;
        public var sy:Number;
        public var size:Number;
        public var index:int;

        public function MinimapZoomState(minimap:BaseMinimap, index:int)
        {
            x=minimap.x;
            y=minimap.y;
            sx=minimap.scaleX;
            sy=minimap.scaleY;
            size=minimap.currentSizeIndex;
            this.index=index;
        }
    }
}
