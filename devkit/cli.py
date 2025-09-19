
import os
from pathlib import Path
from typing import Optional
import typer
import click
from difflib import get_close_matches

from .context import Context
from .iofmt import Exit, envelope, emit
from .ux import console, table, confirm
from .services import load_config, save_config, find_service
from .config_model import Service, Config
from .rails import rails_bin, infer_db_name
from .postgres import choose_restore_tool, validate_connection
from .shell import run, check
from .doctor import diagnose
from .introspect import typer_reference

class DevkitGroup(typer.core.TyperGroup):
    def get_command(self, ctx, cmd_name):
        cmd = super().get_command(ctx, cmd_name)
        if cmd is None:
            B = "\033[1m"; R = "\033[0m"
            click.echo(f"{B}ERROR:{R} unknown command: {cmd_name}", err=True)
            choices = list(self.commands.keys())
            match = get_close_matches(cmd_name, choices, n=1)
            if match:
                click.echo(f"{B}TIP:{R} Did you mean '{match[0]}'?", err=True)
            path = ctx.command_path or "devkit"
            click.echo(f"{B}TIP:{R} Run '{path} --help' for usage.", err=True)
            ctx.exit(2)
        return cmd


app = typer.Typer(no_args_is_help=False, add_help_option=False, cls=DevkitGroup)
service_app = typer.Typer(help="Manage services (Rails apps + backups).", no_args_is_help=False, add_help_option=False, cls=DevkitGroup)
db_app = typer.Typer(help="Database operations.", no_args_is_help=False, add_help_option=False, cls=DevkitGroup)
meta_app = typer.Typer(help="Introspection/metadata commands for agents.", no_args_is_help=False, add_help_option=False, cls=DevkitGroup)

app.add_typer(service_app, name="service", no_args_is_help=False, invoke_without_command=True)
app.add_typer(db_app, name="db", no_args_is_help=False, invoke_without_command=True)
app.add_typer(meta_app, name="meta", no_args_is_help=False, invoke_without_command=True)
app.add_typer(service_app, name="services", no_args_is_help=False, invoke_without_command=True)

CTX = Context()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    format: str = typer.Option("text", "--format", help="Output format: text|json"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Answer yes to destructive prompts"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Allow interactive prompts"),
    safe: bool = typer.Option(False, "--safe", help="Safe mode; requires --yes for destructive operations"),
    quiet: bool = typer.Option(False, "--quiet", help="Reduced output"),
    verbose: bool = typer.Option(False, "--verbose", help="More verbose output"),
    trace: bool = typer.Option(False, "--trace", help="Show executed commands"),
    show_help: bool = typer.Option(False, "--help", is_flag=True, help="Show help for command", rich_help_panel=None, show_default=False, is_eager=True),
):
    CTX.format = format  # type: ignore
    CTX.yes = yes
    CTX.interactive = interactive
    CTX.safe = safe or os.environ.get("DEVKIT_SAFE") == "1"
    CTX.quiet = quiet
    CTX.verbose = verbose
    CTX.trace = trace
    if show_help or ctx.invoked_subcommand is None:
        B = "\033[1m"; R = "\033[0m"
        typer.echo("Work seamlessly with DevKit from the command line.\n")
        typer.echo(f"{B}USAGE{R}")
        typer.echo("  devkit <command> <subcommand> [options]\n")
        typer.echo(f"{B}CORE COMMANDS{R}")
        typer.echo("  service:      Manage services (Rails apps + backups)")
        typer.echo("  db:           Database operations")
        typer.echo("  meta:         Introspection/metadata commands for agents\n")
        typer.echo(f"{B}ADDITIONAL COMMANDS{R}")
        typer.echo("  completion:   Generate shell completion scripts\n")
        typer.echo(f"{B}HELP TOPICS{R}")
        typer.echo("  environment:  Environment variables used by devkit")
        typer.echo("  exit-codes:   Exit codes used by devkit")
        typer.echo("  formatting:   Formatting options for JSON output")
        typer.echo("  reference:    A comprehensive reference of all commands\n")
        typer.echo(f"{B}FLAGS{R}")
        typer.echo("  --help      Show help for command")
        typer.echo("  --version   Show devkit version\n")
        typer.echo(f"{B}EXAMPLES{R}")
        typer.echo("  devkit service list")
        typer.echo("  devkit service add --name myapp --app /path --backup /file.dump")
        typer.echo("  devkit db reset myapp --backup /file.dump\n")
        typer.echo(f"{B}LEARN MORE{R}")
        typer.echo("  Use 'devkit <command> --help' for more information.")
        typer.echo("  Read the manual in docs/index.md\n")
        raise typer.Exit(0)


