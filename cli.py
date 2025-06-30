import mimetypes
import argparse
import os
import json
import hashlib
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
from tabulate import tabulate

from libs.Api import Api
from libs.util import list_files
from app.config import SIMILARITY_THRESHOLD


class DocumentTracker:
    """Tracks ingested documents to prevent duplicate ingestion."""
    
    def __init__(self, tracker_file=".ingestion_tracker.json"):
        self.tracker_file = tracker_file
        self.tracked_docs = self._load_tracker()
    
    def _load_tracker(self):
        """Load the tracking data from file."""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load tracker file {self.tracker_file}, starting fresh.")
        return {}
    
    def _save_tracker(self):
        """Save the tracking data to file."""
        try:
            with open(self.tracker_file, 'w') as f:
                json.dump(self.tracked_docs, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save tracker file: {e}")
    
    def _get_file_hash(self, file_path):
        """Generate a hash for the file based on path and modification time."""
        try:
            stat = os.stat(file_path)
            # Create hash from file path and modification time
            hash_input = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
            return hashlib.md5(hash_input.encode()).hexdigest()
        except OSError:
            return None
    
    def is_already_ingested(self, file_path):
        """Check if a file has already been ingested."""
        file_hash = self._get_file_hash(file_path)
        if not file_hash:
            return False
        
        abs_path = os.path.abspath(file_path)
        return abs_path in self.tracked_docs and self.tracked_docs[abs_path] == file_hash
    
    def mark_as_ingested(self, file_path, doc_id):
        """Mark a file as ingested."""
        file_hash = self._get_file_hash(file_path)
        if file_hash:
            abs_path = os.path.abspath(file_path)
            self.tracked_docs[abs_path] = file_hash
            self._save_tracker()
            return True
        return False


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, api, metadata=None, tracker=None):
        self.api = api
        self.metadata = metadata or {}
        self.tracker = tracker or DocumentTracker()

    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # Skip if already ingested
        if self.tracker.is_already_ingested(file_path):
            print(f"Skipping {file_path} - already ingested")
            return
        
        try:
            result = ingest_file(self.api, file_path, self.metadata, self.tracker)
            print(result)
        except Exception as e:
            print(f"Error ingesting {file_path}: {e}")


def ingest_file(api, file_path, metadata, tracker=None):
    """Helper function to ingest a single file with enhanced metadata."""
    try:
        # Skip if already ingested
        if tracker and tracker.is_already_ingested(file_path):
            return f"Skipped {file_path} - already ingested"
        
        # Get file information
        file_path_obj = Path(file_path)
        abs_path = os.path.abspath(file_path)
        
        file_info = {
            "name": file_path_obj.name,
            "path": file_path,
            "absolute_path": abs_path,
            "directory": str(file_path_obj.parent),
            "mimetype": mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        }
        
        # Enhanced metadata with file path information
        enhanced_meta = {
            **metadata,
            "filename": file_info["name"],
            "filepath": file_info["path"],
            "file_path": file_info["path"],    
            "absolute_path": file_info["absolute_path"],
            "directory": file_info["directory"],
            "mimetype": file_info["mimetype"]
        }
        
        doc_id = api.ingest(local_file_path=file_path, meta=enhanced_meta)
        
        # Mark as ingested
        if tracker:
            tracker.mark_as_ingested(file_path, doc_id)
        
        return f"Ingested {file_path} with ID: {doc_id}"
    except Exception as e:
        return f"Error ingesting {file_path}: {e}"


