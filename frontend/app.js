"use strict";

const API_URL = "/api/tasks";

// Mirrors the backend's STATUS_ORDER: moves to a lower rank are illegal.
const STATUS_ORDER = { todo: 0, in_progress: 1, done: 2 };

// Mirrors the backend's DUE_SOON_WINDOW_DAYS.
const DUE_SOON_WINDOW_DAYS = 2;

const board = document.getElementById("board");
const form = document.getElementById("task-form");
const titleInput = document.getElementById("task-title");
const descriptionInput = document.getElementById("task-description");
const dueDateInput = document.getElementById("task-due-date");
const tagsInput = document.getElementById("task-tags");
const filterBar = document.getElementById("filter-bar");
const activeTagPill = document.getElementById("active-tag-pill");
const searchInput = document.getElementById("search-input");
const searchClear = document.getElementById("search-clear");
const matchCounter = document.getElementById("match-counter");
const toast = document.getElementById("toast");

const SEARCH_DEBOUNCE_MS = 180;

let draggedTaskId = null;
let draggedTaskStatus = null;
let toastTimer = null;
let activeFilter = "all";
let activeTag = null;
let totalTaskCount = 0;
let searchDebounceTimer = null;

// --- API helpers -----------------------------------------------------------

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return response.status === 204 ? null : response.json();
}

const fetchTasks = () => apiRequest(API_URL);
const createTask = (title, description, dueDate, tags) =>
  apiRequest(API_URL, {
    method: "POST",
    body: JSON.stringify({
      title,
      description: description || null,
      due_date: dueDate || null,
      tags,
    }),
  });
const updateTask = (id, payload) =>
  apiRequest(`${API_URL}/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
const deleteTask = (id) => apiRequest(`${API_URL}/${id}`, { method: "DELETE" });

// --- Due-date helpers ------------------------------------------------------

function localISODate(offsetDays = 0) {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${month}-${day}`;
}

function isOverdue(task) {
  return Boolean(task.due_date) && task.status !== "done" && task.due_date < localISODate();
}

function isDueSoon(task) {
  return (
    Boolean(task.due_date) &&
    task.status !== "done" &&
    task.due_date >= localISODate() &&
    task.due_date <= localISODate(DUE_SOON_WINDOW_DAYS)
  );
}

function formatDueDate(isoDate) {
  const [year, month, day] = isoDate.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: year === new Date().getFullYear() ? undefined : "numeric",
  });
}

// --- Tags ------------------------------------------------------------------

const TAG_HUE_COUNT = 6;

function parseTagsInput(raw) {
  return [...new Set(
    raw.split(",").map((t) => t.trim().toLowerCase()).filter(Boolean)
  )];
}

function tagHueClass(tag) {
  let hash = 0;
  for (const char of tag) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return `tag-hue-${hash % TAG_HUE_COUNT}`;
}

function setActiveTag(tag) {
  activeTag = tag;
  activeTagPill.hidden = tag === null;
  if (tag !== null) activeTagPill.textContent = `tag: ${tag} ✕`;
  renderBoard();
}

activeTagPill.addEventListener("click", () => setActiveTag(null));

// --- Filtering -------------------------------------------------------------

const FILTER_PREDICATES = {
  all: () => true,
  overdue: (task) => isOverdue(task),
  soon: (task) => isDueSoon(task),
  none: (task) => !task.due_date,
};

filterBar.addEventListener("click", (event) => {
  const pill = event.target.closest(".filter-pill");
  if (!pill) return;
  activeFilter = pill.dataset.filter;
  for (const p of filterBar.querySelectorAll(".filter-pill")) {
    p.classList.toggle("active", p === pill);
  }
  renderBoard();
});

// --- Rendering -------------------------------------------------------------

