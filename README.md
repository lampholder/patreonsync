# `patreonsync`

`patreonsync` is a tool to keep [Matrix](https://matrix.org/) room and group membership in sync with a [Patreon](https://www.patreon.com/) subscriber list. It serves roughly the same purpose as [the Patreon-Discord](https://www.patreon.com/apps/discord) integration, in that it provides access to one or more Matrix rooms or groups as a Patreon benefit.

This version of `patreonsync` has been radically reworked to maintain associations between Patreon accounts and Matrix IDs.

## To Install

In the cloned directory, run:

```bash
pip install poetry
poetry build
pip install dist/*.whl --force-reinstall
```

## To Uninstall

In any directory, use the command:

```bash
pip uninstall patreonsync
```

## To Use

Once `patreonsync` is installed, you can run it in any directory. You will need a file in that directory called `config.yaml`.

In order for `patreonsync` to be able to link a patron's Patreon account to that patron's Matrix account, the patron must have their Patreon account's listed email address as a lookup address on their Matrix account.

## `config.yaml`

Before creating your `config.yaml`, you must go to the [Clients & API Keys](https://www.patreon.com/portal/registration/register-clients) on the Patreon Platform site to create credentials for `patreonsync` to connect.

On the Clients & API Keys page:

- Click "Create Client"
- Enter something like the following:
  - App Name: Matrix Sync
  - Description: Sync patron IDs with Matrix for group and room membership
  - App Category: Patron Benefits
  - Redirect URIs: `https://yourdomain.com`
- Click "Create Client"
- To the right of the new entry on the page, click the down arrow.

Leaving the browser window open, in another window create a new text file called `config.yaml` and add the following template:

```yaml
patreon:
    creator_refresh_token: ""
    client_id: ""
    client_secret: ""
```

Back in the browser window, copy the Client ID, Client Secret, and Client Refresh Token from the open Patreon Platform page into the corresponding fields in your `config.yaml` and save the file. In order to use this `config.yaml`, you will need to copy or move it to the directory where you will run the `patreonsync` command.

### Command Line Arguments

`patreonsync` uses boolean command-line arguments. That is, none of these arguments take parameters. However, the arguments `--skiplookup` and `--verbose` can only be used in conjunction with other arguments. Any or all of these arguments can also be "stacked" and used in the same command.

```bash
patreonsync --do-room-invites
```

Using the credentials in `config.yaml`, `patreonsync` will read the current list of patrons from the Patreon account, compare that list to the list of members of the Matrix room listed in `config.yaml`, and invite any new patrons to that room.

```bash
patreonsync --do-room-kicks
```

Using the credentials in `config.yaml`, `patreonsync` will read the current list of patrons from the Patreon account, compare that list to the list of members of the Matrix room listed in `config.yaml`, and kick any former patrons from that room.

```bash
patreonsync --do-group-invites
```

Using the credentials in `config.yaml`, `patreonsync` will read the current list of patrons from the Patreon account, compare that list to the list of members of the Matrix group listed in `config.yaml`, and invite any new patrons to that group.

```bash
patreonsync --do-group-kicks
```

Using the credentials in `config.yaml`, `patreonsync` will read the current list of patrons from the Patreon account, compare that list to the list of members of the Matrix group listed in `config.yaml`, and kick any former patrons from that group.

```bash
patreonsync --createrooms
```

`patreonsync` will read the list of Matrix rooms from `config.yaml`, then, using the credentials in `config.yaml`, compare that list to the list of Matrix rooms in the Matrix account, and create any rooms that do not yet exist.

```bash
patreonsync --skiplookup ...
```

This option can be used in conjunction with any of the other options in order to skip looking up the list in \[I'm not exactly sure what this does, yet...\]

```bash
patreonsync --verbose ...
```

This option will print verbose output to the terminal and is useful when you are first setting up `patreonsync`. (It will do nothing if you are running `patreonsync` as an automated task.)

### Automating the Sync

If you are using a Linux computer, it most likely has the automation service `cron` set up. To set up a regular sync process using `cron`, use the following commands:

```bash
sudo crontab -e
```

This will prompt you for an administrative password and then ask you to choose a text editor. Unless you have a good reason otherwise, you should probable choose `nano`.

In `nano`, scroll down to the bottom of the page and one or more lines like the following:

```cron
*/5 * * * * patreonsync [args]
```

In this example, `*/5` represents every five minutes. If you would rather run `patreonsync`, say, once an hour, you can do the following:

```cron
0 * * * * patreonsync [args]
```

For more advanced configurations, you can use a [`crontab` generator](https://crontab-generator.org/) online and copy and paste the configuration from there.

Once you are satisfied with your changes, type `CTRL-O` to save then `CTRL-X` to exit. The command(s) you added to `crontab` will now run as scheduled whenever the computer is running.

## To Set Up a Development Environment

In the cloned repository, use the following commands:

```bash
pip install poetry precommit
poetry config virtualenvs.in-project true
poetry install
pre-commit install
```

If you are using VS Code, it should now automatically detect the Poetry virtual environment.

`patreonsync` uses [`pre-commit`](https://pre-commit.com/) to maintain code quality. Running `pre-commit install` set up `pre-commit` in the cloned Git repository so that whenever you run a commit `pre-commit` will run automatically. If you would like to run `pre-commit` manually, use the following command:

```bash
pre-commit run --all-files
```

To make a Git commit without running `pre-commit`, use the following command:

```bash
git commit --no-verify
```
