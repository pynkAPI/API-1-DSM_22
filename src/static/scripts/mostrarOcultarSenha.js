// para as paginas com apenas uma senha(sem confirmação) 
const password = document.getElementById("senha")
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

// Para as paginas com senha e confirmação de senha


const passwordid = document.getElementById("SenhaId")
const olhoid = document.getElementById("mostrarid")

function mostrarOcultarid(){

    let inputTypeIspasswordid=passwordid.type=='password'

    if (inputTypeIspasswordid){
        
        mostrarSenhaid()
    
    }else{
        
        esconderSenhaid()

    }
}

function mostrarSenhaid(){
    
    passwordid.setAttribute("type","text")
    olhoid.setAttribute("src","/static/img/mostrar.png")

}

function esconderSenhaid(){

    passwordid.setAttribute("type","password")
    olhoid.setAttribute("src","/static/img/ocultar.png")

}


// Para as paginas com senha e confirmação de senha(parte da confirmação)


const passwordidconf = document.getElementById("RepetirsenhaId")
const olhoidconf = document.getElementById("mostraridconf")

function mostrarOcultaridconf(){

    let inputTypeIspasswordidconf=passwordidconf.type=='password'

    if (inputTypeIspasswordidconf){
        
        mostrarSenhaidconf()
    
    }else{
        
        esconderSenhaidconf()

    }
}

function mostrarSenhaidconf(){
    
    passwordidconf.setAttribute("type","text")
    olhoidconf.setAttribute("src","/static/img/mostrar.png")

}

function esconderSenhaidconf(){

    passwordidconf.setAttribute("type","password")
    olhoidconf.setAttribute("src","/static/img/ocultar.png")

}

