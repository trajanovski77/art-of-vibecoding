#!/usr/bin/env python3
"""PreToolUse hook (matcher: Bash|Monitor): block commands that leak secrets, force-push, delete outside the repo,
or delete Docker volumes (which usually hold the data you care about).

Input:  hook JSON on stdin (tool_input.command, cwd, scratchpad_dir).
Output: exit 0 = allow. Exit 2 = block, reason on stderr (Claude sees it and can change course). Exit 1 = the
        hook itself failed: non-blocking, the command was NOT checked, and Claude Code shows a hook-error notice.

Best effort, not a security boundary: it reads the command text. It cannot see through shell variables, scripts
that open files themselves, `xargs`, or programs it does not know print files. Claude Code's own permission
rules stay the first line of defence; this covers forms they miss (`/bin/rm`, `git -C . push -f`,
`bash -c '...'`, newlines, heredocs, `git add ... && git commit`). Standard library only.

Why it is this long: the first, short version of this guard let 8 of 9 bypass tricks through when an
independent reviewer (a stronger model in a fresh context) attacked it. Every branch below closes one of them.

Adapt (usually nothing to change):
  - PROTECT_DOCKER_VOLUMES: set to False if you do not use Docker, or keep it to stop `down -v` style deletes.
  - SECRET_CONTENT: add the credential formats your stack uses (reported by kind, never by value).
  - PRIVATE_KEY_NAMES and is_sensitive(): add paths that hold secrets in your project.
Re-run the sample commands in 01-setup/README.md after any change.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from typing import NamedTuple

PROTECT_DOCKER_VOLUMES = True  # block `docker compose down -v`, `docker volume rm/prune`, ...
SAFE_ENV_SUFFIX = "example"  # .env.example holds variable names only, so it may be read
PRIVATE_KEY_NAMES = {
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    ".netrc",
    ".git-credentials",
}
READERS = set(
    "cat head tail less more sed awk gawk grep egrep fgrep rg ag cut sort uniq tr nl tac rev strings "
    "xxd od hexdump base64 bat batcat cp mv scp rsync curl wget diff paste column fold pr comm join "
    "tar zip openssl tee dd jq".split()
)
COPIERS = {"cp", "mv", "scp", "rsync"}  # only their sources are read
SEARCHERS = {
    "grep",
    "egrep",
    "fgrep",
    "rg",
    "ag",
}  # the first operand is a pattern, not a path
INTERPRETER = re.compile(r"python[\d.]*|node|ruby|perl|php")
INLINE_CODE_FLAG = re.compile(r"-[a-zA-Z]*[ceEp][a-zA-Z]*|--eval|--print")
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}"}
RUNNERS = {"uv", "poetry", "pipenv", "pipx", "npx", "pnpm", "yarn", "bunx"}
WRAPPERS = RUNNERS | set(
    "sudo command builtin exec time nohup nice timeout stdbuf env".split()
)
WRAPPER_OPTIONS_WITH_ARGUMENT = {
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-D", "-R", "-T", "-U"},
    "timeout": {"-s", "-k"},
    "env": {"-u", "-C", "-S"},
    "nice": {"-n"},
    "stdbuf": {"-i", "-o", "-e"},
}
DELETERS = {"rm", "rmdir", "unlink", "shred", "srm", "trash", "trash-put"}
FIND_EXEC_FLAGS = {"-exec", "-execdir", "-ok", "-okdir"}
DOCKER_OPTIONS_WITH_ARGUMENT = {
    "-H",
    "--host",
    "-c",
    "--context",
    "--config",
    "-l",
    "--log-level",
    "--tlscacert",
    "--tlscert",
    "--tlskey",
}
COMPOSE_OPTIONS_WITH_ARGUMENT = {
    "-H",
    "--host",
    "--context",
    "--log-level",
    "--progress",
    "--ansi",
    "--parallel",
    "-f",
    "--file",
    "-p",
    "--project-name",
    "--project-directory",
    "--env-file",
    "--profile",
}
FIND_GLOBAL_OPTIONS = {"-H", "-L", "-P", "-E", "-X", "-s", "-x"}
GIT_OPTIONS_WITH_ARGUMENT = {
    "-C",
    "-c",
    "--git-dir",
    "--work-tree",
    "--namespace",
    "--exec-path",
    "--config-env",
}
GIT_PRINTERS = {"show", "cat-file", "diff", "log", "blame", "grep"}
VERBOSE_CURL = {"-v", "--verbose", "--trace", "--trace-ascii"}

ASSIGNMENT = re.compile(r"\w+=")
SECRET_VARIABLE = re.compile(
    r"\$\{?\w*(?:KEY|TOKEN|SECRET|PASS|PASSWORD|PASSWD|CREDENTIALS?)\}?(?!\w)"
)
SECRET_PATH_CANDIDATE = re.compile(
    r"[\w./~*-]*(?:\.env|secrets/|id_(?:rsa|dsa|ecdsa|ed25519)|\.netrc|\.git-credentials|\.aws/credentials"
    r"|huggingface/token)[\w./*-]*",
    re.I,
)
ENV_ACCESS = re.compile(r"environ|getenv|process\.env|ENVIRON|dotenv", re.I)
SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASS|CREDENTIAL", re.I)
ENV_DUMP = re.compile(r"(?:os\.environ|process\.env)(?!\s*[\[.])")
SUBSTITUTION = re.compile(r"\$\(([^()]*)\)|`([^`]*)`|<\(([^()]*)\)")
BODY_SUBSTITUTION = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")  # what an unquoted heredoc body expands
HEREDOC_RUNNERS = SHELLS | {"source", ".", "eval", "xargs", "ssh"}  # run what they read
OPERATOR = re.compile(r"[();|&]+")
OUTPUT_REDIRECT = re.compile(r"[0-9]*(?:>>?|>&|&>>?|>\|)")
ESCAPED = {";": "\x00S", "(": "\x00L", ")": "\x00R"}

# High-signal credential formats only, so a false positive is rare. Reported by kind, never by value.
SECRET_CONTENT = {
    kind: re.compile(pattern)
    for kind, pattern in {
        "private key": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY",
        "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
        "Anthropic API key": r"\bsk-ant-[A-Za-z0-9_-]{20,}",
        "OpenAI-style API key": r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}",
        "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{36,}",
        "GitHub fine-grained token": r"\bgithub_pat_[A-Za-z0-9_]{50,}",
        "Slack token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}",
        "Google API key": r"\bAIza[0-9A-Za-z_-]{35}",
        "Hugging Face token": r"\bhf_[A-Za-z0-9]{34,}",
    }.items()
}


class Blocked(Exception):
    """Raised with the reason a command must not run."""


class Scope(NamedTuple):
    """Where the session may delete: inside the repo (never .git) and inside its own scratchpad."""

    root: str
    scratch: str | None = None

    def allows_delete(self, path: str, *, allow_root: bool = False) -> bool:
        git_dir = os.path.join(self.root, ".git")
        if path == git_dir or path.startswith(git_dir + os.sep):
            return False
        if allow_root and path == self.root:
            return True
        return any(
            base and path.startswith(base + os.sep)
            for base in (self.root, self.scratch)
        )


# --- paths and secrets -----------------------------------------------------------------------------------


def is_sensitive(path: str) -> bool:
    """Files no session may read or commit: .env files (not the example), secrets/, private keys, tokens."""
    parts = [p.lower() for p in re.split(r"[\\/]+", path) if p]
    if not parts:
        return False
    name = parts[-1]
    if re.fullmatch(r"\.env(?:[.*?\[].*)?", name):
        return name == ".env" or name.rsplit(".", 1)[-1] != SAFE_ENV_SUFFIX
    return (
        "secrets" in parts
        or name in PRIVATE_KEY_NAMES
        or parts[-2:] in ([".aws", "credentials"], ["huggingface", "token"])
    )


def mentions_sensitive(text: str) -> bool:
    return any(is_sensitive(m.group(0)) for m in SECRET_PATH_CANDIDATE.finditer(text))


def secret_kind(text: str) -> str | None:
    return next(
        (kind for kind, pattern in SECRET_CONTENT.items() if pattern.search(text)), None
    )


def credential_message(kind: str, name: str) -> str:
    return (
        f"{name} contains what looks like a {kind}. Remove it, read it from an environment variable "
        "instead, and do not stage or commit it."
    )


def resolve_path(path: str, cwd: str | None, root: str) -> str | None:
    """Absolute, symlink-resolved location of `path`, or None when a shell expansion makes it unknowable."""
    path = path.replace("${CLAUDE_PROJECT_DIR}", root).replace(
        "$CLAUDE_PROJECT_DIR", root
    )
    if cwd:
        path = path.replace("${PWD}", cwd).replace("$PWD", cwd)
    if "$" in path or "`" in path or ("{" in path and ".." in path):
        return None
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        if cwd is None:
            return None
        path = os.path.join(cwd, path)
    path = os.path.normpath(path)
    return os.path.join(os.path.realpath(os.path.dirname(path)), os.path.basename(path))


# --- tokenising ------------------------------------------------------------------------------------------


def split_heredocs(command: str) -> tuple[str, list[tuple[str, str, str, bool]]]:
    """Cut heredoc bodies out of a command. They are data (commit messages, file contents) unless they
    feed a shell or interpreter, so also return, per body: the text before `<<` on its line, the text
    after the delimiter on that line (a pipe there can feed a shell), the body, and whether the delimiter
    was quoted (a quoted delimiter turns off $(...) and backtick expansion).
    The delimiter must end at a word boundary: for `<<EOF.x` the shell's delimiter is `EOF.x`, so a guess
    at `EOF` would hide lines after it. Such forms are left unsplit and their lines checked as commands."""
    bodies = []
    while True:
        match = re.search(
            r"(?<!<)<<(?!<)-?\s*(['\"]?)(\w+)\1(?=[\s;&|<>()]|$)", command
        )
        if not match:
            return command, bodies
        eol = command.find("\n", match.end())
        closing = None
        if eol != -1:
            closing = re.compile(rf"^\s*{re.escape(match.group(2))}\s*$", re.M).search(
                command, eol + 1
            )
        if (
            closing is None
        ):  # `$((1<<4))`, or no terminator: not a body, so drop only the operator
            command = command[: match.start()] + " " + command[match.end() :]
            continue
        opener = command[command.rfind("\n", 0, match.start()) + 1 : match.start()]
        bodies.append(
            (
                opener,
                command[match.end() : eol],
                command[eol + 1 : closing.start()],
                bool(match.group(1)),
            )
        )
        command = (
            command[: match.start()]
            + command[match.end() : eol]
            + command[closing.end() :]
        )


def newlines_to_separators(text: str) -> str:
    """shlex treats newlines as blanks, so turn unquoted ones into `;` and join backslash-continued lines."""
    out, quote, i = [], "", 0
    while i < len(text):
        char, pair = text[i], text[i : i + 2]
        if char == "\\" and quote != "'" and len(pair) == 2:
            out.append(" " if pair == "\\\n" else pair)
            i += 2
            continue
        if quote:
            quote = "" if char == quote else quote
        elif char in "'\"":
            quote = char
        elif char == "\n":
            char = " ; "
        out.append(char)
        i += 1
    return "".join(out)


def segments(command: str) -> list[list[str]]:
    """Split a command line into simple commands (on ; && || | & and newlines), respecting quotes."""
    text = re.sub(
        r"\\([;()])", lambda m: ESCAPED[m.group(1)], newlines_to_separators(command)
    )
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ""  # a comment must never hide the commands after it
        tokens = list(lexer)
    except ValueError:  # unbalanced quotes: over-split on every operator instead of trusting the quoting
        return [w for piece in re.split(r"[;&|()\n]+", text) if (w := piece.split())]
    result: list[list[str]] = [[]]
    for token in tokens:
        if OPERATOR.fullmatch(token):
            result.append([])
        else:
            for char, placeholder in ESCAPED.items():
                token = token.replace(placeholder, char)
            result[-1].append(token)
    return [seg for seg in result if seg]


def unwrap(seg: list[str]) -> tuple[list[str], set[str]]:
    """Strip VAR=value prefixes, shell keywords and wrappers (sudo, env, uv run ...); return (words, wrappers)."""
    i, wrappers = 0, set()
    while i < len(seg) and (ASSIGNMENT.match(seg[i]) or seg[i] in KEYWORDS):
        i += 1
    while i < len(seg) and os.path.basename(seg[i]).lower() in WRAPPERS:
        wrapper = os.path.basename(seg[i]).lower()
        wrappers.add(wrapper)
        i += 1
        while i < len(seg):
            token = seg[i]
            if token.startswith("-"):
                i += 2 if token in WRAPPER_OPTIONS_WITH_ARGUMENT.get(wrapper, ()) else 1
            elif ASSIGNMENT.match(token) or (
                wrapper in ("timeout", "nice") and re.fullmatch(r"[\d.]+[smhd]?", token)
            ):
                i += 1
            elif wrapper in RUNNERS and token in ("run", "exec", "dlx"):
                i += 1
            else:
                break
    return seg[i:], wrappers


def operands(prog: str, args: list[str]) -> list[str]:
    """The arguments of `prog` that name files it reads."""
    positional = [a for a in args if not a.startswith("-")]
    if prog in COPIERS:
        return positional[:-1]
    if prog in SEARCHERS:
        has_pattern_option = "-e" in args or "--regexp" in args
        files, skip_next = [], False
        for arg in args:
            if skip_next:
                skip_next = False
            elif arg in ("-e", "--regexp"):
                skip_next = True
            elif arg.startswith("-") or has_pattern_option:
                files.append(arg)
            else:
                has_pattern_option = True  # the first operand was the pattern
        return files
    return args


def without_output_redirects(args: list[str]) -> list[str]:
    out, skip_next = [], False
    for arg in args:
        if skip_next:
            skip_next = False
        elif OUTPUT_REDIRECT.fullmatch(arg):
            skip_next = True
        else:
            out.append(arg)
    return out


# --- checks ----------------------------------------------------------------------------------------------


def check_env_dump(prog: str, args: list[str]) -> None:
    positional = [a for a in args if not a.startswith("-")]
    dump = (
        (
            prog == "printenv"
            and (
                not positional
                or any(SECRET_VARIABLE.search(f"${a}") for a in positional)
            )
        )
        or (prog == "export" and not positional)
        or (
            prog in ("declare", "typeset")
            and not positional
            and not {"-f", "-F"} & set(args)
        )
        or (prog == "set" and not args)
        or (prog == "gh" and args[:2] == ["auth", "token"])
    )
    if dump:
        raise Blocked(
            "this prints environment variables or credentials, which can hold secrets, into the transcript. "
            "Print one specific non-secret variable instead (for example `echo $PATH`)."
        )


def check_inline_code(code: str) -> None:
    """Code given to an interpreter (-c/-e or a heredoc) must not open a secret file or print secrets."""
    if (
        mentions_sensitive(code)
        or (ENV_ACCESS.search(code) and SECRET_NAME.search(code))
        or ENV_DUMP.search(code)
    ):
        raise Blocked(
            "inline code that opens a secret file (.env, secrets/, private keys) or reads secrets from the "
            'environment is off limits. Ask the user; to test that a variable is set, use `test -n "$NAME"`.'
        )


def check_secret_reads(prog: str, args: list[str]) -> None:
    prints_variable = any(SECRET_VARIABLE.search(a) for a in args)
    if prints_variable and (
        prog in ("echo", "printf", "print", "cat")
        or (prog == "curl" and VERBOSE_CURL & set(args))
    ):
        raise Blocked(
            "this prints a variable whose name looks like a secret (KEY, TOKEN, SECRET, PASS, CREDENTIAL). "
            'Test that it is set with `test -n "$NAME"` instead of printing it.'
        )
    if prog in ("awk", "gawk") or (
        INTERPRETER.fullmatch(prog) and any(INLINE_CODE_FLAG.fullmatch(a) for a in args)
    ):
        check_inline_code(" ".join(args))
    delegating = prog in ("find", "xargs") and any(
        os.path.basename(a) in READERS for a in args
    )
    if prog in READERS or delegating:
        hit = next((a for a in operands(prog, args) if mentions_sensitive(a)), None)
        if hit:
            raise Blocked(
                f"`{prog}` would read a secret file ({hit}): .env files, secrets/ and private keys are off "
                "limits. Ask the user instead. If this is a false positive, rephrase without a path-like argument."
            )


def git_out(workdir: str, *args: str) -> str:
    """stdout of a read-only git command in `workdir`, or '' if it fails."""
    try:
        result = subprocess.run(
            ["git", "-C", workdir, *args], capture_output=True, text=True, timeout=5
        )
    except subprocess.TimeoutExpired:
        raise Blocked(
            "git took too long to inspect what this command would stage or commit, so it was blocked."
        )
    except OSError:
        return ""
    return result.stdout if result.returncode == 0 else ""


def scan_files(workdir: str, names: list[str]) -> tuple[str, str] | None:
    """(kind, name) of the first file whose working-tree content looks like a credential."""
    for name in names:
        try:
            with open(
                os.path.join(workdir, name), encoding="utf-8", errors="replace"
            ) as f:
                kind = secret_kind(f.read(1_000_000))
        except OSError:
            continue
        if kind:
            return kind, name
    return None


def is_force_push(args: list[str]) -> bool:
    for arg in args:
        if arg in ("--force", "--mirror") or arg.startswith(
            ("--force-with-lease", "--force-if-includes")
        ):
            return True
        if re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", arg) or (
            arg.startswith("+") and len(arg) > 1
        ):
            return True
    return False


def check_add(args: list[str], workdir: str) -> None:
    if any(a in ("-p", "--patch", "-i", "--interactive", "-e", "--edit") for a in args):
        return
    would_add = re.findall(
        r"^(?:add|remove) '(.*)'$", git_out(workdir, "add", "-n", *args), re.M
    )
    bad = sorted({p for p in would_add if is_sensitive(p)})
    if bad:
        raise Blocked(
            f"`git add` would stage secret file(s): {', '.join(bad)}. Never commit secrets."
        )
    hit = scan_files(workdir, would_add)
    if hit:
        raise Blocked(credential_message(*hit))


def check_commit(args: list[str], workdir: str) -> None:
    commit_all = any(
        a == "--all" or re.fullmatch(r"-[a-zA-Z]*a[a-zA-Z]*", a) for a in args
    )
    pathspecs = [
        a
        for a in args
        if not a.startswith("-") and os.path.exists(os.path.join(workdir, a))
    ]
    names = git_out(workdir, "diff", "--cached", "--name-only", "-z").split("\0")
    diff_args = ["--no-ext-diff", "--no-textconv", "--no-color", "-U0"]
    diff = git_out(workdir, "diff", "--cached", *diff_args)
    if commit_all:  # `git commit -a` also stages tracked changes
        names += git_out(workdir, "diff", "--name-only", "-z").split("\0")
        diff += git_out(workdir, "diff", *diff_args)
    listed = (
        git_out(workdir, "ls-files", "-z", "--", *pathspecs).split("\0")
        if pathspecs
        else []
    )
    bad = sorted({n for n in names + listed if n and is_sensitive(n)})
    if bad:
        raise Blocked(
            f"this commit would include secret file(s): {', '.join(bad)}. "
            "Unstage them with `git restore --staged <path>`; never commit secrets."
        )
    hit = scan_files(
        workdir, listed
    )  # `git commit <path>` commits the working-tree content of that path
    if hit:
        raise Blocked(credential_message(*hit))
    current = "?"
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[4:].removeprefix("b/")
        elif line.startswith("+"):
            kind = secret_kind(line)
            if kind:
                raise Blocked(
                    credential_message(kind, f"the staged change in {current}")
                )


def git_prints_secret(sub: str, rest: list[str]) -> bool:
    if sub == "log" and not {"-p", "-u", "--patch", "--cc", "-c"} & set(rest):
        return False  # a plain log lists commits, not file content
    return any(
        mentions_sensitive(a)
        for a in (operands("grep", rest) if sub == "grep" else rest)
    )


def check_git(args: list[str], cwd: str | None, scope: Scope) -> None:
    i, workdir = 0, cwd
    while i < len(args) and args[i].startswith("-"):
        if args[i] == "-C" and i + 1 < len(args):
            workdir = (
                resolve_path(args[i + 1], workdir, scope.root) if workdir else None
            )
        i += 2 if args[i] in GIT_OPTIONS_WITH_ARGUMENT else 1
    if i >= len(args):
        return
    sub, rest = args[i], args[i + 1 :]
    if sub == "push" and is_force_push(rest):
        raise Blocked(
            "force-push is not allowed (--force, --force-with-lease, +refspec, --mirror). "
            "If it is really needed, ask the user to run it themselves."
        )
    if sub in GIT_PRINTERS and git_prints_secret(sub, rest):
        raise Blocked(
            "this would print a secret file's contents from git. Ask the user instead."
        )
    if sub in ("add", "commit", "clean", "rm") and workdir is None:
        raise Blocked(
            "cannot tell which repository this runs in (the -C path uses a shell variable)."
        )
    if sub in ("clean", "rm") and not scope.allows_delete(workdir, allow_root=True):
        raise Blocked(
            f"`git {sub}` in {workdir} would delete files outside this repo. Ask the user to run it."
        )
    if sub == "add":
        check_add(rest, workdir)
    elif sub == "commit":
        check_commit(rest, workdir)


def check_delete(prog: str, args: list[str], cwd: str | None, scope: Scope) -> None:
    args = without_output_redirects(args)
    allow_root = False
    if prog in DELETERS:
        targets, options_done = [], False
        for arg in args:
            if arg == "--" and not options_done:
                options_done = True
            elif options_done or not arg.startswith("-"):
                targets.append(arg)
    elif prog == "rsync" and any(a.startswith("--delete") for a in args):
        targets = [a for a in args if not a.startswith("-")][-1:]  # the destination
    elif prog == "find" and (
        "-delete" in args
        or (
            FIND_EXEC_FLAGS & set(args)
            and DELETERS & {os.path.basename(a) for a in args}
        )
    ):
        i = 0
        while i < len(args) and (
            args[i] in FIND_GLOBAL_OPTIONS
            or args[i].startswith("-O")
            or args[i] == "-D"
        ):
            i += 2 if args[i] == "-D" else 1
        starts = []
        while (
            i < len(args) and not args[i].startswith("-") and args[i] not in ("(", "!")
        ):
            starts.append(args[i])
            i += 1
        targets = starts or ["."]
        allow_root = args[i:] != [
            "-delete"
        ]  # a bare `find . -delete` empties the whole tree
    else:
        return
    for target in targets:
        real = resolve_path(target, cwd, scope.root)
        if real is None or not scope.allows_delete(real, allow_root=allow_root):
            raise Blocked(
                f"deleting `{target}` is not allowed: it is outside the repo (and the session scratchpad), is "
                "the repo root or .git, or cannot be resolved from the command text (shell variables). Use a "
                "literal path inside the repo, or ask the user to run it."
            )


def docker_words(args: list[str], with_argument: set[str]) -> list[str]:
    """Drop leading options (and the values of those that take one) to reach the subcommand."""
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in with_argument else 1
    return args[i:]


def check_docker(prog: str, args: list[str]) -> None:
    """Databases and uploads usually live on Docker volumes, and `down -v` deletes them in one keystroke."""
    if not PROTECT_DOCKER_VOLUMES or prog not in ("docker", "docker-compose"):
        return
    shown = f"{prog} {' '.join(args)}"
    if prog == "docker-compose":
        args = ["compose", *args]
    words = docker_words(args, DOCKER_OPTIONS_WITH_ARGUMENT)
    sub, rest = (words[0], words[1:]) if words else ("", [])
    if sub == "compose":
        words = docker_words(rest, COMPOSE_OPTIONS_WITH_ARGUMENT)
        sub, rest = ("compose " + words[0], words[1:]) if words else ("compose", [])
    removes_volumes = any(
        a == "--volumes"
        or a.startswith("--volumes=")
        or re.fullmatch(r"-[a-zA-Z]*v[a-zA-Z]*", a)
        for a in rest
    )
    names_volumes = any(a == "--volumes" or a.startswith("--volumes=") for a in rest)
    if (
        (sub in ("compose down", "compose rm") and removes_volumes)
        or (sub == "volume" and rest[:1] in (["rm"], ["remove"], ["prune"]))
        or (sub == "system" and rest[:1] == ["prune"] and names_volumes)
    ):
        raise Blocked(
            f"`{shown}` would delete Docker volumes, which usually hold the project's data "
            "(databases, uploads, user state). Back up first, then ask the user to run it."
        )


def check_heredoc(
    opener: str,
    tail: str,
    body: str,
    quoted: bool,
    cwd: str | None,
    scope: Scope,
    depth: int,
) -> None:
    """A heredoc is data, unless it feeds a shell (it runs) or an interpreter (it may open a secret file).

    A quoted delimiter (`<<'EOF'`) stops the shell expanding $(...) and backticks, so such a body is not
    scanned for them, but only when the opening line is plain. Quotes, a comment or a substitution
    before `<<` (it may sit inside a string, or feed `eval "$(...)"`), or a pipe after the delimiter, fail
    closed to the unquoted treatment.
    """
    opened_by = segments(opener)
    words, _ = unwrap(opened_by[-1]) if opened_by else ([], set())
    prog = os.path.basename(words[0]).lower() if words else ""
    piped_to = set()
    if "|" in tail:
        for seg in segments(tail):
            seg_words, _ = unwrap(seg)
            if seg_words:
                piped_to.add(os.path.basename(seg_words[0]).lower())
    plain_opener = not re.search(r"[\"'`#]|\$\(", opener) and not piped_to
    if not (quoted and plain_opener):
        if not quoted and SECRET_VARIABLE.search(body):
            raise Blocked(
                "an unquoted heredoc expands $VARIABLES, and this body names a secret one. Quote the "
                "delimiter (<<'EOF') if the text is meant literally."
            )
        for match in BODY_SUBSTITUTION.finditer(body):
            analyze(substitution_command(match), cwd, scope, depth + 1)
    if prog in HEREDOC_RUNNERS or piped_to & HEREDOC_RUNNERS:
        analyze(body, cwd, scope, depth + 1)
    elif INTERPRETER.fullmatch(prog) or any(INTERPRETER.fullmatch(x) for x in piped_to):
        check_inline_code(body)


def substitution_command(match: re.Match[str]) -> str:
    inner = next(group for group in match.groups() if group is not None)
    if inner.lstrip().startswith("<") and "<<" not in inner:  # $(< file) reads the file
        return "cat " + inner.lstrip()[1:]
    return inner


def check_segment(
    seg: list[str], cwd: str | None, scope: Scope, depth: int
) -> str | None:
    """Check one simple command; return the working directory for the commands after it."""
    words, wrappers = unwrap(seg)
    if not words:
        if "env" in wrappers:
            check_env_dump("printenv", [])
        return cwd
    prog, args = os.path.basename(words[0]).lower(), words[1:]
    if prog in ("cd", "pushd"):
        return (
            None
            if args[:1] == ["-"]
            else resolve_path(args[0] if args else "~", cwd, scope.root)
        )
    if prog in SHELLS:
        for i, arg in enumerate(args[:-1]):
            if re.fullmatch(r"-[a-zA-Z]*c[a-zA-Z]*", arg):
                analyze(args[i + 1], cwd, scope, depth + 1)
                break
    elif prog == "eval":
        analyze(" ".join(args), cwd, scope, depth + 1)
    check_env_dump(prog, args)
    check_secret_reads(prog, args)
    if prog == "git":
        check_git(args, cwd, scope)
    check_delete(prog, args, cwd, scope)
    check_docker(prog, args)
    return cwd


def analyze(command: str, cwd: str | None, scope: Scope, depth: int = 0) -> None:
    if depth > 3:
        return
    command, heredocs = split_heredocs(command)
    for opener, tail, body, quoted in heredocs:
        check_heredoc(opener, tail, body, quoted, cwd, scope, depth)
    for match in SUBSTITUTION.finditer(
        command
    ):  # $(...), backticks and <(...), quoted or not
        analyze(substitution_command(match), cwd, scope, depth + 1)
    for seg in segments(command):
        cwd = check_segment(seg, cwd, scope, depth)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError) as error:
        print(
            f"guard_bash: unreadable hook input ({error}); the command was NOT checked",
            file=sys.stderr,
        )
        return 1
    if payload.get("tool_name", "Bash") not in ("Bash", "Monitor"):
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    root = os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    )
    scratch = payload.get("scratchpad_dir")
    scope = Scope(root, os.path.realpath(scratch) if scratch else None)
    try:
        analyze(command, payload.get("cwd") or root, scope)
    except Blocked as reason:
        print(f"BLOCKED by .claude/hooks/guard_bash.py: {reason}", file=sys.stderr)
        return 2
    except Exception as error:  # noqa: BLE001 - a bug here must be visible but must not wedge the session
        print(
            f"guard_bash: internal error ({error!r}); the command was NOT checked",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
