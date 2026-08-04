"use strict";

const API_URL = "/api/tasks";

// Mirrors the backend's STATUS_ORDER: moves to a lower rank are illegal.
const STATUS_ORDER = { todo: 0, in_progress: 1, done: 2 };

const board = document.getElementById("board");
const form = document.getElementById("task-form");
const titleInput = document.getElementById("task-title");
const descriptionInput = document.getElementById("task-description");
const toast = document.getElementById("toast");

let draggedTaskId = null;
let draggedTaskStatus = null;
let toastTimer = null;

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
const createTask = (title, description) =>
  apiRequest(API_URL, {
    method: "POST",
    body: JSON.stringify({ title, description: description || null }),
  });
const updateTask = (id, payload) =>
  apiRequest(`${API_URL}/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
const deleteTask = (id) => apiRequest(`${API_URL}/${id}`, { method: "DELETE" });

// --- Rendering -------------------------------------------------------------

function buildCard(task) {
  const card = document.createElement("article");
  card.className = "card";
  card.draggable = true;
  card.dataset.taskId = String(task.id);
  card.dataset.status = task.status;

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

  for (const column of board.querySelectorAll(".column")) {
    const status = column.dataset.status;
    const list = column.querySelector(".task-list");
    list.replaceChildren();

    const columnTasks = tasks.filter((t) => t.status === status);
    for (const task of columnTasks) list.appendChild(buildCard(task));
    column.querySelector(".task-count").textContent = String(columnTasks.length);
  }
}

// --- Drag and drop ---------------------------------------------------------

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
      // Only legal targets accept the drop.
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

// --- Actions ---------------------------------------------------------------

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) return;

  try {
    await createTask(title, descriptionInput.value.trim());
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

  const trimmedTitle = newTitle.trim();
  if (!trimmedTitle) {
    showToast("Title cannot be empty.");
    return;
  }

  try {
    await updateTask(task.id, {
      title: trimmedTitle,
      description: newDescription.trim() || null,
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

// --- Init ------------------------------------------------------------------

renderBoard();
