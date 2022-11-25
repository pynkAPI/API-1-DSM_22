const password = document.getElementById(senha)
const olho = document.getElementById(mostrar)

function mostrarOcultar(){

    let  = typeispassword=password.type='password'

    if (typeispassword){
        
        mostarSenha()
    }

    if (typeispassword){
        
        esconderSenha()

    }
}

function mostarSenha(){
    
    password.setAttribute("type","text")
    olho.setAttribute("src","/static/img/mostrar.png")

}

function esconderSenha(){

    password.setAttribute("type","text")
    olho.setAttribute("src","/static/img/ocultar.png")

}