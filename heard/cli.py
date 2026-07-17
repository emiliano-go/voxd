import typer

app = typer.Typer(name="heard")
config_app = typer.Typer(name="config", help="Manage persistent configuration.")
app.add_typer(config_app)


@app.command()
def listen():
    """Start the voice-control loop: hold the PTT key, speak, release."""
    from . import stt, intent
    from .tools import registry

    print("heard: listening (hold Shift, speak, release)")
    print("heard: press Ctrl-C to stop")
    try:
        while True:
            text = stt.capture_while_held()
            if not text:
                continue
            print(f"  you: {text}")
            resolution = intent.resolve(text)
            if resolution.tool_call:
                output = registry.dispatch(resolution.tool_call)
            else:
                output = f"declined: {resolution.reason}" if resolution.reason else "declined"
            print(f"  heard: {output}")
    except KeyboardInterrupt:
        print("\nheard: stopped")


@config_app.command()
def get(key: str):
    """Print a single configuration value by dotted key (e.g. wm.backend)."""
    typer.echo(f"{key} = (not implemented yet)")


@config_app.command()
def set(key: str, value: str):
    """Set a configuration value by dotted key."""
    typer.echo(f"set {key} = {value} (not implemented yet)")


@config_app.command()
def show():
    """Print the full merged configuration (configured + detected)."""
    typer.echo("(not implemented yet)")


def main():
    app()


if __name__ == "__main__":
    main()
