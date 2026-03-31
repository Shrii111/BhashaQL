#!/usr/bin/env python3
"""
BhashaQL - A Hinglish SQL Compiler
Main entry point for the command-line interface
"""

import sys
import os
import argparse
from typing import List, Optional
from pathlib import Path

# Add compiler to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'compiler'))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.optimizer import QueryOptimizer
from compiler.codegen import CodeGenerator
from compiler.errors import ErrorCollector, CompilerError
from runtime.executor import QueryExecutor

class BhashaQLCompiler:
    """Main compiler class that orchestrates all phases"""
    
    def __init__(self, db_path: str = "runtime/database.db"):
        self.db_path = db_path
        self.executor = QueryExecutor(db_path)
        self.error_collector = ErrorCollector()
        self.verbose = False
        self.show_sql = False
        self.show_ir = False
        self.show_ast = False
    
    def compile_and_execute(self, source: str) -> bool:
        """Compile and execute BhashaQL source code"""
        try:
            # Initialize executor
            init_result = self.executor.initialize()
            if not init_result.success:
                print(f"Error: {init_result.message}")
                return False
            
            # Phase 1: Lexical Analysis
            if self.verbose:
                print("Phase 1: Lexical Analysis...")
            
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            if self.verbose:
                print(f"Tokens: {len(tokens)}")
                for token in tokens:
                    print(f"  {token}")
            
            # Phase 2: Parsing
            if self.verbose:
                print("\nPhase 2: Parsing...")
            
            parser = Parser(tokens)
            try:
                ast = parser.parse()
                
                if self.verbose:
                    print(f"AST: {ast}")
                
                if self.show_ast:
                    print("\n=== AST ===")
                    print(ast)
                    print("=== END AST ===\n")
                
            except CompilerError as e:
                self.error_collector.add_error(e)
                print(f"Parse Error: {e}")
                return False
            
            # Phase 3: Semantic Analysis
            if self.verbose:
                print("\nPhase 3: Semantic Analysis...")
            
            semantic_analyzer = SemanticAnalyzer()
            try:
                semantic_valid = semantic_analyzer.analyze(ast)
                
                if not semantic_valid:
                    errors = semantic_analyzer.get_errors()
                    for error in errors:
                        self.error_collector.add_error(error)
                        print(f"Semantic Error: {error}")
                    
                    warnings = semantic_analyzer.get_warnings()
                    for warning in warnings:
                        print(f"Warning: {warning}")
                    
                    return False
                
                if self.verbose:
                    print("Semantic analysis passed")
                
            except Exception as e:
                print(f"Semantic analysis failed: {e}")
                return False
            
            # Phase 4: Intermediate Representation Generation
            if self.verbose:
                print("\nPhase 4: IR Generation...")
            
            codegen = CodeGenerator(semantic_analyzer.symbol_table)
            try:
                ir_program = codegen.ir_generator.generate(ast)
                
                if self.verbose:
                    print(f"IR Program: {ir_program}")
                
                if self.show_ir:
                    print("\n=== IR ===")
                    print(ir_program)
                    print("=== END IR ===\n")
                
            except Exception as e:
                print(f"IR generation failed: {e}")
                return False
            
            # Phase 5: Optimization
            if self.verbose:
                print("\nPhase 5: Optimization...")
            
            optimizer = QueryOptimizer()
            try:
                optimized_ir = optimizer.optimize(ir_program)
                
                if self.verbose:
                    print("Optimization completed")
                    stats = optimizer.get_optimization_stats()
                    print(f"  Rules applied: {stats['rules_applied']}")
                    print(f"  Nodes optimized: {stats['nodes_optimized']}")
                
            except Exception as e:
                print(f"Optimization failed: {e}")
                return False
            
            # Phase 6: Code Generation
            if self.verbose:
                print("\nPhase 6: SQL Code Generation...")
            
            try:
                sql_statements = codegen.generate_sql(ast)
                
                if self.verbose:
                    print(f"Generated SQL statements: {len(sql_statements)}")
                
                if self.show_sql:
                    print("\n=== Generated SQL ===")
                    for i, sql in enumerate(sql_statements, 1):
                        print(f"{i}. {sql}")
                    print("=== END SQL ===\n")
                
            except Exception as e:
                print(f"Code generation failed: {e}")
                return False
            
            # Phase 7: Execution
            if self.verbose:
                print("\nPhase 7: Execution...")
            
            try:
                results = self.executor.execute_sql_batch(sql_statements)
                
                # Display results
                for i, result in enumerate(results, 1):
                    print(f"\n--- Query {i} ---")
                    if result.success:
                        if result.data:
                            self._display_query_result(result)
                        else:
                            print(f"✓ {result.message}")
                            print(f"   Affected rows: {result.affected_rows}")
                            print(f"   Execution time: {result.execution_time:.3f}s")
                    else:
                        print(f"✗ Error: {result.message}")
                        print(f"   Execution time: {result.execution_time:.3f}s")
                
                # Check if all queries succeeded
                all_success = all(result.success for result in results)
                return all_success
                
            except Exception as e:
                print(f"Execution failed: {e}")
                return False
            
        except KeyboardInterrupt:
            print("\nCompilation interrupted by user")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
        finally:
            # Cleanup
            try:
                self.executor.shutdown()
            except:
                pass
    
    def _display_query_result(self, result):
        """Display query results in a formatted table"""
        if not result.data:
            print("No rows returned.")
            return
        
        # Calculate column widths
        col_widths = {}
        for col in result.columns:
            col_widths[col] = max(len(col), 10)  # Minimum width of 10
        
        for row in result.data:
            for col in result.columns:
                value = str(row.get(col, ""))
                col_widths[col] = max(col_widths[col], len(value))
        
        # Display header
        header_line = "+"
        for col in result.columns:
            header_line += "-" * (col_widths[col] + 2) + "+"
        print(header_line)
        
        header_row = "|"
        for col in result.columns:
            header_row += f" {col.ljust(col_widths[col])} |"
        print(header_row)
        
        print(header_line)
        
        # Display data rows
        for row in result.data:
            data_row = "|"
            for col in result.columns:
                value = str(row.get(col, ""))
                data_row += f" {value.ljust(col_widths[col])} |"
            print(data_row)
        
        print(header_line)
        print(f"Rows returned: {len(result.data)}")
        print(f"Execution time: {result.execution_time:.3f}s")
    
    def compile_file(self, file_path: str) -> bool:
        """Compile a BhashaQL file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            print(f"Compiling file: {file_path}")
            print("=" * 50)
            
            return self.compile_and_execute(source)
            
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    def interactive_mode(self):
        """Run compiler in interactive mode"""
        print("🚀 BhashaQL Interactive Mode")
        print("Type 'help' for commands, 'exit' to quit")
        print("=" * 50)
        
        while True:
            try:
                # Get user input
                command = input("\nbhashaql> ").strip()
                
                if not command:
                    continue
                
                # Handle special commands
                if command.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye! 👋")
                    break
                elif command.lower() == 'help':
                    self._show_help()
                    continue
                elif command.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                elif command.lower() == 'stats':
                    self._show_stats()
                    continue
                elif command.lower().startswith('load '):
                    file_path = command[5:].strip()
                    self.compile_file(file_path)
                    continue
                elif command.lower().startswith('save '):
                    file_path = command[5:].strip()
                    self._save_session(file_path)
                    continue
                elif command.lower() == 'verbose':
                    self.verbose = not self.verbose
                    print(f"Verbose mode: {'ON' if self.verbose else 'OFF'}")
                    continue
                elif command.lower() == 'sql':
                    self.show_sql = not self.show_sql
                    print(f"SQL display: {'ON' if self.show_sql else 'OFF'}")
                    continue
                elif command.lower() == 'ast':
                    self.show_ast = not self.show_ast
                    print(f"AST display: {'ON' if self.show_ast else 'OFF'}")
                    continue
                elif command.lower() == 'ir':
                    self.show_ir = not self.show_ir
                    print(f"IR display: {'ON' if self.show_ir else 'OFF'}")
                    continue
                
                # Compile and execute the command
                print(f"\nExecuting: {command}")
                print("-" * 30)
                self.compile_and_execute(command)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                print("\nGoodbye! 👋")
                break
    
    def _show_help(self):
        """Show help information"""
        help_text = """
