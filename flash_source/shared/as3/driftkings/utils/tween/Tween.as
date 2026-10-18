package driftkings.utils.tween
{
	import flash.events.EventDispatcher;
	import flash.events.TimerEvent;
	import flash.utils.Timer;
	import flash.utils.getTimer;
	
	[Event(name = "motionStop", type = "driftkings.utils.tween.TweenEvent")]
	[Event(name = "motionStart", type = "driftkings.utils.tween.TweenEvent")]
	[Event(name = "motionResume", type = "driftkings.utils.tween.TweenEvent")]
	[Event(name = "motionLoop", type = "driftkings.utils.tween.TweenEvent")]
	[Event(name = "motionFinish", type = "driftkings.utils.tween.TweenEvent")]
	[Event(name = "motionChange", type = "driftkings.utils.tween.TweenEvent")]
	public class Tween extends EventDispatcher
	{
		private var _position:Number  = NaN;
		public var prevTime:Number    = NaN;
		public var prevPos:Number     = NaN;
		public var isPlaying:Boolean  = false;
		private var _fps:Number       = 30;
		private var _time:Number      = 0;
		public var begin:Number       = NaN;
		public var change:Number      = NaN;
		public var looping:Boolean    = false;
		private var _timer:Timer      = null;
		private var disposed:Boolean = false;
		private var _startTime:Number = NaN;
		public var prop:String        = "";
		private var _duration:Number  = NaN;
		public var obj:Object         = null;
		
		public function Tween(obj:Object, prop:String, begin:Number, finish:Number, duration:Number = 1.0)
		{
			super();
			if (!arguments.length)
			{
				return;
			}
			this.obj = obj;
			this.prop = prop;
			this.begin = begin;
			this.position = begin;
			this.duration = duration;
			this.finish = finish;
			this._timer = new Timer(100);
		}
		
		public function continueTo(finish:Number, duration:Number):void
		{
			if (this.disposed) return;
			this.begin = this.position;
			this.finish = finish;
			if (!isNaN(duration))
			{
				this.duration = duration;
			}
			this.start();
		}
		
		protected function startTimer():void
		{
			if (this.disposed || this._timer == null) return;
			this._timer.delay = 1000 / this._fps;
			// Keep the running tween alive until stopTimer removes the listener.
			this._timer.removeEventListener(TimerEvent.TIMER, this.timerHandler);
			this._timer.addEventListener(TimerEvent.TIMER, this.timerHandler);
			this._timer.start();
			this.isPlaying = true;
		}
		
		public function stop():void
		{
			if (this.disposed) return;
			this.stopTimer();
			this.dispatchEvent(new TweenEvent(TweenEvent.MOTION_STOP, this._time, this._position));
		}
		
		public function dispose():void
		{
			this.disposed = true;
			this.stopTimer();
			this._timer = null;
			this.obj = null;
		}

		private function fixTime():void
		{
			this._startTime = getTimer() - this._time * 1000;
		}
		
		public function get finish():Number
		{
			return this.begin + this.change;
		}
		
		public function get duration():Number
		{
			return this._duration;
		}
		
		protected function stopTimer():void
		{
			if (this._timer != null)
			{
				this._timer.stop();
				this._timer.removeEventListener(TimerEvent.TIMER, this.timerHandler);
			}
			this.isPlaying = false;
		}
		
		public function set time(t:Number):void
		{
			if (this.disposed) return;
			this.prevTime = this._time;
			if (t > this.duration)
			{
				if (this.looping)
				{
					this.rewind(t - this._duration);
					this.update();
					this.dispatchEvent(new TweenEvent(TweenEvent.MOTION_LOOP, this._time, this._position));
				}
				else
				{
					this._time = this._duration;
					this.update();
					this.stop();
					this.dispatchEvent(new TweenEvent(TweenEvent.MOTION_FINISH, this._time, this._position));
				}
			}
			else if (t < 0)
			{
				this.rewind();
				this.update();
			}
			else
			{
				this._time = t;
				this.update();
			}
		}
		
		public function getPosition(t:Number = NaN):Number
		{
			if (isNaN(t))
			{
				t = this._time;
			}
			return this.change * t / this._duration + this.begin;
		}
		
		public function set finish(value:Number):void
		{
			this.change = value - this.begin;
		}
		
		public function set duration(d:Number):void
		{
			this._duration = d <= 0 ? Number(Infinity) : Number(d);
		}
		
		public function get position():Number
		{
			return this.getPosition(this._time);
		}
		
		public function setPosition(p:Number):void
		{
			if (this.disposed) return;
			this.prevPos = this._position;
			if (this.prop.length)
			{
				this.obj[this.prop] = this._position = p;
			}
			this.dispatchEvent(new TweenEvent(TweenEvent.MOTION_CHANGE, this._time, this._position));
		}
		
		public function resume():void
		{
			if (this.disposed) return;
			this.fixTime();
			this.startTimer();
			this.dispatchEvent(new TweenEvent(TweenEvent.MOTION_RESUME, this._time, this._position));
		}
		
		public function fforward():void
		{
			if (this.disposed) return;
			this.time = this._duration;
			this.fixTime();
		}
		
		public function yoyo():void
		{
			this.continueTo(this.begin, this.time);
		}
		
		public function nextFrame():void
		{
			if (this.disposed) return;
			this.time = (getTimer() - this._startTime) / 1000;
		}
		
		protected function timerHandler(timerEvent:TimerEvent):void
		{
			this.nextFrame();
			timerEvent.updateAfterEvent();
		}
		
		public function rewind(t:Number = 0):void
		{
			if (this.disposed) return;
			this._time = t;
			this.fixTime();
			this.update();
		}
		
		public function set position(p:Number):void
		{
			this.setPosition(p);
		}
		
		public function get time():Number
		{
			return this._time;
		}
		
		private function update():void
		{
			this.setPosition(this.getPosition(this._time));
		}
		
		public function start():void
		{
			if (this.disposed) return;
			this.rewind();
			this.startTimer();
			this.dispatchEvent(new TweenEvent(TweenEvent.MOTION_START, this._time, this._position));
		}
	}
}
