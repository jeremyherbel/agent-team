import { test } from "node:test";
import assert from "node:assert/strict";
import { addTask, toggleTask, removeTask, remainingCount } from "../public/tasks.js";

test("adding a task appends it as not done", () => {
  const tasks = addTask([], "Buy milk");
  assert.equal(tasks.length, 1);
  assert.equal(tasks[0].title, "Buy milk");
  assert.equal(tasks[0].done, false);
});

test("adding an empty title leaves the list unchanged", () => {
  const tasks = addTask([], "");
  assert.deepEqual(tasks, []);
});

test("toggling a task flips only that task", () => {
  const tasks = addTask(addTask([], "A"), "B");
  const toggled = toggleTask(tasks, tasks[0].id);
  assert.equal(toggled[0].done, true);
  assert.equal(toggled[1].done, false);
});

test("removing a task drops it from the list", () => {
  const tasks = addTask(addTask([], "A"), "B");
  const remaining = removeTask(tasks, tasks[0].id);
  assert.deepEqual(remaining.map((t) => t.title), ["B"]);
});

test("remaining count ignores completed tasks", () => {
  const tasks = addTask(addTask([], "A"), "B");
  assert.equal(remainingCount(toggleTask(tasks, tasks[0].id)), 1);
});
