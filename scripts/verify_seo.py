#!/usr/bin/env python3
"""Check production SEO output and rebuild isolated bilingual llms fixtures."""

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


class Head(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.capture = None
        self.buffer = []
        self.titles = []
        self.meta = {}
        self.canonical = []
        self.alternates = []
        self.schemas = []
        self.h1 = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self.in_head = True
        if tag == "h1":
            self.h1 += 1
        if not self.in_head:
            return
        if tag == "meta":
            key = attrs.get("name", attrs.get("property", ""))
            self.meta.setdefault(key, []).append(attrs.get("content", ""))
        if tag == "link":
            if attrs.get("rel") == "canonical":
                self.canonical.append(attrs["href"])
            if "hreflang" in attrs:
                self.alternates.append((attrs["hreflang"], attrs["href"]))
        if tag == "title" or (tag == "script" and attrs.get("type") == "application/ld+json"):
            self.capture = tag
            self.buffer = []

    def handle_data(self, data):
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == self.capture:
            value = "".join(self.buffer)
            if tag == "title":
                self.titles.append(value)
            else:
                self.schemas.append(json.loads(value))
            self.capture = None
        if tag == "head":
            self.in_head = False

    def one(self, name):
        values = self.meta.get(name, [])
        assert len(values) == 1 and values[0].strip(), (name, values)
        return values[0]

    def schema(self, kind):
        matches = [s for s in self.schemas if s.get("@type") == kind]
        assert len(matches) == 1, (kind, matches)
        return matches[0]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_manifest():
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted((ROOT / "content").rglob("*")) if p.is_file()}


def snapshot(destination):
    pages = {}
    for path in sorted(destination.rglob("*.html")):
        head = Head(path.read_text())
        # Hugo pagination aliases are redirects, with no normal SEO head.
        if not head.meta.get("description"):
            continue
        pages[str(path.relative_to(destination))] = {
            "title": head.titles,
            "description": head.meta.get("description"),
            "canonical": head.canonical,
            "alternates": [list(item) for item in sorted(head.alternates)],
            "robots": {k: v for k, v in head.meta.items() if k.lower() in ("robots", "googlebot", "bingbot")},
            "schemas": head.schemas,
        }
    return {
        "pages": pages,
        "content": content_manifest(),
        "sitemaps": {str(p.relative_to(destination)): digest(p) for p in destination.rglob("*sitemap*.xml")},
        "robots_txt": digest(destination / "robots.txt") if (destination / "robots.txt").exists() else None,
    }


