// Alterna entre o backend local e o de producao automaticamente.
const API_URL =
    location.hostname === "localhost" || location.hostname === "127.0.0.1"
        ? "http://localhost:8000"
        : "https://github-explorer-api-silecout-epfcaab9chf4b9cb.brazilsouth-01.azurewebsites.net";

const button = document.getElementById("searchBtn");
const input = document.getElementById("username");
const statusEl = document.getElementById("status");
const authStatusEl = document.getElementById("authStatus");
const cadastroStatusEl = document.getElementById("cadastroStatus");
const cadastroBtn = document.getElementById("cadastroBtn");
let token = sessionStorage.getItem("githubExplorerToken");

button.addEventListener("click", buscarUsuario);

// Enter no campo tambem dispara a busca.
input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") buscarUsuario();
});

document
    .getElementById("limparHistoricoBtn")
    .addEventListener("click", limparHistorico);
document.getElementById("loginForm").addEventListener("submit", fazerLogin);
document
    .getElementById("cadastroForm")
    .addEventListener("submit", fazerCadastro);
document.getElementById("logoutBtn").addEventListener("click", () => sair());

// Guarda os repositorios da ultima busca em memoria, para redesenhar
// os cards quando um favorito e adicionado ou removido.
let reposAtuais = [];
// Mapa repo_id -> id do favorito no banco, para saber o que ja esta salvo.
let favoritosPorRepo = {};
// Mapa login -> id do usuario favorito no banco.
let usuariosPorLogin = {};

iniciarSessao();

async function apiFetch(caminho, opcoes = {}) {
    const headers = new Headers(opcoes.headers || {});
    if (token) headers.set("Authorization", `Bearer ${token}`);

    const resposta = await fetch(`${API_URL}${caminho}`, {
        ...opcoes,
        headers,
    });
    if (resposta.status === 401 && token) {
        sair("Sua sessão expirou. Entre novamente.");
    }
    return resposta;
}

function mostrarAuthStatus(texto, tipo = "") {
    authStatusEl.textContent = texto;
    authStatusEl.className = "status " + tipo;
}

async function iniciarSessao() {
    if (!token) {
        atualizarTelaSessao(null);
        return;
    }
    try {
        const resposta = await apiFetch("/auth/me");
        if (!resposta.ok) return;
        atualizarTelaSessao(await resposta.json());
        await carregarDadosPrivados();
    } catch (error) {
        sair("Não foi possível validar a sessão.");
    }
}

async function fazerCadastro(evento) {
    evento.preventDefault();
    cadastroStatusEl.textContent = "Cadastrando, aguarde...";
    cadastroStatusEl.className = "form-status carregando";
    cadastroBtn.disabled = true;
    cadastroBtn.textContent = "Cadastrando...";

    const corpo = {
        nome: document.getElementById("cadastroNome").value,
        email: document.getElementById("cadastroEmail").value,
        senha: document.getElementById("cadastroSenha").value,
    };
    try {
        const resposta = await apiFetch("/auth/cadastro", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(corpo),
        });
        if (!resposta.ok) {
            let mensagem = "Não foi possível criar a conta. Tente novamente.";
            if (resposta.status === 409) {
                mensagem = "Este e-mail já está cadastrado.";
            } else if (resposta.status === 422) {
                mensagem = "Confira o nome, o e-mail e a senha de no mínimo 12 caracteres.";
            } else if (resposta.status >= 500) {
                mensagem = "O servidor não conseguiu concluir o cadastro. Tente novamente em instantes.";
            }
            cadastroStatusEl.textContent = mensagem;
            cadastroStatusEl.className = "form-status erro";
            return;
        }
        cadastroStatusEl.textContent =
            "✓ Cadastro realizado com sucesso! Agora entre com seu e-mail e senha.";
        cadastroStatusEl.className = "form-status ok";
        document.getElementById("loginEmail").value = corpo.email;
        document.getElementById("cadastroForm").reset();
    } catch (error) {
        cadastroStatusEl.textContent =
            "Não foi possível conectar ao servidor. Verifique a conexão e tente novamente.";
        cadastroStatusEl.className = "form-status erro";
    } finally {
        cadastroBtn.disabled = false;
        cadastroBtn.textContent = "Cadastrar";
    }
}

