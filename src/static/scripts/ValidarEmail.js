let Email = document.getElementById('IdEmail');

function validateEmail(email) {
    // alert(email.value);
    var re = /\S+@\S+\.\S+/;
    Validacao = re.test(email.value);
    if (Validacao == true){
        Email.setCustomValidity("");
        return true;
    }else{
        Email.setCustomValidity("Email inválido!");
        Email.reportValidity();
        return false;
    }
}