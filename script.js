const button = document.getElementById("searchBtn");

button.addEventListener("click", buscarUsuario);

async function buscarUsuario() {

    const username = document.getElementById("username").value;

    const profileDiv = document.getElementById("profile");
    const reposDiv = document.getElementById("repos");

    profileDiv.innerHTML = "";
    reposDiv.innerHTML = "";

    try {

        const userResponse = await fetch(`https://api.github.com/users/${username}`);
        const userData = await userResponse.json();

        mostrarPerfil(userData);

        const reposResponse = await fetch(`https://api.github.com/users/${username}/repos`);
        const reposData = await reposResponse.json();

        mostrarRepos(reposData);

    } catch (error) {
        console.log("Erro:", error);
    }
}

function mostrarPerfil(user) {

    const profileDiv = document.getElementById("profile");

    profileDiv.innerHTML = `
        <img src="${user.avatar_url}" width="100">
        <h2>${user.name}</h2>
        <p>${user.bio}</p>
        <p>Seguidores: ${user.followers}</p>
        <p>Seguindo: ${user.following}</p>
    `;
}

function mostrarRepos(repos) {

    const reposDiv = document.getElementById("repos");

    repos.forEach(repo => {

        const repoCard = document.createElement("div");
        repoCard.classList.add("repo");

        repoCard.innerHTML = `
            <h3>${repo.name}</h3>
            <p>${repo.description || "Sem descrição"}</p>
            <p>Linguagem: ${repo.language}</p>
            <p>⭐ ${repo.stargazers_count}</p>
            <a href="${repo.html_url}" target="_blank">Abrir no GitHub</a>
        `;

        reposDiv.appendChild(repoCard);
    });
}