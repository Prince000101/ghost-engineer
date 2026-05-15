import os
import json
import subprocess
import shutil

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class ConfigManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.config_path = os.path.join(DATA_DIR, "config.json")
        self._ensure()

    def _ensure(self):
        if not os.path.exists(self.config_path):
            self._save({"repos": [], "github_token": "", "git_name": "", "git_email": ""})

    def _load(self):
        with open(self.config_path) as f:
            return json.load(f)

    def _save(self, data):
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    # ── Identity (git user) ──

    def get_identity(self):
        d = self._load()
        return d.get("git_name", ""), d.get("git_email", "")

    def save_identity(self, name, email):
        d = self._load()
        d["git_name"] = name
        d["git_email"] = email
        self._save(d)

    def is_identity_set(self):
        n, e = self.get_identity()
        return bool(n and e)

    # ── Repos ──

    def get_repos(self):
        return self._load().get("repos", [])

    def add_repo(self, name, path, remote):
        data = self._load()
        repos = data.setdefault("repos", [])
        for r in repos:
            if r["name"] == name:
                r["path"] = path
                r["remote"] = remote
                self._save(data)
                return False
        repos.append({"name": name, "path": path, "remote": remote})
        self._save(data)
        return True

    def remove_repo(self, name):
        data = self._load()
        data["repos"] = [r for r in data.get("repos", []) if r["name"] != name]
        self._save(data)

    # ── SSH keys ──

    def _keys_dir(self):
        d = os.path.join(DATA_DIR, "keys")
        os.makedirs(d, exist_ok=True)
        return d

    def has_ssh_key(self):
        return self.get_ssh_key_path() is not None

    def get_ssh_key_path(self):
        kd = self._keys_dir()
        for name in ["id_ed25519", "id_rsa", "id_ecdsa"]:
            p = os.path.join(kd, name)
            if os.path.exists(p):
                return p
        for fname in os.listdir(kd):
            fp = os.path.join(kd, fname)
            if os.path.isfile(fp) and not fname.endswith(".pub"):
                return fp
        return None

    def get_ssh_public_key(self):
        kd = self._keys_dir()
        if not os.path.isdir(kd):
            return None
        for name in os.listdir(kd):
            if name.endswith(".pub"):
                with open(os.path.join(kd, name)) as f:
                    return {"content": f.read().strip(), "filename": name}
        return None

    def _rm_all(self, directory):
        for fname in os.listdir(directory):
            fp = os.path.join(directory, fname)
            if os.path.isdir(fp):
                shutil.rmtree(fp)
            else:
                os.remove(fp)

    def generate_ssh_key(self):
        kd = self._keys_dir()
        self._rm_all(kd)
        priv = os.path.join(kd, "id_ed25519")
        r = subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", priv, "-N", "", "-q"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Failed to generate key:\n{r.stderr}")
        os.chmod(priv, 0o600)
        return priv

    def import_ssh_key(self, src):
        if not os.path.exists(src):
            raise FileNotFoundError(f"File not found: {src}")
        kd = self._keys_dir()
        self._rm_all(kd)
        dest = os.path.join(kd, os.path.basename(src))
        shutil.copy2(src, dest)
        os.chmod(dest, 0o600)
        pub_src = src + ".pub"
        if os.path.exists(pub_src):
            shutil.copy2(pub_src, dest + ".pub")
        return dest

    # ── GitHub token ──

    def get_github_token(self):
        return self._load().get("github_token", "")

    def save_github_token(self, token):
        data = self._load()
        data["github_token"] = token
        self._save(data)
