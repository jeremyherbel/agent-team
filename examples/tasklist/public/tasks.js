// Pure task-list logic, shared by the browser app and the tests.

let nextId = 1;

export function createTask(title) {
  return { id: `t${Date.now()}-${nextId++}`, title, done: false };
}

export function addTask(tasks, title) {
  if (title === "") {
    return tasks;
  }
  return [...tasks, createTask(title)];
}

export function toggleTask(tasks, id) {
  return tasks.map((t) => (t.id === id ? { ...t, done: !t.done } : t));
}

export function removeTask(tasks, id) {
  return tasks.filter((t) => t.id !== id);
}

export function remainingCount(tasks) {
  return tasks.filter((t) => !t.done).length;
}