def verify(destination, baseline):
    current = snapshot(destination)
    assert current["content"] == baseline["content"], "Content bytes changed"
    assert current["sitemaps"] == baseline["sitemaps"], "Sitemap URLs/dates/alternates changed"
    assert current["robots_txt"] == baseline["robots_txt"], "robots.txt changed"
    assert current["pages"].keys() == baseline["pages"].keys(), "HTML page inventory changed"
    counts = Counter()
    topic_titles = {"ko": set(), "en": set()}
    topic_descriptions = {"ko": set(), "en": set()}
    for name, old in baseline["pages"].items():
        head = Head((destination / name).read_text())
        new = current["pages"][name]
        for key in ("canonical", "alternates", "robots"):
            assert new[key] == old[key], (name, key)
        assert len(head.canonical) == 1, name
        assert len(head.alternates) == len(set(head.alternates)), name
        assert len(head.titles) == 1 and head.titles[0].strip(), name
        title = head.titles[0]
        description = head.one("description")
        assert head.one("og:title") == head.one("twitter:title") == title, name
        assert head.one("og:description") == head.one("twitter:description") == description, name
        lang = "en" if name.startswith("en/") else "ko"
        local = name.removeprefix("en/")
        article = any(s.get("@type") == "BlogPosting" for s in head.schemas)
        if article:
            counts[f"{lang}_articles"] += 1
            assert new["title"] == old["title"] and new["description"] == old["description"], name
            assert new["schemas"] == old["schemas"], (name, "article JSON-LD changed")
            schema = head.schema("BlogPosting")
            assert schema["inLanguage"] == ("en-US" if lang == "en" else "ko-KR"), name
            assert schema["url"] == head.one("og:url"), name
            assert head.one("og:type") == "article", name
            for meta, field in (("article:published_time", "datePublished"), ("article:modified_time", "dateModified")):
                if field in schema:
                    assert head.one(meta) == schema[field], name
                else:
                    assert meta not in head.meta, name
        else:
            assert head.one("og:type") == "website", name
            assert not any(k.startswith("article:") for k in head.meta), name
        if local.startswith(("tags/", "categories/")):
            counts[f"{lang}_topics"] += 1
            assert title != "HakHubNet" and " | HakHubNet" in title, (name, title)
            assert bool(re.search("[가-힣]", description)) == (lang == "ko"), (name, description)
            assert title not in topic_titles[lang], (name, "duplicate topic title")
            assert description not in topic_descriptions[lang], (name, "duplicate topic description")
            topic_titles[lang].add(title)
            topic_descriptions[lang].add(description)
        if local == "index.html":
            counts[f"{lang}_home"] += 1
            assert title != "HakHubNet", name
            schema = head.schema("WebSite")
            assert schema["description"] == description, name
            assert schema["inLanguage"] == ("en-US" if lang == "en" else "ko-KR"), name
            assert bool(re.search("[가-힣]", description)) == (lang == "ko"), name
        if local == "about/index.html":
            assert head.h1 == 1, (name, head.h1)
            assert '<h1 class="h3 mb-6">' in (destination / name).read_text(), name
            counts[f"{lang}_about"] += 1
        match = re.fullmatch(r"blog/page/(\d+)/index.html", local)
        if match:
            suffix = f"{match[1]}페이지" if lang == "ko" else f"Page {match[1]}"
            assert title.endswith(" | " + suffix), (name, title)
            counts[f"{lang}_pagination"] += 1
    for lang in ("ko", "en"):
        for kind in ("articles", "topics", "home", "about", "pagination"):
            assert counts[f"{lang}_{kind}"] > 0, (lang, kind)
    print(json.dumps({"seo": "PASS", "pages": len(current["pages"]), "coverage": dict(counts), "content_files_unchanged": len(current["content"])}, ensure_ascii=False))


