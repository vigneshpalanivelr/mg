# Command Help
Command to run
```python main.py```<br>

# Configure workspace
```
pip freeze > mg/requirements.txt
pip install -r mg/requirements.txt
```

# Git Commands
```
# Config
- git config --global user.email "vignesh.palanivelr@gmail.com"
- git config --global user.name "Vignesh Palanivel"
- git config remote.origin.url <url>
- git config remote.origin.fetch +refs/heads/*:refs/remotes/origin/*
- git config --get remote.origin.url

# Find the references in local and origin
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
- git fetch # updates submodules according to their settings
- git fetch origin # updates submodules according to their settings
- git fetch --depth <num> # updates submodules according to their settings
- git fetch --depth <num> --no-recurse-submodules # will not updates submodules
- git fetch --depth <num> --recurse-submodules # updates submodules
- git fetch --prune
- git fetch --heads
- git fetch --tags

# Rebase - Do the changes in local repo
- git rebase
# Pull Rebase - Fetch + Rebase
- git pull --rebase

# Remote commands
# List all your remote fetch/push URLs
- git remote -v
# Listing remote url/refs
- git ls-remote --get-url
- git ls-remote --exit-code <url> refs/heads/mpe refs/tags/mpe

# Submodule
- git submodule foreach "git checkout master"
```
# Argparse
```
# Mutually exclusive group
# If one argument from this group is provided, the others are automatically considered invalid
parser.add_mutually_exclusive_group()
```

# Special Function
```
# String Operations
"PROD,INT".split(',')                   # Output: ['PROD', 'INT']
"hello/world/there".rpartition('/')[0]  # Output: ('hello/world', '/', 'there')
```