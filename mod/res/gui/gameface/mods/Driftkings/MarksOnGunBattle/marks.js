(function () {
    'use strict';
    var K=window.__dkMarksKit, root=K.node('div','dk-mog dk-mog--compact',document.body);
    var header=K.node('div','dk-mog__header',root), brand=K.node('div','dk-mog__brand',header);
    K.node('span','dk-mog__logo',brand,'///'); var title=K.node('span','',brand,'');
    var context=K.node('span','dk-mog__context',header);
    var overview=K.node('div','dk-mog__overview',root);
    var hero=K.node('div','dk-mog__hero',overview), main=K.node('div','',hero);
    var estimatedLabel=K.node('div','dk-mog__label',main), estimated=K.node('div','dk-mog__percent',main);
    var starRow=K.node('div','',hero), stars=K.stars(starRow);
    var unavailable=K.node('div','dk-mog__unavailable',root);
    var metrics=K.node('div','dk-mog__metrics',overview), cards=[];
    ['combined','target','needed'].forEach(function(key){
        var card=K.node('div','dk-mog__metric',metrics);
        cards.push({root:card,label:K.node('div','dk-mog__label',card),value:K.node('span','dk-mog__value',card)});
    });
    var progress=K.node('div','',root), bar=K.node('div','dk-mog__bar',progress), fill=K.node('div','dk-mog__fill',bar);
    var next=K.node('div','dk-mog__next',progress), nextLabel=K.node('span','',next), gap=K.node('span','',next);
    var footer=K.node('div','dk-mog__footer',root), current=K.node('span','',footer), trend=K.node('span','dk-mog__trend',footer);
    function render(data) {
        var cfg=data.config||{}, valid=data.state==='data', accent=K.theme(root,cfg,true);
        var interactive=cfg.draggable===true && cfg.locked===false;
        K.style(root,'zIndex','10000');
        K.style(root,'pointerEvents',interactive?'auto':'none');
        K.style(root.firstChild,'pointerEvents',interactive?'auto':'none');
        K.style(root.firstChild,'cursor',interactive?'move':'default');
        K.text(title,K.label(data,'title','Marks of Excellence'));
        K.text(context,K.label(data,'battle','IN BATTLE'));
        K.text(estimatedLabel,K.label(data,'estimated','Estimated mark'));
        K.text(estimated,valid?K.percent(data.estimatedMark):'\u2014'); K.style(estimated,'color',accent);
        K.show(starRow,cfg.showStars!==false); K.updateStars(stars,data.marksAchieved||0);
        K.show(unavailable,!valid); K.text(unavailable,K.label(data,'unavailable','No reliable marks data available'));
        ['combined','target','needed'].forEach(function(key,i){ K.text(cards[i].label,K.label(data,key,key)); });
        K.text(cards[0].value,K.formatted(data.combinedDamage));
        K.text(cards[1].value,valid?K.formatted(data.targetDamage):'\u2014'); K.text(cards[2].value,valid?K.formatted(data.damageNeeded):'\u2014');
        K.style(cards[2].value,'color',accent);
        K.show(cards[0].root,cfg.showCombined!==false); K.show(cards[1].root,cfg.showTargetDamage!==false); K.show(cards[2].root,cfg.showRequiredDamage!==false);
        K.show(metrics,cfg.showCombined!==false||cfg.showTargetDamage!==false||cfg.showRequiredDamage!==false);
        K.show(progress,valid&&cfg.showProgress!==false); K.style(fill,'width',(K.number(data.progress,0)*100)+'%');
        K.style(fill,'backgroundImage','linear-gradient(0deg,'+accent+',#fff1ab)');
        K.text(nextLabel,data.completed?K.label(data,'completed','Three marks achieved'):K.label(data,'next','Next mark')+' '+data.nextMilestone+'%');
        K.text(gap,data.completed?'':K.formatted(data.gap,2)+' pp');
        K.text(current,K.label(data,'current','Consolidated mark')+': '+K.percent(data.currentMark));
        K.text(trend,(data.trend||{}).text||'\u2014'); trend.className='dk-mog__trend dk-mog__trend--'+((data.trend||{}).direction||'unknown');
        K.show(trend,valid&&cfg.showTrend!==false);
    }
    K.connect('DriftkingsMarksOnGunBattle','__dkBattleMarks',root,render,K.position,K.savedPosition);
}());