@service_app.callback(invoke_without_command=True)
def _service_group_entry(ctx: typer.Context, help: bool = typer.Option(False, "--help", is_flag=True, help="Show help for command", is_eager=True)):
    if help or ctx.invoked_subcommand is None:
        B = "\033[1m"; R = "\033[0m"
        typer.echo(f"{B}SERVICES{R}")
        typer.echo("  list         List configured services")
        typer.echo("  add          Add a service")
        typer.echo("  edit NAME    Edit a service")
        typer.echo("  rm NAME      Remove a service\n")
        typer.echo(f"{B}USAGE{R}")
        typer.echo("  devkit service <subcommand> [options]\n")
        typer.echo(f"{B}EXAMPLES{R}")
        typer.echo("  devkit service list")
        typer.echo("  devkit service add --name myapp --app /path --backup /file.dump")
        raise typer.Exit(0)


@db_app.callback(invoke_without_command=True)
def _db_group_entry(ctx: typer.Context, help: bool = typer.Option(False, "--help", is_flag=True, help="Show help for command", is_eager=True)):
    if help or ctx.invoked_subcommand is None:
        B = "\033[1m"; R = "\033[0m"
        typer.echo(f"{B}DATABASE{R}")
        typer.echo("  reset NAME   Drop, create and restore from backup\n")
        typer.echo(f"{B}USAGE{R}")
        typer.echo("  devkit db <subcommand> [options]\n")
        typer.echo(f"{B}EXAMPLES{R}")
        typer.echo("  devkit db reset myapp --backup /file.dump")
        raise typer.Exit(0)


@meta_app.callback(invoke_without_command=True)
def _meta_group_entry(ctx: typer.Context, help: bool = typer.Option(False, "--help", is_flag=True, help="Show help for command", is_eager=True)):
    if help or ctx.invoked_subcommand is None:
        B = "\033[1m"; R = "\033[0m"
        typer.echo(f"{B}META{R}")
        typer.echo("  reference    Emit a JSON command reference")
        typer.echo("  describe     Emit full JSON description\n")
        typer.echo(f"{B}USAGE{R}")
        typer.echo("  devkit meta <subcommand> [options]")
        raise typer.Exit(0)


 


# ------------------- service -------------------
@service_app.command("list")
def service_list():
    cfg = load_config()
    if CTX.format == "json":
        payload = envelope(
            "service list",
            "ok",
            Exit.OK,
            {"services": [s.model_dump() for s in cfg.services]},
        )
        raise typer.Exit(code=emit(CTX, payload))
    else:
        if not cfg.services:
            typer.echo("no services configured")
            typer.echo("tip: add one with 'devkit service add --name NAME --app PATH --backup FILE'\n")
            raise typer.Exit(0)
        rows = [(s.name, s.app_path, s.backup_path, s.env) for s in cfg.services]
        typer.echo(table(["Name", "App Path", "Backup Path", "Env"], rows))


@service_app.command("add", context_settings={"help_option_names": []})
def service_add(
    name: Optional[str] = typer.Option(None, "--name"),
    app_path: Optional[Path] = typer.Option(None, "--app", exists=True, dir_okay=True, file_okay=False),
    backup_path: Optional[Path] = typer.Option(None, "--backup"),
    env: str = typer.Option("development", "--env"),
    db_user: str = typer.Option("postgres", "--db-user"),
    db_host: str = typer.Option("localhost", "--db-host"),
    db_port: int = typer.Option(5432, "--db-port"),
    show_help: bool = typer.Option(False, "--help", is_flag=True, is_eager=True, help="Show help for command"),
):
    if show_help or not (name and app_path and backup_path):
        B = "\033[1m"; R = "\033[0m"
        typer.echo(f"{B}SERVICE ADD{R}")
        typer.echo("  Add a Rails app + backup entry\n")
        typer.echo(f"{B}USAGE{R}")
        typer.echo("  devkit service add --name NAME --app PATH --backup FILE [options]\n")
        typer.echo(f"{B}OPTIONS{R}")
        typer.echo("  --name NAME        Service name")
        typer.echo("  --app PATH         Path to Rails app")
        typer.echo("  --backup FILE      Path to backup file (.dump/.sql)")
        typer.echo("  --env ENV          Rails env (default: development)")
        typer.echo("  --db-user USER     DB user (default: postgres)")
        typer.echo("  --db-host HOST     DB host (default: localhost)")
        typer.echo("  --db-port PORT     DB port (default: 5432)\n")
        typer.echo(f"{B}EXAMPLES{R}")
        typer.echo("  devkit service add --name myapp --app /path --backup /file.dump")
        raise typer.Exit(0)
    cfg = load_config()
    if find_service(cfg, name):
        payload = envelope("service add", "error", Exit.INVALID_ARGS, errors=[{"code":"DUPLICATE","detail":f"Service {name} already exists"}])
        raise typer.Exit(code=emit(CTX, payload))
    s = Service(name=name, app_path=str(app_path), backup_path=str(backup_path), env=env)
    s.db.user = db_user; s.db.host = db_host; s.db.port = db_port
    cfg.services.append(s)
    save_config(cfg)
    if CTX.format == "json":
        payload = envelope("service add", "ok", Exit.OK, {"service": s.model_dump()})
        raise typer.Exit(code=emit(CTX, payload))
    typer.echo(f"service {name} added")


