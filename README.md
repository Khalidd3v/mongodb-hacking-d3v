# MongoDB Data Export Tool

A Python tool for exporting all data from MongoDB databases to JSON files. This tool connects to MongoDB instances and exports all collections (tables) to individual JSON files, organized by database.

## Features

- 🔍 **Read-Only Operations**: Only reads data, never modifies or deletes anything
- 📁 **Organized Export**: Creates a folder structure with JSON files named after collections
- 📊 **Metadata Tracking**: Generates a detailed metadata file with export statistics
- 🔐 **Authentication Support**: Works with both authenticated and unauthenticated MongoDB instances
- 🚀 **Easy to Use**: Simple command-line interface

## Requirements

- Python 3.6+
- pymongo library

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd mongodb-hackiing
```

2. Install dependencies:
```bash
pip install pymongo
```

Or if using a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install pymongo
```

## Usage

### Basic Usage

```bash
python hack.py
```

This will connect to MongoDB running on `127.0.0.1:27017` (default) and export all data.

### Specify Host and Port

```bash
python hack.py --host localhost --port 27017
```

Or use short flags:

```bash
python hack.py -H 192.168.1.100 -p 27017
```

### Custom Output Folder

```bash
python hack.py --host mongodb.example.com --port 27017 --output my_export
```

### Command-Line Options

- `--host` or `-H`: MongoDB host address (default: 127.0.0.1)
- `--port` or `-p`: MongoDB port (default: 27017)
- `--output` or `-o`: Output folder name (default: mongodb_export)

### Authentication

**Note:** This tool bypasses authentication and connects without username/password. It works with MongoDB instances that allow unauthenticated connections. If your MongoDB requires authentication, you'll need to configure it to allow unauthenticated access from your IP address, or modify the connection string in the code.

## Output Structure

The tool creates an `mongodb_export/` folder with the following structure:

```
mongodb_export/
├── collection1.json
├── collection2.json
├── collection3.json
└── export_metadata.txt
```

### JSON Files

Each collection is exported to a separate JSON file named `{collection_name}.json`. The file contains an array of all documents in that collection.

Example:
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "username": "user@example.com",
    "email": "user@example.com",
    ...
  },
  ...
]
```

### Metadata File

The `export_metadata.txt` file contains:
- Export timestamp
- MongoDB server information
- Summary statistics (total databases, collections, records)
- Detailed breakdown by database and collection
- List of all exported files

## Example Output

```
[*] Phase 1: Reconnaissance
[*] Target: 127.0.0.1:27017
[+] MongoDB Version: 8.0.16

[*] Phase 2: Data Export
[*] Exporting all databases and collections to JSON files...
[+] Created output folder: mongodb_export

[mydatabase] Processing database...
  [users] Exporting 150 records...
    ✓ Saved to users.json
  [products] Exporting 500 records...
    ✓ Saved to products.json

[+] Export completed successfully!
[+] Total: 1 databases, 2 collections, 650 records exported
[+] Files saved to: /path/to/mongodb_export
[+] Metadata file created: export_metadata.txt
```

## Security Notes

⚠️ **Important Security Information:**

- This tool performs **read-only** operations - it never modifies or deletes data
- Always ensure you have proper authorization before accessing any MongoDB instance
- For production databases, use read-only user credentials when possible
- The tool skips system databases (admin, config, local) by default
- All operations are logged and can be reviewed in the metadata file

## Troubleshooting

### Connection Failed

If you see "Connection failed", check:
- MongoDB is running and accessible
- Host and port are correct (use `--host` and `--port` flags)
- Firewall allows connections
- MongoDB allows unauthenticated connections from your IP

### Permission Errors

If you get permission errors:
- Ensure the user has read permissions on the databases
- Check that the output folder is writable
- On Linux/Mac, you may need to adjust folder permissions

### Empty Collections

Collections with 0 documents are skipped and not exported.

## Limitations

- Large collections may take time to export (all data is loaded into memory)
- Binary data (GridFS) is not handled - only regular collections
- System databases are excluded from export
- Very large databases may require significant disk space

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes only. Use responsibly and only on systems you own or have explicit permission to access.

## Contact

For questions or issues, please contact:
- Email: khalidbinalikhan@gmail.com

## Disclaimer

This tool is provided for educational and legitimate data export purposes only. Users are responsible for ensuring they have proper authorization before accessing any database. The authors are not responsible for any misuse of this tool.

