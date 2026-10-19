package driftkings.battle.components.minimap
{
    import flash.display.DisplayObject;
    import flash.display.DisplayObjectContainer;
    import flash.events.Event;
    import flash.events.TimerEvent;
    import flash.geom.Rectangle;
    import flash.utils.Dictionary;
    import flash.utils.Timer;
    import net.wg.gui.battle.views.minimap.BaseMinimap;

    // An opt-in, one-shot training experiment, not the production handoff.
    public class TacticalPresentationTrial
    {
        private static var states:Dictionary = new Dictionary(true);

        public static function command(minimap:BaseMinimap, action:String):String
        {
            if (!minimap) return "unavailable";
            var state:Object = states[minimap];
            if (action == "status") return state ? state.status : "idle";
            if (action == "restore")
            {
                if (state && state.status == "active") restore(state, "restored");
                return state ? state.status : "idle";
            }
            if (action != "start") return "invalid-command";
            if (state) return state.status == "active" ? "active" : "already-tested";
            if (!minimap.stage || !minimap.visible || minimap.alpha <= 0) return "unavailable";
            var source:Object = minimap;
            var background:DisplayObject = source.hasOwnProperty("background") ? source["background"] as DisplayObject : null;
            var entries:DisplayObjectContainer = source.hasOwnProperty("entriesContainer") ? source["entriesContainer"] as DisplayObjectContainer : null;
            var hit:DisplayObject = source.hasOwnProperty("mapHit") ? source["mapHit"] as DisplayObject : null;
            if (!background || !entries || !hit || background.parent != minimap || entries.parent != minimap ||
                hit.parent != minimap || background == entries || background == hit || entries == hit || entries.contains(hit)) return "unsupported-tree";
            var backdrop:DisplayObjectContainer = background as DisplayObjectContainer;
            if (backdrop && backdrop.contains(hit)) return "unsupported-tree";
            var targets:Array = [background, entries];
            for (var i:int = 0; i < minimap.numChildren; ++i)
            {
                var child:DisplayObject = minimap.getChildAt(i);
                if (/^foreground[0-5]$/.test(child.name) || child.name == "minimapHint") targets.push(child);
            }
            state = {status:"preparing", records:[], timer:null, complete:null, removed:null};
            states[minimap] = state;
            try
            {
                for each (var target:DisplayObject in targets)
                {
                    var previous:Rectangle = target.scrollRect;
                    state.records.push({target:target, previous:previous ? previous.clone() : null});
                    target.scrollRect = new Rectangle(0, 0, 0, 0);
                }
                state.complete = function(event:TimerEvent):void { restore(state, "restored"); };
                state.removed = function(event:Event):void {
                    if (event.target == minimap) restore(state, "restored-on-remove");
                };
                state.timer = new Timer(3000, 1);
                state.timer.addEventListener(TimerEvent.TIMER_COMPLETE, state.complete);
                minimap.addEventListener(Event.REMOVED_FROM_STAGE, state.removed);
                // Cleanup retains the owner only during the three-second trial.
                state.detach = function():void { minimap.removeEventListener(Event.REMOVED_FROM_STAGE, state.removed); };
                state.status = "active";
                state.timer.start();
            }
            catch (error:Error) { restore(state, "failed-restored"); }
            return state.status;
        }

        private static function restore(state:Object, status:String):void
        {
            if (state.timer)
            {
                state.timer.stop();
                state.timer.removeEventListener(TimerEvent.TIMER_COMPLETE, state.complete);
            }
            if (state.detach != null) state.detach();
            var failed:Boolean = false;
            for each (var record:Object in state.records)
            {
                try
                {
                    var current:Rectangle = record.target.scrollRect;
                    // Do not overwrite a newer clipping choice made by the client.
                    if (current && current.x == 0 && current.y == 0 && current.width == 0 && current.height == 0)
                        record.target.scrollRect = record.previous;
                }
                catch (error:Error) { failed = true; }
            }
            state.status = failed ? "restore-failed" : status;
            state.records = [];
            state.timer = null; state.complete = null; state.removed = null; state.detach = null;
        }
    }
}
