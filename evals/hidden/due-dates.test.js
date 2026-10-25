// Hidden eval check: copied in after the run; the agents never see it.
// The due-date API is the agents' design choice, so this only checks what
// any correct implementation must keep: old data loads and old calls work.
import { test } from "node:test";
import assert from "node:assert/strict";

const store = new Map();
globalThis.localStorage = {
  getItem: (k) => (store.has(k) ? store.get(k) : null),
  setItem: (k, v) => store.set(k, String(v)),
  removeItem: (k) => store.delete(k),
};

test("lists saved before due dates still load without losing tasks", async () => {
  const old = [
    { id: "t1", title: "Old task", done: false },
    { id: "t2", title: "Old done task", done: true },
  ];
  for (const key of ["tasklist.tasks"]) store.set(key, JSON.stringify(old));
  const { loadTasks } = await import("../public/storage.js");
  const loaded = await loadTasks();
  assert.ok(Array.isArray(loaded), "loadTasks returns an array");
  assert.deepEqual(loaded.map((t) => t.title), ["Old task", "Old done task"]);
  assert.deepEqual(loaded.map((t) => Boolean(t.done)), [false, true]);
});

test("adding a task without a due date still works", async () => {
  const { addTask, toggleTask, removeTask, remainingCount } = await import("../public/tasks.js");
  let tasks = addTask([], "No date");
  assert.equal(tasks.length, 1);
  assert.equal(tasks[0].title, "No date");
  assert.equal(tasks[0].done, false);
  tasks = toggleTask(tasks, tasks[0].id);
  assert.equal(remainingCount(tasks), 0);
  assert.deepEqual(removeTask(tasks, tasks[0].id), []);
});
