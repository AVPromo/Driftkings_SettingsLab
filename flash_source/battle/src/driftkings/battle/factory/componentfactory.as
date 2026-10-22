package driftkings.battle.factory
{
    import flash.display.DisplayObject;
    import driftkings.battle.base.battledisplayable;
    import net.wg.gui.battle.views.BaseBattlePage;

    public class componentfactory
    {
        public static function create(host:Object, aliases:Array, surface:String):void
        {
            if (aliases == null || (surface == "battle" && !(host is BaseBattlePage))) return;
            var classes:Object = componentcatalog.classes(surface);
            for each (var alias:String in aliases)
            {
                if (host.isFlashComponentRegisteredS(alias)) continue;
                var type:Class = classes[alias] as Class;
                if (type == null) continue;
                var component:DisplayObject = new type() as DisplayObject;
                var hud:battledisplayable = component as battledisplayable;
                if (hud) hud.battlePage = host as BaseBattlePage;
                host.addChild(component);
                // Preserve the client's verified public DAAPI registration contract.
                host.registerFlashComponentS(component, alias);
            }
        }
    }
}
