#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
from pathlib import Path


def get_all_tables(conn):
    """Get all table names from the SQLite database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]


def table_to_json(conn, table_name):
    """Convert a single table to a list of dictionaries (for JSON serialization)."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    
    # Get column names
    columns = [description[0] for description in cursor.description]
    
    # Fetch all rows and convert to dictionaries
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    
    return results


def save_json_file(data, output_dir, table_name, pretty=False):
    """Save data as JSON to a file."""
    output_path = Path(output_dir) / f"{table_name}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)
    
    return output_path


def sqlite_to_json(db_path, output_dir, pretty=False, single_file=False):
    """Convert all tables in a SQLite database to JSON."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    # Get all tables
    tables = get_all_tables(conn)
    
    if not tables:
        print("No tables found in the database.")
        conn.close()
        return
    
    results = {}
    files_created = []
    
    # Process each table
    for table_name in tables:
        print(f"Processing table: {table_name}")
        data = table_to_json(conn, table_name)
        
        # Store data for single file mode or save individual files
        if single_file:
            results[table_name] = data
        else:
            output_path = save_json_file(data, output_dir, table_name, pretty)
            files_created.append(output_path)
    
    # Save all tables to a single file if requested
    if single_file:
        output_path = Path(output_dir) / "all_tables.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(results, f, indent=2, ensure_ascii=False)
            else:
                json.dump(results, f, ensure_ascii=False)
        files_created.append(output_path)
    
    conn.close()
    return files_created


def main():
    parser = argparse.ArgumentParser(description="Convert SQLite database to JSON")
    parser.add_argument("db_path", help="Path to the SQLite database file")
    parser.add_argument(
        "--output-dir", "-o", default="./json_output", 
        help="Directory to save JSON files (default: ./json_output)"
    )
    parser.add_argument(
        "--pretty", "-p", action="store_true", 
        help="Generate pretty (indented) JSON"
    )
    parser.add_argument(
        "--single-file", "-s", action="store_true", 
        help="Save all tables to a single JSON file"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db_path):
        print(f"Error: Database file '{args.db_path}' does not exist.")
        return
    
    files = sqlite_to_json(
        args.db_path, 
        args.output_dir, 
        pretty=args.pretty,
        single_file=args.single_file
    )
    
    if files:
        print(f"\nConversion completed successfully!")
        print(f"JSON files saved to: {os.path.abspath(args.output_dir)}")
        print(f"Files created: {len(files)}")


if __name__ == "__main__":
    main()
