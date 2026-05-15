import os
import re
import json
import random
import subprocess
import math
from datetime import datetime, timedelta, date

# ─── EXTENSION WEIGHTS ──────────────────────────────────────────
EXT_WEIGHTS = {
    ".py": 22, ".js": 14, ".ts": 10, ".tsx": 6,
    ".css": 7, ".scss": 3, ".html": 8,
    ".md": 10, ".json": 8, ".yml": 4, ".yaml": 2,
    ".sh": 3, ".sql": 2, ".env.example": 1,
}

def pick_extension():
    exts = list(EXT_WEIGHTS.keys())
    weights = list(EXT_WEIGHTS.values())
    return random.choices(exts, weights=weights, k=1)[0]

# ─── SCHEDULING ────────────────────────────────────────────────

def generate_daily_schedule(days_back, num_commits):
    end = date.today()
    start = end - timedelta(days=days_back - 1)
    total_days = days_back
    base = num_commits // total_days
    extra = num_commits % total_days
    schedule = {}
    for i in range(total_days):
        d = start + timedelta(days=i)
        wd = d.weekday()
        if wd >= 5:
            weight = random.uniform(0.2, 0.6)
        elif wd == 0:
            weight = random.uniform(0.6, 1.0)
        else:
            weight = random.uniform(0.7, 1.3)
        count = max(0, round(base * weight))
        schedule[d] = count
    total_so_far = sum(schedule.values())
    diff = num_commits - total_so_far
    days_list = list(schedule.keys())
    random.shuffle(days_list)
    i = 0
    while diff != 0 and days_list:
        d = days_list[i % len(days_list)]
        if diff > 0:
            schedule[d] += 1
            diff -= 1
        else:
            if schedule[d] > 0:
                schedule[d] -= 1
                diff += 1
        i += 1
    return {d: schedule[d] for d in sorted(schedule.keys()) if schedule[d] > 0}

def generate_timestamps_for_day(day, count):
    base = datetime(day.year, day.month, day.day)
    peak_hours = list(range(10, 12)) + list(range(14, 17))
    other_hours = [h for h in range(8, 22) if h not in peak_hours]
    tss = []
    for _ in range(count):
        if random.random() < 0.65:
            hour = random.choice(peak_hours)
        else:
            hour = random.choice(other_hours)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        ts = base + timedelta(hours=hour, minutes=minute, seconds=second)
        tss.append(ts)
    tss.sort()
    return tss

# ─── MODULE NAMES (for content variety only) ─────────────────────
MODULE_NAMES = ["auth", "api", "db", "ui", "core", "deps", "scripts", "docs"]
GHOST_DIR = "_ge"

PROTECTED_FILES = {
    "README.md", "readme.md", "Readme.md",
    ".gitignore", ".gitattributes",
    "LICENSE", "LICENSE.txt", "LICENSE.md",
}

PROTECTED_NAMES = {n.lower() for n in PROTECTED_FILES}

def ghost_file_path(include_subdir=True):
    ext = pick_extension()
    name_parts = [
        random.choice(["update", "fix", "add", "refactor", "implement", "optimize",
                        "remove", "rename", "extract", "bump", "drop", "migrate",
                        "validate", "parse", "render", "fetch", "cache", "merge",
                        "split", "flatten", "normalize", "sanitize", "encrypt",
                        "compress", "serialize", "deserialize", "hydrate", "purge"]),
        random.choice(["handler", "manager", "service", "provider", "factory",
                        "helper", "wrapper", "adapter", "builder", "parser",
                        "loader", "watcher", "scheduler", "task", "queue",
                        "module", "component", "container", "decorator", "filter"]),
        random.choice(["base", "core", "shared", "common", "utils", "internal",
                        "v2", "impl", "proto", "types", "config", "test"]),
    ]
    stem = "_".join(random.sample(name_parts, random.randint(2, 3)))
    if include_subdir and random.random() < 0.4:
        sub = random.choice(["core", "utils", "internal", "legacy", "v2", "experimental"])
        return f"{GHOST_DIR}/{sub}/{stem}{ext}", random.choice(MODULE_NAMES)
    return f"{GHOST_DIR}/{stem}{ext}", random.choice(MODULE_NAMES)

