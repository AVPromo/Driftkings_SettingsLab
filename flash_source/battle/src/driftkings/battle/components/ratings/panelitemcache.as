package driftkings.battle.components.ratings
{
    /** Internal discovery state; items retain the native display objects. */
    internal class panelitemcache
    {
        public var items:Array;
        public var mode:String;
        public var time:int;

        public function panelitemcache(items:Array, mode:String, time:int)
        {
            this.items=items;
            this.mode=mode;
            this.time=time;
        }
    }
}
