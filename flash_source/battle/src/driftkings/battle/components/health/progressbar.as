package driftkings.battle.components.health
{
    import driftkings.utils.utils;
    import driftkings.utils.textext;
    import driftkings.utils.constants;
	
	import flash.display.*;
	import flash.text.*;
	import driftkings.utils.tween.tween;

	public class progressbar extends Sprite
	{
		private var bar:Shape            = new Shape();
		private var outline:Shape        = new Shape();
		private var uiText:textext       = null;
		private var animation:tween      = null;
		private var barColor:uint        = 0;
		private var animationTime:Number = 1.0;
		private var barEnabled:Boolean   = true;
		
		public function progressbar(x:Number, y:Number, width:Number, height:Number, color:String, bgColor:String = "#000000", time:Number = 1.0)
		{
			super();
			if (bgColor == null)
			{
				bgColor = "#000000";
			}
			this.animationTime = time;
			this.x = x;
			this.y = y;
			if (width == 0 || height == 0)
			{
				this.barEnabled = false;
			}
			else
			{
				this.barColor = utils.colorConvert(color);
				this.graphics.beginFill(utils.colorConvert(bgColor), constants.BG_ALPHA);
				this.graphics.drawRect(0, 0, width, height);
				this.graphics.endFill();
				this.bar.graphics.beginFill(this.barColor, constants.ALPHA);
				this.bar.graphics.drawRect(0, 0, width, height);
				this.bar.graphics.endFill();
				this.addChild(this.bar);
				if (this.animationTime > 0)
				{
					this.animation = new tween(this.bar, "scaleX", 1.0, 0, this.animationTime);
				}
			}
		}
		
		public function setNewScale(newScale:Number):void
		{
			if (this.barEnabled && this.bar.scaleX != newScale)
			{
				var scale:Number = Math.max(0, newScale);
				if (this.animationTime > 0)
				{
					this.animation.continueTo(scale, this.visible ? this.animationTime : constants.HUNDREDTH);
				}
				else
				{
					this.bar.scaleX = scale;
				}
			}
		}
		
		public function setText(text:String):void
		{
			this.uiText.htmlText = text;
		}
		
		public function addTextField(x:Number, y:Number, align:String, format:TextFormat):void
		{
			this.uiText = new textext(x, y, format, align, this);
		}
		
		public function setOutline(width:Number = 0, height:Number = 0):void
		{
			if (this.barEnabled)
			{
				this.outline.graphics.lineStyle(1, this.barColor, constants.ALPHA, true, LineScaleMode.NONE);
				this.outline.graphics.drawRect(-1, -1, width + 1, height + 1);
				this.addChild(this.outline);
			}
		}
		
		public function setVisible(vis:Boolean):void
		{
			if (this.barEnabled)
			{
				var active:Boolean = vis && this.bar.scaleX > 0;
				if (this.visible != active)
				{
					this.visible = active;
				}
			}
			else
			{
				this.visible = vis;
			}
		}
		
		public function updateColor(color:String):void
		{
			if (this.barEnabled)
			{
				utils.updateColor(this.bar, color);
				if (this.outline)
				{
					utils.updateColor(this.outline, color);
				}
			}
		}
		
		public function remove():void
		{
			this.removeChildren();
			this.bar = null;
			this.outline = null;
			this.uiText = null;
			if (this.animation)
			{
				this.animation.dispose();
				this.animation = null;
			}
		}
	}
}