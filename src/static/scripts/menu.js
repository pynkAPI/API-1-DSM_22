// variáveis
const btn = document.querySelector('#btn_menu');
const sidebar = document.querySelector('.topo-sidebar');
const home = document.querySelector('.pageContent');

// eventos de escuta do click
btn.addEventListener('click', () => {
    sidebar.classList.toggle('active');
    home.classList.toggle('active');
    btn.classList.toggle('active');
});