document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    var usuario = document.getElementById('login').value;
    var senha = document.getElementById('senha').value;

    // Simula a verificação dos dados de login (usuario e senha)
    if (usuario === 'Jose' && senha === 'Jp12345') {
        window.location.href = 'Dashboard.html';
    } else {
        var messageElement = document.getElementById('message');
        messageElement.style.display = 'block';
        messageElement.textContent = 'Usuário ou senha incorretos'; // Exibe a mensagem na página
    }
});