@service_app.command("edit", context_settings={"help_option_names": []})
def service_edit(
    name: Optional[str] = typer.Argument(None),
    app_path: Optional[Path] = typer.Option(None, "--app"),
    backup_path: Optional[Path] = typer.Option(None, "--backup"),
    env: Optional[str] = typer.Option(None, "--env"),
    db_user: Optional[str] = typer.Option(None, "--db-user"),
    db_host: Optional[str] = typer.Option(None, "--db-host"),
    db_port: Optional[int] = typer.Option(None, "--db-port"),
    show_help: bool = typer.Option(False, "--help", is_flag=True, is_eager=True, help="Show help for command"),
):
    if show_help or name is None or all(v is None for v in [app_path, backup_path, env, db_user, db_host, db_port]):
        B = "\033[1m"; R = "\033[0m"
        typer.echo(f"{B}SERVICE EDIT{R}")
        typer.echo("  Edit a service entry\n")
        typer.echo(f"{B}USAGE{R}")
        typer.echo("  devkit service edit NAME [--app PATH] [--backup FILE] [--env ENV] [DB options]\n")
        typer.echo(f"{B}EXAMPLES{R}")
        typer.echo("  devkit service edit myapp --env production")
        raise typer.Exit(0)
    cfg = load_config()
    s = find_service(cfg, name)
    if not s:
        payload = envelope("service edit", "error", Exit.NOT_FOUND, errors=[{"code":"NOT_FOUND","detail":name}])
        raise typer.Exit(code=emit(CTX, payload))
    if app_path:
        s.app_path = str(app_path)
    if backup_path:
        s.backup_path = str(backup_path)
    if env:
        s.env = env
    if db_user:
        s.db.user = db_user
    if db_host:
        s.db.host = db_host
    if db_port:
        s.db.port = db_port
    save_config(cfg)
    if CTX.format == "json":
        payload = envelope("service edit", "ok", Exit.OK, {"service": s.model_dump()})
        raise typer.Exit(code=emit(CTX, payload))
    typer.echo(f"service {name} updated")


@service_app.command("rm", context_settings={"help_option_names": []})
def service_rm(
    name: Optional[str] = typer.Argument(None),
    yes: bool = typer.Option(False, "--yes", "-y"),
    show_help: bool = typer.Option(False, "--help", is_flag=True, is_eager=True, help="Show help for command"),
):
    show_help = False  # placeholder: Typer doesn't allow adding --help on positional-only nicely here
    if show_help or name is None:
        B = "\033[1m"; R = "\033[0m"
        typer.echo(f"{B}SERVICE REMOVE{R}")
        typer.echo("  Remove a service entry\n")
        typer.echo(f"{B}USAGE{R}")
        typer.echo("  devkit service rm NAME [-y]\n")
        typer.echo(f"{B}EXAMPLES{R}")
        typer.echo("  devkit service rm myapp -y")
        raise typer.Exit(0)
    cfg = load_config()
    s = find_service(cfg, name)
    if not s:
        payload = envelope("service rm", "error", Exit.NOT_FOUND, errors=[{"code":"NOT_FOUND","detail":name}])
        raise typer.Exit(code=emit(CTX, payload))
    proceed = yes or CTX.yes or (CTX.interactive and confirm(f"Delete service \"{name}\"?"))
    if not proceed:
        raise typer.Exit(code=Exit.OK)
    cfg.services = [x for x in cfg.services if x.name != name]
    save_config(cfg)
    if CTX.format == "json":
        payload = envelope("service rm", "ok", Exit.OK, {"removed": name})
        raise typer.Exit(code=emit(CTX, payload))
    typer.echo(f"service {name} removed")


