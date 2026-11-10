#!/usr/bin/env python3
"""Exercise the real npm production build without editing editorial sources."""

import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit
from unittest.mock import patch

from build_previews import SEGMENT, OUTPUT_MARKER, mounted_inputs, validate_destination

ROOT = Path(__file__).resolve().parents[1]


def manifest(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class HTML(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.meta = {}
        self.links = []
        self.scripts = []
        self.options = {}
        self.alternates = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.meta[attrs.get("name")] = attrs.get("content")
        if tag in ("link", "a"):
            self.links.append(attrs.get("href", ""))
        if tag == "option":
            self.links.append(attrs.get("value", ""))
            self.options[attrs.get("id")] = attrs.get("value", "")
        if tag == "link" and "hreflang" in attrs:
            self.alternates.append(attrs["href"])
        if tag == "script":
            self.scripts.append(attrs.get("src", ""))


def page(root, language, slug, *, draft=True, opt=True, future=False, expired=False, bundle=False, classified=True):
    path = root / "content" / language / "blog" / (f"{slug}/index.md" if bundle else f"{slug}.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = dict(title=f"Preview regression {slug}", slug=slug, translationKey=slug,
                    draft=draft, unlisted_preview=opt, date="2099-01-01T00:00:00Z" if future else "2020-01-01T00:00:00Z",
                    categories=["PreviewRegressionCategory"], tags=["PreviewRegressionTag"],
                    author="PreviewRegressionAuthor", aliases=[f"/old-{slug}/"])
    if expired:
        metadata["expiryDate"] = "2021-01-01T00:00:00Z"
    body = f"\n\nPreviewRegressionBody-{slug}\n\n## Example\n\nA harmless test fixture.\n"
    if not classified:
        metadata.pop("categories")
        metadata.pop("tags")
        metadata["title"] = "Published translation fixture"
        body = "\n\nPublished translation fixture.\n"
    if bundle:
        (path.parent / "sample.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>')
        body += '\n![Fixture](sample.svg)\n'
    path.write_text(json.dumps(metadata) + body)
    return path


def build(root, name, destination=None, cli=False, cold=False):
    sources = manifest(root / "content")
    log = root / f"{name}.log"
    with log.open("w") as stream:
        command = ["npm", "run", "build"]
        if cli:
            command += ["--", "--destination", str(destination)]
        env = dict(os.environ, HUGO_PUBLISHDIR=str(root / "content" if cli else destination or root / "public"),
                   HUGO_BUILDDRAFTS="true", HUGO_BUILDFUTURE="true", HUGO_BUILDEXPIRED="true")
        if cold:
            for key in ("HUGO_CACHEDIR", "GOMODCACHE", "GOCACHE"):
                path = root.parent / key.lower()
                assert not path.exists(), ("Cache must start absent", path)
                env[key] = str(path)
        result = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT, env=env)
    if result.returncode:
        print(log.read_text())
    assert result.returncode == 0, (name, result.returncode)
    assert manifest(root / "content") == sources, "Build changed editorial sources"
    print(f"PASS {name}: npm run build (exit 0), sources preserved" + (", fresh Hugo/Go caches" if cold else ""), flush=True)


def assert_mount_parser():
    with tempfile.TemporaryDirectory(prefix="mount-parser-") as temporary:
        source = Path(temporary) / "mounted-input"
        source.mkdir()
        sentinel = source / "sentinel"
        sentinel.write_text("preserve mounted input")
        module = {"dir": str(ROOT), "mounts": [{"source": str(source), "target": "assets"}]}
        second = {"dir": str(Path(temporary) / "module"), "mounts": [{"source": "layouts", "target": "layouts"}]}
        stream = json.dumps(module) + "\n" + json.dumps(second) + "\n"
        expected = [source, Path(second["dir"]), Path(second["dir"]) / "layouts"]
        for prefix in ("", "hugo: downloading modules …\n", "hugo: downloading modules …\r\n"):
            with patch("build_previews.run", return_value=subprocess.CompletedProcess([], 0, prefix + stream)):
                inputs = mounted_inputs([])
            assert inputs == expected
            try:
                validate_destination(source / "new-output", inputs)
            except ValueError as error:
                assert "overlaps an input" in str(error)
            else:
                raise AssertionError("Prefixed mount data failed to protect the mounted source")
        malformed_modules = [None, [], {}, {"dir": "relative", "mounts": []},
                             {"dir": "", "mounts": []}, {"dir": 3, "mounts": []},
                             {"dir": str(ROOT), "mounts": None}, {"dir": str(ROOT), "mounts": []},
                             {"dir": str(ROOT), "mounts": [None]}]
        for field in ("source", "target"):
            for value in (None, "", 1, "nul\0path"):
                mount = {"source": str(source), "target": "assets", field: value}
                malformed_modules.append({"dir": str(ROOT), "mounts": [mount]})
        invalid = ["", "hugo: downloading modules …\n", "unexpected diagnostic\n" + stream,
                   "hugo: downloading modules …\n{broken}\n" + stream, stream + "trailing diagnostic",
                   json.dumps(module) + '\n{"dir":', stream + '\n{"mounts":null}',
                   json.dumps(module) + "\nhugo: downloading modules …\n" + json.dumps(second)]
        invalid += [json.dumps(value) for value in malformed_modules]
        for value in invalid:
            for prefix in ("", "hugo: downloading modules …\n"):
                with patch("build_previews.run", return_value=subprocess.CompletedProcess([], 0, prefix + value)):
                    try:
                        mounted_inputs([])
                    except ValueError as error:
                        assert "Invalid Hugo mount data" in str(error), error
                    else:
                        raise AssertionError(f"Invalid mounts were accepted: {value!r}")
        assert sentinel.read_text() == "preserve mounted input"
        assert not (source / "new-output").exists()
    print(f"PASS mount parser: warm/prefixed streams preserve input guards; {len(invalid) * 2} malformed streams refused", flush=True)


def assert_destination_safety(root):
    capsule = root.parent
    metadata = capsule / "metadata"
    lane = metadata / "worktrees/lane"
    lane.mkdir(parents=True)
    (lane / "commondir").write_text("../..")
    (root / ".git").write_text(f"gitdir: {lane}\n")
    (root / ".hermes").mkdir()
    (root / ".hermes/sentinel").write_text("metadata")
    unrelated = capsule / "unrelated"
    unrelated.mkdir()
    (unrelated / "sentinel").write_text("preserve this directory")
    (capsule / "plain-file").write_text("preserve this file")
    counterfeit = capsule / "not-output"
    counterfeit.mkdir()
    (counterfeit / OUTPUT_MARKER).write_text("invalid marker")
    link = capsule / "linked-parent"
    link.symlink_to(unrelated, target_is_directory=True)
    broken = capsule / "broken-link"
    broken.symlink_to(capsule / "missing", target_is_directory=True)
    external = capsule / "external-inputs"
    shutil.copytree(root / "config", external / "config")
    shutil.copytree(root / "content", external / "content")
    languages = external / "config/_default/languages.toml"
    text = languages.read_text()
    for directory in ("korean", "english"):
        text = text.replace(f'"content/{directory}"', repr(str(external / "content" / directory)))
    languages.write_text(text)
    (external / "mounted-assets").mkdir()
    (external / "mounted-assets/sentinel").write_text("mounted input")
    module = external / "config/_default/module.toml"
    module.write_text(module.read_text() + f'\n[[mounts]]\nsource = "{external / "mounted-assets"}"\ntarget = "assets"\n')
    before = {name: manifest(root / name) for name in ("content", "config", "assets", "scripts", ".hermes")}
    external_before = manifest(external)
    metadata_before = manifest(metadata)
    cases = [(root / name, []) for name in ("content", "content/korean/blog/new-output", "config", "config/nested",
             "assets", "layouts", "static", "fixtures", "scripts", "resources", "node_modules", ".hermes", ".git",
             "new-repo-directory", "public/nested")]
    cases += [(path, []) for path in (root, capsule, unrelated, capsule / "plain-file", counterfeit,
              metadata, lane / "new-output", link, link / "new-output", link / "../other-output", broken / "new-output")]
    cases += [(path, ["--configDir", str(external / "config")]) for path in
              (external, external / "config", external / "config/nested", external / "content",
               external / "content/english/new-output", external / "mounted-assets/new-output")]
    for target, flags in cases:
        for cli in (True, False):
            command = ["python3", "scripts/build_previews.py", *flags]
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            if cli:
                command += ["--destination", str(target)]
                env.pop("HUGO_PUBLISHDIR", None)
            else:
                env["HUGO_PUBLISHDIR"] = str(target)
            result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
            assert result.returncode != 0 and "Unsafe output destination" in result.stderr, (target, cli, result.stdout, result.stderr)
            assert all(manifest(root / name) == original for name, original in before.items()), (target, cli)
            assert manifest(external) == external_before, (target, cli)
            assert manifest(metadata) == metadata_before, (target, cli)
            assert (root / ".git").read_text() == f"gitdir: {lane}\n"
            assert (unrelated / "sentinel").read_text() == "preserve this directory"
            assert (capsule / "plain-file").read_text() == "preserve this file"
            assert (counterfeit / OUTPUT_MARKER).read_text() == "invalid marker"
    (root / "public").symlink_to(unrelated, target_is_directory=True)
    for cli in (True, False):
        command = ["python3", "scripts/build_previews.py"] + (["--destination", "public"] if cli else [])
        result = subprocess.run(command, cwd=root, env=dict(os.environ, HUGO_PUBLISHDIR="public"), capture_output=True, text=True)
        assert result.returncode != 0 and "symlink ancestry" in result.stderr
        assert (unrelated / "sentinel").exists()
    (root / "public").unlink()
    (root / ".git").unlink()
    print(f"PASS R1: {len(cases) * 2 + 2} CLI/environment unsafe destinations rejected; inputs and sentinels preserved", flush=True)


def assert_translation(output, slug, target, *, published=False):
    source = output / (f"blog/{slug}/index.html" if published else f"blog/{SEGMENT}/{slug}/index.html")
    html = HTML(source.read_text())
    assert urlsplit(html.options["en"]).path == target, (slug, html.options)
    if target != "/en/":
        assert any(urlsplit(link).path == target for link in html.alternates), (slug, html.alternates)
    else:
        assert not any(urlsplit(link).path.startswith("/en/blog/") for link in html.alternates), (slug, html.alternates)
    for link in html.alternates + list(html.options.values()):
        path = urlsplit(link).path.lstrip("/")
        file = output / path
        assert (file / "index.html").is_file() if path.endswith("/") or not path else file.is_file(), (slug, link)


def assert_preview(output, prefix, slug, counterpart=True):
    target = f"{prefix}blog/{SEGMENT}/{slug}/"
    path = output / target / "index.html"
    assert path.is_file(), target
    source = path.read_text()
    html = HTML(source)
    assert html.meta.get("robots") == "noindex,nofollow", target
    assert html.meta.get("referrer") == "no-referrer", target
    assert any("css/style." in link for link in html.links), "Regular theme stylesheet missing"
    assert not any("googletagmanager" in src or "google-analytics" in src or "embed.js" in src for src in html.scripts)
    assert "open-remark" not in source and "share-icons" not in source and "Related Posts" not in source
    if counterpart:
        other = "" if prefix else "en/"
        assert any(f"/{other}blog/{SEGMENT}/{slug}/" in link for link in html.links), "Counterpart missing"
    assert not (output / f"{prefix}blog/{slug}/index.html").exists(), "Regular draft URL exists"
    assert not (output / f"{prefix}old-{slug}/index.html").exists(), "Draft alias exists"
    assert not (output / target / "index.md").exists()
    assert not (output / target / "index.xml").exists()


def assert_unlisted(output, slugs):
    for path in output.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(output)
        if SEGMENT in relative.parts:
            assert any(slug in relative.parts for slug in slugs), relative
            continue
        data = path.read_bytes()
        assert SEGMENT.encode() not in data, f"Preview path leaked: {relative}"
        for slug in slugs:
            assert f"Preview regression {slug}".encode() not in data, f"Preview title leaked: {relative}"
            assert f"PreviewRegressionBody-{slug}".encode() not in data, f"Preview body leaked: {relative}"
        assert b"PreviewRegressionCategory" not in data and b"previewregressioncategory" not in data, relative
        assert b"PreviewRegressionTag" not in data and b"previewregressiontag" not in data, relative


def main():
    assert_mount_parser()
    originals = {name: manifest(ROOT / name) for name in ("content", "assets", "static")}
    with tempfile.TemporaryDirectory(prefix="preview-regression-") as temporary:
        root = Path(temporary) / "repo"
        root.mkdir()
        for name in ("assets", "config", "content", "data", "fixtures", "i18n", "layouts", "scripts", "static", "themes", "node_modules"):
            shutil.copytree(ROOT / name, root / name, symlinks=False)
        if (ROOT / "resources").exists():
            shutil.copytree(ROOT / "resources", root / "resources")
        for name in ("hugo.toml", "go.mod", "go.sum", "package.json", "package-lock.json"):
            shutil.copy2(ROOT / name, root / name)
        assert_destination_safety(root)
        languages = root / "config/_default/languages.toml"
        text = languages.read_text()
        for directory in ("korean", "english"):
            text = text.replace(f'"content/{directory}"', f"'content/{directory}'")
        languages.write_text(text)
        for language in ("korean", "english"):
            page(root, language, "preview-regression-opted")
            page(root, language, "preview-regression-future", future=True)
            page(root, language, "preview-regression-hidden", opt=False)
            page(root, language, "preview-regression-string", opt="true")
            page(root, language, "preview-regression-bundle", bundle=True)
            page(root, language, "preview-regression-scheduled", draft=False, future=True)
        # A one-language opt-in must not create a translated public URL.
        page(root, "korean", "preview-regression-solo")
        page(root, "english", "preview-regression-solo", opt=False)
        translation_slugs = ["preview-regression-to-future", "preview-regression-to-expired", "preview-regression-to-live"]
        for slug in translation_slugs:
            page(root, "korean", slug)
        page(root, "english", translation_slugs[0], draft=False, opt=False, future=True)
        page(root, "english", translation_slugs[1], draft=False, opt=False, expired=True)
        page(root, "english", translation_slugs[2], draft=False, opt=False, classified=False)
        for language in ("korean", "english"):
            page(root, language, "preview-regression-published-pair", draft=False, opt=False, classified=False)
        build(root, "initial", cold=True)
        output = root / "public"
        slugs = ["preview-system-check", "preview-regression-opted", "preview-regression-future", "preview-regression-bundle", "preview-regression-solo"]
        for prefix in ("", "en/"):
            for slug in slugs[:-1]:
                assert_preview(output, prefix, slug)
            for slug in ("preview-regression-hidden", "preview-regression-string", "preview-regression-scheduled"):
                assert not (output / f"{prefix}blog/{slug}/index.html").exists()
                assert not (output / f"{prefix}blog/{SEGMENT}/{slug}/index.html").exists()
            assert (output / f"{prefix}blog/{SEGMENT}/preview-regression-bundle/sample.svg").exists()
        assert_preview(output, "", slugs[-1], counterpart=False)
        assert not (output / f"en/blog/{SEGMENT}/{slugs[-1]}/index.html").exists()
        assert_translation(output, "preview-regression-solo", "/en/")
        for slug in translation_slugs[:2]:
            assert_translation(output, slug, "/en/")
            assert not (output / f"en/blog/{slug}/index.html").exists()
        assert_translation(output, translation_slugs[2], f"/en/blog/{translation_slugs[2]}/")
        assert_translation(output, "preview-regression-published-pair", "/en/blog/preview-regression-published-pair/", published=True)
        assert_unlisted(output, slugs + translation_slugs + ["preview-regression-hidden", "preview-regression-string", "preview-regression-scheduled"])
        # Fixture is a demo, with no fabricated publication time in HTML or JSON-LD.
        demo = (output / f"blog/{SEGMENT}/preview-system-check/index.html").read_text()
        assert "0001" not in demo and "datePublished" not in demo
        print("PASS bilingual/future/bundle/single-language/strict opt-in/privacy/discovery", flush=True)
        print("PASS R2/C1: future/expired/unselected translations fall back home with no hreflang; existing production and published pairs retain links; single-quoted contentDir supported", flush=True)
        for language in ("korean", "english"):
            page(root, language, "preview-regression-opted", draft=False)
            page(root, language, "preview-regression-future", opt=False, future=True)
            (root / "content" / language / "blog/preview-regression-bundle/index.md").unlink()
        (root / "content/korean/blog/preview-regression-solo.md").unlink()
        for slug in translation_slugs:
            (root / f"content/korean/blog/{slug}.md").unlink()
        # Exercise recognition of the pre-wrapper public tree without its ownership marker.
        (output / OUTPUT_MARKER).unlink()
        for fixture in (root / "fixtures/draft-previews").rglob("*.md"):
            fixture.write_text(fixture.read_text() + "\nPREVIEW-DEMO-EDIT\n")
        build(root, "promotion-removal")
        for prefix in ("", "en/"):
            assert "PREVIEW-DEMO-EDIT" in (output / f"{prefix}blog/{SEGMENT}/preview-system-check/index.html").read_text()
            published = (output / f"{prefix}blog/preview-regression-opted/index.html").read_text()
            html = HTML(published)
            assert html.meta.get("robots") != "noindex,nofollow"
            assert "share-icons" in published and "open-remark" in published
            assert "Unpublished preview" not in published and "미발행 미리보기" not in published
            assert SEGMENT not in published
            assert "preview-regression-opted" in (output / f"{prefix}index.xml").read_text()
            for slug in slugs[1:]:
                assert not (output / f"{prefix}blog/{SEGMENT}/{slug}/index.html").exists(), slug
        # Remove infrastructure fixture opt-in as well: no stale segment directory remains.
        shutil.rmtree(root / "fixtures/draft-previews")
        output = root.parent / "external-output"
        output.mkdir()
        build(root, "all-removed", destination=output)
        assert not list(output.glob(f"**/{SEGMENT}"))
        assert all(b"PREVIEW-DEMO-EDIT" not in p.read_bytes() for p in output.rglob("*") if p.is_file())
        (output / "stale-output").write_text("remove on rebuild")
        build(root, "external-reuse", destination=output, cli=True)
        assert not (output / "stale-output").exists()
        assert (output / OUTPUT_MARKER).is_file()
        print("PASS R1: default/legacy public reuse, empty external destination, owned external CLI reuse, CLI precedence over unsafe environment", flush=True)
        print("PASS promotion with stale flag, opt-out, deletion, and stale-output removal", flush=True)
    for name, before in originals.items():
        assert manifest(ROOT / name) == before, f"Regression changed original {name}"
    print("PASS original editorial content/assets preserved; all preview regressions passed", flush=True)


if __name__ == "__main__":
    main()
