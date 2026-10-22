// Shithead web client.
// The server owns the game: this file only draws the latest "state" message it receives
// and sends the player's clicks back as actions. See the protocol table in README.md.

const VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"];
const SUITS = { Hearts: "♥", Diamonds: "♦", Clubs: "♣", Spades: "♠" };
const RED_SUITS = ["Hearts", "Diamonds"];
const NAME_KEY = "shithead-name";

let ws = null;          // the WebSocket connection
let me = null;          // my name, as the server knows it
let wanted = 2;         // how many players I asked for
let game = null;        // latest state message from the server
let selected = [];      // indices (in my active zone) I've selected to play
let leaving = false;    // true when I close the connection on purpose

const $ = (id) => document.getElementById(id);

// -----------------------------
// Screens
// -----------------------------
function showScreen(id) {
  for (const screen of document.querySelectorAll(".screen")) {
    screen.hidden = screen.id !== id;
  }
}

function toast(text) {
  const el = $("toast");
  el.textContent = text;
  el.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => el.classList.remove("show"), 2600);
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

// -----------------------------
// Connection
// -----------------------------
function connect(name, players) {
  leaving = false;
  wanted = players;
  game = null;
  selected = [];

  showScreen("screen-waiting");
  renderWaiting(0, players, "Connecting…");

  ws = new WebSocket(window.BACKEND_URL);
  ws.onopen = () => send({ type: "join", name, players });
  ws.onmessage = (event) => handleMessage(JSON.parse(event.data));
  ws.onclose = () => {
    if (leaving) return;
    if (!game) {
      backToMenu("Couldn't reach the game server. Is it running?");
    } else if (game.state !== "game_over") {
      showResults("Connection lost", "You were disconnected from the server.");
    }
  };
}

function send(message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
  }
}

function backToMenu(error = "") {
  leaving = true;
  if (ws) ws.close();
  ws = null;
  game = null;
  $("results").hidden = true;
  $("menu-error").textContent = error;
  showScreen("screen-menu");
}

function handleMessage(msg) {
  switch (msg.type) {
    case "joined":
      me = msg.you;
      renderWaiting(1, wanted, "Looking for players…");
      break;
    case "waiting":
      renderWaiting(msg.joined, msg.needed);
      break;
    case "state":
      game = msg;
      selected = [];
      showScreen("screen-game");
      renderGame();
      break;
    case "error":
      toast(msg.message);
      break;
  }
}

// -----------------------------
// Waiting room
// -----------------------------
function renderWaiting(joined, needed, text) {
  $("waiting-text").textContent = text || `${joined} of ${needed} players joined`;
  $("waiting-seats").innerHTML = Array.from({ length: needed }, (_, i) =>
    `<span class="seat ${i < joined ? "filled" : ""}">${i < joined ? "✓" : ""}</span>`
  ).join("");
}

// -----------------------------
// Cards
// -----------------------------
function cardFace(card, { zone = "", index = -1, playable = false, isSelected = false, extra = "", style = "" } = {}) {
  const suit = SUITS[card.suit];
  const red = RED_SUITS.includes(card.suit) ? "red" : "";
  const classes = ["card", red, extra, playable ? "playable" : "", isSelected ? "selected" : ""].join(" ");
  const label = `${card.value} of ${card.suit}`;
  return `<button class="${classes}" style="${style}" data-zone="${zone}" data-index="${index}" aria-label="${label}"
    aria-pressed="${isSelected}" ${playable ? "" : "disabled"}>
    <span class="corner">${card.value}<small>${suit}</small></span>
    <span class="pip">${suit}</span>
    <span class="corner bottom">${card.value}<small>${suit}</small></span>
  </button>`;
}

function cardBack({ zone = "", index = -1, playable = false, extra = "", style = "" } = {}) {
  return `<button class="card back ${extra} ${playable ? "playable" : ""}" style="${style}" data-zone="${zone}" data-index="${index}"
    aria-label="Face-down card" ${playable ? "" : "disabled"}></button>`;
}

const rank = (card) => VALUES.indexOf(card.value);

// Face-down cards with face-up cards resting on top, like on a real table
function tableSlots(faceUp, faceDownCount, options = {}) {
  const { upPlayable = false, downPlayable = false, mini = false } = options;
  const slots = Math.max(faceUp.length, faceDownCount);
  let html = "";
  for (let i = 0; i < slots; i++) {
    html += `<div class="slot ${mini ? "mini" : ""}">`;
    if (i < faceDownCount) html += cardBack({ zone: "face_down", index: i, playable: downPlayable });
    if (i < faceUp.length) {
      html += cardFace(faceUp[i], {
        zone: "face_up", index: i, playable: upPlayable,
        isSelected: upPlayable && selected.includes(i), extra: "up",
      });
    }
    html += "</div>";
  }
  return html;
}

