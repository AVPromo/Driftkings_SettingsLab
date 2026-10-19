package driftkings.battle.components.minimap
{
    import flash.display.DisplayObject;
    import flash.display.DisplayObjectContainer;
    import flash.display.MovieClip;
    import net.wg.gui.battle.views.minimap.components.entries.personal.SimpleAttentionToFlashMinimapEntry;
    import flash.geom.Point;
    import flash.geom.Rectangle;
    import net.wg.gui.battle.views.minimap.BaseMinimap;

    // Read-only geometry on the actual native component, independent of our view.
    public class TacticalGeometry
    {
        public static function cellPings(minimap:BaseMinimap):String
        {
            var area:Object = capture(minimap);
            if (!area.available || !minimap.visible || minimap.alpha <= 0) return "";
            var pending:Array = [minimap], budget:int = 4000, result:Array = [], seen:Object = {};
            while (pending.length && --budget > 0 && result.length < 32)
            {
                var item:DisplayObject = pending.pop() as DisplayObject;
                if (!item || !item.visible || item.alpha <= 0) continue;
                var entry:SimpleAttentionToFlashMinimapEntry = item as SimpleAttentionToFlashMinimapEntry;
                if (entry)
                {
                    var animation:MovieClip = entry.mcAnimation;
                    if (!animation || !animation.visible || animation.alpha <= 0 ||
                        animation.totalFrames <= 1 || animation.currentFrame >= animation.totalFrames) continue;
                    var bounds:Rectangle = animation.getBounds(minimap.stage);
                    if (bounds.width <= 0 || bounds.height <= 0) continue;
                    var x:Number = (bounds.x + bounds.width / 2 - area.x) / area.width;
                    var y:Number = (bounds.y + bounds.height / 2 - area.y) / area.height;
                    if (x < 0 || x > 1 || y < 0 || y > 1) continue;
                    var column:int = Math.min(9, int(x * 10)), row:int = Math.min(9, int(y * 10));
                    var key:String = column + "," + row;
                    if (!seen[key])
                    {
                        seen[key] = true;
                        result.push(((column + .5) / 10) + "," + ((row + .5) / 10));
                    }
                    continue;
                }
                var container:DisplayObjectContainer = item as DisplayObjectContainer;
                if (container) for (var i:int = 0; i < container.numChildren; ++i) pending.push(container.getChildAt(i));
            }
            return result.join(";");
        }

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
