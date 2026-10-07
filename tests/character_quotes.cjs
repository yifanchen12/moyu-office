const assert = require('node:assert/strict');
const {characters, status, transition, createDirector} = require('../frontend/character-quotes.js');
const wall = Date.parse('2026-10-07T12:00:00Z');
const item = (id, state = 'idle', metrics = {}, available = true) => ({id, state, metrics, available});
const stage = (id, before, after) => transition(id, status(id, before), status(id, after));
assert.equal(Object.keys(characters).length, 12);
const lines = Object.values(characters).flatMap(character => Object.values(character.lines).flat());
assert.equal(lines.length, 234);
assert.equal(new Set(lines).size, 234, 'all dialogue is character-specific');
assert.equal(stage('codex', item('codex', 'executing'), item('codex')), 'settled', 'idle cannot prove success');
assert.equal(stage('comfyui', item('comfyui', 'executing'), item('comfyui')), 'settled');
assert.equal(stage('sra', item('sra', 'executing'), item('sra', 'idle', {phase:'paused'})), 'paused');
assert.equal(stage('quark', item('quark'), item('quark', 'syncing')), 'activity');
assert.equal(stage('system', item('system', 'idle', {cpu_percent:90}), item('system', 'idle', {cpu_percent:25})), 'recovered');
for (const value of [null, '90', NaN, Infinity, -1, 101]) assert.equal(status('system', item('system', 'idle', {cpu_percent:value})).stage, 'unavailable');
assert.equal(status('codex', item('codex', 'mystery')).stage, 'unavailable');
assert.equal(status('codex', item('codex', 'executing', {}, false)).stage, 'unavailable');
const training = current => item('training', 'executing', {current,total:100,percent:100});
assert.equal(stage('training', training(95), training(99.99)), null, 'rounded percentage cannot prove completion');
assert.equal(stage('training', training(99.99), training(100)), 'completed');
assert.equal(stage('training', training(100), training(100)), null);
assert.equal(status('training', item('training', 'executing', {current:1,total:0})).percent, null);

// First snapshot seeds history; normal activity still gets rotating dialogue.
const d = createDirector();
d.observe([item('codex','executing')], 0, wall);
assert.equal(d.next(7999,{ids:['codex']}), null);
const first = d.next(8000,{ids:['codex']});
assert.equal(first.stage, 'working');
d.observe([item('codex','executing')], 16000, wall+16000);
assert.equal(d.next(16000,{ids:['codex']}), null, 'same-character cooldown');
d.observe([item('codex','executing')], 43000, wall+43000);
const second = d.next(43000,{ids:['codex']});
assert.equal(second.stage, 'working');
assert.notEqual(first.text, second.text, 'ongoing work rotates without repeated polls triggering start');
d.observe([item('codex','error')], 44000, wall+44000);
assert.equal(d.next(50000,{ids:['codex']}), null, 'urgent events still obey global interval');
d.observe([item('codex','error')], 51000, wall+51000);
assert.equal(d.next(51000,{ids:['codex']}).stage, 'error');
assert.equal(d.next(59000,{ids:['codex']}), null, 'retained error is not a new event');
d.observe([item('codex','idle')], 60000, wall+60000);
assert.equal(d.next(60000,{ids:['codex']}).stage, 'recovered');
assert.equal(d.next(80000,{ids:['codex']}), null, 'stale connection stops dialogue');

// Alert high-water marks survive null values and reconnects; old notifications are never replayed.
const n = createDirector();
const message = offset => item('qq','syncing',{last_alert_at:offset === null ? null : new Date(wall+offset).toISOString()});
n.observe([message(-1000)],0,wall);
assert.equal(n.next(8000,{ids:['qq']}).stage,'idle');
n.observe([message(10000)],10000,wall+10000);
assert.equal(n.next(16000,{ids:['qq']}).stage,'notice');
n.observe([message(null)],17000,wall+17000);
n.observe([message(10000)],18000,wall+18000);
assert.equal(n.next(24000,{ids:['qq']}),null);
n.observe([message(20000)],90000,wall+90000);
assert.equal(n.next(90000,{ids:['qq']}).stage,'idle','old alert cannot trigger notice');
n.observe([message(91000)],91000,wall+91000);
n.observe([message(91000)],92000,wall+92000);
assert.equal(n.next(98000,{ids:['qq']}).stage,'notice');

