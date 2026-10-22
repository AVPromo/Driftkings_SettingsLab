package driftkings.battle.components.minimap
{
    import flash.display.DisplayObject;
    import flash.text.TextField;
    import flash.text.TextFormat;
    import flash.utils.Dictionary;

    /** Native display properties changed by the minimap, restored on settings change or dispose. */
    public class nativestyles
    {
        private var styles:Dictionary = new Dictionary(true);

        public function remember(target:DisplayObject):Object
        {
            if (!styles[target])
                styles[target] = {alpha:target.alpha, color:target.transform.colorTransform, filters:target.filters,
                    sx:target.scaleX, sy:target.scaleY, size:target is TextField ? TextField(target).defaultTextFormat.size : null};
            return styles[target];
        }

        public function restore():void
        {
            for (var key:Object in styles)
            {
                var target:DisplayObject = key as DisplayObject;
                var saved:Object = styles[key];
                target.alpha = saved.alpha;
                if (saved.filtersChanged) target.filters = saved.filters;
                if (saved.scaleChanged) { target.scaleX = saved.sx; target.scaleY = saved.sy; }
                target.transform.colorTransform = saved.color;
                if (target is TextField && saved.size != null)
                {
                    var field:TextField = target as TextField;
                    var format:TextFormat = field.getTextFormat();
                    format.size = saved.size;
                    field.setTextFormat(format);
                    field.defaultTextFormat = format;
                }
            }
            styles = new Dictionary(true);
        }
    }
}
