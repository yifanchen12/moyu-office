// Exercise the actual scene functions with a small Phaser stand-in. No browser dependency.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../frontend/index.html'), 'utf8');
for (const script of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) {
  if (script[1].trim()) new vm.Script(script[1]);
}
// A touch-capable desktop must still fit the complete 1280x720 office.
const configCode = html.slice(html.indexOf('        const config = {'), html.indexOf('        let totalAssets ='));
const fitContext = {LOCAL_SCENE:true,IS_TOUCH_DEVICE:true,Phaser:{AUTO:0,Scale:{FIT:1,RESIZE:2,CENTER_BOTH:3}},preload(){},create(){},update(){}};
vm.createContext(fitContext);
assert.equal(vm.runInContext(configCode+'config.scale.mode',fitContext),1,'local touch screens must not crop the cat');
const code = html.slice(html.indexOf('        function getAreaRect('), html.indexOf('        function maybeShowGuestBubble('));
const tweens = [];
function object(x, y) {
  return {x, y, handlers:{},
    setOrigin(){return this},setScale(){return this},setDepth(){return this},
    setInteractive(){return this},setFlipX(){return this},setText(){return this},setVisible(){return this},destroy(){this.destroyed=true},
    setPosition(x,y){this.x=x;this.y=y;return this},on(event,handler){this.handlers[event]=handler;return this}};
}
const context = {Math,Map,Set,Date,LOCAL_SCENE:true,LOCAL_CHARACTER_SPECS:{},DEMO_MODE:false,GUEST_AVATARS:[],
  document:{body:{append(){}},createElement(){return {style:{},setAttribute(){},remove(){}}}},
  guestSprites:{},guestTweens:{},guestBubbles:{},localItems:new Map(),characterDialog:null,
  visitors:[{agentId:'local_codex',sourceId:'codex',name:'Codex',state:'executing',area:'breakroom'},
            {agentId:'local_qq',sourceId:'qq',name:'QQ',state:'idle'}],
  game:{time:{now:0},textures:{exists:()=>false},anims:{exists:()=>false},add:{text:object},
    tweens:{add(config){const tween={config,stopped:false,stop(){this.stopped=true}};tweens.push(tween);return tween}}},
};
context.getMergedVisitors = () => context.visitors;
vm.createContext(context);vm.runInContext(code,context);
context.renderGuestAgentsInScene();
const codex = context.guestSprites.local_codex;
assert.equal(codex.area,'writing','fresh executing state must override stale lounge metadata');
const rect = context.getAreaRect('writing');
assert.ok(codex.sprite.x>=rect.x1 && codex.sprite.x<=rect.x2 && codex.sprite.y>=rect.y1 && codex.sprite.y<=rect.y2);
let selected;
context.showCharacterDetails = id => {selected=id};
codex.sprite.handlers.pointerup({getDistance:()=>0},0,0,{stopPropagation(){}});
assert.equal(selected,'codex','click must resolve the stable software ID');
// Fix this movement leg; random floor routing can start with a zero-distance waypoint.
for (const g of Object.values(context.guestSprites)) g.route=[{x:g.sprite.x+10,y:g.sprite.y}];
context.game.time.now=4000;context.updateGuestMovement(4000);
assert.equal(tweens.length,2);
codex.sprite.x+=3;
const position=codex.sprite.x;
context.renderGuestAgentsInScene();context.updateGuestMovement(4100);
assert.equal(codex.sprite.x,position,'a status poll must not snap the character back');
assert.equal(tweens.length,2,'a status poll must not restart walking');
assert.equal(codex.nameText.x,codex.sprite.x,'name follows movement');
// Overlay coordinates must use the render matrix, including its origin offset.
context.game.game={canvas:{getBoundingClientRect:()=>({left:20,top:100,width:2560,height:1440,right:2580,bottom:1540})}};
context.game.scale={width:1280,height:720};
context.game.cameras={main:{scrollX:40,scrollY:20,zoom:1.5,
  matrix:{transformPoint(x,y){return {x:1.5*x-320,y:1.5*y-180}}}}};
context.updateGuestMovement(4200);
assert.equal(parseFloat(codex.labelButton.style.left),20+2*(1.5*(codex.sprite.x-40)-320));
assert.equal(parseFloat(codex.labelButton.style.top),100+2*(1.5*(codex.sprite.y-codex.nameOffset-20)-180));
const workTween=context.guestTweens.local_codex.move;
context.visitors[0].state='idle';context.renderGuestAgentsInScene();
assert.ok(workTween.stopped,'area changes cancel the old movement');
assert.equal(codex.area,'breakroom');
for (const area of ['breakroom','writing','error']) {
  for (let i=0;i<80;i++) {
    const point=context.characterPoint(area,'new');const bounds=context.getAreaRect(area);
    assert.ok(point.x>=bounds.x1 && point.x<=bounds.x2 && point.y>=bounds.y1 && point.y<=bounds.y2);
  }
}
context.visitors.pop();context.renderGuestAgentsInScene();
assert.equal(context.guestSprites.local_qq,undefined,'removed characters clean up');
console.log('Scene syntax, touch-screen FIT, camera labels, state mapping, walking, selection and cleanup: PASS');

