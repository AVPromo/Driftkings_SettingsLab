package driftkings.battle.components.ratings
{
    import flash.display.DisplayObject;
    import flash.display.DisplayObjectContainer;
    import flash.events.Event;
    import flash.utils.Dictionary;
    import flash.utils.getTimer;

    // Finds the native player rows of a panel list and caches them per list.
    public class PanelItems
    {
        private var itemCache:Dictionary=new Dictionary(true);
        private var watchedLists:Dictionary=new Dictionary(true);

        public function find(list:DisplayObjectContainer,mode:String):Array
        {
            var cached:PanelItemCache=itemCache[list];
            // ADDED/REMOVED invalidate membership immediately, but native rows
            // may initialise their identifying fields without a display event.
            // Retain the one-second scan to discover those late-bound rows.
            if (isStale(list,cached,mode,getTimer()))
                cached=discover(list,mode);
            return cached.items;
        }
        public function reset():void
        {
            for (var target:Object in watchedLists)
            {
                var list:DisplayObjectContainer=target as DisplayObjectContainer;
                list.removeEventListener(Event.ADDED,childrenChanged);
                list.removeEventListener(Event.REMOVED,childrenChanged);
            }
            watchedLists=new Dictionary(true);
            itemCache=new Dictionary(true);
        }
        private function childrenChanged(event:Event):void
        {
            var cached:PanelItemCache=itemCache[event.currentTarget];
            if (cached) cached.time=-1000;
        }
        private function watch(list:DisplayObjectContainer):void
        {
            if (watchedLists[list]) return;
            list.addEventListener(Event.ADDED,childrenChanged,false,0,true);
            list.addEventListener(Event.REMOVED,childrenChanged,false,0,true);
            watchedLists[list]=true;
        }
        private function isStale(list:DisplayObjectContainer,cached:PanelItemCache,mode:String,now:int):Boolean
        {
            if (!cached || cached.mode!==mode || now-cached.time>=1000) return true;
            for each (var item:DisplayObject in cached.items)
                if (!item.stage || !list.contains(item)) return true;
            return false;
        }
        private function discover(list:DisplayObjectContainer,mode:String):PanelItemCache
        {
            watch(list);
            var items:Array=[];
            collect(list,items);
            var cached:PanelItemCache=new PanelItemCache(items,mode,getTimer());
            itemCache[list]=cached;
            return cached;
        }
        private function collect(node:DisplayObjectContainer,items:Array):void
        {
            if (!node) return;
            for (var i:int=0;i<node.numChildren;++i)
            {
                var child:DisplayObject=node.getChildAt(i);
                if ("playerNameFullTF" in child && "vehicleTF" in child && "holderItemID" in child)
                    items.push(child);
                else if (child is DisplayObjectContainer) collect(child as DisplayObjectContainer,items);
            }
        }
    }
}
