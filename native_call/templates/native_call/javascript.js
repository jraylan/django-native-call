
(()=>{
    class NativeCall{
        constructor(){
        }
        load_function(event){
            if(!(event instanceof Event)){
                throw("Argument must be a event.")
            }
            if(!event.isTrusted){
                throw("Event must be a trusted event")
            }
            let csrf = event.target.getAttribute('dnc-csrf')
            event.target.setAttribute("dnc-csrf", "")
            if(!csrf || !csrf.length){
                throw("This element are not allowed to perform this action")
            }
            return (...args)=>{
                return new Promise((resolve, reject)=>{
                    try{
                        let ajax = new XMLHttpRequest();
                        let formData = new FormData();
                        formData.append('params[]', args);
                        formData.append("dnc_csrf", csrf);
                        ajax.open("POST", "{% url 'nativecall_call' %}");
                        ajax.onreadystatechange = ()=>{
                            if(ajax.readyState == 4){
                                if(ajax.status == 200){
                                    try{
                                        resolve(JSON.parse(ajax.responseText));
                                    }catch(e){
                                        reject(ajax.status);
                                    }
                                }
                                else{
                                    reject(ajax.status);
                                }
                                csrf = ajax.getResponseHeader("X-DNC-CSRF")
                                if(csrf){
                                    event.target.setAttribute("dnc-csrf", csrf)
                                }
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