# ------------------- db -------------------
@db_app.command("reset", context_settings={"help_option_names": []})
def db_reset(
    name: Optional[str] = typer.Argument(None),
    backup: Optional[Path] = typer.Option(None, "--backup"),
    env: Optional[str] = typer.Option(None, "--env"),
    db_name: Optional[str] = typer.Option(None, "--db-name"),
    show_help: bool = typer.Option(False, "--help", is_flag=True, is_eager=True, help="Show help for command"),
):
    if show_help or (name is None and backup is None and env is None and db_name is None):
        B = "\033[1m"; R = "\033[0m"
        typer.echo(f"{B}DB RESET{R}")
        typer.echo("  Drop, create and restore the database from a backup\n")
        typer.echo(f"{B}USAGE{R}")
        typer.echo("  devkit db reset NAME --backup FILE [--env ENV] [--db-name NAME]\n")
        typer.echo(f"{B}EXAMPLES{R}")
        typer.echo("  devkit db reset myapp --backup /file.dump")
        raise typer.Exit(0)
    if CTX.safe and not (CTX.yes):
        payload = envelope("db reset", "error", Exit.FORBIDDEN, errors=[{"code":"SAFE_MODE","detail":"Use --yes to confirm in safe mode"}])
        raise typer.Exit(code=emit(CTX, payload))

    cfg = load_config()
    s = find_service(cfg, name)
    if not s:
        payload = envelope("db reset", "error", Exit.NOT_FOUND, errors=[{"code":"NOT_FOUND","detail":name}])
        raise typer.Exit(code=emit(CTX, payload))

    app_path = Path(s.app_path)
    backup_path = Path(str(backup or s.backup_path))
    if not backup_path.exists():
        payload = envelope("db reset", "error", Exit.PRECONDITION, errors=[{"code":"BACKUP_MISSING","detail":str(backup_path)}])
        raise typer.Exit(code=emit(CTX, payload))

    env_name = env or s.env
    dbn = db_name or s.db.name or None
    if not dbn:
        try:
            dbn = infer_db_name(app_path, env_name)
        except Exception as e:
            payload = envelope("db reset", "error", Exit.PRECONDITION, errors=[{"code":"DB_NAME_INFER","detail":str(e)}])
            raise typer.Exit(code=emit(CTX, payload))
    proceed = CTX.yes or (CTX.interactive and confirm(f"This will drop and recreate \"{dbn}\". Continue?"))
    if not proceed:
        raise typer.Exit(code=Exit.OK)

    rails_cmd = rails_bin(app_path)
    envp = os.environ.copy()
    envp["RAILS_ENV"] = env_name

    # Ask once for Postgres password if needed and interactive
    if "PGPASSWORD" not in envp and CTX.interactive:
        try:
            pwd = typer.prompt(
                f"Postgres password for user '{s.db.user}' on {s.db.host}:{s.db.port}",
                hide_input=True,
                default="",
                show_default=False,
            )
        except Exception:
            pwd = ""
        if pwd:
            envp["PGPASSWORD"] = pwd

    # drop & create
    try:
        check(rails_cmd + ["db:drop"], cwd=app_path, env=envp, trace=CTX.trace)
        check(rails_cmd + ["db:create"], cwd=app_path, env=envp, trace=CTX.trace)
    except Exception as e:
        payload = envelope("db reset", "error", Exit.EXTERNAL, errors=[{"code":"RAILS_CMD","detail":str(e)}])
        raise typer.Exit(code=emit(CTX, payload))

    # restore
    tool, flags = choose_restore_tool(backup_path)
    args = [tool, "-U", s.db.user, "-h", s.db.host, "-p", str(s.db.port), "-d", dbn] + flags
    if tool.endswith("psql") and "-f" not in flags:
        # choose_restore_tool already adds -f for psql
        pass
    if tool.endswith("pg_restore") and "-1" not in flags:
        flags.append("-1")
    if tool.endswith("pg_restore"):
        args.append(str(backup_path))

    rc = run(args, env=envp, trace=CTX.trace)
    if rc != 0:
        payload = envelope("db reset", "error", Exit.EXTERNAL, errors=[{"code":"RESTORE_FAILED","detail":"pg_restore/psql"}])
        raise typer.Exit(code=emit(CTX, payload))

    # validate
    vrc = validate_connection(s.db.user, s.db.host, s.db.port, dbn, trace=CTX.trace, env=envp)
    if vrc != 0:
        payload = envelope("db reset", "error", Exit.EXTERNAL, errors=[{"code":"VALIDATE_FAILED","detail":"psql SELECT 1"}])
        raise typer.Exit(code=emit(CTX, payload))

    data = {
        "service": s.name,
        "app_path": s.app_path,
        "backup": str(backup_path),
        "env": env_name,
        "db": {"name": dbn, "user": s.db.user, "host": s.db.host, "port": s.db.port},
        "steps": [
            {"name":"drop","status":"ok"},
            {"name":"create","status":"ok"},
            {"name":"restore","status":"ok","tool": tool},
            {"name":"validate","status":"ok"},
        ],
    }
    if CTX.format == "json":
        payload = envelope("db reset", "ok", Exit.OK, data)
        raise typer.Exit(code=emit(CTX, payload))
    typer.echo(f"reset db • {s.name} • env={env_name} • db={dbn}")
    typer.echo("database restored successfully.")


