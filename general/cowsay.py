import subprocess


def run_cowsay():
    try:
        # Run `fortune` and capture its output
        pfortune = subprocess.run(
            ["/usr/games/fortune"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )

        # Pipe the fortune output into `cowsay`
        pcowsay = subprocess.run(
            ["/usr/games/cowsay"],
            input=pfortune.stdout,
            stdout=subprocess.PIPE,
            text=True
        )

        # Relay cowsay's stdout to this script's stdout
        return pcowsay.stdout

    except FileNotFoundError as e:
        return f"Command not found: {e}"
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e}"
