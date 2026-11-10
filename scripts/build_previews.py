#!/usr/bin/env python3
"""Build production first, then overlay only explicitly selected draft HTML/resources."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SEGMENT = "966685151eac268b47652f9a"
LANGUAGES = {"korean": "", "english": "en/"}
ASSET_ROOTS = ("css", "js", "images", "plugins", "fonts")
OUTPUT_MARKER = ".blog-output.json"
OUTPUT_IDENTITY = '{"format":"blog-production-output-v1"}\n'


def overlaps(left, right):
    return left == right or left in right.parents or right in left.parents


def git_inputs():
    dot_git = ROOT / ".git"
    if not dot_git.is_file():
        return [dot_git.resolve()]
    pointer = dot_git.read_text(encoding="utf-8").strip()
    if not pointer.startswith("gitdir: "):
        raise ValueError("Invalid Git metadata pointer")
    directory = (ROOT / pointer.removeprefix("gitdir: ")).resolve()
    common = directory / "commondir"
    return [directory, (directory / common.read_text().strip()).resolve()] if common.is_file() else [directory]


def mounted_inputs(common):
    result = run("hugo", "config", "mounts", *common, capture_output=True, text=True)
    remaining = result.stdout.strip()
    inputs = []
    while remaining:
        module, end = json.JSONDecoder().raw_decode(remaining)
        directory = Path(module["dir"]).resolve()
        if directory != ROOT:
            inputs.append(directory)
        inputs.extend(directory / mount["source"] for mount in module["mounts"])
        remaining = remaining[end:].lstrip()
    return inputs


def validate_destination(raw, inputs):
    candidate = ROOT / raw
    # Inspect lexical ancestors before resolve(), including symlink/../ paths.
    if any(path.is_symlink() for path in (candidate, *candidate.parents)):
        raise ValueError("Unsafe output destination: symlink ancestry")
    destination = candidate.resolve()
    if destination == ROOT or destination in ROOT.parents:
        raise ValueError("Unsafe output destination: repository ancestor")
    if ROOT in destination.parents and destination != ROOT / "public":
        raise ValueError("Unsafe output destination: only public is allowed inside the repository")
    if any(overlaps(destination, path.resolve()) for path in inputs):
        raise ValueError("Unsafe output destination: overlaps an input")
    if destination.exists():
        if not destination.is_dir():
            raise ValueError("Unsafe output destination: not a directory")
        marker = destination / OUTPUT_MARKER
        owned = marker.is_file() and not marker.is_symlink() and marker.read_text() == OUTPUT_IDENTITY
        # Migrate the pre-wrapper public tree, but never adopt arbitrary external trees.
        legacy_files = [destination / name for name in ("index.html", "en/index.html", "CNAME", "sitemap.xml")]
        legacy = (destination == ROOT / "public"
                  and all(path.is_file() and not path.is_symlink() for path in legacy_files)
                  and (destination / "CNAME").read_text().strip() == "blog.hakhub.net"
                  and re.search(r'name=[\"\']?generator[\"\']?\s+content=[\"\']?Hugo',
                                (destination / "index.html").read_text()) is not None)
        if any(destination.iterdir()) and not (owned or legacy):
            raise ValueError("Unsafe output destination: existing directory is not a recognized output")
    return destination


def public_urls(output, selected):
    urls = set()
    for path in output.rglob("*.html"):
        relative = path.relative_to(output).as_posix()
        urls.add(relative.removesuffix("index.html") if path.name == "index.html" else relative)
    return sorted(urls | {f"{target}/" for target in selected})


def run(*args, **kwargs):
    env = dict(os.environ)
    # Hugo gives these environment settings precedence over their CLI equivalents.
    for key in ("HUGO_PUBLISHDIR", "HUGO_BUILDDRAFTS", "HUGO_BUILDFUTURE", "HUGO_BUILDEXPIRED"):
        env.pop(key, None)
    return subprocess.run(args, cwd=ROOT, env=env, check=True, **kwargs)


def read_page(path):
    source = path.read_text(encoding="utf-8")
    metadata, end = json.JSONDecoder().raw_decode(source.lstrip())
    return metadata, source.lstrip()[end:]


def write_page(path, metadata, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + body, encoding="utf-8")


def select_previews(content, fixtures):
    selected = {}
    candidates = [(p, content) for p in sorted(content.rglob("*.md"))]
    candidates += [(p, fixtures) for p in sorted(fixtures.rglob("*.md"))]
    for source, base in candidates:
        relative = source.relative_to(base)
        if relative.parts[0] not in LANGUAGES:
            continue
        metadata, body = read_page(source)
        if metadata.get("draft") is not True or metadata.get("unlisted_preview") is not True:
            continue
        if base == content and (len(relative.parts) < 3 or relative.parts[1] != "blog"):
            raise ValueError(f"Preview opt-in is supported only in blog: {relative}")
        basename = source.parent.name if source.stem == "index" else source.stem
        slug = metadata.get("slug", basename)
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"Preview requires a kebab-case slug: {relative}")
        prefix = LANGUAGES[relative.parts[0]]
        target = f"{prefix}blog/{SEGMENT}/{slug}"
        if target in selected:
            raise ValueError(f"Duplicate preview URL: {target}")
        # Only the disposable copy becomes renderable. No draft build flag is used.
        metadata.update(draft=False, url=f"/{target}/", aliases=[], outputs=["HTML"],
                        sitemap={"disable": True}, build={"list": "never", "render": "always"},
                        unlisted_preview=True, canonical="", noindex=True)
        metadata.pop("_build", None)
        metadata.pop("cascade", None)
        if base == fixtures:
            source = content / relative.parts[0] / "blog" / f"{slug}.md"
            if source.exists():
                raise ValueError(f"Fixture conflicts with editorial source: {source.name}")
        write_page(source, metadata, body)
        selected[target] = source
    selected_sources = set(selected.values())
    for source in content.rglob("*.md"):
        if source not in selected_sources:
            metadata, body = read_page(source)
            # Keep ref/relref targets available without rendering the public site twice.
            metadata["build"] = {"list": "never", "render": "link"}
            metadata.pop("_build", None)
            write_page(source, metadata, body)
    return selected


def merge_previews(stage, output, selected):
    # Never merge stage indexes, feeds, sitemaps, manifests, or normal-page HTML.
    for target in selected:
        source = stage / target
        if not (source / "index.html").is_file():
            raise ValueError(f"Preview was not rendered: {target}")
        destination = output / target
        if destination.exists():
            raise ValueError(f"Preview collides with production output: {target}")
        shutil.copytree(source, destination)
    # Image processing and fingerprinting may produce preview-only shared assets.
    # Existing production assets are authoritative and must remain byte-identical.
    for name in ASSET_ROOTS:
        for source in sorted((stage / name).rglob("*")):
            if not source.is_file():
                continue
            relative = source.relative_to(stage)
            destination = output / relative
            if destination.exists():
                if destination.read_bytes() != source.read_bytes():
                    raise ValueError(f"Preview asset collides with production asset: {relative}")
            else:
                if SEGMENT.encode() in source.read_bytes():
                    raise ValueError(f"Preview path leaked into shared asset: {relative}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)


def build():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configDir", default="config")
    parser.add_argument("--destination", default=os.environ.get("HUGO_PUBLISHDIR", "public"))
    parser.add_argument("--baseURL")
    args = parser.parse_args()
    common = ["--configDir", str(Path(args.configDir).resolve())]
    if args.baseURL:
        common += ["--baseURL", args.baseURL]
    language_config = (Path(args.configDir) / "_default/languages.toml").read_text(encoding="utf-8")
    language_data = tomllib.loads(language_config)
    inputs = [Path(args.configDir).resolve(), *git_inputs(),
              *(ROOT / language_data[code]["contentDir"] for code in ("ko", "en"))]
    destination = validate_destination(args.destination, inputs)
    inputs.extend(mounted_inputs(common))
    validate_destination(args.destination, inputs)
    run("node", "scripts/themeGenerator.js")
    with tempfile.TemporaryDirectory(prefix="blog-build-") as directory:
        temporary = Path(directory)
        output = temporary / "production"
        run("hugo", "--environment", "production", "--gc", "--minify", "--forceSyncStatic",
            "--buildDrafts=false", "--buildFuture=false", "--buildExpired=false",
            "--destination", str(output), *common)
        content = temporary / "content"
        # A tiny conversion project also supports external contentDir overlays used by tests.
        # Hugo's converter does not traverse those mounts in the full site's configuration.
        converter = temporary / "converter"
        for code, directory in (("ko", "korean"), ("en", "english")):
            shutil.copytree(ROOT / language_data[code]["contentDir"], converter / "content" / directory)
        shutil.copytree(ROOT / "layouts", converter / "layouts")
        for name in ("go.mod", "go.sum"):
            shutil.copy2(ROOT / name, converter / name)
        (converter / "config/_default").mkdir(parents=True)
        shutil.copy2(ROOT / "config/_default/module.toml", converter / "config/_default/module.toml")
        (converter / "hugo.toml").write_text(
            f'theme = "hugoplate"\nthemesDir = {json.dumps(str(ROOT / "themes"))}\n'
            'defaultContentLanguage = "ko"\n[languages.ko]\ncontentDir = "content/korean"\n'
            '[languages.en]\ncontentDir = "content/english"\n', encoding="utf-8")
        # Let Hugo parse YAML/TOML/JSON instead of maintaining a second front-matter parser.
        run("hugo", "convert", "toJSON", "--source", str(converter), "--output", str(content))
        selected = select_previews(content, ROOT / "fixtures/draft-previews")
        if selected:
            stage = temporary / "previews"
            config_dir = temporary / "config"
            shutil.copytree(Path(args.configDir).resolve(), config_dir)
            staged_languages = json.loads(json.dumps(language_data))
            for code, directory in (("ko", "korean"), ("en", "english")):
                staged_languages[code]["contentDir"] = str(content / directory)
            (config_dir / "_default/languages.toml").unlink()
            (config_dir / "_default/languages.json").write_text(json.dumps(staged_languages), encoding="utf-8")
            config = temporary / "preview.json"
            config.write_text(json.dumps({
                "resourceDir": str(temporary / "resources"),
                "services": {"googleAnalytics": {"ID": ""}},
                "params": {"draft_preview_build": True, "draft_preview_urls": public_urls(output, selected),
                           "google_tag_manager": "", "google_adsense": "",
                           "custom_script": "", "open_remark": {"enable": False},
                           "search": {"enable": False}, "pwa": {"enable": False},
                           "llms": {"generate_llms_txt": False, "generate_llms_full_txt": False}},
            }), encoding="utf-8")
            run("hugo", "--environment", "production", "--config", f"hugo.toml,{config}",
                "--minify", "--forceSyncStatic", "--buildDrafts=false", "--buildFuture", "--buildExpired",
                "--destination", str(stage), "--configDir", str(config_dir),
                *(["--baseURL", args.baseURL] if args.baseURL else []))
            merge_previews(stage, output, selected)
        # Replace instead of updating: opt-out, deletion, and promotion remove old URLs.
        (output / OUTPUT_MARKER).write_text(OUTPUT_IDENTITY, encoding="utf-8")
        validate_destination(args.destination, inputs)
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(output, destination)
        print(f"Production build complete; {len(selected)} unlisted previews.")


if __name__ == "__main__":
    build()