def llms_regression(destination):
    before = snapshot(destination)
    output_hashes = {str(p.relative_to(destination)): digest(p) for p in destination.rglob("*") if p.is_file()}
    work = ROOT / ".atl" / "seo-regression"
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fixture-", dir=work) as temporary:
        temp = Path(temporary)
        content = temp / "content"
        shutil.copytree(ROOT / "content", content)
        config_dir = temp / "config"
        shutil.copytree(ROOT / "config", config_dir)
        languages = config_dir / "_default/languages.toml"
        language_config = languages.read_text()
        for directory in ("korean", "english"):
            language_config = language_config.replace(f'"content/{directory}"', json.dumps(str(content / directory)))
        languages.write_text(language_config)
        output = temp / "public"
        env = dict(os.environ, HUGO_PUBLISHDIR=str(output))
        # The parent build's isolated resource and module caches are reused only
        # within this checkout; fixture output never enters the publish tree.
        for stage in ("NEW", "UPDATED"):
            for lang, directory in (("ko", "korean"), ("en", "english")):
                posts = content / directory / "blog"
                for draft in (False, True):
                    slug = "seo-regression-draft" if draft else "seo-regression-fixture"
                    marker = f"{stage}-{lang}-{'DRAFT' if draft else 'PUBLISHED'}"
                    (posts / f"{slug}.md").write_text(f'''---
title: "{marker}-TITLE"
description: "{marker}-DESCRIPTION"
date: 2020-01-02T03:04:05Z
lastmod: 2020-02-03T04:05:06Z
translationKey: "{slug}"
draft: {str(draft).lower()}
---
{marker}-BODY
''')
                # Exercise explicit term/taxonomy overrides without real edits.
                terms = content / directory / "tags"
                terms.mkdir(exist_ok=True)
                (terms / "_index.md").write_text('---\nmeta_title: "EXPLICIT-TAXONOMY-TITLE"\nmeta_description: "EXPLICIT-TAXONOMY-DESCRIPTION"\n---\n')
                term = terms / "seo-fixture"
                term.mkdir(exist_ok=True)
                (term / "_index.md").write_text('---\nmeta_title: "EXPLICIT-TERM-TITLE"\nmeta_description: "EXPLICIT-TERM-DESCRIPTION"\ndescription: "LOWER-PRIORITY-DESCRIPTION"\n---\n')
                fallback = terms / "seo-fallback"
                fallback.mkdir(exist_ok=True)
                (fallback / "_index.md").write_text('---\ntitle: "Fallback topic"\ndescription: "EXPLICIT-FALLBACK-DESCRIPTION"\n---\n')
            log = work / f"{stage.lower()}-build.log"
            command = ["npm", "run", "build", "--", "--configDir", str(config_dir)]
            with log.open("w") as stream:
                subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True)
            for lang, prefix in (("ko", ""), ("en", "en/")):
                base = output / prefix
                index = (base / "llms.txt").read_text()
                full = (base / "llms-full.txt").read_text()
                md = (base / "blog/seo-regression-fixture/index.md").read_text()
                marker = f"{stage}-{lang}-PUBLISHED"
                assert marker + "-TITLE" in index and marker + "-DESCRIPTION" in index, (stage, lang, "index")
                assert marker + "-BODY" in full and marker + "-BODY" in md, (stage, lang, "body")
                for value in (index, full, md):
                    assert "DRAFT-" not in value, (stage, lang, "draft leaked")
                    if stage == "UPDATED":
                        assert "NEW-" + lang + "-PUBLISHED" not in value, (stage, lang, "stale output")
                assert not (base / "blog/seo-regression-draft").exists(), (stage, lang, "draft HTML/Markdown")
                for path, title, description in (("tags", "EXPLICIT-TAXONOMY-TITLE", "EXPLICIT-TAXONOMY-DESCRIPTION"), ("tags/seo-fixture", "EXPLICIT-TERM-TITLE", "EXPLICIT-TERM-DESCRIPTION"), ("tags/seo-fallback", "Fallback topic | " + ("태그" if lang == "ko" else "Tags") + " | HakHubNet", "EXPLICIT-FALLBACK-DESCRIPTION")):
                    head = Head((base / path / "index.html").read_text())
                    assert head.titles == [title] and head.one("description") == description, (lang, path)
                article = Head((base / "blog/seo-regression-fixture/index.html").read_text())
                assert article.one("article:published_time") == "2020-01-02T03:04:05Z"
                assert article.one("article:modified_time") == "2020-02-03T04:05:06Z"
                assert article.schema("BlogPosting")["dateModified"] == article.one("article:modified_time")
            # All real article URLs/dates and source bytes survive each rebuild.
            rebuilt = snapshot(output)
            assert rebuilt["content"] == before["content"]
            for name, original in before["pages"].items():
                if any(s.get("@type") == "BlogPosting" for s in original["schemas"]):
                    assert rebuilt["pages"][name]["canonical"] == original["canonical"], name
                    assert rebuilt["pages"][name]["schemas"] == original["schemas"], name
            print(f"llms {stage}: PASS (KO/EN title, description, body, draft exclusion, explicit metadata, real article URLs/dates)")
    assert snapshot(destination) == before, "Production snapshot changed"
    assert {str(p.relative_to(destination)): digest(p) for p in destination.rglob("*") if p.is_file()} == output_hashes, "Production output bytes changed"
    assert not temp.exists(), "Fixture directory remains"
    assert not list((ROOT / "content").rglob("*seo-regression*")), "Fixture leaked into real content"
    print("llms cleanup: PASS (overlay removed; real content and every production output byte unchanged)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=ROOT / "public")
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--llms-regression", action="store_true")
    args = parser.parse_args()
    if args.snapshot:
        args.snapshot.write_text(json.dumps(snapshot(args.destination), ensure_ascii=False, indent=2))
        print(f"Snapshot saved: {args.snapshot}")
    if args.baseline:
        verify(args.destination, json.loads(args.baseline.read_text()))
    if args.llms_regression:
        llms_regression(args.destination)
    assert args.snapshot or args.baseline or args.llms_regression, "Select a verification mode"


if __name__ == "__main__":
    main()
