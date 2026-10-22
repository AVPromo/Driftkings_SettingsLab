package driftkings.battle.components.ratings
{
    import flash.utils.getTimer;

    // Diagnostics: per-frame timings, reported every five seconds while enabled.
    public class frameprofiler
    {
        public var scans:int=0, search:int=0, panel:int=0, table:int=0, cleanup:int=0;
        public var drawn:int=0, reused:int=0;
        private var start:int=0, frames:int=0, time:int=0, max:int=0;

        public function finish(now:int,enabled:Boolean,report:Function):void
        {
            if (!enabled) { reset(now); return; }
            var elapsed:int=getTimer()-now;
            ++frames; time+=elapsed; max=Math.max(max,elapsed);
            if (now-start>=5000 && report!=null)
            {
                report("frames="+frames+" avg="+(time/frames).toFixed(2)+"ms max="+max+"ms scans="+scans+
                    " search="+(search/frames).toFixed(2)+"ms panel="+(panel/frames).toFixed(2)+
                    "ms table="+(table/frames).toFixed(2)+"ms cleanup="+(cleanup/frames).toFixed(2)+
                    "ms rowsDrawn="+drawn+" rowsReused="+reused);
                reset(now);
            }
        }
        private function reset(now:int):void
        {
            start=now; frames=time=max=scans=0;
            search=panel=table=cleanup=drawn=reused=0;
        }
    }
}