PY_FUNCTIONS = [
    (
        "def validate_{name}(data: dict) -> bool:\n"
        "    errors = []\n"
        "    for field in REQUIRED_FIELDS:\n"
        "        if field not in data or not data[field]:\n"
        "            errors.append(f'{{field}} is required')\n"
        "    if errors:\n"
        "        logger.warning(f'Validation failed: {{errors}}')\n"
        "        return False\n"
        "    return True\n"
    ),
    (
        "def process_{name}(items: list, **kwargs) -> list:\n"
        "    results = []\n"
        "    for item in items:\n"
        "        try:\n"
        "            transformed = transform_item(item, **kwargs)\n"
        "            results.append(transformed)\n"
        "        except ProcessingError as e:\n"
        "            logger.error(f'Failed to process {{item}}: {{e}}')\n"
        "            continue\n"
        "    return results\n"
    ),
    (
        "def {name}_handler(request: Request, response: Response) -> None:\n"
        "    if not request.user.is_authenticated:\n"
        "        response.status_code = 401\n"
        "        response.json({{'error': 'Unauthorized'}})\n"
        "        return\n"
        "    try:\n"
        "        data = request.json()\n"
        "        validated = validate_{name}_input(data)\n"
        "        result = process_{name}(validated)\n"
        "        response.json({{'status': 'ok', 'data': result}})\n"
        "    except ValidationError as e:\n"
        "        response.status_code = 422\n"
        "        response.json({{'error': str(e)}})\n"
    ),
    (
        "async def fetch_{name}(session: ClientSession, url: str) -> dict:\n"
        "    async with semaphore:\n"
        "        for attempt in range(MAX_RETRIES):\n"
        "            try:\n"
        "                async with session.get(url) as resp:\n"
        "                    if resp.status == 200:\n"
        "                        return await resp.json()\n"
        "                    logger.warning(f'Got {{resp.status}}, retry {{attempt+1}}')\n"
        "            except aiohttp.ClientError as e:\n"
        "                logger.error(f'Request failed: {{e}}')\n"
        "                if attempt == MAX_RETRIES - 1:\n"
        "                    raise\n"
        "                await asyncio.sleep(2 ** attempt)\n"
    ),
    (
        "class {Name}Manager:\n"
        "    def __init__(self, config: dict = None):\n"
        "        self.config = config or {{}}\n"
        "        self._items: dict = {{}}\n"
        "        self._init_resources()\n\n"
        "    def _init_resources(self) -> None:\n"
        "        self.pool = ConnectionPool(\n"
        "            min_size=self.config.get('pool_min', 5),\n"
        "            max_size=self.config.get('pool_max', 20),\n"
        "        )\n"
        "        self.cache = CacheClient(\n"
        "            ttl=self.config.get('cache_ttl', 300)\n"
        "        )\n\n"
        "    def get(self, key: str) -> Optional[dict]:\n"
        "        cached = self.cache.get(key)\n"
        "        if cached:\n"
        "            return cached\n"
        "        result = self.pool.query(\n"
        "            'SELECT * FROM items WHERE key = $1', key\n"
        "        )\n"
        "        if result:\n"
        "            self.cache.set(key, result)\n"
        "        return result\n"
    ),
]

JS_FUNCTIONS = [
    (
        "export function validate{Name}(data: {Name}Input): ValidationResult {{\n"
        "    const errors: Record<string, string> = {{}};\n\n"
        "    if (!data.email || !isValidEmail(data.email)) {{\n"
        "        errors.email = 'A valid email is required';\n"
        "    }}\n"
        "    if (!data.password || data.password.length < 8) {{\n"
        "        errors.password = 'Password must be at least 8 characters';\n"
        "    }}\n\n"
        "    return {{\n"
        "        valid: Object.keys(errors).length === 0,\n"
        "        errors,\n"
        "    }};\n"
        "}}\n"
    ),
    (
        "export const use{Name} = () => {{\n"
        "    const [data, setData] = useState<{Name}Data | null>(null);\n"
        "    const [loading, setLoading] = useState(true);\n"
        "    const [error, setError] = useState<string | null>(null);\n\n"
        "    useEffect(() => {{\n"
        "        const controller = new AbortController();\n"
        "        fetch{Name}(controller.signal)\n"
        "            .then(setData)\n"
        "            .catch(err => setError(err.message))\n"
        "            .finally(() => setLoading(false));\n"
        "        return () => controller.abort();\n"
        "    }}, []);\n\n"
        "    return {{ data, loading, error, refetch: () => fetch{Name}() }};\n"
        "}};\n"
    ),
    (
        "export async function fetch{Name}(signal?: AbortSignal): Promise<{Name}Response> {{\n"
        "    const response = await fetch(`/api/v1/{name_plural}`, {{\n"
        "        headers: {{\n"
        "            'Content-Type': 'application/json',\n"
        "            'Authorization': `Bearer ${{getToken()}}`,\n"
        "        }},\n"
        "        signal,\n"
        "    }});\n\n"
        "    if (!response.ok) {{\n"
        "        const error = await response.json();\n"
        "        throw new ApiError(error.message, response.status);\n"
        "    }}\n\n"
        "    return response.json();\n"
        "}}\n"
    ),
]

