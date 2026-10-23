import { addTask, toggleTask, removeTask, remainingCount } from "./tasks.js";
import { loadTasks, saveTasks } from "./storage.js";

let tasks = loadTasks();

const form = document.querySelector("#new-task-form");
const input = document.querySelector("#new-task");
const list = document.querySelector("#task-list");
const counter = document.querySelector("#counter");

function render() {
  list.innerHTML = "";
  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = task.done ? "task done" : "task";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = task.done;
    checkbox.addEventListener("change", () => update(toggleTask(tasks, task.id)));

    const title = document.createElement("span");
    title.textContent = task.title;

    const del = document.createElement("button");
    del.className = "delete";
    del.textContent = "×";
    del.addEventListener("click", () => update(removeTask(tasks, task.id)));

    li.append(checkbox, title, del);
    list.append(li);
  }
  counter.textContent = `${remainingCount(tasks)} tasks left`;
}

function update(next) {
  tasks = next;
  saveTasks(tasks);
  render();
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  update(addTask(tasks, input.value));
  input.value = "";
});

render();
