#!/usr/bin/env python3
"""
MongoDB Data Export Tool
Read-only tool for exporting all MongoDB databases and collections to JSON files

This script:
1. Connects to MongoDB (with or without authentication)
2. Exports all databases and collections to JSON files
3. Creates a metadata file with export statistics
4. Organizes exports in a dedicated folder

Note: This is a read-only tool - it never modifies or deletes data
"""

import pymongo
from pymongo import MongoClient
from bson import ObjectId
from bson import json_util
import os
import json
import sys
import socket
import time
import argparse
from datetime import datetime

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Print tool banner"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("="*70)
    print("  MongoDB Data Export Tool")
    print("  Read-Only Data Export to JSON Files")
    print("="*70)
    print(f"{Colors.RESET}\n")

def connect_to_mongodb(host='127.0.0.1', port=27017):
    """Connect to MongoDB without authentication (bypass username/password)"""
    print(f"{Colors.CYAN}[*] Phase 1: Connection{Colors.RESET}")
    print(f"[*] Connecting to MongoDB: {host}:{port}")
    print(f"{Colors.YELLOW}[*] Authentication bypassed - connecting without username/password{Colors.RESET}")
    
    try:
        # Build connection string without authentication
        conn_str = f'mongodb://{host}:{port}/'
        
        client = MongoClient(conn_str, 
                           serverSelectionTimeoutMS=10000)
        server_info = client.server_info()
        version = server_info['version']
        
        print(f"[+] {Colors.GREEN}Connected successfully!{Colors.RESET}")
        print(f"[+] MongoDB Version: {Colors.BOLD}{version}{Colors.RESET}\n")
        
        return client
            
    except Exception as e:
        print(f"{Colors.RED}[-] Connection failed: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}[*] Make sure MongoDB is accessible at {host}:{port}{Colors.RESET}")
        return None

