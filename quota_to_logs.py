#!/usr/bin/env python3
import subprocess
import json
import argparse
import datetime
import sys
from google.cloud import logging as cloud_logging

def fetch_quotas(project):
    try:
        out = subprocess.check_output([
            "gcloud", "beta", "quotas", "info", "--project", project, "--format=json"
        ], stderr=subprocess.STDOUT)
        return json.loads(out)
    except subprocess.CalledProcessError as e:
        print("gcloud command failed:\n", e.output.decode(), file=sys.stderr)
        raise

def write_log(project, payload, logger_name="quota_snapshot"):
    client = cloud_logging.Client(project=project)
    logger = client.logger(logger_name)
    logger.log_struct(payload, severity="INFO")

def main():
    p = argparse.ArgumentParser(description="Fetch Cloud Quotas and write a structured log entry to Cloud Logging.")
    p.add_argument("--project", required=True, help="GCP project ID")
    p.add_argument("--logger", default="quota_snapshot", help="Logger name in Cloud Logging")
    args = p.parse_args()

    data = fetch_quotas(args.project)
    envelope = {
        "project": args.project,
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        "quotas": data,
    }
    write_log(args.project, envelope, args.logger)
    print("Wrote quota snapshot to Cloud Logging logger:", args.logger)

if __name__ == "__main__":
    main()
