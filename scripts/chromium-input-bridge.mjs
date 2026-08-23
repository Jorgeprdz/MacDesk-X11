#!/usr/bin/env node

import { spawn } from "node:child_process";

const display = process.env.DISPLAY || ":2.0";
const devices = (process.env.MACDESK_KEYBOARD_DEVICES || process.env.MACDESK_KEYBOARD_DEVICE || "5,8")
  .split(",")
  .map((device) => device.trim())
  .filter(Boolean);
const port = process.env.MACDESK_CHROMIUM_DEBUG_PORT || "9225";
const expectedWindowClass = process.env.MACDESK_WINDOW_CLASS || "";
const timezone = process.env.MACDESK_TIMEZONE || "";
const allowedHosts = (process.env.MACDESK_CHROMIUM_TARGET_HOSTS || "web.whatsapp.com")
  .split(",")
  .map((host) => host.trim())
  .filter(Boolean);
const allowAnyHost = allowedHosts.includes("*");
const recoverEmptyChatResponse = process.env.MACDESK_EMPTY_CHAT_RESPONSE_RELOAD === "1";
const configuredResponsiveMinWidth = Number(
  process.env.MACDESK_RESPONSIVE_MIN_WIDTH || (allowedHosts.includes("web.whatsapp.com") ? "748" : "0"),
);
const responsiveMinWidth = Number.isFinite(configuredResponsiveMinWidth) && configuredResponsiveMinWidth > 0
  ? configuredResponsiveMinWidth
  : 0;
const focusExpression = allowAnyHost
  ? "document.hasFocus()"
  : `document.hasFocus() && ${JSON.stringify(allowedHosts)}.includes(location.hostname)`;
const responsiveExpression = `(() => {
  const minimumLayoutWidth = ${JSON.stringify(responsiveMinWidth)};
  const factor = Math.min(1, innerWidth / minimumLayoutWidth);
  const value = factor < 0.999 ? factor.toFixed(6) : "";
  if (document.documentElement.style.zoom !== value) {
    document.documentElement.style.zoom = value;
  }
})()`;
const chatResponseExpression = `(() => {
  const assistants = Array.from(document.querySelectorAll('[data-message-author-role="assistant"]'));
  const conversationResponses = performance.getEntriesByType('resource').filter((entry) => {
    try {
      return /\\/backend-api\\/(?:f\\/)?conversation$/.test(new URL(entry.name).pathname);
    } catch {
      return false;
    }
  }).length;
  return {
    userMessages: document.querySelectorAll('[data-message-author-role="user"]').length,
    lastAssistantLength: (assistants.at(-1)?.textContent || '').trim().length,
    generating: !!document.querySelector('[data-testid="stop-button"]'),
    conversationResponses,
  };
})()`;

let socket;
let sequence = 0;
let pageFocused = false;
let xWindowFocused = expectedWindowClass === "";
let activeWindowSequence = 0;
let activeWindowWatcher;
let activeWindowWatcherRetry;
let stoppingActiveWindowWatcher = false;
const replies = new Map();
const pressed = new Set();
const repeatingKeys = new Map();
let capsLock = false;
let deadKey = "";
let responseWatchInitialized = false;
let observedUserMessages = 0;
let previousConversationResponses = 0;
let responseBaseline = 0;
let pendingChatResponse = false;
let emptyResponseSince = 0;

const printable = new Map([
  [10, ["1", "!"]], [11, ["2", '"']], [12, ["3", "#"]],
  [13, ["4", "$"]], [14, ["5", "%"]], [15, ["6", "&"]],
  [16, ["7", "/"]], [17, ["8", "("]], [18, ["9", ")"]],
  [19, ["0", "="]], [20, ["'", "?"]], [21, ["¿", "¡"]],
  [24, ["q", "Q"]], [25, ["w", "W"]], [26, ["e", "E"]],
  [27, ["r", "R"]], [28, ["t", "T"]], [29, ["y", "Y"]],
  [30, ["u", "U"]], [31, ["i", "I"]], [32, ["o", "O"]],
  [33, ["p", "P"]], [35, ["+", "*"]], [38, ["a", "A"]],
  [39, ["s", "S"]], [40, ["d", "D"]], [41, ["f", "F"]],
  [42, ["g", "G"]], [43, ["h", "H"]], [44, ["j", "J"]],
  [45, ["k", "K"]], [46, ["l", "L"]], [47, ["ñ", "Ñ"]],
  [48, ["{", "["]], [49, ["|", "°"]], [51, ["}", "]"]],
  [52, ["z", "Z"]], [53, ["x", "X"]], [54, ["c", "C"]],
  [55, ["v", "V"]], [56, ["b", "B"]], [57, ["n", "N"]],
  [58, ["m", "M"]], [59, [",", ";"]], [60, [".", ":"]],
  [61, ["-", "_"]], [65, [" ", " "]],
]);