CSS_SNIPPETS = [
    (
        ".{name}-container {{\n"
        "    display: flex;\n"
        "    flex-direction: column;\n"
        "    gap: var(--spacing-md);\n"
        "    padding: var(--spacing-lg);\n"
        "    background: var(--surface-color);\n"
        "    border-radius: var(--radius-lg);\n"
        "    box-shadow: var(--shadow-sm);\n"
        "}}\n\n"
        ".{name}-container:hover {{\n"
        "    box-shadow: var(--shadow-md);\n"
        "    transition: box-shadow 0.2s ease;\n"
        "}}\n"
    ),
    (
        "@media (max-width: 768px) {{\n"
        "    .{name}-grid {{\n"
        "        grid-template-columns: 1fr;\n"
        "        gap: var(--spacing-sm);\n"
        "    }}\n\n"
        "    .{name}-header {{\n"
        "        font-size: var(--font-size-lg);\n"
        "        padding: var(--spacing-sm);\n"
        "    }}\n"
        "}}\n"
    ),
]

HTML_SNIPPETS = [
    (
        '<div class="{name}-card">\n'
        '    <div class="{name}-card__header">\n'
        '        <h3>{{ title }}</h3>\n'
        '        <span class="badge">{{ status }}</span>\n'
        '    </div>\n'
        '    <div class="{name}-card__body">\n'
        '        <p>{{ description }}</p>\n'
        '        <div class="{name}-card__meta">\n'
        '            <span>Created: {{ created_at | date }}</span>\n'
        '            <span>By: {{ author }}</span>\n'
        '        </div>\n'
        '    </div>\n'
        '    <div class="{name}-card__actions">\n'
        '        <button (click)="onEdit()">Edit</button>\n'
        '        <button (click)="onDelete()">Delete</button>\n'
        '    </div>\n'
        '</div>\n'
    ),
]

MD_SNIPPETS = [
    (
        "## {Name}\n\n"
        "### Overview\n"
        "The {name} module handles all {name_description} operations. "
        "It integrates with the core pipeline and provides extensible hooks for customization.\n\n"
        "### Usage\n"
        "```python\n"
        "from src.{module} import {Name}Manager\n\n"
        "manager = {Name}Manager(config={{\n"
        "    'timeout': 30,\n"
        "    'retries': 3,\n"
        "    'cache_ttl': 600,\n"
        "}})\n"
        "result = manager.process(data)\n"
        "```\n\n"
        "### Configuration\n"
        "| Parameter | Type | Default | Description |\n"
        "|-----------|------|---------|-------------|\n"
        "| timeout | int | 30 | Request timeout in seconds |\n"
        "| retries | int | 3 | Number of retry attempts |\n"
        "| cache_ttl | int | 600 | Cache TTL in seconds |\n"
        "| log_level | str | INFO | Logging verbosity |\n\n"
        "### Error Handling\n"
        "Common exceptions and their handling strategies are documented in the error reference.\n"
    ),
]

JSON_SNIPPETS = [
    (
        '"{name}": {{\n'
        '    "enabled": true,\n'
        '    "version": "2.1.0",\n'
        '    "settings": {{\n'
        '        "timeout_ms": {timeout},\n'
        '        "max_retries": {retries},\n'
        '        "log_level": "{log_level}"\n'
        '    }},\n'
        '    "features": [\n'
        '        "{feat1}",\n'
        '        "{feat2}"\n'
        '    ]\n'
        '}}'
    ),
]

YAML_SNIPPETS = [
    (
        "{name}:\n"
        "  image: {image}:${{{{TAG}}}}\n"
        "  build:\n"
        "    context: .\n"
        "    dockerfile: Dockerfile.{name}\n"
        "    args:\n"
        "      NODE_ENV: production\n"
        "  ports:\n"
        "    - \"{port}:{port}\"\n"
        "  environment:\n"
        "    - LOG_LEVEL={log_level}\n"
        "    - CACHE_TTL={cache_ttl}\n"
        "  volumes:\n"
        "    - {name}_data:/var/lib/data\n"
        "  restart: unless-stopped\n"
    ),
]