# ------------------- meta -------------------
@meta_app.command("reference")
def meta_reference(format: str = typer.Option(None, "--format")):
    fmt = format or CTX.format
    ref = typer_reference(app)
    payload = envelope("reference", "ok", Exit.OK, {"reference": ref})
    class _ctx: ...
    _ctx.format = fmt  # type: ignore
    raise typer.Exit(code=emit(_ctx, payload))


@meta_app.command("describe")
def meta_describe(command: Optional[str] = typer.Argument(None), format: str = typer.Option(None, "--format")):
    fmt = format or CTX.format
    ref = typer_reference(app)
    data = {"command": command, "reference": ref}
    payload = envelope("describe", "ok", Exit.OK, data)
    class _ctx: ...
    _ctx.format = fmt  # type: ignore
    raise typer.Exit(code=emit(_ctx, payload))


# ------------------- completion (simple placeholder) -------------------
@app.command("completion")
def completion(shell: str = typer.Argument("bash")):
    from typer.main import get_command
    import click
    cli = get_command(app)
    if shell == "bash":
        ctx = click.Context(cli)
        typer.echo(cli.get_help(ctx))  # Placeholder: integrate real Click completion if desired
    else:
        typer.echo("Completion generator placeholder. Integrate Click completion if needed.")


# ------------------- help topics -------------------
TOPICS = {
    "environment": (
        "Environment variables used by devkit",
        [
            "DEVKIT_SAFE=1  Enable safe mode; requires --yes for destructive actions",
            "PGPASSWORD     Password for Postgres tools (psql/pg_restore)",
            "PATH          Must include rails, psql, pg_restore when needed",
        ],
    ),
    "exit-codes": (
        "Exit codes used by devkit",
        [
            "0   OK",
            f"{Exit.INVALID_ARGS}   INVALID_ARGS",
            f"{Exit.NOT_FOUND}   NOT_FOUND",
            f"{Exit.DEP_MISSING}   DEP_MISSING",
            f"{Exit.PRECONDITION}   PRECONDITION",
            f"{Exit.EXTERNAL}   EXTERNAL",
            f"{Exit.FORBIDDEN}   FORBIDDEN",
            f"{Exit.INTERNAL}   INTERNAL",
        ],
    ),
    "formatting": (
        "Formatting options for JSON output",
        [
            "Use --format json to emit a stable envelope:",
            "{command, status, exit_code, data, errors}",
            "Combine with --no-interactive and --yes for deterministic runs.",
        ],
    ),
    "reference": (
        "A comprehensive reference of all commands",
        [
            "Generate docs/commands.md with 'make docs'.",
            "Or inspect JSON: 'devkit meta reference --format json'",
        ],
    ),
}


@app.command("help")
def help_topics(topic: Optional[str] = typer.Argument(None)):
    B = "\033[1m"; R = "\033[0m"
    if topic is None:
        typer.echo(f"{B}HELP TOPICS{R}")
        width = max(len(k) for k in TOPICS)
        for name, (desc, _) in TOPICS.items():
            pad = " " * (width - len(name) + 2)
            typer.echo(f"  {name}:{pad}{desc}")
        typer.echo("\nUse 'devkit help <topic>' for more information about a topic.")
        raise typer.Exit(0)
    if topic not in TOPICS:
        typer.echo(f"{B}ERROR:{R} unknown help topic: {topic}", err=True)
        typer.echo(f"{B}TIP:{R} Run 'devkit help' to list available topics.", err=True)
        raise typer.Exit(2)
    title, lines = TOPICS[topic]
    typer.echo(f"{B}{topic.upper()}{R}")
    typer.echo(f"  {title}\n")
    for ln in lines:
        typer.echo(f"  {ln}")
