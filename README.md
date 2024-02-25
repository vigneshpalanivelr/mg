# lab-python

Command to run main.py file:

```python main.py```<br>
pip freeze > mg/requirements.txt<br>
pip install -r mg/requirements.txt


Git Commands
```
# Config
git config --global user.email "vignesh.palanivelr@gmail.com"
git config --global user.name "Vignesh Palanivel"

# Clone & Fetch
git clone https://github.com/vigneshpalanivelr/products products
git fetch origin

# Verify the references
git show-ref refs/heads/next/develop
git show-ref refs/remotes/next/develop
git show-refs refs/remotes/origin/next/develop
git show-ref refs/heads/next/develop refs/remotes/next/develop refs/remotes/origin/next/develop

# Switch branch & clean
git checkout next/develop
git reset --hard origin/next/develop
```