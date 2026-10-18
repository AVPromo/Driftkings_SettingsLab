package driftkings.battle.components.ratings
{
    /** Internal discovery state; items retain the native display objects. */
    internal class PanelItemCache
    {
        public var items:Array;
        public var mode:String;
        public var time:int;

        public function PanelItemCache(items:Array, mode:String, time:int)
        {
            this.items=items;
            this.mode=mode;
            this.time=time;
        }
    }
}