SH_SNIPPETS = [
    (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n\n"
        "{name}() {{\n"
        "    local input=\"${{1:-}}\"\n"
        "    if [[ -z \"$input\" ]]; then\n"
        "        echo \"Usage: {name} <input>\"\n"
        "        return 1\n"
        "    fi\n\n"
        "    echo \"Processing {name}: $input\"\n"
        "    # Validate\n"
        "    if [[ ! -f \"$input\" ]]; then\n"
        "        echo \"Error: File not found\" >&2\n"
        "        return 1\n"
        "    fi\n\n"
        "    # Process\n"
        "    local result=$(sanitize \"$input\")\n"
        "    echo \"$result\"\n"
        "}}\n\n"
        "main() {{\n"
        "    {name} \"$@\"\n"
        "}}\n\n"
        "main \"$@\"\n"
    ),
]

SQL_SNIPPETS = [
    (
        "CREATE TABLE IF NOT EXISTS {name} (\n"
        "    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"
        "    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),\n"
        "    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),\n"
        "    status VARCHAR(20) NOT NULL DEFAULT 'active',\n"
        "    metadata JSONB DEFAULT '{{}}'::jsonb,\n"
        "    CONSTRAINT {name}_status_check CHECK (status IN ('active', 'inactive', 'archived'))\n"
        ");\n\n"
        "CREATE INDEX idx_{name}_created_at ON {name}(created_at DESC);\n"
        "CREATE INDEX idx_{name}_status ON {name}(status) WHERE status = 'active';\n"
    ),
]

CONTENT_TEMPLATES = {
    ".py": PY_FUNCTIONS,
    ".js": JS_FUNCTIONS,
    ".ts": JS_FUNCTIONS,
    ".tsx": JS_FUNCTIONS,
    ".css": CSS_SNIPPETS,
    ".scss": CSS_SNIPPETS,
    ".html": HTML_SNIPPETS,
    ".md": MD_SNIPPETS,
    ".json": JSON_SNIPPETS,
    ".yml": YAML_SNIPPETS,
    ".yaml": YAML_SNIPPETS,
    ".sh": SH_SNIPPETS,
    ".sql": SQL_SNIPPETS,
}

# ─── MESSAGE GENERATION ─────────────────────────────────────────

COMMIT_TYPES = ["feat", "fix", "chore", "docs", "refactor", "test", "style", "perf"]
SCOPES = ["auth", "api", "db", "ui", "core", "config", "deps", "ci", "docs", "utils"]

DESCRIPTIONS = [
    "add input validation for {thing}",
    "implement {thing} handler with error handling",
    "update {thing} to support new requirements",
    "refactor {thing} to reduce code duplication",
    "fix edge case in {thing} when input is empty",
    "optimize {thing} query performance",
    "add unit tests for {thing} module",
    "improve error messaging in {thing}",
    "bump {thing} dependency version",
    "migrate {thing} to use new API pattern",
    "add logging and monitoring for {thing}",
    "implement caching layer for {thing}",
    "add configuration options for {thing}",
    "handle timeout gracefully in {thing}",
    "add pagination support to {thing}",
    "fix memory leak in {thing} handler",
    "add retry logic for {thing} failures",
    "improve type annotations in {thing}",
    "add rate limiting to {thing} endpoint",
    "update documentation for {thing}",
    "extract shared logic from {thing}",
    "add health check endpoint for {thing}",
    "implement data export for {thing}",
    "add sorting and filtering to {thing}",
    "migrate {thing} to async implementation",
    "fix race condition in {thing} worker",
    "add webhook support for {thing} events",
    "implement soft delete for {thing}",
    "add bulk operations for {thing}",
    "improve input sanitization for {thing}",
]

THINGS = [
    "pipeline", "hook", "adapter", "broker", "orchestrator", "saga",
    "dispatcher", "serializer", "middleware", "interceptor", "proxy",
    "circuit breaker", "throttle", "rate limiter", "pool", "cursor",
    "migration", "seeder", "scaffold", "blueprint", "recipe",
    "template", "snippet", "patch", "hotfix", "release candidate",
]