const altGraph = new Map([
  [13, "~"], [16, "{"], [17, "["], [18, "]"], [19, "}"],
  [20, "\\"], [24, "@"], [26, "€"], [35, "~"], [47, "~"],
  [48, "^"], [51, "`"], [52, "«"], [53, "»"],
]);

const special = new Map([
  [9, ["Escape", "Escape", 27]], [22, ["Backspace", "Backspace", 8]],
  [23, ["Tab", "Tab", 9]], [36, ["Enter", "Enter", 13]],
  [104, ["Enter", "NumpadEnter", 13]], [110, ["Home", "Home", 36]],
  [111, ["ArrowUp", "ArrowUp", 38]], [112, ["PageUp", "PageUp", 33]],
  [113, ["ArrowLeft", "ArrowLeft", 37]], [114, ["ArrowRight", "ArrowRight", 39]],
  [115, ["End", "End", 35]], [116, ["ArrowDown", "ArrowDown", 40]],
  [117, ["PageDown", "PageDown", 34]], [118, ["Insert", "Insert", 45]],
  [119, ["Delete", "Delete", 46]],
]);

function modifiers() {
  let value = 0;
  if (pressed.has(37) || pressed.has(64) || pressed.has(105)) value |= 2;
  if (pressed.has(50) || pressed.has(62)) value |= 8;
  if (pressed.has(108)) value |= 3;
  return value;
}

function send(method, params, callback) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  const id = ++sequence;
  if (callback) replies.set(id, callback);
  socket.send(JSON.stringify({ id, method, params }));
}

function dispatch(type, key, code, virtualKey, text = "", autoRepeat = false) {
  const params = {
    type,
    key,
    code,
    modifiers: modifiers(),
    windowsVirtualKeyCode: virtualKey,
    nativeVirtualKeyCode: virtualKey,
  };
  if (text && type === "keyDown") {
    params.text = text;
    params.unmodifiedText = text;
  }
  if (autoRepeat && type === "keyDown") params.autoRepeat = true;
  send("Input.dispatchKeyEvent", params);
}

function stopKeyRepeat(token) {
  const timers = repeatingKeys.get(token);
  if (!timers) return;
  clearTimeout(timers.delay);
  if (timers.interval) clearInterval(timers.interval);
  repeatingKeys.delete(token);
}

function stopAllKeyRepeats() {
  for (const token of repeatingKeys.keys()) stopKeyRepeat(token);
}

function setXWindowFocused(value) {
  if (xWindowFocused === value) return;
  xWindowFocused = value;
  process.stdout.write(`x11 window focus ${value ? "active" : "inactive"}: ${expectedWindowClass}\n`);
}

function inspectActiveWindow(windowId) {
  const token = ++activeWindowSequence;
  setXWindowFocused(false);
  if (!/^0x[0-9a-f]+$/i.test(windowId) || windowId === "0x0") return;

  const query = spawn("/usr/bin/xprop", ["-id", windowId, "WM_CLASS"], {
    env: { ...process.env, DISPLAY: display },
    stdio: ["ignore", "pipe", "ignore"],
  });
  let output = "";
  query.stdout.setEncoding("utf8");
  query.stdout.on("data", (chunk) => { output += chunk; });
  query.on("close", () => {
    if (token !== activeWindowSequence) return;
    const classes = [...output.matchAll(/"([^"]*)"/g)].map((match) => match[1]);
    setXWindowFocused(classes.includes(expectedWindowClass));
  });
  query.on("error", () => {
    if (token === activeWindowSequence) setXWindowFocused(false);
  });
}

function startActiveWindowWatcher() {
  if (!expectedWindowClass || stoppingActiveWindowWatcher) return;
  const watcher = spawn("/usr/bin/xprop", ["-root", "-spy", "_NET_ACTIVE_WINDOW"], {
    env: { ...process.env, DISPLAY: display },
    stdio: ["ignore", "pipe", "ignore"],
  });
  activeWindowWatcher = watcher;
  let buffer = "";
  let disconnected = false;
  watcher.stdout.setEncoding("utf8");
  watcher.stdout.on("data", (chunk) => {
    buffer += chunk;
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      const match = line.match(/window id # (0x[0-9a-f]+)/i);
      if (match) inspectActiveWindow(match[1]);
    }
  });
  const reconnect = () => {
    if (disconnected) return;
    disconnected = true;
    if (activeWindowWatcher === watcher) activeWindowWatcher = undefined;
    setXWindowFocused(false);
    if (stoppingActiveWindowWatcher || activeWindowWatcherRetry) return;
    activeWindowWatcherRetry = setTimeout(() => {
      activeWindowWatcherRetry = undefined;
      startActiveWindowWatcher();
    }, 1000);
  };
  watcher.once("error", reconnect);
  watcher.once("exit", reconnect);
}

