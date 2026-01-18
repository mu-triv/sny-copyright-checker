#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""
Demo: Init Wizard with Pre-commit Config Automation

This demo shows how the enhanced init wizard automatically creates
.pre-commit-config.yaml configuration.
"""

import tempfile
import os
from pathlib import Path
from scripts.init_wizard import create_or_update_precommit_config
import yaml


def demo_create_new_config():
    """Demo: Creating a new .pre-commit-config.yaml"""
    print("=" * 70)
    print("DEMO 1: Creating a New .pre-commit-config.yaml")
    print("=" * 70)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 Working in temporary directory: {tmpdir}")
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            print("\n📝 Calling: create_or_update_precommit_config()")
            print("   - copyright_file: 'copyright.txt'")
            print("   - extensions: ['.py', '.js', '.ts', '.cpp']")
            print()

            result = create_or_update_precommit_config(
                "copyright.txt", [".py", ".js", ".ts", ".cpp"]
            )

            if result:
                print("✅ Success! Config file created")
                print()

                config_path = Path(".pre-commit-config.yaml")
                with open(config_path, "r") as f:
                    content = f.read()

                print("📄 Generated .pre-commit-config.yaml:")
                print("-" * 70)
                print(content)
                print("-" * 70)

                # Parse and show structure
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)

                print()
                print("🔍 Configuration Structure:")
                print(f"   - Number of repos: {len(config['repos'])}")
                print(f"   - Checker version: {config['repos'][0]['rev']}")
                print(
                    f"   - Copyright file: {config['repos'][0]['hooks'][0]['args'][0]}"
                )
                print(
                    f"   - File pattern: {config['repos'][0]['hooks'][0].get('files', 'N/A')}"
                )
            else:
                print("❌ Failed to create config")
        finally:
            os.chdir(old_cwd)

    print()
    print()


def demo_update_existing_config():
    """Demo: Updating existing .pre-commit-config.yaml"""
    print("=" * 70)
    print("DEMO 2: Updating Existing .pre-commit-config.yaml")
    print("=" * 70)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 Working in temporary directory: {tmpdir}")
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Create initial config
            print("\n📝 Creating initial config with 'black' formatter...")
            initial_config = {
                "repos": [
                    {
                        "repo": "https://github.com/psf/black",
                        "rev": "23.0.0",
                        "hooks": [{"id": "black"}],
                    }
                ]
            }

            config_path = Path(".pre-commit-config.yaml")
            with open(config_path, "w") as f:
                yaml.dump(initial_config, f)

            print("✅ Initial config created")
            print()
            print("📄 Initial .pre-commit-config.yaml:")
            print("-" * 70)
            with open(config_path, "r") as f:
                print(f.read())
            print("-" * 70)

            # Now update it
            print()
            print("📝 Now adding sny-copyright-checker...")
            print("   - copyright_file: 'my_copyright.txt'")
            print("   - extensions: ['.py', '.yaml']")
            print()

            result = create_or_update_precommit_config(
                "my_copyright.txt", [".py", ".yaml"]
            )

            if result:
                print("✅ Success! Config file updated")
                print()

                print("📄 Updated .pre-commit-config.yaml:")
                print("-" * 70)
                with open(config_path, "r") as f:
                    content = f.read()
                    print(content)
                print("-" * 70)

                # Parse and show structure
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)

                print()
                print("🔍 Configuration Structure:")
                print(f"   - Number of repos: {len(config['repos'])}")
                print(
                    f"   - Repo 1: {config['repos'][0]['repo'].split('/')[-1]} (preserved)"
                )
                print("   - Repo 2: sny-copyright-checker (added)")
                print(
                    f"   - File pattern: {config['repos'][1]['hooks'][0].get('files', 'N/A')}"
                )
            else:
                print("❌ Failed to update config")
        finally:
            os.chdir(old_cwd)

    print()
    print()


def demo_update_checker_config():
    """Demo: Updating existing checker configuration"""
    print("=" * 70)
    print("DEMO 3: Updating Existing Checker Configuration")
    print("=" * 70)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 Working in temporary directory: {tmpdir}")
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Create initial config with old version
            print("\n📝 Creating config with OLD checker version (v1.0.6)...")
            initial_config = {
                "repos": [
                    {
                        "repo": "https://github.com/mu-triv/sny-copyright-checker",
                        "rev": "v1.0.6",
                        "hooks": [
                            {
                                "id": "sny-copyright-checker",
                                "args": ["--notice=old.txt"],
                            }
                        ],
                    }
                ]
            }

            config_path = Path(".pre-commit-config.yaml")
            with open(config_path, "w") as f:
                yaml.dump(initial_config, f)

            print("✅ Old config created")
            print()
            print("📄 Old .pre-commit-config.yaml:")
            print("-" * 70)
            with open(config_path, "r") as f:
                print(f.read())
            print("-" * 70)

            # Now update it
            print()
            print("📝 Now updating to NEW version...")
            print("   - copyright_file: 'new_copyright.txt'")
            print("   - extensions: ['.py', '.js', '.go']")
            print()

            result = create_or_update_precommit_config(
                "new_copyright.txt", [".py", ".js", ".go"]
            )

            if result:
                print("✅ Success! Checker config updated")
                print()

                print("📄 Updated .pre-commit-config.yaml:")
                print("-" * 70)
                with open(config_path, "r") as f:
                    content = f.read()
                    print(content)
                print("-" * 70)

                # Parse and show what changed
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)

                print()
                print("🔍 What Changed:")
                print(f"   - Version: v1.0.6 → {config['repos'][0]['rev']}")
                print(
                    f"   - Copyright file: old.txt → {config['repos'][0]['hooks'][0]['args'][0].split('=')[1]}"
                )
                print(
                    f"   - File pattern: (none) → {config['repos'][0]['hooks'][0].get('files', 'N/A')}"
                )
            else:
                print("❌ Failed to update config")
        finally:
            os.chdir(old_cwd)

    print()
    print()


def main():
    """Run all demos"""
    print()
    print("🎬 SNY Copyright Checker - Pre-commit Config Automation Demo")
    print()

    demo_create_new_config()
    demo_update_existing_config()
    demo_update_checker_config()

    print("=" * 70)
    print("✅ All Demos Complete!")
    print("=" * 70)
    print()
    print("💡 Key Takeaways:")
    print("   1. Wizard automatically creates .pre-commit-config.yaml")
    print("   2. Smart updates preserve existing hooks")
    print("   3. File patterns generated from selected extensions")
    print("   4. Existing checker configs are updated, not duplicated")
    print()
    print("🚀 Try it yourself:")
    print("   sny-copyright-checker init")
    print()


if __name__ == "__main__":
    main()