async function fazerLogin(evento) {
    evento.preventDefault();
    const corpo = {
        email: document.getElementById("loginEmail").value,
        senha: document.getElementById("loginSenha").value,
    };
    try {
        const resposta = await apiFetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(corpo),
        });
        if (!resposta.ok) {
            mostrarAuthStatus("E-mail ou senha inválidos.", "erro");
            return;
        }
        const dados = await resposta.json();
        token = dados.access_token;
        sessionStorage.setItem("githubExplorerToken", token);
        atualizarTelaSessao(dados.usuario);
        mostrarAuthStatus("");
        document.getElementById("loginForm").reset();
        await carregarDadosPrivados();
    } catch (error) {
        mostrarAuthStatus("Erro de conexão ao entrar.", "erro");
    }
}

function atualizarTelaSessao(usuario) {
    document.getElementById("authForms").classList.toggle("hidden", !!usuario);
    document.getElementById("sessao").classList.toggle("hidden", !usuario);
    document.getElementById("conteudoPrivado").classList.toggle("hidden", !usuario);
    document.getElementById("sessaoUsuario").textContent = usuario
        ? `Olá, ${usuario.nome}`
        : "";
}

async function carregarDadosPrivados() {
    await Promise.all([
        carregarFavoritos(),
        carregarHistorico(),
        carregarUsuariosFavoritos(),
    ]);
}

function sair(mensagem = "") {
    token = null;
    sessionStorage.removeItem("githubExplorerToken");
    favoritosPorRepo = {};
    usuariosPorLogin = {};
    document.getElementById("loginForm").reset();
    document.getElementById("cadastroForm").reset();
    atualizarTelaSessao(null);
    mostrarAuthStatus(mensagem);
}

function mostrarStatus(texto, tipo = "") {
    statusEl.textContent = texto;
    statusEl.className = "status " + tipo;
}

async function buscarUsuario() {
    const username = input.value.trim();

    const profileDiv = document.getElementById("profile");
    const reposSection = document.getElementById("reposSection");
    const reposDiv = document.getElementById("repos");

    profileDiv.innerHTML = "";
    reposDiv.innerHTML = "";
    reposSection.classList.add("hidden");

    if (!username) {
        mostrarStatus("Digite um nome de usuário.", "erro");
        return;
    }

    mostrarStatus("Buscando...");

    try {
        const userResponse = await fetch(
            `https://api.github.com/users/${username}`
        );

        if (!userResponse.ok) {
            mostrarStatus(`Usuário "${username}" não encontrado.`, "erro");
            return;
        }

        const userData = await userResponse.json();
        mostrarPerfil(userData);

        const reposResponse = await fetch(
            `https://api.github.com/users/${username}/repos?per_page=100&sort=updated`
        );
        const reposData = await reposResponse.json();

        reposAtuais = Array.isArray(reposData) ? reposData : [];
        mostrarRepos();
        reposSection.classList.remove("hidden");

        mostrarStatus("");

        // Registra a busca no historico (nao trava a interface se falhar).
        salvarBusca(userData.login, userData.avatar_url);
    } catch (error) {
        console.log("Erro:", error);
        mostrarStatus("Erro ao buscar. Verifique a conexão.", "erro");
    }
}

