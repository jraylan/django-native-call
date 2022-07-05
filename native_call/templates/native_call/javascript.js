
(()=>{
    class NativeCall{
        constructor(){
        }
        load_function(event){
            if (event.originalEvent)
                event = event.originalEvent;
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
                        args.map(v=>{
                            formData.append('params[]', v)
                        })
                        formData.append("dnc_csrf", csrf);
                        ajax.open("POST", "{% url 'nativecall_call' %}");
                        ajax.onreadystatechange = ()=>{
                            if(ajax.readyState == 4){
                                let callback = reject
                                if(ajax.status == 200){
                                    callback = resolve
                                }
                                csrf = ajax.getResponseHeader("X-DNC-CSRF")
                                if(csrf){
                                    event.target.setAttribute("dnc-csrf", csrf)
                                }
                                let response = ''
                                try {
                                    response = JSON.parse(ajax.responseText)
                                } catch (e) {
                                    response = ajax.responseText
                                }
                                callback(response,  ajax.status)
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

