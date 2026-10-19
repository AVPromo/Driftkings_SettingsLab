package driftkings.battle.components.minimap
{
    import flash.geom.Point;
    import flash.geom.Rectangle;
    import net.wg.gui.battle.views.minimap.BaseMinimap;

    // Read-only geometry on the actual native component, independent of our view.
    public class TacticalGeometry
    {
        public static function capture(minimap:BaseMinimap):Object
        {
            var data:Object = {available:false, reason:"minimap-unavailable"};
            if (minimap && minimap.stage && minimap.stage.stageWidth > 0 && minimap.stage.stageHeight > 0)
            {
                try
                {
                    // Native map inset/size, not getBounds() over vehicle labels.
                    var origin:Point = minimap.currentTopLeftPoint;
                    var area:Rectangle = minimap.getMinimapRectBySizeIndex(minimap.currentSizeIndex);
                    if (origin && area && area.width > 0 && area.height > 0)
                    {
                        var a:Point = minimap.localToGlobal(origin);
                        var b:Point = minimap.localToGlobal(new Point(origin.x + area.width, origin.y));
                        var c:Point = minimap.localToGlobal(new Point(origin.x, origin.y + area.height));
                        var d:Point = minimap.localToGlobal(new Point(origin.x + area.width, origin.y + area.height));
                        var left:Number = Math.min(a.x, b.x, c.x, d.x);
                        var top:Number = Math.min(a.y, b.y, c.y, d.y);
                        data = {available:true, x:Math.round(left * 100) / 100,
                            y:Math.round(top * 100) / 100,
                            width:Math.round((Math.max(a.x,b.x,c.x,d.x) - left) * 100) / 100,
                            height:Math.round((Math.max(a.y,b.y,c.y,d.y) - top) * 100) / 100,
                            stageWidth:minimap.stage.stageWidth, stageHeight:minimap.stage.stageHeight};
                    }
                    else data.reason = "empty-map-area";
                }
                catch (error:Error) { data = {available:false, reason:"map-area-unavailable"}; }
            }
            else if (minimap) data.reason = "stage-unavailable";
            return data;
        }

    }
}