function mostrarPerfil(user) {
    const profileDiv = document.getElementById("profile");

    const nome = user.name || user.login;
    const bio = user.bio ? `<p>${user.bio}</p>` : "";
    const jaFavoritado = usuariosPorLogin[user.login] !== undefined;

    const botao = jaFavoritado
        ? `<button class="btn-remover" id="btnUsuario">Remover usuário dos favoritos</button>`
        : `<button class="btn-favoritar" id="btnUsuario">⭐ Favoritar usuário</button>`;

    profileDiv.innerHTML = `
        <img src="${user.avatar_url}" width="100" alt="Avatar de ${nome}">
        <h2>${nome}</h2>
        ${bio}
        <p>Seguidores: ${user.followers} · Seguindo: ${user.following}</p>
        ${botao}
    `;

    document.getElementById("btnUsuario").addEventListener("click", () => {
        if (usuariosPorLogin[user.login] !== undefined) {
            removerUsuarioFavorito(usuariosPorLogin[user.login]);
        } else {
            adicionarUsuarioFavorito(user);
        }
    });
}

function mostrarRepos() {
    const reposDiv = document.getElementById("repos");
    reposDiv.innerHTML = "";

    if (reposAtuais.length === 0) {
        reposDiv.innerHTML = "<p>Nenhum repositório público.</p>";
        return;
    }

    reposAtuais.forEach((repo) => {
        const repoCard = document.createElement("div");
        repoCard.classList.add("repo");

        const linguagem = repo.language || "N/A";
        const jaFavoritado = favoritosPorRepo[repo.id] !== undefined;

        const botao = jaFavoritado
            ? `<button class="btn-remover" data-repo="${repo.id}">Remover dos favoritos</button>`
            : `<button class="btn-favoritar" data-repo="${repo.id}">⭐ Favoritar</button>`;

        repoCard.innerHTML = `
            <h3>${repo.name}</h3>
            <p>${repo.description || "Sem descrição"}</p>
            <p>Linguagem: ${linguagem} · ⭐ ${repo.stargazers_count}</p>
            <a href="${repo.html_url}" target="_blank">Abrir no GitHub</a>
            ${botao}
        `;

        reposDiv.appendChild(repoCard);
    });

    // Liga os botoes de favoritar / remover.
    reposDiv.querySelectorAll(".btn-favoritar").forEach((btn) => {
        btn.addEventListener("click", () =>
            adicionarFavorito(Number(btn.dataset.repo))
        );
    });
    reposDiv.querySelectorAll(".btn-remover").forEach((btn) => {
        btn.addEventListener("click", () => {
            const favId = favoritosPorRepo[Number(btn.dataset.repo)];
            removerFavorito(favId);
        });
    });
}

// ---------- Favoritos ----------

async function carregarFavoritos() {
    try {
        const resp = await apiFetch("/favoritos");
        const favoritos = await resp.json();

        favoritosPorRepo = {};
        favoritos.forEach((f) => {
            favoritosPorRepo[f.repo_id] = f.id;
        });

        mostrarFavoritos(favoritos);
        mostrarRepos(); // atualiza os botoes dos cards
    } catch (error) {
        console.log("Erro ao carregar favoritos:", error);
    }
}

function mostrarFavoritos(favoritos) {
    const div = document.getElementById("favoritos");
    div.innerHTML = "";

    if (favoritos.length === 0) {
        div.innerHTML = "<p class='vazio'>Nenhum favorito ainda.</p>";
        return;
    }

    favoritos.forEach((f) => {
        const card = document.createElement("div");
        card.classList.add("favorito");

        const nota = f.nota || "";

        card.innerHTML = `
            <h4><a href="${f.url}" target="_blank">${f.full_name}</a></h4>
            <p>${f.descricao || "Sem descrição"}</p>
            <p>Linguagem: ${f.linguagem || "N/A"} · ⭐ ${f.estrelas}</p>
            <textarea class="nota" placeholder="Sua nota...">${nota}</textarea>
            <div class="favorito-acoes">
                <button class="btn-nota" data-id="${f.id}">Salvar nota</button>
                <button class="btn-remover" data-id="${f.id}">Remover</button>
            </div>
        `;

        div.appendChild(card);
    });

    div.querySelectorAll(".btn-nota").forEach((btn) => {
        btn.addEventListener("click", () => {
            const textarea = btn
                .closest(".favorito")
                .querySelector(".nota");
            salvarNota(Number(btn.dataset.id), textarea.value);
        });
    });
    div.querySelectorAll(".btn-remover").forEach((btn) => {
        btn.addEventListener("click", () =>
            removerFavorito(Number(btn.dataset.id))
        );
    });
}

