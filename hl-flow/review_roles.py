"""Select review roles from the confirmed impact of a single-team change."""
import argparse
import json


def review(impacts):
    reviewers = ["analyst", "test-engineer"]
    if impacts:
        reviewers.append("executor")
    if "ui" in impacts:
        reviewers.append("designer")
    if impacts & {"architecture", "migration", "accounting"}:
        reviewers.append("architect")
    if "authorization" in impacts:
        reviewers.append("security-reviewer")
    return {"reviewers": reviewers,
            "formal_handoff": bool(impacts & {"accounting", "cross-team"})}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    supported = {"ui", "architecture", "migration", "accounting", "authorization", "cross-team"}
    parser.add_argument("impact", nargs="*", help="本次已确认的影响项，可选 " + ", ".join(sorted(supported)))
    impacts = set(parser.parse_args().impact)
    unknown = impacts - supported
    if unknown:
        parser.error("未知影响项 " + ", ".join(sorted(unknown)))
    print(json.dumps(review(impacts), ensure_ascii=False))
