let CPF = document.getElementById('CPFId');

function ValidarCPF(CPF) {
    CPFVal = (CPF.value).replaceAll(".","");
    CPFVal = CPFVal.replace("-","");
    var Soma;
    var Resto;
    Soma = 0;
    if (CPFVal.length != 11 || 
		CPFVal == "00000000000" || 
		CPFVal == "11111111111" || 
		CPFVal == "22222222222" || 
		CPFVal == "33333333333" || 
		CPFVal == "44444444444" || 
		CPFVal == "55555555555" || 
		CPFVal == "66666666666" || 
		CPFVal == "77777777777" || 
		CPFVal == "88888888888" || 
		CPFVal == "99999999999") {
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
                CPF.setCustomValidity("");
                return true;
            }
        }
    }
}

function mascara(i){
    var v = i.value;

    if(isNaN(v[v.length-1])){ // impede entrar outro caractere que não seja número
        i.value = v.substring(0, v.length-1);
        return;
    }

    i.setAttribute("maxlength", "14");
    if (v.length == 3 || v.length == 7) i.value += ".";
    if (v.length == 11) i.value += "-";
}

CPF.addEventListener('input', ValidarCPF);