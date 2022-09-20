let CPF = document.getElementById('CPFId');
function ValidarCPF() {
    CPFVal = CPF.value;
    var Soma;
    var Resto;
    Soma = 0;
    if (CPFVal == "00000000000") {
        CPF.setCustomValidity("CPF inválido!");
        CPF.reportValidity();
        return false;
    }else{
        for (i=1; i<=9; i++) Soma = Soma + parseInt(CPFVal.substring(i-1, i)) * (11 - i);
        Resto = (Soma * 10) % 11;

        if ((Resto == 10) || (Resto == 11))  Resto = 0;
        if (Resto != parseInt(CPFVal.substring(9, 10)) ) {
            CPF.setCustomValidity("CPF inválido!");
            CPF.reportValidity();
            return false;
        }else{
            Soma = 0;
            for (i = 1; i <= 10; i++) Soma = Soma + parseInt(CPFVal.substring(i-1, i)) * (12 - i);
            Resto = (Soma * 10) % 11;

            if ((Resto == 10) || (Resto == 11))  Resto = 0;
            if (Resto != parseInt(CPFVal.substring(10, 11) ) ) {
                CPF.setCustomValidity("CPF inválido!");
                CPF.reportValidity();
                return false;
            }else{
                return true;
            }
        }
    }
}

CPF.addEventListener('input', ValidarCPF);