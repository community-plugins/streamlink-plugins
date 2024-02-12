# streamlink-plugins

## Installation
- using git
```
# install
git clone https://github.com/community-plugins/streamlink-plugins $HOME/.local/share/streamlink

# update
cd "$HOME/.local/share/streamlink"
git pull --rebase
```
## recommend to do

Some plugins may require an additional dependency, [cloudscraper](https://github.com/VeNoMouS/cloudscraper), to access a website's cloudflare-protected public API. You can download it if you encounter any issues.

### Install
* pip install [cloudscraper](https://pypi.org/project/cloudscraper)
  * For Windows users with streamlink builds which come bundled with an embedded Python environment, regular pip will not suffice and a ModuleNotFoundError will be raised when running streamlink. You can fix this by adding ```--target=<StreamLinkInstallPath>\pkgs```

# Record bat
- check [Record](Recorder/README.md) for more usage.