function buildCard(task) {
  const card = document.createElement("article");
  card.className = "card";
  card.draggable = true;
  card.dataset.taskId = String(task.id);
  card.dataset.status = task.status;
  card.dataset.title = task.title;
  card.dataset.description = task.description || "";
  card.dataset.searchText =
    `${task.title}\n${task.description || ""}\n${task.tags.join("\n")}`.toLowerCase();

  const overdue = isOverdue(task);
  const dueSoon = isDueSoon(task);
  if (overdue) card.classList.add("overdue");
  else if (dueSoon) card.classList.add("due-soon");

  const title = document.createElement("div");
  title.className = "card-title";
  title.textContent = task.title;
  card.appendChild(title);

  if (task.description) {
    const description = document.createElement("div");
    description.className = "card-description";
    description.textContent = task.description;
    card.appendChild(description);
  }

  if (task.tags.length > 0) {
    const tagRow = document.createElement("div");
    tagRow.className = "tag-row";
    for (const tag of task.tags) {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = `tag-chip ${tagHueClass(tag)}`;
      chip.textContent = tag;
      chip.title = `Filter by tag "${tag}"`;
      chip.addEventListener("click", () => setActiveTag(tag));
      tagRow.appendChild(chip);
    }
    card.appendChild(tagRow);
  }

  if (task.due_date) {
    const badge = document.createElement("span");
    badge.className = "due-badge";
    let label = `\u{1F4C5} ${formatDueDate(task.due_date)}`;
    if (task.status === "done") {
      badge.classList.add("done");
    } else if (overdue) {
      badge.classList.add("overdue");
      label += " · Overdue";
    } else if (dueSoon) {
      badge.classList.add("due-soon");
      label += " · Due soon";
    }
    badge.textContent = label;
    card.appendChild(badge);
  }

  const actions = document.createElement("div");
  actions.className = "card-actions";

  const editBtn = document.createElement("button");
  editBtn.type = "button";
  editBtn.textContent = "Edit";
  editBtn.addEventListener("click", () => editTask(task));

  const deleteBtn = document.createElement("button");
  deleteBtn.type = "button";
  deleteBtn.className = "delete-btn";
  deleteBtn.textContent = "Delete";
  deleteBtn.addEventListener("click", () => removeTask(task.id));

  actions.append(editBtn, deleteBtn);
  card.appendChild(actions);

  card.addEventListener("dragstart", (event) => {
    draggedTaskId = task.id;
    draggedTaskStatus = task.status;
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", String(task.id));
    card.classList.add("dragging");
  });

  card.addEventListener("dragend", () => {
    draggedTaskId = null;
    draggedTaskStatus = null;
    card.classList.remove("dragging");
    clearDropHighlights();
  });

  return card;
}

async function renderBoard() {
  let tasks;
  try {
    tasks = await fetchTasks();
  } catch (error) {
    showToast(error.message);
    return;
  }

  totalTaskCount = tasks.length;
  const visibleTasks = tasks
    .filter(FILTER_PREDICATES[activeFilter])
    .filter((t) => activeTag === null || t.tags.includes(activeTag));

  for (const column of board.querySelectorAll(".column")) {
    const status = column.dataset.status;
    const list = column.querySelector(".task-list");
    list.replaceChildren();

    const columnTasks = visibleTasks.filter((t) => t.status === status);
    for (const task of columnTasks) list.appendChild(buildCard(task));
  }

  applySearch();
}

function renderHighlighted(element, text, query) {
  element.replaceChildren();
  if (!query) {
    element.textContent = text;
    return;
  }
  const lowerText = text.toLowerCase();
  let cursor = 0;
  let matchIndex;
  while ((matchIndex = lowerText.indexOf(query, cursor)) !== -1) {
    element.append(text.slice(cursor, matchIndex));
    const mark = document.createElement("mark");
    mark.className = "search-hit";
    mark.textContent = text.slice(matchIndex, matchIndex + query.length);
    element.append(mark);
    cursor = matchIndex + query.length;
  }
  element.append(text.slice(cursor));
}

function applySearch() {
  const query = searchInput.value.trim().toLowerCase();
  searchClear.hidden = query === "";

  let visibleTotal = 0;
  for (const column of board.querySelectorAll(".column")) {
    const list = column.querySelector(".task-list");
    list.querySelector(".empty-state")?.remove();

    let visibleInColumn = 0;
    for (const card of list.querySelectorAll(".card")) {
      const matches = query === "" || card.dataset.searchText.includes(query);
      card.classList.toggle("search-hidden", !matches);
      if (matches) visibleInColumn += 1;

      const highlightQuery = matches ? query : "";
      renderHighlighted(card.querySelector(".card-title"), card.dataset.title, highlightQuery);
      const descriptionEl = card.querySelector(".card-description");
      if (descriptionEl) {
        renderHighlighted(descriptionEl, card.dataset.description, highlightQuery);
      }
    }

    const filtering = query !== "" || activeFilter !== "all" || activeTag !== null;
    if (visibleInColumn === 0 && filtering) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No matching tasks";
      list.appendChild(empty);
    }

    column.querySelector(".task-count").textContent = String(visibleInColumn);
    visibleTotal += visibleInColumn;
  }

  const filtering = query !== "" || activeFilter !== "all" || activeTag !== null;
  matchCounter.hidden = !filtering;
  if (filtering) {
    const noun = totalTaskCount === 1 ? "task" : "tasks";
    matchCounter.textContent = `Showing ${visibleTotal} of ${totalTaskCount} ${noun}`;
  }
}

