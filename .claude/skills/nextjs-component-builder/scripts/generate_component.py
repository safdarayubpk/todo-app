#!/usr/bin/env python3
"""
Next.js Component Generator Script
===================================
Generates React/Next.js component files from a component name.

Usage:
    python generate_component.py <ComponentName> [--output-dir <path>] [--client]

Examples:
    python generate_component.py TaskCard
    python generate_component.py TaskCard --output-dir frontend/src/components
    python generate_component.py AddTaskForm --client
"""

import argparse
import re
from pathlib import Path


def to_pascal_case(name: str) -> str:
    """Convert various formats to PascalCase, preserving existing PascalCase."""
    # If already PascalCase (starts with uppercase, has no separators), return as-is
    if re.match(r'^[A-Z][a-zA-Z0-9]*$', name) and not ('_' in name or '-' in name):
        return name

    # Split on separators and capitalize each part
    parts = re.split(r'[-_]', name)
    return ''.join(word.capitalize() for word in parts if word)


# Using __NAME__ as placeholder to avoid conflicts with JSX braces
SERVER_COMPONENT_TEMPLATE = '''interface __NAME__Props {
  // Define props here
}

export default function __NAME__({ }: __NAME__Props) {
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold">__NAME__</h2>
      {/* Component content */}
    </div>
  );
}
'''

CLIENT_COMPONENT_TEMPLATE = ''''use client';

import { useState } from 'react';

interface __NAME__Props {
  // Define props here
}

export default function __NAME__({ }: __NAME__Props) {
  const [state, setState] = useState('');

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold">__NAME__</h2>
      {/* Component content */}
    </div>
  );
}
'''


def generate_component(
    component_name: str,
    output_dir: str = ".",
    is_client: bool = False
) -> dict[str, str]:
    """Generate component files."""
    name = to_pascal_case(component_name)

    template = CLIENT_COMPONENT_TEMPLATE if is_client else SERVER_COMPONENT_TEMPLATE

    # Replace placeholder with actual component name
    component_content = template.replace("__NAME__", name)

    # Create output path
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    component_file = output_path / f"{name}.tsx"
    component_file.write_text(component_content)

    return {
        "component_file": str(component_file),
        "is_client": is_client,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Next.js React components")
    parser.add_argument("component", help="Component name (e.g., TaskCard, AddTaskForm)")
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory")
    parser.add_argument("--client", "-c", action="store_true", help="Generate client component with 'use client'")

    args = parser.parse_args()

    files = generate_component(args.component, args.output_dir, args.client)

    component_type = "client" if files["is_client"] else "server"
    print(f"Generated {component_type} component '{to_pascal_case(args.component)}':")
    print(f"  Component: {files['component_file']}")
    print()
    print("Next steps:")
    print("  1. Add props interface to the component")
    print("  2. Implement the component logic and UI")
    print("  3. Add Tailwind CSS classes for styling")
    print("  4. Import and use in parent component")


if __name__ == "__main__":
    main()
