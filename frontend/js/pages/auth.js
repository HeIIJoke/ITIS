import { authenticatedFetch, readError, submitCredentials } from "../auth.js";

const roleLabels = new Map([
  ["guest", "Гость"],
  ["student", "Студент"],
  ["teacher", "Преподаватель"],
  ["admin", "Администратор"],
]);

export function renderCredentials(container, navigate) {
  container.innerHTML = `<section class="account-panel"><h2>Вход в личный кабинет</h2>
    <p>Используйте учётную запись, выданную администратором.</p>
    <form><label>Логин<input name="login" required autocomplete="username" maxlength="50"></label>
    <label>Пароль<input name="password" type="password" required autocomplete="current-password" maxlength="1024"></label>
    <button type="submit">Войти</button><p role="status"></p></form></section>`;
  const form = container.querySelector('form');
  const button = form.querySelector('button');
  const status = form.querySelector('[role="status"]');
  form.addEventListener('submit', async event => {
    event.preventDefault(); button.disabled = true; status.textContent = '';
    try {
      await submitCredentials(Object.fromEntries(new FormData(form)));
      if (form.isConnected) navigate('/', {replace: true});
    } catch (error) { status.textContent = error.message; }
    finally { button.disabled = false; }
  });
}

export function renderProfile(container, account) {
  container.innerHTML = `
    <section class="account-panel">
      <h2>Личный кабинет</h2>
      <dl>
        <dt>Логин</dt><dd id="profile-login"></dd>
        <dt>Роль</dt><dd id="profile-role"></dd>
      </dl>
    </section>`;
  container.querySelector("#profile-login").textContent = account.login;
  container.querySelector("#profile-role").textContent = roleLabels.get(account.role) ?? account.role;
}

export function renderUserAdmin(container) {
  container.innerHTML = `
    <section class="account-panel">
      <h2>Роли пользователей</h2>
      <form id="user-lookup">
        <label>Логин пользователя
          <input name="login" required maxlength="50">
        </label>
        <button type="submit">Найти</button>
      </form>
      <form id="user-role" hidden>
        <p id="target-account"></p>
        <label>Новая роль
          <select name="role">
            <option value="guest">Гость</option>
            <option value="student">Студент</option>
            <option value="teacher">Преподаватель</option>
          </select>
        </label>
        <button type="submit">Сохранить роль</button>
      </form>
      <p role="status"></p>
    </section>`;

  const lookup = container.querySelector("#user-lookup");
  const roleForm = container.querySelector("#user-role");
  const target = roleForm.querySelector("#target-account");
  const status = container.querySelector('[role="status"]');
  let selectedAccount = null;

  lookup.addEventListener("submit", async (event) => {
    event.preventDefault();
    selectedAccount = null;
    roleForm.hidden = true;
    status.textContent = "";
    lookup.querySelector("button").disabled = true;
    try {
      const query = new URLSearchParams(new FormData(lookup));
      const response = await authenticatedFetch(`/api/admin/users?${query}`);
      if (!response.ok) throw new Error(await readError(response, "Не удалось найти пользователя."));
      selectedAccount = await response.json();
      const label = roleLabels.get(selectedAccount.role) ?? selectedAccount.role;
      if (selectedAccount.role === "admin") {
        status.textContent = `${selectedAccount.login} · ${label}`;
        return;
      }
      target.textContent = `${selectedAccount.login} · ${label}`;
      roleForm.elements.role.value = roleLabels.has(selectedAccount.role) ? selectedAccount.role : "guest";
      roleForm.hidden = false;
    } catch (error) {
      status.textContent = error.message;
    } finally {
      lookup.querySelector("button").disabled = false;
    }
  });

  roleForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!selectedAccount) return;
    const query = new URLSearchParams({ login: selectedAccount.login });
    const role = roleForm.elements.role.value;
    const buttons = [lookup.querySelector("button"), roleForm.querySelector("button")];
    buttons.forEach((button) => { button.disabled = true; });
    status.textContent = "";
    try {
      const response = await authenticatedFetch(`/api/admin/users/role?${query}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role }),
      });
      if (!response.ok) throw new Error(await readError(response, "Не удалось изменить роль."));
      selectedAccount = await response.json();
      target.textContent = `${selectedAccount.login} · ${roleLabels.get(selectedAccount.role)}`;
      status.textContent = "Роль сохранена.";
    } catch (error) {
      status.textContent = error.message;
    } finally {
      buttons.forEach((button) => { button.disabled = false; });
    }
  });
}
