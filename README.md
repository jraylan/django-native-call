# django-native-call

installação
```
pip install git+https://github.com/jraylan/django-native-call.git
```

functions.py
```python
from native_call.registry import registry

@registry.register(name="soma", arg_types=[int, int], permission=[])
def sum(a,b):
    return a+b
```


HTML
```html
{% load nativecall %}

{% dnc_script %}

<script type="text/javascript">

    function soma(event){
        NativeCall.load_function(event)(1,2).then(alert).catch(alert)
    }
</script>
<a {% native_function soma %} onclick="soma(event)"> Soma 1+2</a>

```


urls.py
```py
    ...
    url(r'^native/', include(registry.get_urls())),
    ...
```