// -----------------------------
// The table
// -----------------------------
function renderGame() {
  const myTurn = game.turn === me;
  const meInGame = game.players.find((p) => p.name === me);

  renderOpponents();
  renderCenter();

  $("message").textContent = game.message;
  $("me").classList.toggle("active", myTurn && game.state !== "game_over");

  const banner = $("turn-banner");
  banner.classList.toggle("mine", myTurn);
  if (game.state === "setup") {
    banner.textContent = myTurn
      ? `Pick 3 cards to place face-up (${game.selected.length}/3)`
      : `${game.turn} is choosing face-up cards…`;
  } else if (game.state === "playing") {
    banner.textContent = myTurn ? "Your turn" : `${game.turn}'s turn`;
  } else {
    banner.textContent = "Game over";
  }

  if (!meInGame) {
    const place = game.finish_order.indexOf(me) + 1;
    $("my-table").innerHTML = "";
    $("my-hand").innerHTML = place
      ? `<p class="finished-note">You finished #${place}! 🎉 Watching the rest of the game…</p>`
      : "";
    $("actions").innerHTML = "";
  } else {
    renderMyCards(meInGame, myTurn);
  }

  if (game.state === "game_over") {
    const normalEnd = game.players.length <= 1;
    showResults(normalEnd ? "Game over" : "Game ended", game.message);
  }
}

function renderOpponents() {
  // Seat opponents in turn order starting after me
  const players = game.players;
  const myIndex = players.findIndex((p) => p.name === me);
  const ordered = myIndex === -1
    ? players
    : [...players.slice(myIndex + 1), ...players.slice(0, myIndex)];

  let html = ordered.map((p) => {
    const active = p.name === game.turn && game.state !== "game_over";
    const fan = Array.from({ length: Math.min(p.hand_count, 8) }, () => cardBack({ extra: "mini" })).join("");
    return `<div class="opponent ${active ? "active" : ""}">
      <div class="opponent-head">
        <span class="opponent-name">${escapeHtml(p.name)}</span>
        ${active ? `<span class="badge turn">${game.state === "setup" ? "Choosing" : "Playing"}</span>` : ""}
      </div>
      <div class="opponent-hand"><div class="fan">${fan}</div><span>${p.hand_count} in hand</span></div>
      <div class="table-cards mini">${tableSlots(p.face_up, p.face_down_count, { mini: true })}</div>
    </div>`;
  }).join("");

  // Players who already got rid of all their cards
  for (const name of game.finish_order) {
    if (name === me || players.some((p) => p.name === name)) continue;
    const place = game.finish_order.indexOf(name) + 1;
    html += `<div class="opponent"><div class="opponent-head">
      <span class="opponent-name">${escapeHtml(name)}</span><span class="badge">Finished #${place}</span>
    </div></div>`;
  }

  $("opponents").innerHTML = html;
}

function renderCenter() {
  // Deck: a small stack of backs
  const deckCount = game.deck_count;
  $("deck").innerHTML = deckCount
    ? Array.from({ length: Math.min(deckCount, 3) }, (_, i) =>
        cardBack({ style: `transform: translate(${i * 2}px, ${-i * 2}px)` })
      ).join("")
    : `<div class="empty-slot">Empty</div>`;
  $("deck-label").textContent = `Deck · ${deckCount}`;

  // Pile: the last few cards, slightly fanned
  const pile = game.pile;
  const shown = pile.slice(-4);
  $("pile").innerHTML = shown.length
    ? shown.map((card, i) => {
        const fromTop = shown.length - 1 - i;
        const angle = [0, -10, 8, -5][fromTop];
        const shift = [0, -10, 10, -4][fromTop];
        return cardFace(card, { style: `transform: translateX(${shift}px) rotate(${angle}deg)` });
      }).join("")
    : `<div class="empty-slot">Play any card</div>`;
  $("pile-label").textContent = `Pile · ${pile.length}`;
  $("burned-label").textContent = `Burned · ${game.burned_count}`;

  $("pile-hint").textContent = pileHint(pile);
}

// Mirrors Cards.isValidCard: a 3 is transparent, so the card under it is what counts
function pileHint(pile) {
  if (!pile.length) return "";
  let top = pile[pile.length - 1];
  let prefix = "";
  if (top.value === "3" && pile.length > 1) {
    top = pile[pile.length - 2];
    prefix = `3 is invisible: beat the ${top.value}. `;
  }
  if (top.value === "7") return `${prefix}Next card must be 7 or lower.`;
  if (top.value === "Q") return `${prefix}No 2, 3 or 10 on a Q.`;
  if (top.value === "2") return `${prefix}Pile reset: play anything.`;
  return prefix ? `${prefix}` : "";
}

