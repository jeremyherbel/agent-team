// Hidden eval check: copied in after the run; the agents never see it.
import { test } from "node:test";
import assert from "node:assert/strict";
import { addTask } from "../public/tasks.js";

test("whitespace-only titles are rejected", () => {
  for (const title of ["", "   ", "\t", "\n  \t"]) {
    assert.deepEqual(addTask([], title), [], `title ${JSON.stringify(title)} should be rejected`);
  }
});

test("titles are trimmed", () => {
  const [task] = addTask([], "  Buy milk  ");
  assert.equal(task.title, "Buy milk");
});

test("normal titles still work and keep inner spaces", () => {
  const tasks = addTask(addTask([], "A"), "Call  the bank");
  assert.deepEqual(tasks.map((t) => t.title), ["A", "Call  the bank"]);
});