function stopActiveWindowWatcher(signal) {
  stoppingActiveWindowWatcher = true;
  if (activeWindowWatcherRetry) clearTimeout(activeWindowWatcherRetry);
  activeWindowWatcherRetry = undefined;
  if (activeWindowWatcher) activeWindowWatcher.kill(signal);
  activeWindowWatcher = undefined;
}

function startBackspaceRepeat(token, named) {
  if (repeatingKeys.has(token)) return;
  const timers = { delay: null, interval: null };
  timers.delay = setTimeout(() => {
    if (!pageFocused || !repeatingKeys.has(token)) return;
    dispatch("keyDown", ...named, "", true);
    timers.interval = setInterval(() => {
      if (pageFocused && repeatingKeys.has(token)) {
        dispatch("keyDown", ...named, "", true);
      }
    }, 50);
  }, 500);
  repeatingKeys.set(token, timers);
}

function insertText(text) {
  if (deadKey) {
    const mark = deadKey === "acute" ? "\u0301" : "\u0308";
    text = (text + mark).normalize("NFC");
    deadKey = "";
  }
  send("Input.insertText", { text });
}

function keyCodeName(keycode) {
  if (keycode >= 24 && keycode <= 58 && printable.has(keycode)) {
    const base = printable.get(keycode)[0];
    if (/^[a-zñ]$/u.test(base)) return [base.toUpperCase(), `Key${base === "ñ" ? "N" : base.toUpperCase()}`, base.toUpperCase().charCodeAt(0)];
  }
  return null;
}

function handleKey(kind, keycode, sourceDevice) {
  const down = kind === "press";
  const repeatToken = `${sourceDevice}:${keycode}`;

  if ([37, 64, 105, 50, 62, 108].includes(keycode)) {
    if (down) pressed.add(keycode);
    const ctrl = [37, 64, 105].includes(keycode);
    const shift = [50, 62].includes(keycode);
    const data = ctrl ? ["Control", "ControlLeft", 17] : shift ? ["Shift", "ShiftLeft", 16] : ["AltGraph", "AltRight", 18];
    if (pageFocused) dispatch(down ? "keyDown" : "keyUp", ...data);
    if (!down) pressed.delete(keycode);
    return;
  }

  if (keycode === 66 && down) capsLock = !capsLock;
  if (!pageFocused) {
    if (!down) stopKeyRepeat(repeatToken);
    return;
  }

  if (keycode === 34 && down) {
    deadKey = (pressed.has(50) || pressed.has(62)) ? "diaeresis" : "acute";
    return;
  }

  const named = special.get(keycode);
  if (named) {
    if (down) {
      const autoRepeat = repeatingKeys.has(repeatToken);
      dispatch("keyDown", ...named, keycode === 36 ? "\r" : "", autoRepeat);
      if (keycode === 22 && !autoRepeat) startBackspaceRepeat(repeatToken, named);
    } else {
      stopKeyRepeat(repeatToken);
      dispatch("keyUp", ...named);
    }
    return;
  }

  const ctrlDown = pressed.has(37) || pressed.has(64) || pressed.has(105);
  const namedCode = keyCodeName(keycode);
  if (ctrlDown && namedCode) {
    dispatch(down ? "keyDown" : "keyUp", ...namedCode);
    return;
  }

  if (!down || !printable.has(keycode)) return;
  if (pressed.has(108) && altGraph.has(keycode)) {
    insertText(altGraph.get(keycode));
    return;
  }
  const shifted = pressed.has(50) || pressed.has(62);
  const pair = printable.get(keycode);
  let text = pair[shifted ? 1 : 0];
  if (/^[a-zñ]$/iu.test(pair[0]) && capsLock) text = shifted ? pair[0] : pair[1];
  insertText(text);
}