def generate_commit_message():
    ctype = random.choice(COMMIT_TYPES)
    scope = random.choice(SCOPES) if random.random() < 0.45 else None
    thing = random.choice(THINGS)
    desc = random.choice(DESCRIPTIONS).format(thing=thing)
    headline = f"{ctype}"
    if scope:
        headline += f"({scope})"
    headline += f": {desc}"
    lines = [headline]
    if random.random() < 0.4:
        lines.append("")
        body_lines = random.sample(DESCRIPTIONS, k=random.randint(1, 3))
        for bl in body_lines:
            lines.append(bl.format(thing=random.choice(THINGS)))
    if random.random() < 0.3 and ctype in ("feat", "fix"):
        lines.append("")
        lines.append(f"Closes #{random.randint(100, 999)}")
    if random.random() < 0.15:
        if not lines[-1]:
            lines.pop()
        lines.append("")
        lines.append(f"BREAKING CHANGE: {random.choice(DESCRIPTIONS).format(thing=random.choice(THINGS))}")
    return "\n".join(lines)


def generate_content(ext, module_name):
    templates = CONTENT_TEMPLATES.get(ext, MD_SNIPPETS)
    template = random.choice(templates)

    name = random.choice([
        "auth", "login", "register", "session", "profile", "token",
        "cache", "queue", "worker", "config", "logger", "metrics",
        "api", "route", "middleware", "serializer", "validator",
        "model", "schema", "migration", "query", "repo",
        "button", "modal", "form", "table", "dashboard", "navbar",
        "utils", "helpers", "decorators", "exceptions",
    ])
    Name = name.title()
    name_plural = name + ("es" if name.endswith("s") else "s")

    kwargs = {
        "name": name,
        "Name": Name,
        "name_plural": name_plural,
        "module": module_name or "core",
        "name_description": name.replace("_", " "),
        "timeout": random.choice([15, 30, 60, 120, 300]),
        "retries": random.choice([2, 3, 5]),
        "log_level": random.choice(["DEBUG", "INFO", "WARNING"]),
        "cache_ttl": random.choice([60, 120, 300, 600, 3600]),
        "image": random.choice(["node", "python", "alpine", "nginx"]),
        "port": random.choice([3000, 4000, 5000, 8080, 8000]),
        "feat1": random.choice(["caching", "logging", "metrics", "audit"]),
        "feat2": random.choice(["webhooks", "export", "batch", "realtime"]),
    }

    return template.format(**kwargs)

# ─── FILE REGISTRY ──────────────────────────────────────────────

NOOP_FILE = ".ghost_engine_state"

# ─── ENGINE ─────────────────────────────────────────────────────

