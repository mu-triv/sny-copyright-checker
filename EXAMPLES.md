<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

<!--
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Example: Python file with copyright

```python
#!/usr/bin/env python
# Copyright 2026 SNY Group Corporation
# Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
# License: For licensing see the License.txt file

"""Example Python module"""


def hello_world():
    """Print a greeting"""
    print("Hello, World!")


if __name__ == "__main__":
    hello_world()
```

# Example: SQL file with copyright

```sql
-- Copyright 2026 Sony Group Corporation
-- Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
-- License: For licensing see the License.txt file

CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255)
);

SELECT * FROM users;
```

# Example: C file with copyright

```c
/**************************************************************************
* Copyright 2026 Sony Group Corporation                                   *
* Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation   *
* License: For licensing see the License.txt file                         *
**************************************************************************/

#include <stdio.h>

int main() {
    printf("Hello, World!\n");
    return 0;
}
```

# Example: JavaScript file with copyright

```javascript
// Copyright 2026 Sony Group Corporation
// Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
// License: For licensing see the License.txt file

function helloWorld() {
    console.log("Hello, World!");
}

helloWorld();
```

# Example: File with existing copyright (preserved)

When you run the checker on a file that already has a copyright, it's left unchanged:

```python
# Before running checker:
# Copyright 2025 SNY Group Corporation
# Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
# License: For licensing see the License.txt file

def old_function():
    """This function was written in 2025"""
    pass

# After running checker: UNCHANGED
# The 2025 copyright is preserved, not replaced with 2026
```

# Example: Using --changed-only flag

Check only files that have been modified in git:

```bash
# Scenario: You modified file1.py and file2.py, but not file3.py

# Check only the changed files
$ python -m scripts.main --changed-only

INFO: Checking only changed files from git
INFO: Checking 2 file(s) for copyright notices (auto-fix: True)
INFO: Adding copyright notice to: file1.py
INFO: Adding copyright notice to: file2.py

# file3.py was not checked since it wasn't modified
```

# Example: Using Variables for Maximum Maintainability

The recommended approach uses variables to define common values once:

```
# copyright.txt with variables
[VARIABLES]
SPDX_LICENSE = MIT
COMPANY = Sony Group Corporation
AUTHOR = R&D Center Europe Brussels Laboratory, Sony Group Corporation
YEAR_PATTERN = {regex:\d{4}(-\d{4})?}

[.js, .ts, .go, .rs]
// SPDX-License-Identifier: {SPDX_LICENSE}
// Copyright {YEAR_PATTERN} {COMPANY}
// Author: {AUTHOR}

[.py, .yaml, .yml, .sh]
# SPDX-License-Identifier: {SPDX_LICENSE}
# Copyright {YEAR_PATTERN} {COMPANY}
# Author: {AUTHOR}

[.c, .h, .cpp]
/* SPDX-License-Identifier: {SPDX_LICENSE}
 * Copyright {YEAR_PATTERN} {COMPANY}
 * Author: {AUTHOR} */
```

**Benefits:** Change the company name or license once and it applies to all file types!

# Example: SPDX License Identifiers

The tool fully supports SPDX license identifiers for machine-readable licensing:

```python
# Result after adding copyright with SPDX:
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation

def hello_world():
    print("Hello, World!")
```

You can use any SPDX identifier: `Apache-2.0`, `GPL-3.0-only`, `BSD-3-Clause`, or even complex expressions like `Apache-2.0 OR MIT`.

# Example: Grouped Extensions in Template

You can group multiple file extensions that share the same copyright format:

```
# copyright.txt (traditional format without variables)
[.js, .ts, .go, .rs]
// Copyright {regex:\d{4}(-\d{4})?} Sony Group Corporation
// Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
// License: For licensing see the License.txt file

[.py, .yaml, .yml, .sh]
# Copyright {regex:\d{4}(-\d{4})?} Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file
```

All extensions in a group will use the same copyright format, making maintenance easier.

# Example: Line ending preservation

The tool automatically preserves your file's line ending style:

```bash
# Windows file with CRLF (\\r\\n)
# Before: Uses CRLF line endings
# After adding copyright: Still uses CRLF line endings

# Linux file with LF (\\n)
# Before: Uses LF line endings
# After adding copyright: Still uses LF line endings
```