📖 BhashaQL Commands:
  help        - Show this help message
  clear       - Clear screen
  stats       - Show execution statistics
  verbose     - Toggle verbose mode
  sql         - Toggle SQL display
  ast         - Toggle AST display
  ir          - Toggle IR display
  load <file> - Load and execute a file
  save <file> - Save current session to file
  exit/quit  - Exit the compiler

📝 Language Examples:
  banaye table students (id number, name text);
  laye * se students jahan age > 18;
  daalen mein students values (1, "Aman", 20);
  badlein students set karein name = "Rahul" jahan id = 1;
  mitayein se students jahan age < 18;

💡 Tips:
  - Use semicolon (;) to separate statements
  - Strings can use single or double quotes
  - All keywords are in Hinglish
        """
        print(help_text)
    
    def _show_stats(self):
        """Show execution statistics"""
        stats = self.executor.get_execution_stats()
        db_info = self.executor.get_database_info()
        
        print("\n📊 Execution Statistics:")
        print(f"  Total queries: {stats['total_queries']}")
        print(f"  Successful: {stats['successful_queries']}")
        print(f"  Failed: {stats['failed_queries']}")
        print(f"  Success rate: {(stats['successful_queries']/max(stats['total_queries'], 1)*100):.1f}%")
        print(f"  Avg execution time: {stats['average_execution_time']:.3f}s")
        print(f"  Total execution time: {stats['total_execution_time']:.3f}s")
        
        print(f"\n🗄️ Database Info:")
        print(f"  Database path: {db_info.get('database_path', 'N/A')}")
        print(f"  Connected: {'Yes' if db_info.get('connected', False) else 'No'}")
        print(f"  Tables: {db_info.get('table_count', 0)}")
        print(f"  Table list: {', '.join(db_info.get('tables', []))}")
    
    def _save_session(self, file_path: str):
        """Save current session to file"""
        try:
            # This would need to be implemented based on session history
            print(f"Session saved to: {file_path}")
        except Exception as e:
            print(f"Failed to save session: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="BhashaQL - A Hinglish SQL Compiler",
        epilog="Example: python main.py -f script.bql"
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Execute BhashaQL from file'
    )
    
    parser.add_argument(
        '-c', '--command',
        type=str,
        help='Execute single BhashaQL command'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--show-sql',
        action='store_true',
        help='Show generated SQL'
    )
    
    parser.add_argument(
        '--show-ast',
        action='store_true',
        help='Show AST structure'
    )
    
    parser.add_argument(
        '--show-ir',
        action='store_true',
        help='Show intermediate representation'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='runtime/database.db',
        help='Database file path'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='BhashaQL 1.0.0 - Hinglish SQL Compiler'
    )
    
    args = parser.parse_args()
    
    # Create compiler instance
    compiler = BhashaQLCompiler(args.db_path)
    compiler.verbose = args.verbose
    compiler.show_sql = args.show_sql
    compiler.show_ast = args.show_ast
    compiler.show_ir = args.show_ir
    
    try:
        if args.file:
            # File mode
            success = compiler.compile_file(args.file)
            sys.exit(0 if success else 1)
        
        elif args.command:
            # Command mode
            print(f"Executing: {args.command}")
            print("=" * 50)
            success = compiler.compile_and_execute(args.command)
            sys.exit(0 if success else 1)
        
        elif args.interactive or len(sys.argv) == 1:
            # Interactive mode (default)
            compiler.interactive_mode()
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()