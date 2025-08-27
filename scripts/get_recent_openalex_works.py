import sys
import os
import yaml
import requests


def get_recent_works(openalex_id):
    url = f"https://api.openalex.org/works?filter=author.id:{openalex_id}&sort=publication_date:desc"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data


def write_researcher_md(researcher_record):
    import yaml as pyyaml

    name = researcher_record["name"]
    filename = f"content/researchers/{name.lower().replace(' ', '-')}.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    name = researcher_record["name"]
    slug = name.lower().replace(" ", "-")
    filename = f"content/researchers/{slug}.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # Add layout to front matter
    metadata = {"layout": "author-profile", "slug": slug}
    metadata.update(researcher_record)
    with open(filename, "w") as f:
        f.write("---\n")
        f.write(pyyaml.safe_dump(metadata, sort_keys=False))
        f.write("---\n")


def load_overrides():
    overrides_path = "data/overrides.yml"
    if os.path.exists(overrides_path):
        with open(overrides_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def main(config_path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    overrides = load_overrides()
    researchers = config.get("researchers", [])
    researchers_data = []
    for researcher in researchers:
        name = researcher.get("name")
        openalex_id = researcher.get("openalex_id")
        slug = name.lower().replace(" ", "-")
        researcher_record = {
            "name": name,
            "openalex_id": openalex_id,
            "slug": slug,
            "bio": researcher.get("bio", ""),
            "recent_works": [],
        }
        manual_works = []
        # Find manual works for this researcher
        if overrides:
            for entry in overrides:
                if (entry.get("openalex_id") == openalex_id) or (
                    entry.get("slug") == slug
                ):
                    manual_works.append(entry)
        if not openalex_id:
            print(f"No OpenAlex ID for {name}. Writing empty author.md.")
            researcher_record["recent_works"] = manual_works
            write_researcher_md(researcher_record)
            print(f"Wrote content/researchers/{slug}.md")
            continue
        print(f"Recent works for {name} (OpenAlex ID: {openalex_id}):")
        try:
            works_response = get_recent_works(openalex_id)
            if isinstance(works_response, dict):
                works = works_response.get("results", [])
            else:
                works = works_response
            openalex_works = [
                {
                    "title": work.get("title", "No title"),
                    "publication_date": work.get("publication_date", "No date"),
                    "link_to_pdf": work.get("primary_location", {}).get(
                        "pdf_url", None
                    ),
                    "source": (
                        work.get("primary_location", {}).get("source") or {}
                    ).get("display_name", None),
                    "cited_by_count": work.get("cited_by_count", 0),
                    "authors": [
                        author.get("author", {}).get("display_name", "Unknown")
                        for author in work.get("authorships", [])
                    ],
                }
                for work in works
            ]
            all_works = manual_works + openalex_works
            researcher_record["recent_works"] = all_works
            if not all_works:
                print(f"  No works found for {name}.")
            researchers_data.append(researcher_record)
            write_researcher_md(researcher_record)
            print(f"Wrote content/researchers/{slug}.md")
        except requests.RequestException as e:
            print(f"Error fetching works for {name}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_recent_openalex_works.py <config.yaml>")
        sys.exit(1)
    main(sys.argv[1])
