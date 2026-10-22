package driftkings.battle.components.flight_timer
{
	import flash.events.Event;
    import driftkings.utils.constants;
    import driftkings.utils.align;
    import driftkings.utils.textext;
    import driftkings.battle.base.battledisplayable;

    public class flighttimerui extends battledisplayable
    {
        private var flightTime:textext;
        private var pendingText:String = "";
        private var alignX:String = align.CENTER;
        private var alignY:String = align.CENTER;

        public var getSettings:Function;

        public function flighttimerui()
        {
            super();
            this.tabEnabled = false;
            this.tabChildren = false;
            this.mouseEnabled = false;
            this.mouseChildren = false;
            this.buttonMode = false;
            this.addEventListener(Event.RESIZE, onResizeHandle);
        }

        override protected function onPopulate():void 
        {
            super.onPopulate();
            if (this.getSettings != null)
            {
                var settings:Object = this.getSettings();
                if (settings != null)
				{
                    this.alignX = settings.alignX || align.CENTER;
                    this.alignY = settings.alignY || align.CENTER;
                    this.flightTime = new textext(settings.x, settings.y, constants.middleText, settings.align, this);
                    this.flightTime.htmlText = this.pendingText;
                    this.updatePosition();
                }
            }
        }

        override protected function onBeforeDispose():void 
        {
            super.onBeforeDispose();
            this.flightTime = null;
            this.pendingText = "";
            this.removeEventListener(Event.RESIZE, onResizeHandle);
        }

        private function updatePosition() : void
        {
            align.position(this, App.appWidth, App.appHeight, this.alignX, this.alignY);
        }

        public function as_onCrosshairPositionChanged(x:Number, y:Number):void
        {
            this.x = x;
            this.y = y;
        }

        private function onResizeHandle(event:Event) : void
        {
            this.updatePosition();
        }

        public function as_flightTime(text:String):void
        {
            this.pendingText = text;
            if (this.flightTime != null)
            {
                this.flightTime.htmlText = text;
            }
        }
    }
}
