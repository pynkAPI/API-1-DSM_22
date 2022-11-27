// para as paginas com apenas uma senha(sem confirmação) 
const password = document.getElementById("textoInputElemento")
const olho = document.getElementById("mostrar")

function mostrarOcultar(){

    let inputTypeIspassword=password.type=='password'

    if (inputTypeIspassword){
        
        mostrarSenha()
    
    }else{
        
        esconderSenha()

    }
}

function mostrarSenha(){
    
    password.setAttribute("type","text")
    olho.setAttribute("src","/static/img/mostrar.png")

}

function esconderSenha(){

    password.setAttribute("type","password")
    olho.setAttribute("src","/static/img/ocultar.png")

}