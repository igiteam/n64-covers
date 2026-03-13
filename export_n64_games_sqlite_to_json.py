#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import sqlite3
from pathlib import Path

def export_table_to_json(db_path, table_name, output_dir, pretty=False):
    """Export a specific table to JSON."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get table data
    cursor.execute("SELECT * FROM {}".format(table_name))
    rows = cursor.fetchall()
    
    # Convert to list of dicts
    data = [dict(row) for row in rows]
    
    # Save to JSON
    output_path = Path(output_dir) / "{}.json".format(table_name)
    with open(output_path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        else:
            json.dump(data, f, ensure_ascii=False, default=str)
    
    conn.close()
    print("[OK] Exported {} records from '{}' to {}".format(len(data), table_name, output_path))
    return data

def main():
    parser = argparse.ArgumentParser(description="Export games table from N64 database")
    parser.add_argument("--db", default="database.sqlite", help="Database file path")
    parser.add_argument("--output", "-o", default="./n64_games_export", help="Output directory")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print JSON")
    parser.add_argument("--table", "-t", default="games", help="Table to export (default: games)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db):
        print("[ERROR] Database file '{}' not found!".format(args.db))
        return
    
    # Export the specified table
    data = export_table_to_json(args.db, args.table, args.output, args.pretty)
    
    # Show sample of the data
    if data and len(data) > 0:
        print("\nFirst record sample:")
        sample = data[0]
        for key, value in list(sample.items())[:5]:
            print("  {}: {}".format(key, value))
        
        # Create a summary file
        summary = {
            "export_date": str(Path(args.db).stat().st_mtime),
            "table": args.table,
            "record_count": len(data),
            "columns": list(data[0].keys()) if data else []
        }
        
        summary_path = Path(args.output) / "export_info.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print("\nExport summary saved to {}".format(summary_path))

if __name__ == "__main__":
    main()