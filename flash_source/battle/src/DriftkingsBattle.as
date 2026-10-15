package {
import driftkings.battle.factory.ComponentFactory;
import net.wg.gui.battle.views.BaseBattlePage;
import net.wg.infrastructure.base.AbstractView;

// One library, with a separate factory contract for each root surface.
public class DriftkingsBattle extends AbstractView {
    private static function registerCreators():void {
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
