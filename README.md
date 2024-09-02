
> :warning: **This module is now legacy**: The same functionality is now in proton-vpn-network-manager module, version `0.6.3` and upwards.


#  Proton VPN Network Manager Wireguard

The `proton-vpn-network-manager-wireguard` component implements the
[wireguard](https://www.wireguard.com) VPN protocol  using
[NetworkManager](https://networkmanager.dev).

## Development

Even though our CI pipelines always test and build releases using Linux
distribution packages, you can use pip to set up your development environment.

### Proton package registry

If you didn't do it yet, to be able to pip install ProtonVPN components you'll 
need to set up our internal Python package registry. You can do so running the
command below, after replacing `{GITLAB_TOKEN`} with your
[personal access token](https://gitlab.protontech.ch/help/user/profile/personal_access_tokens.md)
with the scope set to `api`.

```shell
pip config set global.index-url https://__token__:{GITLAB_TOKEN}@gitlab.protontech.ch/api/v4/groups/777/-/packages/pypi/simple
```

In the index URL above, `777` is the id of the current root GitLab group, 
the one containing the repositories of all our ProtonVPN components.

### Known issues

This component depends on the `PyGObject` python package. Unfortunately, quite
a few distribution packages are required before being able to pip install it.
Please check the required distribution packages in the
[official documentation](https://pygobject.readthedocs.io/en/latest/devguide/dev_environ.html).

### Virtual environment

You can create the virtual environment and install the rest of dependencies as
follows:

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Tests

You can run the tests with:

```shell
pytest
```
