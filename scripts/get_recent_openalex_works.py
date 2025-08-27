import yaml
import requests
import sys

OPENALEX_API_URL = "https://api.openalex.org/works"


def get_recent_works(openalex_id, per_page=5):
    params = {
        "filter": f"author.id:https://openalex.org/{openalex_id}",
        "sort": "publication_date:desc",
        "per-page": per_page,
    }
    response = requests.get(OPENALEX_API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or "results" not in data:
        print("Unexpected API response:", data)
        return []
    print(data.keys())
    return data.get("results", [])


def write_yaml_data_to_home(researchers_data):
    frontmatter = {"researchers": researchers_data}
    with open("content/_index.md", "w") as f:
        f.write("---\n")
        yaml.dump(frontmatter, f, sort_keys=False)
        f.write("---\n")


def main(yaml_path):
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    researchers = config.get("researchers", [])
    researchers_data = []
    for researcher in researchers:
        name = researcher.get("name")
        openalex_id = researcher.get("openalex_id")
        if not openalex_id:
            print(f"Skipping {name}: no openalex_id")
            continue
        print(f"Recent works for {name} (OpenAlex ID: {openalex_id}):")
        try:
            works = get_recent_works(openalex_id)
            if not works:
                print(f"  No works found for {name}.")
                continue
            researchers_data.append(
                {
                    "name": name,
                    "openalex_id": openalex_id,
                    "recent_works": [
                        {
                            "title": work.get("title", "No title"),
                            "publication_date": work.get("publication_date", "No date"),
                            "link_to_pdf": work["primary_location"].get(
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
                    ],
                }
            )
            for work in works:
                title = work.get("title", "No title")
                pub_date = work.get("publication_date", "No date")
                print(f"  - {title} ({pub_date})")
        except Exception as e:
            import traceback

            print(f"  Error fetching works: {e}")
            traceback.print_exc()
        print()
    write_yaml_data_to_home(researchers_data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_openalex_works.py <path_to_yaml>")
        sys.exit(1)
    main(sys.argv[1])
