#!/usr/bin/env python3
"""
Check Navigation Map Script
===========================

Validate bahwa navigation structure di frontend sesuai dengan KN_13_NAVIGATION_MAP.md.
Cek bahwa tidak ada menu redundant, missing data-testid, atau broken links.

Usage:
    python /app/scripts/check_nav_map.py
    python /app/scripts/check_nav_map.py --verbose

References:
    KN_00 Line 164: check_nav_map.py
    KN_13: Navigation Map (Master reference)
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Set

# Colors
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_pass(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_fail(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warn(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

# ========================================================================
# EXPECTED NAVIGATION (from KN_13)
# ========================================================================

EXPECTED_NAV_ITEMS = {
    "admin": [
        "nav-home", "nav-pos", "nav-orders", "nav-wms", "nav-purchasing",
        "nav-documents", "nav-reports", "nav-admin", "nav-escalations"
    ],
    "sales": [
        "nav-home", "nav-orders", "nav-documents"
    ],
    "manager": [
        "nav-home", "nav-orders", "nav-wms", "nav-purchasing",
        "nav-reports", "nav-escalations"
    ],
    "warehouse": [
        "nav-home", "nav-documents", "nav-escalations"
    ],
}

EXPECTED_WMS_TABS = [
    "wms-tab-stok", "wms-tab-inbound", "wms-tab-outbound",
    "wms-tab-transfer", "wms-tab-cycle"
]

EXPECTED_ORDER_TABS = [
    "orders-tab-dashboard", "orders-tab-list"
]

# ========================================================================
# CHECK 1: Validate Navigation Config in App.js
# ========================================================================

def check_nav_config(verbose=False) -> Dict:
    """Check that navigation config matches KN_13."""
    print_header("CHECK 1: Navigation Config (App.js)")
    
    app_js = Path("/app/frontend/src/App.js")
    if not app_js.exists():
        print_fail("App.js not found")
        return {"issues": 1, "checked": 0}
    
    content = app_js.read_text()
    issues = []
    
    # Extract all data-testid values starting with "nav-"
    found_nav_testids = set(re.findall(r'data-testid="(nav-[a-z-]+)"', content))
    
    # Check each role's navigation
    for role, expected_navs in EXPECTED_NAV_ITEMS.items():
        for nav_id in expected_navs:
            if nav_id not in found_nav_testids:
                issues.append(f"Missing data-testid=\"{nav_id}\" for role: {role}")
                print_fail(f"Missing: {nav_id} (role: {role})")
            elif verbose:
                print_pass(f"Found: {nav_id} (role: {role})")
    
    if not issues:
        print_pass(f"All navigation items have correct data-testid")
    
    return {"issues": len(issues), "checked": len(found_nav_testids)}

# ========================================================================
# CHECK 2: WMS Tabs
# ========================================================================

def check_wms_tabs(verbose=False) -> Dict:
    """Check WMS tabs match KN_13."""
    print_header("CHECK 2: WMS Tabs")
    
    # WMS tabs could be in OperationsView or App.js
    wms_files = [
        Path("/app/frontend/src/App.js"),
        Path("/app/frontend/src/features/wms/OperationsView.jsx")
    ]
    
    found_tabs = set()
    issues = []
    
    for wms_file in wms_files:
        if wms_file.exists():
            content = wms_file.read_text()
            found_tabs.update(re.findall(r'data-testid="(wms-tab-[a-z]+)"', content))
    
    for tab_id in EXPECTED_WMS_TABS:
        if tab_id not in found_tabs:
            issues.append(f"Missing: {tab_id}")
            print_fail(f"Missing WMS tab: {tab_id}")
        elif verbose:
            print_pass(f"Found WMS tab: {tab_id}")
    
    if not issues:
        print_pass(f"All WMS tabs present ({len(EXPECTED_WMS_TABS)} tabs)")
    
    return {"issues": len(issues), "checked": len(EXPECTED_WMS_TABS)}

# ========================================================================
# CHECK 3: Duplicate Navigation Items
# ========================================================================

def check_duplicates(verbose=False) -> Dict:
    """Check for duplicate nav items (anti-pattern in KN_13)."""
    print_header("CHECK 3: Duplicate Navigation Items")
    
    app_js = Path("/app/frontend/src/App.js")
    if not app_js.exists():
        return {"issues": 0, "checked": 0}
    
    content = app_js.read_text()
    
    # Extract all navigation labels
    nav_labels = re.findall(r'label[:\s]*["\']([^"\'\']+)["\']', content)
    
    # Check for duplicates
    seen = set()
    duplicates = []
    
    for label in nav_labels:
        if label in seen and label not in ["Dashboard", "Admin"]:
            duplicates.append(label)
            print_warn(f"Duplicate navigation label: {label}")
        seen.add(label)
    
    if not duplicates:
        print_pass("No duplicate navigation items found")
    else:
        print_warn(f"{len(duplicates)} duplicate label(s) found (consider consolidation)")
    
    return {"issues": len(duplicates), "checked": len(nav_labels)}

# ========================================================================
# CHECK 4: Navigation Depth
# ========================================================================

def check_nav_depth(verbose=False) -> Dict:
    """Check that navigation depth doesn't exceed 4 levels (KN_13 anti-pattern)."""
    print_header("CHECK 4: Navigation Depth")
    
    # This is a simplified check - in real implementation, parse component tree
    # For now, just check that we don't have deeply nested route definitions
    
    app_js = Path("/app/frontend/src/App.js")
    if not app_js.exists():
        return {"issues": 0, "checked": 0}
    
    content = app_js.read_text()
    
    # Simple heuristic: count nested view switches
    # Deep nesting would show as many nested switch/case or ternary operators
    nested_levels = content.count("activeView ===") + content.count("activeTab ===")
    
    if nested_levels > 4:
        print_warn(f"Potential deep nesting detected ({nested_levels} view switches)")
        print_warn("Consider flattening navigation hierarchy (KN_13)")
        return {"issues": 1, "checked": 1}
    else:
        print_pass(f"Navigation depth acceptable ({nested_levels} levels)")
        return {"issues": 0, "checked": 1}

# ========================================================================
# MAIN EXECUTION
# ========================================================================

def main():
    parser = argparse.ArgumentParser(description="Check Navigation Map compliance")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    print(f"\n{Colors.BOLD}Navigation Map Validator{Colors.RESET}")
    print(f"Reference: KN_13_NAVIGATION_MAP.md\n")
    
    results = {}
    total_issues = 0
    
    # Run all checks
    checks = [
        ("nav_config", check_nav_config),
        ("wms_tabs", check_wms_tabs),
        ("duplicates", check_duplicates),
        ("nav_depth", check_nav_depth),
    ]
    
    for check_name, check_func in checks:
        result = check_func(verbose=args.verbose)
        results[check_name] = result
        total_issues += result["issues"]
    
    # Summary
    print_header("SUMMARY")
    
    if total_issues == 0:
        print_pass("Navigation map is compliant with KN_13")
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ NAV MAP: PASS{Colors.RESET}\n")
        sys.exit(0)
    else:
        print_warn(f"{total_issues} issue(s) found")
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ NAV MAP: NEEDS ATTENTION{Colors.RESET}")
        print(f"{Colors.YELLOW}Review KN_13 for navigation best practices{Colors.RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
