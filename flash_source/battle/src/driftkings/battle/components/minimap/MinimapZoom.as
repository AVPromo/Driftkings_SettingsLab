package driftkings.battle.components.minimap
{
    import flash.display.DisplayObjectContainer;
    import net.wg.gui.battle.views.minimap.BaseMinimap;
    import net.wg.infrastructure.events.LifeCycleEvent;

    /** Alternative-mode zoom: enlarge and reposition the native minimap, then restore it. */
    public class MinimapZoom
    {
        private var zoomed:Boolean = false;
        private var original:MinimapZoomState;
        private var lastWidth:Number = 0;
        private var lastHeight:Number = 0;

        public function MinimapZoom()
        {
            lastWidth = App.appWidth;
            lastHeight = App.appHeight;
        }

        public function apply(minimap:BaseMinimap, page:DisplayObjectContainer, active:Boolean, options:Object):void
        {
            if (!minimap) return;
            if (active)
            {
                if (!zoomed)
                    original = new MinimapZoomState(minimap, page.getChildIndex(minimap));
                zoomed = true;
                minimap.setAllowedSizeIndex(Number(options.sizeIndex));
                var scale:Number = Math.max(1, Math.min(3, Number(options.scale)));
                // Keep the full map on screen even on smaller resolutions.
                scale = Math.min(scale, App.appWidth / Math.max(1, minimap.currentWidth),
                                App.appHeight / Math.max(1, minimap.currentHeight));
                minimap.scaleX = minimap.scaleY = scale;
                if (options.center)
                {
                    minimap.x = (App.appWidth - minimap.currentWidth * scale) * .5;
                    minimap.y = (App.appHeight - minimap.currentHeight * scale) * .5;
                }
                else
                {
                    minimap.x = App.appWidth - minimap.currentWidth * scale;
                    minimap.y = App.appHeight - minimap.currentHeight * scale;
                }
                page.setChildIndex(minimap, page.numChildren - 1);
            }
            else if (zoomed)
            {
                zoomed = false;
                minimap.scaleX = original.sx;
                minimap.scaleY = original.sy;
                minimap.setAllowedSizeIndex(original.size);
                minimap.x = original.x;
                minimap.y = original.y;
                page.setChildIndex(minimap, Math.min(original.index, page.numChildren - 1));
                original = null;
            }
            minimap.dispatchEvent(new LifeCycleEvent(LifeCycleEvent.ON_GRAPHICS_RECTANGLES_UPDATE));
        }

        // The restored position follows the screen edge after a resolution change.
        public function resized(minimap:BaseMinimap, page:DisplayObjectContainer, options:Object):void
        {
            if (zoomed)
            {
                original.x += App.appWidth - lastWidth;
                original.y += App.appHeight - lastHeight;
                apply(minimap, page, true, options);
            }
            lastWidth = App.appWidth;
            lastHeight = App.appHeight;
        }
    }
}
