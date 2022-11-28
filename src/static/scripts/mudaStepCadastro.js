const index = document.querySelector('.index');
const cpf = document.querySelector('#cpf');
const CPFId = document.querySelector('#CPFId');
const cadastro = document.querySelector('.cadastro');

function fieldValidator() {
    let valid = false;

    if ((cpf.value && cpf.value != '' && ValidarCPF(cpf))) {
        valid = true;
    }

    return valid;
}

function changeStep(next) {
    if(fieldValidator()){
        if (next) {
            CPFId.value = cpf.value;
            cadastro.style.display = 'flex';
            index.style.display = 'none';
        } else {
            index.style.display = 'block';
            cadastro.style.display = 'none';
        }
    }

}