async function adicionarFavorito(repoId) {
    const repo = reposAtuais.find((r) => r.id === repoId);
    if (!repo) return;

    const corpo = {
        repo_id: repo.id,
        nome: repo.name,
        full_name: repo.full_name,
        descricao: repo.description,
        url: repo.html_url,
        linguagem: repo.language,
        estrelas: repo.stargazers_count,
    };

    try {
        const resp = await apiFetch("/favoritos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(corpo),
        });

        if (resp.status === 409) {
            mostrarStatus("Esse repositório já está nos favoritos.", "erro");
            return;
        }

        await carregarFavoritos();
    } catch (error) {
        console.log("Erro ao favoritar:", error);
    }
}

async function salvarNota(favId, nota) {
    try {
        await apiFetch(`/favoritos/${favId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nota }),
        });
        mostrarStatus("Nota salva.", "ok");
    } catch (error) {
        console.log("Erro ao salvar nota:", error);
    }
}

async function removerFavorito(favId) {
    try {
        await apiFetch(`/favoritos/${favId}`, { method: "DELETE" });
        await carregarFavoritos();
    } catch (error) {
        console.log("Erro ao remover favorito:", error);
    }
}

// ---------- Historico ----------

async function salvarBusca(username, avatarUrl) {
    try {
        await apiFetch("/buscas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, avatar_url: avatarUrl }),
        });
        carregarHistorico();
    } catch (error) {
        console.log("Erro ao salvar busca:", error);
    }
}

async function carregarHistorico() {
    try {
        const resp = await apiFetch("/buscas");
        const buscas = await resp.json();
        mostrarHistorico(buscas);
    } catch (error) {
        console.log("Erro ao carregar histórico:", error);
    }
}

function mostrarHistorico(buscas) {
    const div = document.getElementById("historico");
    div.innerHTML = "";

    if (buscas.length === 0) {
        div.innerHTML = "<p class='vazio'>Nenhuma busca ainda.</p>";
        return;
    }

    buscas.forEach((b) => {
        const item = document.createElement("div");
        item.classList.add("historico-item");

        const avatar = b.avatar_url
            ? `<img src="${b.avatar_url}" width="30">`
            : "";

        item.innerHTML = `
            ${avatar}
            <span class="historico-nome" data-user="${b.username}">${b.username}</span>
            <button class="btn-remover" data-id="${b.id}">✕</button>
        `;

        div.appendChild(item);
    });

    // Clicar no nome refaz a busca.
    div.querySelectorAll(".historico-nome").forEach((el) => {
        el.addEventListener("click", () => {
            input.value = el.dataset.user;
            buscarUsuario();
        });
    });
    div.querySelectorAll(".btn-remover").forEach((btn) => {
        btn.addEventListener("click", () =>
            removerBusca(Number(btn.dataset.id))
        );
    });
}

async function removerBusca(buscaId) {
    try {
        await apiFetch(`/buscas/${buscaId}`, { method: "DELETE" });
        carregarHistorico();
    } catch (error) {
        console.log("Erro ao remover busca:", error);
    }
}

async function limparHistorico() {
    try {
        await apiFetch("/buscas", { method: "DELETE" });
        carregarHistorico();
    } catch (error) {
        console.log("Erro ao limpar histórico:", error);
    }
}
// ---------- Usuarios favoritos ----------

async function carregarUsuariosFavoritos() {
    try {
        const resp = await apiFetch("/usuarios-favoritos");
        const usuarios = await resp.json();

        usuariosPorLogin = {};
        usuarios.forEach((u) => {
            usuariosPorLogin[u.login] = u.id;
        });

        mostrarUsuariosFavoritos(usuarios);
    } catch (error) {
        console.log("Erro ao carregar usuários favoritos:", error);
    }
}

function mostrarUsuariosFavoritos(usuarios) {
    const div = document.getElementById("usuariosFavoritos");
    div.innerHTML = "";

    if (usuarios.length === 0) {
        div.innerHTML = "<p class='vazio'>Nenhum usuário favorito.</p>";
        return;
    }

    usuarios.forEach((u) => {
        const card = document.createElement("div");
        card.classList.add("favorito");

        const avatar = u.avatar_url
            ? `<img src="${u.avatar_url}" width="40">`
            : "";
        const nota = u.nota || "";

        card.innerHTML = `
            <div class="usuario-cabecalho">
                ${avatar}
                <h4 class="usuario-login" data-user="${u.login}">${u.nome || u.login}</h4>
            </div>
            <p>${u.bio || "Sem bio"}</p>
            <textarea class="nota" placeholder="Sua nota...">${nota}</textarea>
            <div class="favorito-acoes">
                <button class="btn-nota" data-id="${u.id}">Salvar nota</button>
                <button class="btn-remover" data-id="${u.id}">Remover</button>
            </div>
        `;

        div.appendChild(card);
    });

    // Clicar no nome refaz a busca.
    div.querySelectorAll(".usuario-login").forEach((el) => {
        el.addEventListener("click", () => {
            input.value = el.dataset.user;
            buscarUsuario();
        });
    });
    div.querySelectorAll(".btn-nota").forEach((btn) => {
        btn.addEventListener("click", () => {
            const textarea = btn.closest(".favorito").querySelector(".nota");
            salvarNotaUsuario(Number(btn.dataset.id), textarea.value);
        });
    });
    div.querySelectorAll(".btn-remover").forEach((btn) => {
        btn.addEventListener("click", () =>
            removerUsuarioFavorito(Number(btn.dataset.id))
        );
    });
}

async function adicionarUsuarioFavorito(user) {
    const corpo = {
        login: user.login,
        nome: user.name,
        avatar_url: user.avatar_url,
        url: user.html_url,
        bio: user.bio,
    };

    try {
        const resp = await apiFetch("/usuarios-favoritos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(corpo),
        });

        if (resp.status === 409) {
            mostrarStatus("Esse usuário já está nos favoritos.", "erro");
            return;
        }

        await carregarUsuariosFavoritos();
        // Redesenha o perfil para o botao virar "Remover".
        const r = await fetch(`https://api.github.com/users/${user.login}`);
        if (r.ok) mostrarPerfil(await r.json());
    } catch (error) {
        console.log("Erro ao favoritar usuário:", error);
    }
}

async function salvarNotaUsuario(usuarioId, nota) {
    try {
        await apiFetch(`/usuarios-favoritos/${usuarioId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nota }),
        });
        mostrarStatus("Nota salva.", "ok");
    } catch (error) {
        console.log("Erro ao salvar nota do usuário:", error);
    }
}

async function removerUsuarioFavorito(usuarioId) {
    try {
        await apiFetch(`/usuarios-favoritos/${usuarioId}`, {
            method: "DELETE",
        });
        await carregarUsuariosFavoritos();
        // Redesenha o perfil se o usuario removido for o que esta na tela.
        const loginAtual = input.value.trim();
        if (loginAtual) {
            const r = await fetch(`https://api.github.com/users/${loginAtual}`);
            if (r.ok) mostrarPerfil(await r.json());
        }
    } catch (error) {
        console.log("Erro ao remover usuário favorito:", error);
    }
}
