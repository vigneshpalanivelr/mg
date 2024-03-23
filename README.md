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
- git config --global credential.helper store
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
# Partial Cloning - cloning only a subset of a repository's history and files
- git clone --depth 5000 <url> <dir>
# Sparse Checkout - checking out only specific files or directories from a fully cloned repository in local
- git clone --no-checkout <url> <dir>
- git sparse-checkout init
- git sparse-checkout set <pattern>
# Clone - With submodules
- git clone --recursive <url> <dir>

# Fetch - Retrieves changes but not update
# Updates submodules according to their settings
- git fetch
- git fetch origin
- git fetch --depth <num>
# will not updates submodules irrespective of their settings
- git fetch --depth <num> --no-recurse-submodules
# Updates submodules irrespective of their settings
- git fetch --depth <num> --recurse-submodules
# Removing any local references to remote branches that have been deleted on the remote repository.
- git fetch --prune
# Fetch the latest updates to branch references from the remote repository, without fetching other objects like tags or commits. 
- git fetch --heads
# Fetches all tags from the remote repository without retrieving branch updates. 
- git fetch --tags

# Rebase - Do the changes in local repo
- git rebase

# Pull automatically updates submodules
git pull | git pull --recurse-submodules
# Pull Rebase - Fetch + Rebase
# Rebase the current branch on top of the fetched branch from remote
- git pull --rebase
# Avoid rebasing the current branch after fetching
- git pull --no-rebase
# Git pull automatically takes care of submodules
git pull --depth <num>
# Git pull only the main repo
git pull --no-recurse-submodule
# Only perform a fast-forward merge if possible, otherwise abort.
git pull --ff-only | --ff
# Create a merge commit even if a fast-forward merge is possible.
git pull --no-ff

# Remote commands
# List all your remote fetch/push URLs
- git remote -v
# Listing remote url/refs
- git ls-remote --get-url
- git ls-remote --exit-code <url> refs/heads/mpe refs/tags/mpe

# Tagging
# Lists all tags in the repository
- git tag
# Associated with a commit and contain additional metadata such as the tagger name, email, date, and a message
- git tag -a -m <message> <tag>
# Force creation of tag even if it already present
- git tag -a -m <message> -f <tag>
# Delete tags
- git tag -d <tag1> <tag2>
# Lists tags matching a pattern
- git tag --list <REGEX-PATTERN>
# Lists tags sorted by a specific key (authordate, creatordate, committerdate, refname, taggerdate).
- git tag --sort <>

# Push
git push origin <TAG/BRANCH>
git push --tags
git push -f --tags
git push origin --delete <TAG/BRANCH>


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