def generate_embeddings(args):
    """Generate embeddings for files in the specified directory."""
    try:
        metadata_dict = json.loads(args.metadata)
    except json.JSONDecodeError:
        print("Error: Metadata must be a valid JSON string.")
        return

    api = Api()
    tracker = DocumentTracker(args.tracker_file)
    files = list_files(args.path)
    
    print(f"Found {len(files)} files in {args.path}")
    
    # Filter out already ingested files
    files_to_process = []
    for file_info in files:
        if not tracker.is_already_ingested(file_info["path"]):
            files_to_process.append(file_info)
        else:
            print(f"Skipping {file_info['path']} - already ingested")
    
    print(f"Processing {len(files_to_process)} new files")
    
    if not files_to_process:
        print("No new files to process.")
        if not args.background:
            return

    # Parallel ingestion
    if files_to_process:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_file = {
                executor.submit(ingest_file, api, file_info["path"], metadata_dict, tracker): file_info["path"] 
                for file_info in files_to_process
            }
            for future in as_completed(future_to_file):
                print(future.result())

    if args.background:
        print(f"Starting background monitoring for {args.path}")
        event_handler = FileEventHandler(api, metadata_dict, tracker)
        observer = Observer()
        observer.schedule(event_handler, args.path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


def query_embeddings(args):
    """Query embeddings with a text input and return matching files."""
    api = Api()
    results = api.query(question=args.text, top_k=args.top_k)
    
    if not results:
        print("No results found.")
        return

    if args.output == "table":
        table_data = []
        for r in results:
            # Extract filename and path from metadata
            filename = r["meta"].get("filename", r["id"])
            file_path = (r["meta"].get("filepath") or 
                        r["meta"].get("file_path") or 
                        r["meta"].get("absolute_path") or 
                        "N/A")
            #absolute_path = r["meta"].get("absolute_path", "N/A")
            similarity = f"{1 - r['distance']:.4f}"
            snippet = r["doc"][:50] + ("..." if len(r["doc"]) > 50 else "")
            
            table_data.append([filename, file_path, similarity, snippet])
        
        headers = ["Filename", "Path", "Similarity", "Document Snippet"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        # Enhanced JSON output with better formatting
        formatted_results = []
        for r in results:
            formatted_result = {
                "id": r["id"],
                "filename": r["meta"].get("filename", "N/A"),
                "filepath": r["meta"].get("filepath", "N/A"),
                "file_path": r["meta"].get("file_path", "N/A"),
                "absolute_path": r["meta"].get("absolute_path", "N/A"),
                "directory": r["meta"].get("directory", "N/A"),
                "mimetype": r["meta"].get("mimetype", "N/A"),
                "similarity": round(1 - r["distance"], 4),
                "distance": r["distance"],
                "document_snippet": r["doc"][:100] + ("..." if len(r["doc"]) > 100 else ""),
                "metadata": r["meta"]
            }
            formatted_results.append(formatted_result)
        
        print(json.dumps(formatted_results, indent=2))


def reset_tracker(args):
    """Reset the ingestion tracker."""
    if os.path.exists(args.tracker_file):
        os.remove(args.tracker_file)
        print(f"Tracker file {args.tracker_file} has been reset.")
    else:
        print(f"Tracker file {args.tracker_file} does not exist.")


def show_tracker_status(args):
    """Show the current status of the tracker."""
    tracker = DocumentTracker(args.tracker_file)
    print(f"Tracker file: {args.tracker_file}")
    print(f"Total tracked documents: {len(tracker.tracked_docs)}")
    
    if args.verbose and tracker.tracked_docs:
        print("\nTracked documents:")
        for path, hash_val in tracker.tracked_docs.items():
            print(f"  {path} -> {hash_val}")


def main():
    parser = argparse.ArgumentParser(
        description="File Embedding CLI Tool: Generate and query embeddings for files.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate embeddings for files')
    generate_parser.add_argument(
        '--path', 
        required=True, 
        type=str,
        help='Root directory to process files'
    )
    generate_parser.add_argument(
        '--background', 
        action='store_true',
        help='Run in background and monitor for new files'
    )
    generate_parser.add_argument(
        '--metadata', 
        default='{}',
        help='JSON string of metadata to include with all files'
    )
    generate_parser.add_argument(
        '--workers', 
        default=4, 
        type=int,
        help='Number of parallel workers for ingestion'
    )
    generate_parser.add_argument(
        '--tracker-file',
        default='.ingestion_tracker.json',
        help='File to track ingested documents'
    )
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query embeddings')
    query_parser.add_argument(
        '--text', 
        required=True,
        help='Query text to search for'
    )
    query_parser.add_argument(
        '--top-k', 
        default=5, 
        type=int,
        help='Number of results to return'
    )
    query_parser.add_argument(
        '--output', 
        default='table',
        choices=['table', 'json'],
        help='Output format (table or json)'
    )
    
    # Tracker management commands
    reset_parser = subparsers.add_parser('reset-tracker', help='Reset the ingestion tracker')
    reset_parser.add_argument(
        '--tracker-file',
        default='.ingestion_tracker.json',
        help='Tracker file to reset'
    )
    
    status_parser = subparsers.add_parser('tracker-status', help='Show tracker status')
    status_parser.add_argument(
        '--tracker-file',
        default='.ingestion_tracker.json',
        help='Tracker file to check'
    )
    status_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        # Validate path exists
        if not os.path.exists(args.path):
            print(f"Error: Directory '{args.path}' does not exist.")
            return
        if not os.path.isdir(args.path):
            print(f"Error: '{args.path}' is not a directory.")
            return
        generate_embeddings(args)
    elif args.command == 'query':
        query_embeddings(args)
    elif args.command == 'reset-tracker':
        reset_tracker(args)
    elif args.command == 'tracker-status':
        show_tracker_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()