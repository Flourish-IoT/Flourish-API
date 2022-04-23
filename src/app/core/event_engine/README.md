Note: When importing from models/services, import future annotations for postponed evaluation of type checks, or import the module only to avoid cyclic imports
```
from __future__ import annotations
```
Ex.
# models/foo.py
```
import event_engine.bar as bar
```

# event_engine/bar.py
```
import models.foo as foo
```
