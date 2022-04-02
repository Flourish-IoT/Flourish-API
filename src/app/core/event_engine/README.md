Note: When importing from models/services, import the module only to avoid cyclic imports
Ex.
# models/foo.py
```
import event_engine.bar as bar
```

# event_engine/bar.py
```
import models.foo as foo
```