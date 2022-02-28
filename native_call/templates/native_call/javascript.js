
(()=>{

    class A{
        constructor(){
        }
        load_command(a){
            if(!(event instanceof Event)){
                throw("Argument must be a event.")
            }
            if(!event.isTrusted){
                throw("Event must be a trusted event")
            }
            let csrf = event.target.getAttribute('dnc-csrf')
            if(!csrf || !csrf.length){
                throw("This element are not allowed to perform this action")
            }
            return (...args)=>{
                return new Promise((resolve, reject)=>{
                    try{
                        let ajax
                        if (window.XMLHttpRequest) { // Mozilla, Safari, IE7+ ...
                            ajax  = new XMLHttpRequest();
                        } else if (window.ActiveXObject) { // IE 6 and older
                            ajax  = new ActiveXObject("Microsoft.XMLHTTP");
                        }
                        let formData = new FormData();
                        args.map((arg, i)=>{
                            formData.append('params[]', arg);
                        })
                        formData.append("dnc_csrf", csrf);
                        ajax.open("POST", "{% url 'nativecall:call' %}");
                        if(ajax.readyState == 4 && ajax.status == 200){
                            let data
                            try{
                                resolve(JSON.parse(ajax.responseText));
                            }catch(e){
                                reject(ajax.status);
                            }
                        }
                        ajax.send(formData);
                    }catch(e){
                        reject(e);
                    }
                })
            }
        }
    }
    var _native_call = new NativeCall()
    Object.defineProperty(window, "NativeCall", {
        get: ()=>_native_call,
        set: ()=>{throw("NativeCall"+' cannot be re-declared.')}
      }
    )
})()