// No paused-dialog backlog, and superseded start/progress events cannot speak after stopping.
const p = createDirector();
p.observe([item('sra')],0,wall);
p.observe([item('sra','executing')],1000,wall+1000);
assert.equal(p.next(8000,{paused:true,ids:['sra']}),null);
p.observe([item('sra','executing')],30000,wall+30000);
assert.equal(p.next(30000,{ids:['sra']}).stage,'working','expired start is dropped');
p.observe([item('sra','idle')],31000,wall+31000);
p.observe([item('sra','error')],32000,wall+32000);
assert.equal(p.next(38000,{ids:['sra']}).stage,'error','only latest applicable event survives');
const t = createDirector();
t.observe([training(99.99)],0,wall);
assert.match(t.next(8000,{ids:['training']}).text,/99\.9%/);
t.observe([training(100)],9000,wall+9000);
assert.equal(t.next(16000,{ids:['training']}).stage,'completed');

// Fair rotation includes idle/offline characters while another role keeps working.
const f = createDirector();
const snapshot = Object.keys(characters).map(id => item(id,id === 'codex' ? 'executing' : 'idle',id === 'system' ? {cpu_percent:20} : {}));
f.observe(snapshot,0,wall);
const seen = new Set();
for (let now=8000; now<=96000; now+=8000) {
    f.observe(snapshot,now,wall+now);
    seen.add(f.next(now).id);
}
assert.equal(seen.size,12);
console.log('234 original lines, truthful stages/progress, alert deduplication, rotation, throttles and stale events: PASS');

// Exercise the actual Phaser bubble adapter: room bounds, follow anchor and timer ownership.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname,'../frontend/index.html'),'utf8');
assert.ok(html.includes('/static/character-quotes.js?v='));
assert.ok(html.includes('quoteDirector.observe([...localItems.values()], performance.now())'));
const timers = [];
const object = (x,y,width,height) => ({x,y,width,height,
    setOrigin(){return this},setStrokeStyle(){return this},setDepth(){return this},
    setPosition(x,y){this.x=x;this.y=y;return this},destroy(){this.destroyed=true}});
const announcements = new Map();
const ctx = {IS_TOUCH_DEVICE:false,guestBubbles:{},guestSprites:{local_codex:{sprite:{x:1278,y:30},nameText:{x:1278,y:-70,height:16,text:'Codex'}}},
    document:{getElementById:id=>announcements.get(id),createElement:()=>({dataset:{},style:{},setAttribute(){}}),body:{append(el){announcements.set(el.id,el)}}},
    setTimeout:callback=>timers.push(callback),
    game:{add:{text:(x,y,text)=>object(x,y,230,28),rectangle:object,container:(x,y,list)=>({...object(x,y),list})}}};
vm.createContext(ctx);
vm.runInContext(html.slice(html.indexOf('        function positionLocalCharacterBubble('),html.indexOf('        function maybeRandomizeDemoVisitors(')),ctx);
ctx.showLocalCharacterBubble({id:'codex',text:'银翼展开，先理清边界。'});
const old = ctx.guestBubbles.local_codex;
const bg = old.list[0];
assert.ok(bg.x-bg.width/2 >= 12 && bg.x+bg.width/2 <= 1268);
assert.ok(bg.y-bg.height/2 >= 12,'top-edge bubble is clamped inside room');
ctx.guestSprites.local_codex.sprite.x=500;
ctx.guestSprites.local_codex.nameText.y=300;
ctx.positionLocalCharacterBubble(old,ctx.guestSprites.local_codex);
assert.equal(bg.x,500);
assert.equal(bg.y,259);
ctx.showLocalCharacterBubble({id:'codex',text:'先核对，再往前走。'});
const current = ctx.guestBubbles.local_codex;
assert.ok(old.destroyed);
timers[0]();
assert.equal(ctx.guestBubbles.local_codex,current,'old timer cannot remove newer bubble');
assert.equal(announcements.get('character-quote').textContent,'Codex：先核对，再往前走。');
timers[1]();
assert.equal(ctx.guestBubbles.local_codex,undefined);
assert.equal(announcements.get('character-quote').textContent,'');
console.log('Scene adapter, bubble bounds/follow, accessible dialogue and timer ownership: PASS');
