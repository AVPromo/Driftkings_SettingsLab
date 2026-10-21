// Generated from Driftkings/interface_catalog.py; regenerate with generate_ui_catalog.py --write.
package driftkings.battle.factory
{
    import driftkings.battle.components.armor_calculator.ArmorCalculatorUI;
    import driftkings.battle.components.dispersion_timer.DispersionTimerUI;
    import driftkings.battle.components.distance_marker.DistanceMarkerUI;
    import driftkings.battle.components.flight_timer.FlightTimerUI;
    import driftkings.battle.components.health.OwnHealthUI;
    import driftkings.battle.components.minimap.MinimapEnhancementsUI;
    import driftkings.battle.components.overlay.OverlayUI;
    import driftkings.battle.components.ratings.RatingScreens;
    import driftkings.battle.components.sixth_sense.SixthSenseUI;

    public class ComponentCatalog
    {
        public static function classes(surface:String):Object
        {
        if (surface == "battle") return {
                ArmorCalculatorView:ArmorCalculatorUI,
                DispersionTimerView:DispersionTimerUI,
                DistanceMarkerView:DistanceMarkerUI,
                DriftkingsOverlay:OverlayUI,
                DriftkingsRatingScreens:RatingScreens,
                FlightTimerView:FlightTimerUI,
                MinimapEnhancementsView:MinimapEnhancementsUI,
                OwnHealthView:OwnHealthUI,
                SixthSenseView:SixthSenseUI
            };
        if (surface == "ratings") return {
                DriftkingsRatingScreens:RatingScreens
            };
            return {};
        }
    }
}