function renderMyCards(player, myTurn) {
  const setup = game.state === "setup";
  const playing = game.state === "playing" && myTurn;
  const zone = game.active_zone;

  // Face-up / face-down cards on the table
  $("my-table").innerHTML = tableSlots(player.face_up, player.face_down_count, {
    upPlayable: playing && zone === "face_up",
    downPlayable: playing && zone === "face_down",
  });

  // Hand, sorted low → high but keeping each card's real index for the server
  const hand = game.hand.map((card, index) => ({ card, index })).sort((a, b) => rank(a.card) - rank(b.card));
  const handPlayable = (setup && myTurn) || (playing && zone === "hand");
  const handEl = $("my-hand");
  handEl.classList.toggle("roomy", hand.length <= 6);
  handEl.innerHTML = hand.map(({ card, index }) => cardFace(card, {
    zone: "hand", index, playable: handPlayable,
    isSelected: setup ? game.selected.includes(index) : selected.includes(index),
  })).join("");

  // Buttons
  let actions = "";
  if (setup && myTurn) {
    actions = `<button class="btn btn-primary" data-action="setup_confirm" ${game.selected.length === 3 ? "" : "disabled"}>
      Confirm face-up cards</button>`;
  } else if (playing) {
    if (zone === "face_down") {
      actions = `<span class="hint">Pick one of your face-down cards. Good luck!</span>`;
    } else {
      const label = selected.length > 1 ? `Play ${selected.length} cards` : "Play card";
      actions = `<button class="btn btn-primary" data-action="play" ${selected.length ? "" : "disabled"}>${label}</button>`;
    }
    actions += `<button class="btn btn-secondary" data-action="take_pile" ${game.pile.length ? "" : "disabled"}>Take pile</button>`;
  }
  $("actions").innerHTML = actions;
}

// -----------------------------
// Clicks
// -----------------------------
function cardsInZone(zone) {
  if (zone === "hand") return game.hand;
  const player = game.players.find((p) => p.name === me);
  return player ? player.face_up : [];
}

function onCardClick(zone, index) {
  if (game.state === "setup") {
    send({ type: "setup_toggle", index });
    return;
  }

  if (zone === "face_down") {
    send({ type: "play_face_down", index });
    return;
  }

  // Selecting cards to play: only cards of the same value can go together
  const cards = cardsInZone(zone);
  if (selected.includes(index)) {
    selected = selected.filter((i) => i !== index);
  } else if (selected.length && cards[selected[0]].value !== cards[index].value) {
    selected = [index];
  } else {
    selected.push(index);
  }
  updateSelection();
}

// Only flip the highlight classes (no full redraw), so the card element stays the same
// and a double-click on it still works
function updateSelection() {
  for (const el of document.querySelectorAll(`#me .card[data-zone="${game.active_zone}"]`)) {
    const isSelected = selected.includes(Number(el.dataset.index));
    el.classList.toggle("selected", isSelected);
    el.setAttribute("aria-pressed", isSelected);
  }
  const play = document.querySelector('[data-action="play"]');
  if (play) {
    play.disabled = !selected.length;
    play.textContent = selected.length > 1 ? `Play ${selected.length} cards` : "Play card";
  }
}

function onCardDoubleClick(zone, index) {
  // Double-click a card to play it (and any other selected cards of the same value) right away
  if (game.state !== "playing" || zone === "face_down") return;
  if (!selected.includes(index)) selected = [index];
  playSelected();
}

function playSelected() {
  if (!selected.length) return;
  send({ type: "play", zone: game.active_zone, indices: selected });
}

$("screen-game").addEventListener("click", (event) => {
  const card = event.target.closest(".card.playable");
  if (card) {
    onCardClick(card.dataset.zone, Number(card.dataset.index));
    return;
  }
  const button = event.target.closest("[data-action]");
  if (!button || button.disabled) return;
  const action = button.dataset.action;
  if (action === "play") playSelected();
  else send({ type: action });
});

$("screen-game").addEventListener("dblclick", (event) => {
  const card = event.target.closest(".card.playable");
  if (card) onCardDoubleClick(card.dataset.zone, Number(card.dataset.index));
});

// -----------------------------
// Results
// -----------------------------
function showResults(title, message) {
  $("results-title").textContent = title;
  $("results-message").textContent = message;

  const order = game ? game.finish_order : [];
  const normalEnd = game && game.players.length <= 1;
  const medals = ["🥇", "🥈", "🥉"];
  $("results-list").innerHTML = order.map((name, i) => {
    const loser = normalEnd && i === order.length - 1 && order.length > 1;
    const place = loser ? "💩" : (medals[i] || `#${i + 1}`);
    const tag = loser ? "Shithead" : name === me ? "You" : "";
    return `<li class="${loser ? "loser" : ""} ${name === me ? "you" : ""}">
      <span class="place">${place}</span>${escapeHtml(name)}<span class="tag">${tag}</span></li>`;
  }).join("");

  $("results").hidden = false;
}

// -----------------------------
// Menu, rules, leaving
// -----------------------------
const nameInput = $("name-input");
try { nameInput.value = localStorage.getItem(NAME_KEY) || ""; } catch { /* storage blocked */ }

$("join-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const name = nameInput.value.trim();
  if (!name) return;
  try { localStorage.setItem(NAME_KEY, name); } catch { /* storage blocked */ }
  $("menu-error").textContent = "";
  const players = Number(document.querySelector('input[name="players"]:checked').value);
  connect(name, players);
});

for (const button of document.querySelectorAll("[data-leave]")) {
  button.addEventListener("click", () => backToMenu());
}

for (const button of document.querySelectorAll("[data-open-rules]")) {
  button.addEventListener("click", () => $("rules").showModal());
}