async function connect() {
  try {
    const response = await fetch(`http://127.0.0.1:${port}/json/list`);
    const targets = await response.json();
    const target = targets.find((item) => {
      if (item.type !== "page") return false;
      try {
        return allowAnyHost || allowedHosts.includes(new URL(item.url).hostname);
      } catch {
        return false;
      }
    });
    if (!target) throw new Error("Chromium app target not ready");
    socket = new WebSocket(target.webSocketDebuggerUrl);
    socket.onopen = () => {
      process.stdout.write("input bridge ready\n");
      if (timezone) {
        send("Emulation.setTimezoneOverride", { timezoneId: timezone });
      }
      if (responsiveMinWidth === 0) {
        send("Runtime.evaluate", {
          expression: 'document.documentElement.style.zoom = ""',
        });
      }
    };
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      const callback = replies.get(message.id);
      if (callback) {
        replies.delete(message.id);
        callback(message);
      }
    };
    socket.onclose = () => {
      pageFocused = false;
      stopAllKeyRepeats();
      setTimeout(connect, 500);
    };
    socket.onerror = () => {};
  } catch {
    setTimeout(connect, 500);
  }
}

setInterval(() => {
  send("Runtime.evaluate", {
    expression: focusExpression,
    returnByValue: true,
  }, (message) => {
    pageFocused = message?.result?.result?.value === true && xWindowFocused;
  });
}, 100);

if (responsiveMinWidth > 0) {
  setInterval(() => {
    send("Runtime.evaluate", { expression: responsiveExpression });
  }, 250);
}

if (recoverEmptyChatResponse) {
  setInterval(() => {
    send("Runtime.evaluate", {
      expression: chatResponseExpression,
      returnByValue: true,
    }, (message) => {
      const state = message?.result?.result?.value;
      if (!state) return;

      if (!responseWatchInitialized) {
        responseWatchInitialized = true;
        observedUserMessages = state.userMessages;
        previousConversationResponses = state.conversationResponses;
        return;
      }

      if (state.userMessages > observedUserMessages) {
        responseBaseline = previousConversationResponses;
        observedUserMessages = state.userMessages;
        pendingChatResponse = true;
        emptyResponseSince = 0;
      }
      previousConversationResponses = state.conversationResponses;

      if (!pendingChatResponse) return;
      if (state.lastAssistantLength > 0) {
        pendingChatResponse = false;
        emptyResponseSince = 0;
        return;
      }

      const responseFinished = state.conversationResponses > responseBaseline;
      if (!responseFinished || state.generating) {
        emptyResponseSince = 0;
        return;
      }

      if (!emptyResponseSince) {
        emptyResponseSince = Date.now();
        return;
      }
      if (Date.now() - emptyResponseSince < 1500) return;

      pendingChatResponse = false;
      emptyResponseSince = 0;
      process.stdout.write("empty chat response recovered by reload\n");
      send("Page.reload", { ignoreCache: false });
    });
  }, 500);
}

const inputs = new Map();
const inputRetries = new Map();
let stoppingInputs = false;

function startInput(device) {
  if (stoppingInputs) return;
  const input = spawn("/usr/bin/xinput", ["test-xi2", "--root", device], {
    env: { ...process.env, DISPLAY: display },
    stdio: ["ignore", "pipe", "inherit"],
  });
  inputs.set(device, input);
  let buffer = "";
  let eventKind = "";
  let disconnected = false;
  input.stdout.setEncoding("utf8");
  input.stdout.on("data", (chunk) => {
    buffer += chunk;
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.includes("(RawKeyPress)")) eventKind = "press";
      else if (line.includes("(RawKeyRelease)")) eventKind = "release";
      else {
        const match = line.match(/^\s*detail:\s*(\d+)/);
        if (match && eventKind) {
          handleKey(eventKind, Number(match[1]), device);
          eventKind = "";
        }
      }
    }
  });

  const reconnect = () => {
    if (disconnected) return;
    disconnected = true;
    if (inputs.get(device) === input) inputs.delete(device);
    if (stoppingInputs || inputRetries.has(device)) return;
    process.stdout.write(`input capture ${device} disconnected; retrying\n`);
    inputRetries.set(device, setTimeout(() => {
      inputRetries.delete(device);
      startInput(device);
    }, 1000));
  };
  input.once("error", reconnect);
  input.once("exit", reconnect);
}

for (const device of devices) startInput(device);

function stopInputs(signal) {
  stoppingInputs = true;
  stopAllKeyRepeats();
  for (const retry of inputRetries.values()) clearTimeout(retry);
  inputRetries.clear();
  for (const input of inputs.values()) input.kill(signal);
  inputs.clear();
}

process.on("SIGTERM", () => {
  stopInputs("SIGTERM");
  stopActiveWindowWatcher("SIGTERM");
  process.exit(0);
});
process.on("SIGINT", () => {
  stopInputs("SIGINT");
  stopActiveWindowWatcher("SIGINT");
  process.exit(0);
});

startActiveWindowWatcher();
connect();