// Expanded roaming endpoints and routes must stay on floor, not cross furniture.
for (const area of ['writing','breakroom']) {
  const floors=context.characterFloors(area);
  const inside=p=>floors.some(r=>p.x>=r.x1 && p.x<=r.x2 && p.y>=r.y1 && p.y<=r.y2);
  for (let i=0;i<120;i++) {
    const from=context.characterPoint(area,'new1'),to=context.characterPoint(area,'new2');
    assert.ok(inside(from) && inside(to));
    let previous=from;
    for (const next of context.characterRoute(from,to,area)) {
      for(let step=0;step<=20;step++) assert.ok(inside({x:previous.x+(next.x-previous.x)*step/20,y:previous.y+(next.y-previous.y)*step/20}),'walking must follow clear floor strips');
      previous=next;
    }
  }
}
// The hearth is a reachable lounge destination, including the narrow table-side approach.
const loungeFloors=context.characterFloors('breakroom');
const loungeInside=p=>loungeFloors.some(r=>p.x>=r.x1 && p.x<=r.x2 && p.y>=r.y1 && p.y<=r.y2);
const hearth={x:670,y:266};
assert.ok(loungeInside(hearth),'fireplace foreground is walkable');
for (const [from,to] of [[{x:700,y:610},hearth],[hearth,{x:890,y:350}],[hearth,{x:600,y:600}],[{x:558,y:400},hearth]]) {
 let previous=from;
 for (const next of context.characterRoute(from,to,'breakroom')) {
  for (let step=0;step<=60;step++) assert.ok(loungeInside({x:previous.x+(next.x-previous.x)*step/60,y:previous.y+(next.y-previous.y)*step/60}),'hearth routes must go around the coffee table and sofa');
  previous=next;
 }
 assert.deepEqual(previous,to);
}
const narrow=loungeFloors.find(r=>r.x2-r.x1<36);
for (let i=0;i<30;i++) {
 const point=context.randomPointInRect(narrow);
 assert.ok(point.x>=narrow.x1 && point.x<=narrow.x2 && point.y>=narrow.y1 && point.y<=narrow.y2,'padding must fit narrow floor strips');
}
for (const [from,to,area] of [[hearth,{x:400,y:600},'writing'],[{x:400,y:600},hearth,'breakroom'],[hearth,{x:1000,y:320},'error']]) {
 const route=context.characterRoute(from,to,area);
 assert.equal(route.at(-1).x,to.x);assert.equal(route.at(-1).y,to.y);
 assert.ok(route.some(p=>p.x===558),'cross-state movement uses the hearth approach');
}
console.log('Hearth reachability, furniture detours, narrow-strip sampling and cross-state routes: PASS');
// The animated sofa cat is decor and remains visible through program-state changes.
const catContext={LOCAL_SCENE:true,window:{},IDLE_STAR_SCALE:1,IDLE_SOFA_ANCHOR:{x:798,y:272},serverroom:null,syncAnimSprite:null,
 star:{setVisible(v){this.visible=v},setScale(){},setPosition(x,y){this.x=x;this.y=y},anims:{play(key){catContext.animation=key}}},
 sofa:{anims:{stop(){}},setTexture(){}}};
vm.createContext(catContext);
vm.runInContext(html.slice(html.indexOf('        function applyVisualState('),html.indexOf('        function fetchStatus(')),catContext);
for (const state of ['idle','writing','error','syncing']) {
 catContext.applyVisualState(state);assert.equal(catContext.star.visible,true);assert.equal(catContext.animation,'star_idle');
 assert.equal(catContext.star.x,798);assert.equal(catContext.star.y,272);
}
console.log('Expanded floor endpoints/routes and persistent sofa cat: PASS');

// Custom art uses stable software IDs and changes animation with actual movement.
const specStart=html.indexOf('        const LOCAL_CHARACTER_SPECS =');
const specs=vm.runInContext(html.slice(specStart,html.indexOf('        const IS_TOUCH_DEVICE =',specStart))+'LOCAL_CHARACTER_SPECS',context);
context.LOCAL_CHARACTER_SPECS=specs;
context.guestSprites={};context.guestTweens={};
context.visitors=Object.keys(specs).map(id=>({agentId:'local_'+id,sourceId:id,name:id,state:'idle'}));
context.game.textures.exists=key=>Object.values(specs).some(s=>s.key===key);
context.game.anims.exists=()=>true;
context.game.add.sprite=(x,y)=>{const o=object(x,y);o.anims={play(key){o.animation=key}};return o};
context.renderGuestAgentsInScene();
for (const [id,spec] of Object.entries(specs)) {
 const g=context.guestSprites['local_'+id];assert.equal(g.animPrefix,spec.key);assert.equal(g.sprite.animation,spec.key+'_idle');
 g.route=[{x:g.sprite.x+10,y:g.sprite.y}];
}
context.updateGuestMovement(context.game.time.now+5000);
for (const [id,spec] of Object.entries(specs)) {
 const g=context.guestSprites['local_'+id];assert.equal(g.sprite.animation,spec.key+'_walk');
 const tween=context.guestTweens['local_'+id].move;g.route=[];tween.config.onComplete();
 assert.equal(g.sprite.animation,spec.key+'_idle');
 const sprite=g.sprite;context.renderGuestAgentsInScene();assert.equal(g.sprite,sprite,'polls retain custom sprite identity');
}
console.log('Custom software identities, idle/walk switching and poll stability: PASS');