class GhostEngine:
    def _run_git(self, args, cwd=None, env=None):
        cmd = ["git"] + args
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True,
            timeout=120, env=merged_env,
        )
        return result

    def _ensure_git_config(self, repo_path, git_name=None, git_email=None):
        for key in ("user.name", "user.email"):
            r = self._run_git(["config", key], cwd=repo_path)
            if r.returncode == 0 and r.stdout.strip():
                continue
            if key == "user.name" and git_name:
                self._run_git(["config", key, git_name], cwd=repo_path)
            elif key == "user.email" and git_email:
                self._run_git(["config", key, git_email], cwd=repo_path)
            else:
                raise RuntimeError(
                    f"Git '{key}' is not set. Set your name and email in Settings."
                )

    def _detect_default_branch(self, repo_path):
        r = self._run_git(["symbolic-ref", "refs/remotes/origin/HEAD"], cwd=repo_path)
        if r.returncode == 0:
            ref = r.stdout.strip()
            m = re.search(r'/([^/]+)$', ref)
            if m:
                return m.group(1)
        for candidate in ("main", "master"):
            r = self._run_git(["show-ref", f"refs/remotes/origin/{candidate}"], cwd=repo_path)
            if r.returncode == 0:
                return candidate
        return "main"

    def _emit(self, callback, level, message):
        if callback:
            callback(level, message)

    def run(self, repo_path, repo_remote, num_commits, days_back=1,
            ssh_key_path=None, github_token=None, git_name=None,
            git_email=None, callback=None):
        path = os.path.expanduser(repo_path)
        remote = repo_remote

        base_env = os.environ.copy()
        base_env["GIT_TERMINAL_PROMPT"] = "0"

        if ssh_key_path and os.path.exists(ssh_key_path):
            base_env["GIT_SSH_COMMAND"] = (
                f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no "
                f"-o IdentitiesOnly=yes -o BatchMode=yes"
            )
        elif ssh_key_path:
            self._emit(callback, "warning", f"SSH key not found at:\n  {ssh_key_path}")
        elif github_token and remote.startswith("https://"):
            self._emit(callback, "info", "Using GitHub token for auth")

        if not os.path.exists(path):
            clone_url = remote
            if github_token and remote.startswith("https://"):
                clone_url = remote.replace(
                    "https://", f"https://git:{github_token}@"
                )
            self._emit(callback, "info", f"Cloning {remote} …")
            r = self._run_git(["clone", clone_url, path], env=base_env)
            if r.returncode != 0:
                err = r.stderr.strip()
                if "could not read from remote" in err.lower() or "permission denied" in err.lower():
                    raise RuntimeError(
                        "Clone failed — authentication error.\n"
                        "• For SSH: set an SSH key in Settings and add to GitHub\n"
                        "• For HTTPS: set a GitHub token in Settings"
                    )
                raise RuntimeError(f"Clone failed:\n{err}")

        self._ensure_git_config(path, git_name, git_email)

        self._emit(callback, "info", "Stashing any uncommitted changes...")
        self._run_git(["stash", "push", "--include-untracked", "-m", "ghost-engineer-autostash"],
                       cwd=path, env=base_env)

        branch = self._detect_default_branch(path)
        self._emit(callback, "info", f"Syncing with remote '{branch}'...")
        self._run_git(["fetch", "origin"], cwd=path, env=base_env)
        self._run_git(["checkout", branch], cwd=path, env=base_env)
        self._run_git(["reset", "--hard", f"origin/{branch}"], cwd=path, env=base_env)

        schedule = generate_daily_schedule(days_back, num_commits)
        total_planned = sum(schedule.values())
        self._emit(callback, "info",
            f"Schedule: {len(schedule)} days, ~{total_planned} commits total")

        file_registry = {}
        all_timestamps = []
        for d in sorted(schedule.keys()):
            count = schedule[d]
            tss = generate_timestamps_for_day(d, count)
            all_timestamps.extend((ts, d) for ts in tss)

        all_timestamps.sort(key=lambda x: x[0])
        total = len(all_timestamps)

        self._emit(callback, "info", f"Generating {total} commits across {len(schedule)} days...\n")

        for idx, (ts, day) in enumerate(all_timestamps):
            date_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            env = base_env.copy()
            env["GIT_AUTHOR_DATE"] = date_str
            env["GIT_COMMITTER_DATE"] = date_str
            msg = generate_commit_message()

            try:
                commit_type = random.choices(
                    ["code", "multi", "empty", "doc"],
                    weights=[50, 25, 5, 20],
                    k=1
                )[0]

                if commit_type == "empty":
                    r = self._run_git(
                        ["commit", "--allow-empty", "-m", msg],
                        cwd=path, env=env
                    )
                    if r.returncode != 0:
                        self._emit(callback, "warning", f"Commit {idx+1} failed:\n{r.stderr}")
                        continue

                elif commit_type == "multi":
                    files_to_change = min(random.randint(2, 4), 6)
                    for _ in range(files_to_change):
                        fpath, module = ghost_file_path()
                        full = os.path.join(path, fpath)
                        ext = os.path.splitext(fpath)[1]

                        if os.path.basename(fpath).lower() in PROTECTED_NAMES:
                            continue
                        if fpath not in file_registry and os.path.exists(full):
                            continue

                        os.makedirs(os.path.dirname(full), exist_ok=True)

                        if fpath not in file_registry:
                            file_registry[fpath] = {"created": True, "version": 1}
                            content = generate_content(ext, module)
                            with open(full, "w") as f:
                                f.write(content)
                        else:
                            file_registry[fpath]["version"] += 1
                            snippet = generate_content(ext, module)
                            with open(full, "a") as f:
                                f.write(f"\n\n{snippet}")

                        self._run_git(["add", fpath], cwd=path)

                    r = self._run_git(["commit", "-m", msg], cwd=path, env=env)
                    if r.returncode != 0:
                        self._emit(callback, "warning", f"Commit {idx+1} failed:\n{r.stderr}")
                        continue

                elif commit_type == "doc":
                    doc_name = random.choice(THINGS).replace(" ", "_")
                    doc_path = os.path.join(path, GHOST_DIR, "docs", f"{doc_name}.md")
                    fpath = os.path.join(GHOST_DIR, "docs", f"{doc_name}.md")

                    if os.path.basename(fpath).lower() in PROTECTED_NAMES or os.path.exists(doc_path):
                        continue

                    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
                    with open(doc_path, "w") as f:
                        f.write(generate_content(".md", "docs"))
                    file_registry[fpath] = {"created": True, "version": 1}
                    self._run_git(["add", fpath], cwd=path)
                    r = self._run_git(["commit", "-m", msg], cwd=path, env=env)
                    if r.returncode != 0:
                        self._emit(callback, "warning", f"Commit {idx+1} failed:\n{r.stderr}")
                        continue

                else:
                    fpath, module = ghost_file_path()
                    full = os.path.join(path, fpath)
                    ext = os.path.splitext(fpath)[1]

                    if os.path.basename(fpath).lower() in PROTECTED_NAMES:
                        continue
                    if fpath not in file_registry and os.path.exists(full):
                        continue

                    os.makedirs(os.path.dirname(full), exist_ok=True)

                    if fpath not in file_registry:
                        file_registry[fpath] = {"created": True, "version": 1}
                        content = generate_content(ext, module)
                        with open(full, "w") as f:
                            f.write(content)
                    else:
                        file_registry[fpath]["version"] += 1
                        snippet = generate_content(ext, module)
                        with open(full, "a") as f:
                            f.write(f"\n\n{snippet}")

                    self._run_git(["add", fpath], cwd=path)
                    r = self._run_git(["commit", "-m", msg], cwd=path, env=env)
                    if r.returncode != 0:
                        self._emit(callback, "warning", f"Commit {idx+1} failed:\n{r.stderr}")
                        continue

            except Exception as e:
                self._emit(callback, "warning", f"Commit {idx+1} failed: {e}")
                continue

            day_label = day.strftime("%m/%d")
            short = msg[:55].replace("\n", "\\n")
            self._emit(callback, "progress",
                f"[{idx+1}/{total}] {day_label} {ts.strftime('%H:%M')}  {short}")

        self._emit(callback, "info", f"\nPushing to '{branch}'...")

        try:
            push_env = base_env.copy()
            push_args = ["push", "origin", branch]

            if github_token and remote.startswith("https://"):
                authed_url = remote.replace(
                    "https://", f"https://git:{github_token}@"
                )
                push_args = ["push", authed_url, branch]

            r = self._run_git(push_args, cwd=path, env=push_env)

            if r.returncode == 0:
                self._emit(callback, "success",
                    f"Done — {total} commits across {len(schedule)} days pushed to '{branch}'")

                if file_registry:
                    self._emit(callback, "info", "Cleaning up generated files...")
                    self._run_git(["rm", "-rf", GHOST_DIR], cwd=path)
                    cleanup_msg = "cleanup: remove generated files"
                    cr = self._run_git(["commit", "-m", cleanup_msg], cwd=path, env=base_env)
                    if cr.returncode == 0:
                        self._emit(callback, "info", "Pushing cleanup commit...")
                        self._run_git(push_args, cwd=path, env=push_env)
                        self._emit(callback, "success", "Ghost files deleted from repo and pushed — clean ✓")
                        self._emit(callback, "success", "All done — changes committed, pushed, and cleaned ✓")
                    else:
                        self._emit(callback, "warning", "No files to clean up")
            else:
                stderr_lower = r.stderr.lower()
                if "could not read from remote" in stderr_lower or "permission denied" in stderr_lower:
                    raise RuntimeError(
                        "Push failed — authentication error.\n"
                        "• For SSH: add your public key at github.com/settings/keys\n"
                        "• For HTTPS: set a valid GitHub token in Settings\n"
                        "  (needs 'repo' scope)"
                    )
                if "invalid username or token" in stderr_lower or "authentication failed" in stderr_lower:
                    raise RuntimeError(
                        "Push failed — invalid token.\n"
                        "Go to Settings and paste a valid GitHub token\n"
                        "with at least 'repo' scope."
                    )
                raise RuntimeError(f"Push failed:\n{r.stderr}")
        finally:
            self._emit(callback, "done", "Restoring your uncommitted changes...")
            pop_r = self._run_git(["stash", "pop"], cwd=path, env=base_env)
            if pop_r.returncode != 0 and "No stash entries" in pop_r.stderr:
                pass  # nothing was stashed, that's fine
