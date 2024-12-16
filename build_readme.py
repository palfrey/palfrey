import json
import pathlib
import re

import dateutil.parser
import feedparser
import requests

root = pathlib.Path(__file__).parent.resolve()


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def fetch_blog_entries():
    entries = feedparser.parse("https://tevps.net/rss")["entries"][:5]
    return "\n".join(
        [
            f"* {dateutil.parser.parse(entry['published']):%d %b %Y} [{entry['title']}]({entry['link']})"
            for entry in entries
        ]
    )


def fetch_prs():
    try:
        repos = json.load(open("repos.json", "r"))
    except FileNotFoundError:
        repos = {}

    user = "palfrey"
    query = f"is:pr author:{user} is:public -user:{user} is:merged"
    url = f"https://api.github.com/search/issues?&q={query}&sort=updated&order=desc"

    data = requests.get(url)
    data.raise_for_status()
    prs = []
    for pr in data.json()["items"]:
        repo_url = pr["repository_url"]
        if "rust-unofficial/awesome-rust" in repo_url:
            continue
        if repo_url not in repos:
            data = requests.get(repo_url)
            data.raise_for_status()
            repos[repo_url] = data.json()
            with open("repos.json", "w") as fp:
                json.dump(repos, fp, sort_keys=True, indent=4)
                fp.write("\n")
        repo = repos[repo_url]
        # pprint.pprint(pr)
        prs.append(
            (
                pr["closed_at"],
                f"* {dateutil.parser.isoparse(pr['closed_at']):%d %b %Y} [{repo['full_name']}]({repo['html_url']}) - [{pr['title']}]({pr['html_url']})",
            )
        )
        # break
    prs.sort(reverse=True)

    return "\n".join([pr[1] for pr in prs[:5]])


if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open().read()

    rewritten = replace_chunk(readme_contents, "prs", fetch_prs())
    rewritten = replace_chunk(rewritten, "blog", fetch_blog_entries())

    readme.open("w").write(rewritten)
