// Original Chinese character dialogue. Keep numeric substitutions allowlisted.
(function (root) {
    'use strict';
    const characters = {
    "codex": {
        "name": "Codex · 银龙",
        "voice": "冷静、清晰，银龙般稳重；用逻辑、边界与线索做意象。",
        "lines": {
            "idle": [
                "银翼收好，等下一条线索。",
                "先把思路放整齐。",
                "留一点空白，给新问题。"
            ],
            "start": [
                "银翼展开，先理清边界。",
                "收到任务，沿着线索出发。",
                "先拆问题，再落笔。"
            ],
            "working": [
                "把绕路的逻辑慢慢拉直。",
                "先核对，再往前走。",
                "让每一步都能说清楚。"
            ],
            "settled": [
                "这一段先告一段落。",
                "银翼暂收，等下一步。",
                "先停在这里，留好思路线。"
            ],
            "error": [
                "这条线索碰到了异常。",
                "先停一下，看看详情。",
                "问题出现了，边界要重看。"
            ],
            "recovered": [
                "异常信号消退，继续观察。",
                "线索又接上了。",
                "状态重新可读，慢慢来。"
            ],
            "unavailable": [
                "暂时听不到任务的回声。",
                "线索不足，先不下结论。",
                "等状态来源重新亮起。"
            ]
        }
    },
    "dsh": {
        "name": "DSH · 鲸鱼女仆",
        "voice": "温柔、细致，鲸鱼与茶点意象；陪伴而不替软件承诺执行结果。",
        "lines": {
            "idle": [
                "茶还温着，等你吩咐。",
                "鲸尾轻轻摆，先歇一会儿。",
                "空闲时间也要好好呼吸。"
            ],
            "start": [
                "收到吩咐，鲸尾开工。",
                "这轮任务，慢慢理顺。",
                "把小围裙系好，出发。"
            ],
            "working": [
                "像梳理浪花一样理清步骤。",
                "细节要轻轻放稳。",
                "这一轮，耐心比着急有用。"
            ],
            "settled": [
                "这轮先歇，添一杯茶。",
                "鲸尾收一收，等下一步。",
                "先告一段落，别忘了伸腰。"
            ],
            "error": [
                "浪花有点乱，请看详情。",
                "这一步卡住了，先别急。",
                "发现异常，茶先放一边。"
            ],
            "recovered": [
                "浪花平静些了，继续观察。",
                "状态又传回来了。",
                "信号接上，茶也还温着。"
            ],
            "unavailable": [
                "暂时听不清海那边的信号。",
                "会话还没连上，先等一等。",
                "没有新状态，先不猜啦。"
            ]
        }
    },
    "sra": {
        "name": "SRA · 阿哈",
        "voice": "顽皮、戏剧感，把自动化流程当成一场舞台演出；不鼓励越界或自动操作。",
        "lines": {
            "idle": [
                "幕布没开，我先偷笑。",
                "下一幕，谁来报幕？",
                "休息也是节目的一部分。"
            ],
            "start": [
                "幕布一掀，流程登场！",
                "好戏开场，看看这一轮。",
                "铃声响了，演员就位！"
            ],
            "working": [
                "这一幕，还在走流程。",
                "别催，转场也有节奏。",
                "看，流程还在台上呢。"
            ],
            "settled": [
                "这一幕先落个帷幕。",
                "节目暂歇，掌声先存着。",
                "先退场，等下一张节目单。"
            ],
            "paused": [
                "暂停键也是舞台机关。",
                "幕布停半空，等你示意。",
                "这一拍先留白。"
            ],
            "error": [
                "咦，剧本拐到异常区了。",
                "这场意外，请看详情。",
                "舞台亮红灯，先停一停。"
            ],
            "recovered": [
                "红灯退场，继续看状态。",
                "信号回来了，别急着鼓掌。",
                "这一幕又有消息啦。"
            ],
            "unavailable": [
                "舞台还没接通信号。",
                "演员未到，先别喊开场。",
                "没收到状态，谜底先留着。"
            ]
        }
    },
    "bgi": {
        "name": "BetterGI · 芙宁娜",
        "voice": "优雅、略带傲娇的舞台感，偶尔露出体贴；全部为原创台词。",
        "lines": {
            "idle": [
                "休息时间，也要保持仪态。",
                "茶点就位，等下一幕。",
                "现在，允许我小憩片刻。"
            ],
            "start": [
                "请欣赏，今日的流程序章。",
                "帽子扶正，准备开场。",
                "这一轮，也请从容一点。"
            ],
            "working": [
                "舞台上的步骤，正在继续。",
                "优雅一点，别急着抢拍。",
                "每个转场，都有自己的节奏。"
            ],
            "settled": [
                "这一幕，暂且谢幕。",
                "本轮告一段落，稍作休息。",
                "掌声先留给下一幕吧。"
            ],
            "paused": [
                "幕间休息，等你的示意。",
                "舞台暂停，仪态照旧。",
                "这一拍，先停在这里。"
            ],
            "error": [
                "这可不在预定的演出里。",
                "舞台有异常，请看详情。",
                "先别催促，情况需要确认。"
            ],
            "recovered": [
                "异常信号退下，继续观察。",
                "舞台重新传来消息了。",
                "状态恢复可读，先稳住节奏。"
            ],
            "unavailable": [
                "舞台信号尚未送达。",
                "没有可靠消息，先不报幕。",
                "等日志把情况说明白。"
            ]
        }
    },
    "onedragon": {
        "name": "一条龙 · 千夏",
        "voice": "活泼、利落，小喇叭和节拍意象；有活力但不会反复催促。",
        "lines": {
            "idle": [
                "小喇叭休息，耳朵也放假。",
                "下一轮之前，先伸个懒腰。",
                "节拍放轻，等你的安排。"
            ],
            "start": [
                "喇叭就位，这轮出发！",
                "跟上节拍，流程开跑。",
                "收到，先把第一步踩稳！"
            ],
            "working": [
                "节拍还在，流程继续。",
                "一步一步，别跳拍。",
                "这轮正在推进，稳住节奏。"
            ],
            "settled": [
                "这一段先收音啦。",
                "本轮停在这里，歇一拍。",
                "小喇叭放下，等下一轮。"
            ],
            "paused": [
                "暂停一拍，等你接着来。",
                "喇叭静音，流程先等等。",
                "现在是幕间休息时间。"
            ],
            "error": [
                "节拍卡住了，请看详情。",
                "这一步有异常，先别冲。",
                "小喇叭提醒：状态要确认。"
            ],
            "recovered": [
                "信号回来了，先找回节拍。",
                "异常提示退了，继续观察。",
                "重新听到消息啦。"
            ],
            "unavailable": [
                "暂时没收到流程的回音。",
                "等入口亮起，再谈开场。",
                "信号没接上，先不乱喊。"
            ]
        }
    },
    "wechat": {
        "name": "微信 · 绿白信使",
        "voice": "亲切、轻声，气泡与信封意象；只提醒信号，不涉及内容或联系人。",
        "lines": {
            "idle": [
                "信封先收好，安静等消息。",
                "气泡歇一会儿，留点清静。",
                "没新提醒，先陪你摸会儿鱼。"
            ],
            "notice": [
                "有新的提醒信号啦。",
                "小气泡亮了一下。",
                "收到了提醒，要不要看看？"
            ],
            "recovered": [
                "提醒通道又接上了。",
                "信使回到岗位，继续等候。",
                "状态重新可读啦。"
            ],
            "unavailable": [
                "信使还没接上提醒通道。",
                "暂时看不到微信状态。",
                "消息信号不可读，先等一等。"
            ]
        }
    },
    "qq": {
        "name": "QQ · 企鹅围巾少女",
        "voice": "俏皮、轻快，企鹅、红围巾和脚步意象；不把未观察到的消息当作事实。",
        "lines": {
            "idle": [
                "红围巾一甩，先溜达两步。",
                "企鹅小队，安静待命。",
                "没有新信号，先暖暖手。"
            ],
            "notice": [
                "叮，企鹅收到提醒信号！",
                "红围巾动了，有新提醒。",
                "小脚一跺：提醒来啦！"
            ],
            "recovered": [
                "企鹅又接上信号啦。",
                "围巾理好，继续站岗。",
                "状态回来了，小步归队。"
            ],
            "unavailable": [
                "企鹅雷达暂时没信号。",
                "QQ 状态还读不到。",
                "先等通道接上，不乱报信。"
            ]
        }
    },
    "training": {
        "name": "论文训练 · 紫色研究员",
        "voice": "严谨、耐心，书页、步数和实验意象；不把 loss 变化说成模型一定变好。",
        "lines": {
            "idle": [
                "先翻翻笔记，等下一组实验。",
                "休息一会儿，让思路沉淀。",
                "实验之外，也要给自己留白。"
            ],
            "start": [
                "新一轮实验，先看清指标。",
                "训练开始，耐心也要上线。",
                "把问题记好，再看数据。"
            ],
            "working": [
                "一步一页，慢慢往下读。",
                "先观察趋势，不急着下结论。",
                "训练还在继续，记得歇歇眼。"
            ],
            "progress": [
                "已观察到训练步数 {percent}%。",
                "进度记到 {percent}%，继续观察。",
                "实验记录：步数进度 {percent}%。"
            ],
            "completed": [
                "已观察到训练步数达到 100%。",
                "步数走完了，结果还要评估。",
                "进度到达终点，结论要看验证。"
            ],
            "settled": [
                "训练活动暂歇，原因看详情。",
                "这一轮先停在这里。",
                "先把进度状态确认清楚。"
            ],
            "error": [
                "实验出现异常，请看详情。",
                "这条曲线先别急着解释。",
                "遇到异常，先确认运行情况。"
            ],
            "recovered": [
                "实验状态重新可读。",
                "信号接回来了，继续观察。",
                "异常信号消退，结论先不急。"
            ],
            "unavailable": [
                "进度还没接上，先不猜步数。",
                "实验日志暂时没有可靠消息。",
                "数据未更新，状态需要确认。"
            ]
        }
    },
    "baidu": {
        "name": "百度网盘 · 云盘管理员",
        "voice": "有条理、可靠，用云朵、文件柜意象；明确磁盘活动不等于下载速度或下载完成。",
        "lines": {
            "idle": [
                "云朵排好队，先等新动静。",
                "文件柜安静着，慢慢来。",
                "蓝色云包，暂时待命。"
            ],
            "activity": [
                "读到磁盘活动，云包有动静。",
                "客户端有活动，继续观察。",
                "有数据活动，进度还读不到。"
            ],
            "settled": [
                "磁盘活动放缓，先歇一会儿。",
                "动静小了，不等于下载完啦。",
                "活动暂歇，具体进度看客户端。"
            ],
            "recovered": [
                "云包的状态又读到了。",
                "信号接上，继续看活动。",
                "云端小管家回到观察岗位。"
            ],
            "unavailable": [
                "云包暂时没有可读状态。",
                "客户端还没连上观察窗口。",
                "先等网盘状态回来。"
            ]
        }
    },
    "quark": {
        "name": "夸克网盘 · 星环少女",
        "voice": "轻盈、好奇，轨道与星环意象；保持活动数据的真实边界。",
        "lines": {
            "idle": [
                "星环慢转，等下一阵风。",
                "轨道空闲，先散个步。",
                "蓝色小星球，安静待命。"
            ],
            "activity": [
                "轨道有动静，读到磁盘活动。",
                "客户端正在活动，继续看信号。",
                "星环动了，下载进度尚不可读。"
            ],
            "settled": [
                "轨道安静些了，先等等。",
                "活动放缓，完成与否看客户端。",
                "星环慢下来，不代表下载完。"
            ],
            "recovered": [
                "轨道信号重新接上。",
                "星环又能读到状态啦。",
                "观察窗口恢复，继续等消息。"
            ],
            "unavailable": [
                "暂时找不到这条轨道的信号。",
                "夸克状态还没传回来。",
                "没有可读数据，先不猜进度。"
            ]
        }
    },
    "comfyui": {
        "name": "ComfyUI · 节点工匠",
        "voice": "专注、灵巧，用节点、画布与拼装意象；节点进度与整体视频进度明确区分。",
        "lines": {
            "idle": [
                "节点暂歇，画布留点空白。",
                "工具收好，等下一张工作单。",
                "空队列时，也适合发会儿呆。"
            ],
            "start": [
                "队列开始忙碌，节点登场。",
                "画布上的流程开动啦。",
                "新一轮生成活动，继续观察。"
            ],
            "working": [
                "节点还在忙，慢慢拼画面。",
                "这一段流程正在向前走。",
                "画布的节奏，交给当前节点。"
            ],
            "progress": [
                "当前节点进度 {percent}%。",
                "采样节点走到 {percent}%。",
                "节点刻度到了 {percent}%。"
            ],
            "settled": [
                "生成活动暂歇，结果看界面。",
                "队列安静下来，先看任务状态。",
                "这一段停了，成片还需确认。"
            ],
            "error": [
                "节点报了异常，请看详情。",
                "这块拼图卡住了，先停一下。",
                "流程有异常，别急着重跑。"
            ],
            "recovered": [
                "节点状态重新可读啦。",
                "异常信号消退，先看看节点。",
                "工作台又传来状态消息。"
            ],
            "unavailable": [
                "工作台暂时没有可读信号。",
                "还没连上节点的状态。",
                "队列读不到，先不猜生成进度。"
            ]
        }
    },
    "system": {
        "name": "电脑性能 · 硬件工程师",
        "voice": "冷静、关心，芯片、仪表与节拍意象；只使用采集到的数值，不假装清理或降温。",
        "lines": {
            "idle": [
                "仪表轻轻跳，我在这里值班。",
                "芯片小队，按自己的节奏走。",
                "负载平缓，眼睛也歇一会儿。"
            ],
            "load": [
                "CPU 忙起来了，当前 {cpu}%。",
                "读数偏高：CPU {cpu}%。",
                "算力节拍加快，CPU {cpu}%。"
            ],
            "working": [
                "仪表持续更新，慢慢看读数。",
                "忙碌时，也记得给自己倒水。",
                "机器在忙，你不必一直盯着。"
            ],
            "recovered": [
                "CPU 负载回落，继续观察。",
                "读数平缓些了，节奏放轻。",
                "忙碌的那一阵，暂时过去了。"
            ],
            "unavailable": [
                "仪表数据暂时读不到。",
                "先等监测信号重新亮起。",
                "没有读数，先不判断负载。"
            ]
        }
    }
};
    const ACTIVE = new Set(['writing', 'researching', 'executing', 'syncing']);
    const STATES = new Set(['idle', 'error', ...ACTIVE]);
    const MESSENGERS = new Set(['wechat', 'qq']);
    const CLOUDS = new Set(['baidu', 'quark']);
    const number = value => typeof value === 'number' && Number.isFinite(value);
    const percentage = value => number(value) && value >= 0 && value <= 100;

    function status(id, item) {
        const metrics = item?.metrics || {};
        const available = item?.available === true && STATES.has(item?.state);
        const result = {available, stage: 'unavailable', percent: null, cpu: null, complete: false, alert: null};
        if (!available) return result;
        result.stage = item.state === 'error' ? 'error' : ACTIVE.has(item.state) ? 'working' : 'idle';
        if (['sra', 'bgi', 'onedragon'].includes(id) && metrics.phase === 'paused' && result.stage !== 'error') result.stage = 'paused';
        if (MESSENGERS.has(id)) {
            result.stage = 'idle'; // A retained notification flag is not a new notification.
            const stamp = typeof metrics.last_alert_at === 'string' ? Date.parse(metrics.last_alert_at) : NaN;
            if (Number.isFinite(stamp)) result.alert = stamp;
        }
        if (CLOUDS.has(id)) result.stage = item.state === 'syncing' ? 'activity' : 'idle';
        if (id === 'training') {
            if (number(metrics.current) && number(metrics.total) && metrics.current >= 0 && metrics.total > 0) {
                result.percent = Math.min(100, 100 * metrics.current / metrics.total);
                result.complete = metrics.current >= metrics.total;
            }
        }
        if (id === 'comfyui' && percentage(metrics.percent)) result.percent = metrics.percent;
        if (id === 'system') {
            if (!percentage(metrics.cpu_percent)) return {...result, available: false, stage: 'unavailable'};
            result.cpu = metrics.cpu_percent;
            result.stage = result.cpu > 80 ? 'working' : 'idle';
        }
        return result;
    }

    function transition(id, before, after) {
        if (after.stage === 'error') return before.stage === 'error' ? null : 'error';
        if (!after.available) return before.available ? 'unavailable' : null;
        if (MESSENGERS.has(id) && after.alert !== null && (before.alert === null || after.alert > before.alert)) return 'notice';
        if (id === 'system') {
            if (before.available && before.stage === 'working' && after.stage === 'idle') return 'recovered';
            return after.stage === 'working' && before.stage !== 'working' ? 'load' : null;
        }
        if (!before.available || before.stage === 'error') return 'recovered';
        if (after.stage === 'paused' && before.stage !== 'paused') return 'paused';
        if (id === 'training' && before.percent !== null && !before.complete && after.complete) return 'completed';
        if (after.stage === 'working' && before.stage !== 'working') return 'start';
        if (after.stage === 'activity' && before.stage !== 'activity') return 'activity';
        if (after.stage === 'idle' && ['working', 'activity', 'paused'].includes(before.stage)) return 'settled';
        return null;
    }

    // One short pending event per character; stale events never form a replay backlog.
    function createDirector() {
        const records = new Map();
        const pending = new Map();
        const spoken = new Map();
        const cursors = new Map();
        const alerts = new Map();
        let lastGlobal = -Infinity;
        let lastObserved = -Infinity;
        let initialized = false;

        function observe(items, now, wallNow = Date.now()) {
            const incoming = new Map((Array.isArray(items) ? items : []).filter(item => item && Object.hasOwn(characters, item.id)).map(item => [item.id, item]));
            for (const id of Object.keys(characters)) {
                const after = status(id, incoming.get(id));
                const before = records.get(id);
                if (before) {
                    if (after.stage !== before.stage || after.complete !== before.complete) pending.delete(id);
                    let stage = transition(id, before, after);
                    if (stage === 'notice' && (after.alert <= (alerts.get(id) ?? -Infinity) || wallNow - after.alert > 60000 || after.alert - wallNow > 5000)) stage = null;
                    if (stage && characters[id].lines[stage]) {
                        pending.set(id, {stage, at: now, priority: ['error', 'notice'].includes(stage) ? 5 : 4});
                    } else if (after.stage === 'working' && after.percent !== null && before.percent !== null && Math.abs(after.percent - before.percent) >= 10 && !pending.has(id)) {
                        pending.set(id, {stage: 'progress', at: now, priority: 2});
                    }
                }
                if (MESSENGERS.has(id)) alerts.set(id, Math.max(alerts.get(id) ?? wallNow, after.alert ?? -Infinity));
                records.set(id, after);
            }
            if (!initialized) lastGlobal = now; // First snapshot seeds history, without replaying old events.
            initialized = true;
            lastObserved = now;
        }

        function next(now, {paused = false, ids = Object.keys(characters)} = {}) {
            for (const [id, event] of pending) if (now - event.at > 24000) pending.delete(id);
            if (!initialized || paused || now - lastGlobal < 8000 || now - lastObserved > 15000) return null;
            const candidates = [];
            for (const id of ids) {
                const record = records.get(id);
                if (!record || !Object.hasOwn(characters, id)) continue;
                const event = pending.get(id);
                const last = spoken.get(id)?.at ?? -Infinity;
                if ((!event || event.priority < 4) && now - last < 35000) continue;
                let stage = event?.stage || record.stage;
                if (!event && stage === 'working' && record.percent !== null && !record.complete && characters[id].lines.progress) stage = 'progress';
                if (!event && id === 'training' && record.complete && stage === 'working') stage = 'idle';
                if (!characters[id].lines[stage]) continue;
                candidates.push({id, stage, record, priority: event?.priority || 0, last});
            }
            candidates.sort((a, b) => b.priority - a.priority || a.last - b.last || Number(b.record.stage === 'working') - Number(a.record.stage === 'working'));
            const chosen = candidates[0];
            if (!chosen) return null;
            const {id, stage, record} = chosen;
            const lines = characters[id].lines[stage];
            const key = id + ':' + stage;
            const index = ((cursors.get(key) ?? -1) + 1) % lines.length;
            cursors.set(key, index);
            const percent = id === 'training' && !record.complete ? Math.floor(record.percent * 10) / 10 : Math.round(record.percent);
            const text = lines[index].replace('{percent}', record.percent === null ? '?' : String(percent))
                .replace('{cpu}', record.cpu === null ? '?' : String(Math.round(record.cpu)));
            pending.delete(id);
            spoken.set(id, {at: now});
            lastGlobal = now;
            return {id, stage, text};
        }
        return {observe, next};
    }
    const api = {characters, status, transition, createDirector};
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    else root.OfficeCharacterQuotes = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
