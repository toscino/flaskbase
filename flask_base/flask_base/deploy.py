"""Deploy script for Google App Engine."""

import os
import subprocess
import sys
from pathlib import Path

# Try to load python-dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def resolve_deploy_yaml(explicit_path: str | None = None) -> str:
    """
    Choose App Engine config for deploy.

    Uses explicit_path if given, else app.production.yaml when present, else app.yaml.
    """
    if explicit_path:
        return explicit_path
    prod = Path("app.production.yaml")
    if prod.is_file():
        return str(prod)
    return "app.yaml"


def set_gcloud_project() -> None:
    """Set the gcloud active project from GOOGLE_CLOUD_PROJECT environment variable."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("ERROR: GOOGLE_CLOUD_PROJECT environment variable is required")
        sys.exit(1)
    
    print(f"Setting project to: {project_id}")
    try:
        result = subprocess.run(
            f"gcloud config set project {project_id}",
            capture_output=True,
            text=True,
            check=False,
            shell=True  # Use shell=True on Windows
        )
        # Only print stderr if there's an actual error
        if result.returncode != 0:
            for line in result.stderr.splitlines():
                if "quota" not in line.lower():
                    print(line)
    except FileNotFoundError:
        print("ERROR: gcloud CLI not found. Please install Google Cloud SDK.")
        sys.exit(1)


def main(yaml_path: str | None = None) -> None:
    """Main entry point for deploy script."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("ERROR: GOOGLE_CLOUD_PROJECT environment variable is required")
        sys.exit(1)

    chosen = resolve_deploy_yaml(yaml_path)
    deploy_file = Path(chosen)
    if not deploy_file.is_file():
        print(f"ERROR: App Engine config not found: {deploy_file}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("   Flask App - Deployment")
    print("=" * 60 + "\n")
    
    # Set the correct project
    set_gcloud_project()
    
    print(f"\nDeploying to App Engine ({deploy_file})...\n")
    
    # Deploy to App Engine
    try:
        subprocess.run(
            f"gcloud app deploy {deploy_file} --quiet",
            check=True,
            shell=True  # Use shell=True on Windows
        )
        
        print("\n" + "=" * 60)
        print("   Deployment Complete!")
        print("=" * 60 + "\n")
        print(f"Your app is live at: https://{project_id}.appspot.com\n")
        
    except subprocess.CalledProcessError:
        print("\nERROR: Deployment failed.")
        sys.exit(1)
