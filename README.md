# Sync GitHub Stars to a Notion Table

This scratches a particular itch of mine but maybe you will find it
useful too!

Give this Python script a GitHub username and it will sync that
user's stars to a table in [Notion](https://www.notion.so/).

## Usage

Create a YAML file somewhere that contains the following info:

```
github:
  username: < a GitHub username >
  token: < a personal access token for GitHub >
notion:
  table_url: < https://www.notion.so/some_cool_table?v=the_view_id_maybe >
  token_v2: < your notion token_v2 >
```

* [GitHub personal access token](https://github.com/settings/tokens)
* [Where to find Notion token_v2 and table URL](https://github.com/jamalex/notion-py#quickstart)

Install the required Python packages: `pip install -r requirements.txt`

Invoke the Python script with the path of your config YAML file:
`python github_stars_to_notion/__init__.py config.yml`

I recommend running the script in a nightly `cron` job.

## Why

I use my [GitHub Stars](https://github.com/jmpinit?tab=stars) as a
way to squirrel away projects that might come in handy later. It's
nice to follow other people who do the same and look at what they star
because that allows me to discover new projects that I wouldn't have
come across on my own. I want to be the same kind of resource for
people but I also have a lot of other bookmarks and want to
manage/search/etc. them in a centralized way. Right now I use Notion
for that because it has a nice interface and is flexible. So this
little utility script lets me participate in my tiny GitHub community
but still have the flexibility to annotate my stars with extra info.

If you are curious what that looks like here's [a link to my GitHub
stars table in Notion](https://www.notion.so/7765b7496b134dabbc1a2765cd381701?v=c832f36c6591435db269d793b77dcb0f).
