# lab-python

Command to run main.py file:
```python main.py```<br>

Configure workspace
```
pip freeze > mg/requirements.txt<br>
pip install -r mg/requirements.txt
```

## Git Commands
```
# Config
- git config --global user.email "vignesh.palanivelr@gmail.com"
- git config --global user.name "Vignesh Palanivel"

# Find the references
- git show-ref refs/heads/next/develop
- git show-ref refs/remotes/next/develop
- git show-refs refs/remotes/origin/next/develop
- git show-ref refs/heads/next/develop refs/remotes/next/develop refs/remotes/origin/next/develop

# Switch branch & clean
- git checkout next/develop
- git reset --hard origin/next/develop

# Initialize repo
- git init -q

# Clone
- git clone <url>
# Clone - Options
- git clone --branch main <url> <dir>
# Clone - Large repositories
Partial Cloning - cloning only a subset of a repository's history and files
- git clone --depth 5000 <url> <dir>
Sparse Checkout - checking out only specific files or directories from a fully cloned repository in local
- git clone --no-checkout <url> <dir>
- git sparse-checkout init
- git sparse-checkout set <pattern>
# Clone - With submodules
- git clone --recursive <url> <dir>

# Fetch - Retrieves changes but not update
- git fetch origin
# Fetch - Merge or Rebase
- git rebase
# Pull Rebase - Fetch and Rebase your local workspace
- git pull --rebase

# Remote commands
git ls-remote --exit-code <url> refs/heads/mpe refs/tags/mpe
```
## Argparse
```
# Mutually exclusive group
# If one argument from this group is provided, the others are automatically considered invalid
parser.add_mutually_exclusive_group()
```

Special Function used
```
# String Operations
"PROD,INT".split(',')                   # Output: ['PROD', 'INT']
"hello/world/there".rpartition('/')[0]  # Output: ('hello/world', '/', 'there')
```
