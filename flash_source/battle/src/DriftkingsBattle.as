package {
import driftkings.battle.factory.ComponentFactory;
import driftkings.battle.components.minimap.TacticalGeometry;
import net.wg.gui.battle.views.minimap.BaseMinimap;
import net.wg.gui.battle.views.BaseBattlePage;
import net.wg.infrastructure.base.AbstractView;

// One library, with a separate factory contract for each root surface.
public class DriftkingsBattle extends AbstractView {
    private static function registerCreators():void {
        BaseMinimap.prototype.as_DriftkingsMinimapGeometry = function(includePlayer:Boolean = false):String {
            var data:Object = TacticalGeometry.capture(this as BaseMinimap);
            if (!data.available) return "0|" + data.reason;
            var result:Array = ["1", data.x, data.y, data.width, data.height, data.stageWidth, data.stageHeight];
            if (includePlayer) {
                var own:Object = TacticalGeometry.player(this as BaseMinimap, data);
                if (own) result.push(own.x, own.y, own.heading);
            }
            return result.join("|");
        };
        BaseBattlePage.prototype.as_DriftkingsCreate = function(aliases:Array):void {
            ComponentFactory.create(this, aliases, "battle");
            this.updateStage(App.appWidth, App.appHeight);
        };
        AbstractView.prototype.as_DriftkingsCreateRatings = function(aliases:Array):void {
            ComponentFactory.create(this, aliases, "ratings");
        };
    }

    { registerCreators(); }

    public function DriftkingsBattle() {
        super();
        registerCreators();
    }
}
}