searchInput.addEventListener("input", () => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(applySearch, SEARCH_DEBOUNCE_MS);
});

searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    searchInput.value = "";
    applySearch();
    searchInput.blur();
  }
});

searchClear.addEventListener("click", () => {
  searchInput.value = "";
  applySearch();
  searchInput.focus();
});

document.addEventListener("keydown", (event) => {
  const isModK = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k";
  const isSlash =
    event.key === "/" && !event.metaKey && !event.ctrlKey && !event.altKey;
  if (!isModK && !isSlash) return;

  const target = event.target;
  const isTyping =
    target instanceof HTMLElement &&
    (target.tagName === "INPUT" ||
      target.tagName === "TEXTAREA" ||
      target.isContentEditable);
  if (isSlash && isTyping) return;

  event.preventDefault();
  searchInput.focus();
  searchInput.select();
});

function isLegalMove(fromStatus, toStatus) {
  return STATUS_ORDER[toStatus] >= STATUS_ORDER[fromStatus];
}

function clearDropHighlights() {
  for (const column of board.querySelectorAll(".column")) {
    column.classList.remove("drop-allowed", "drop-forbidden");
  }
}

for (const column of board.querySelectorAll(".column")) {
  const targetStatus = column.dataset.status;

  column.addEventListener("dragover", (event) => {
    if (draggedTaskStatus === null) return;
    const legal = isLegalMove(draggedTaskStatus, targetStatus);
    column.classList.toggle("drop-allowed", legal);
    column.classList.toggle("drop-forbidden", !legal);
    if (legal) {
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
    }
  });

  column.addEventListener("dragleave", (event) => {
    if (!column.contains(event.relatedTarget)) {
      column.classList.remove("drop-allowed", "drop-forbidden");
    }
  });

  column.addEventListener("drop", async (event) => {
    event.preventDefault();
    clearDropHighlights();
    if (draggedTaskId === null) return;

    if (!isLegalMove(draggedTaskStatus, targetStatus)) {
      showToast("Illegal move: tasks can only move forward (To Do → In Progress → Done).");
      return;
    }
    if (draggedTaskStatus === targetStatus) return;

    try {
      await updateTask(draggedTaskId, { status: targetStatus });
    } catch (error) {
      showToast(error.message);
    }
    renderBoard();
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) return;

  try {
    await createTask(
      title,
      descriptionInput.value.trim(),
      dueDateInput.value,
      parseTagsInput(tagsInput.value)
    );
    form.reset();
    titleInput.focus();
    renderBoard();
  } catch (error) {
    showToast(error.message);
  }
});

async function editTask(task) {
  const newTitle = prompt("Task title:", task.title);
  if (newTitle === null) return;
  const newDescription = prompt("Description:", task.description || "");
  if (newDescription === null) return;
  const newDueDate = prompt("Due date (YYYY-MM-DD, empty to clear):", task.due_date || "");
  if (newDueDate === null) return;
  const newTags = prompt("Tags (comma-separated, empty to clear):", task.tags.join(", "));
  if (newTags === null) return;

  const trimmedTitle = newTitle.trim();
  if (!trimmedTitle) {
    showToast("Title cannot be empty.");
    return;
  }

  const trimmedDueDate = newDueDate.trim();
  if (trimmedDueDate && !/^\d{4}-\d{2}-\d{2}$/.test(trimmedDueDate)) {
    showToast("Due date must be in YYYY-MM-DD format.");
    return;
  }

  try {
    await updateTask(task.id, {
      title: trimmedTitle,
      description: newDescription.trim() || null,
      due_date: trimmedDueDate || null,
      tags: parseTagsInput(newTags),
    });
    renderBoard();
  } catch (error) {
    showToast(error.message);
  }
}

async function removeTask(taskId) {
  if (!confirm("Delete this task?")) return;
  try {
    await deleteTask(taskId);
    renderBoard();
  } catch (error) {
    showToast(error.message);
  }
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 3500);
}

renderBoard();