def export_all_data_to_json(client, output_folder='mongodb_export'):
    """Export all MongoDB databases and collections to JSON files"""
    print(f"{Colors.CYAN}[*] Phase 2: Data Export{Colors.RESET}")
    print(f"[*] Exporting all databases and collections to JSON files...")
    
    # Create output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"[+] Created output folder: {output_folder}")
    
    export_stats = {
        'export_timestamp': datetime.now().isoformat(),
        'databases': [],
        'total_databases': 0,
        'total_collections': 0,
        'total_records': 0
    }
    
    try:
        # Get list of all databases (excluding system databases)
        db_list = client.list_database_names()
        system_dbs = ['admin', 'config', 'local']
        
        for db_name in db_list:
            if db_name in system_dbs:
                continue  # Skip system databases
                
            db = client[db_name]
            db_stats = {
                'database_name': db_name,
                'collections': [],
                'total_collections': 0,
                'total_records': 0
            }
            
            print(f"\n[{Colors.BLUE}{db_name}{Colors.RESET}] Processing database...")
            
            # Get list of collections
            collections = db.list_collection_names()
            
            for collection_name in collections:
                collection = db[collection_name]
                record_count = collection.count_documents({})
                
                if record_count == 0:
                    print(f"  [{collection_name}] {Colors.YELLOW}Empty collection, skipping{Colors.RESET}")
                    continue
                
                print(f"  [{collection_name}] Exporting {record_count} records...")
                
                # Fetch all documents
                documents = list(collection.find())
                
                # Convert MongoDB documents to JSON-serializable format
                # Use bson.json_util to handle ObjectId, datetime, and other BSON types
                json_documents = json_util.dumps(documents)
                json_documents = json.loads(json_documents)  # Convert to Python dict/list
                
                # Create JSON file name (collection name)
                json_filename = f"{collection_name}.json"
                json_filepath = os.path.join(output_folder, json_filename)
                
                # Write to JSON file
                with open(json_filepath, 'w', encoding='utf-8') as json_file:
                    json.dump(json_documents, json_file, indent=2, ensure_ascii=False)
                
                print(f"    {Colors.GREEN}✓{Colors.RESET} Saved to {json_filename}")
                
                # Update statistics
                collection_stats = {
                    'collection_name': collection_name,
                    'record_count': record_count,
                    'file_name': json_filename
                }
                db_stats['collections'].append(collection_stats)
                db_stats['total_collections'] += 1
                db_stats['total_records'] += record_count
                export_stats['total_records'] += record_count
            
            if db_stats['total_collections'] > 0:
                export_stats['databases'].append(db_stats)
                export_stats['total_databases'] += 1
                export_stats['total_collections'] += db_stats['total_collections']
        
        print(f"\n{Colors.GREEN}[+] Export completed successfully!{Colors.RESET}")
        print(f"[+] Total: {export_stats['total_databases']} databases, "
              f"{export_stats['total_collections']} collections, "
              f"{export_stats['total_records']} records exported")
        print(f"[+] Files saved to: {os.path.abspath(output_folder)}")
        
        return export_stats
        
    except Exception as e:
        print(f"{Colors.RED}[-] Export failed: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        return None

def create_metadata_file(export_stats, output_folder='mongodb_export', host='127.0.0.1', port=27017):
    """Create a metadata TXT file with export information"""
    metadata_filepath = os.path.join(output_folder, 'export_metadata.txt')
    
    try:
        with open(metadata_filepath, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("MongoDB Data Export Metadata\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Export Timestamp: {export_stats['export_timestamp']}\n")
            f.write(f"MongoDB Server: {host}:{port}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("EXPORT SUMMARY\n")
            f.write("-"*70 + "\n")
            f.write(f"Total Databases: {export_stats['total_databases']}\n")
            f.write(f"Total Collections: {export_stats['total_collections']}\n")
            f.write(f"Total Records: {export_stats['total_records']}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("DATABASE DETAILS\n")
            f.write("-"*70 + "\n\n")
            
            for db_stat in export_stats['databases']:
                f.write(f"Database: {db_stat['database_name']}\n")
                f.write(f"  Collections: {db_stat['total_collections']}\n")
                f.write(f"  Total Records: {db_stat['total_records']}\n")
                f.write(f"  Collections List:\n")
                
                for coll_stat in db_stat['collections']:
                    f.write(f"    - {coll_stat['collection_name']}: "
                           f"{coll_stat['record_count']} records "
                           f"(file: {coll_stat['file_name']})\n")
                f.write("\n")
            
            f.write("-"*70 + "\n")
            f.write("FILES EXPORTED\n")
            f.write("-"*70 + "\n")
            for db_stat in export_stats['databases']:
                for coll_stat in db_stat['collections']:
                    f.write(f"  {coll_stat['file_name']}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("Export completed successfully\n")
            f.write("="*70 + "\n")
        
        print(f"{Colors.GREEN}[+] Metadata file created: export_metadata.txt{Colors.RESET}\n")
        return True
        
    except Exception as e:
        print(f"{Colors.RED}[-] Failed to create metadata file: {e}{Colors.RESET}")
        return False

def simulate_exploit_connections(host='127.0.0.1', port=27017):
    """Simulate the rapid connection pattern used by MongoBleed exploit
    
    IMPORTANT: This exploit works WITHOUT authentication because:
    1. The vulnerability is in the compression handling code
    2. Compression/decompression happens DURING the initial handshake
    3. Authentication is checked AFTER the handshake completes
    4. So malformed packets can leak memory before auth is verified
    """
    print(f"{Colors.CYAN}[*] Phase 3: Exploit Execution{Colors.RESET}")
    print("[*] Initiating MongoBleed attack pattern...")
    print(f"{Colors.YELLOW}[!] Attack characteristics:{Colors.RESET}")
    print("    - Rapid connection establishment (100k+ connections/min)")
    print("    - NO client metadata sent (red flag)")
    print("    - Malformed zlib-compressed packets")
    print("    - Reading uninitialized heap memory")
    print(f"{Colors.RED}    - WORKS WITHOUT AUTHENTICATION (pre-auth vulnerability!){Colors.RESET}\n")
    
    leaked_data = []
    connection_count = 0
    
    # Simulate multiple exploit attempts
    print(f"[*] Establishing exploit connections...")
    
    for attempt in range(5):  # Limited for demo, real exploit uses thousands
        try:
            # Create connection without proper metadata
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host, port))
            
            connection_count += 1
            
            # In real exploit: send malformed zlib compressed packet here
            # This would trigger the buffer overflow and memory leak
            print(f"[{connection_count}] Connection established (no metadata sent)")
            
            # Simulate reading leaked memory (would contain random heap data)
            # In reality, this is where sensitive data leaks occur
            leaked_fragment = f"memory_leak_fragment_{attempt}"
            leaked_data.append(leaked_fragment)
            
            sock.close()
            time.sleep(0.1)  # Small delay for demo
            
        except Exception as e:
            print(f"[-] Connection {attempt} failed: {e}")
    
    print(f"\n{Colors.RED}[!] Exploit connections completed: {connection_count} connections{Colors.RESET}")
    print(f"{Colors.RED}[!] Memory leak fragments captured: {len(leaked_data)}{Colors.RESET}\n")
    
    return leaked_data

def demonstrate_memory_leak(client):
    """Demonstrate what data could be leaked from memory"""
    print(f"{Colors.CYAN}[*] Phase 4: Memory Leak Analysis{Colors.RESET}")
    print("[*] Analyzing data that could be leaked from server memory...\n")
    
    print(f"{Colors.RED}[!] LEAKED SENSITIVE DATA (from uninitialized heap memory):{Colors.RESET}\n")
    
    try:
        db = client['production_db']
        
        # Show what's actually in memory that could leak
        print(f"{Colors.YELLOW}1. USER CREDENTIALS:{Colors.RESET}")
        for user in db['users'].find().limit(3):
            print(f"   Username: {user['username']}")
            print(f"   Password: {Colors.RED}{user['password']}{Colors.RESET}")
            print(f"   Session Token: {user['session_token'][:30]}...")
            if 'credit_card' in user:
                print(f"   Credit Card: {Colors.RED}{user['credit_card']}{Colors.RESET}")
            if 'ssn' in user:
                print(f"   SSN: {Colors.RED}{user['ssn']}{Colors.RESET}")
            print()
        
        print(f"{Colors.YELLOW}2. API KEYS AND SECRETS:{Colors.RESET}")
        for key in db['api_keys'].find():
            print(f"   Service: {key['service']}")
            print(f"   Key: {Colors.RED}{key['key']}{Colors.RESET}")
            if 'secret_key' in key:
                print(f"   Secret: {Colors.RED}{key['secret_key']}{Colors.RESET}")
            print()
        
        print(f"{Colors.YELLOW}3. ACTIVE SESSIONS:{Colors.RESET}")
        for session in db['sessions'].find().limit(3):
            print(f"   Session ID: {session['session_id']}")
            print(f"   User: {session['user_id']}")
            print(f"   IP: {session['ip_address']}")
            print()
            
    except Exception as e:
        print(f"[-] Analysis failed: {e}")

def show_impact():
    """Show the real-world impact of this vulnerability"""
    print(f"{Colors.CYAN}[*] Phase 5: Impact Assessment{Colors.RESET}\n")
    
    print(f"{Colors.RED}{Colors.BOLD}WHAT ATTACKERS CAN DO WITH LEAKED DATA:{Colors.RESET}\n")
    
    impacts = [
        ("Account Takeover", "Use leaked credentials to access user accounts"),
        ("API Abuse", "Use stolen API keys to access external services"),
        ("Financial Fraud", "Use leaked credit card numbers for fraudulent transactions"),
        ("Identity Theft", "Use SSN and personal info for identity theft"),
        ("Session Hijacking", "Use leaked session tokens to impersonate users"),
        ("Lateral Movement", "Use AWS/GitHub credentials to access infrastructure"),
        ("Data Exfiltration", "Access sensitive business data and intellectual property"),
        ("Supply Chain Attack", "Compromise third-party integrations with stolen keys"),
    ]
    
    for i, (attack, description) in enumerate(impacts, 1):
        print(f"{Colors.YELLOW}{i}. {attack}:{Colors.RESET}")
        print(f"   → {description}\n")
    
    print(f"{Colors.RED}SEVERITY: CRITICAL (CVSS 8.7){Colors.RESET}")
    print(f"{Colors.RED}Impact: Confidentiality breach, no authentication required{Colors.RESET}\n")

def show_mitigation():
    """Show how to protect against this vulnerability"""
    print(f"{Colors.CYAN}[*] Phase 6: Mitigation Strategies{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}{Colors.BOLD}HOW TO PROTECT YOUR SYSTEM:{Colors.RESET}\n")
    
    mitigations = [
        ("Immediate Patch", "Upgrade to MongoDB 8.0.17+, 7.0.28+, 6.0.27+, 5.0.32+, or 4.4.30+"),
        ("Disable zlib", "Set compressors to 'snappy,zstd' in config (remove zlib)"),
        ("Monitor Logs", "Watch for connections without client metadata (Event ID 51800)"),
        ("Network Segmentation", "Restrict MongoDB access to trusted networks only"),
        ("Enable Authentication", "Always require authentication (NOTE: Won't prevent this exploit, but protects against other attacks)"),
        ("Firewall Rules", "Block external access, allow only from application servers"),
        ("Rate Limiting", "Implement connection rate limits to detect exploit attempts"),
        ("Intrusion Detection", "Alert on >100 connections/min from single IP"),
    ]
    
    for i, (strategy, description) in enumerate(mitigations, 1):
        print(f"{Colors.GREEN}{i}. {strategy}:{Colors.RESET}")
        print(f"   {description}\n")

def main():
    print_banner()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='MongoDB Data Export Tool - Exports all databases to JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python hack.py --host localhost --port 27017
  python hack.py --host 192.168.1.100 --port 27017
  python hack.py --host mongodb.example.com --port 27017
        '''
    )
    parser.add_argument('--host', '-H', 
                       default='127.0.0.1',
                       help='MongoDB host address (default: 127.0.0.1)')
    parser.add_argument('--port', '-p', 
                       type=int,
                       default=27017,
                       help='MongoDB port (default: 27017)')
    parser.add_argument('--output', '-o',
                       default='mongodb_export',
                       help='Output folder for exported JSON files (default: mongodb_export)')
    
    args = parser.parse_args()
    
    host = args.host
    port = args.port
    output_folder = args.output
    
    # Connect to MongoDB (authentication bypassed)
    client = connect_to_mongodb(host=host, port=port)
    
    if not client:
        print(f"{Colors.RED}[-] Cannot connect to MongoDB.{Colors.RESET}")
        print(f"{Colors.YELLOW}[*] Make sure MongoDB is running on {host}:{port}{Colors.RESET}")
        sys.exit(1)
    
    # Export all data to JSON files
    export_stats = export_all_data_to_json(client, output_folder=output_folder)
    
    if not export_stats:
        print(f"{Colors.RED}[-] Export failed. Exiting.{Colors.RESET}")
        client.close()
        sys.exit(1)
    
    # Create metadata file
    create_metadata_file(export_stats, output_folder=output_folder, host=host, port=port)
    
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}Export Complete{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}Summary:{Colors.RESET}")
    print(f"  • Databases exported: {export_stats['total_databases']}")
    print(f"  • Collections exported: {export_stats['total_collections']}")
    print(f"  • Total records: {export_stats['total_records']}")
    print(f"  • Output folder: {os.path.abspath(output_folder)}")
    print(f"  • Metadata file: {os.path.join(output_folder, 'export_metadata.txt')}\n")
    
    print(f"{Colors.YELLOW}Note:{Colors.RESET}")
    print("• This tool is for educational purposes only")
    print("• Only use on databases you own or have permission to access")
    print("• All data is exported in read-only mode (no modifications made)")
    
    client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[*] Export interrupted by user{Colors.RESET}")
        sys.exit(0)