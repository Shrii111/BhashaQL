# 🚀 BhashaQL - A Hinglish SQL Compiler

A complete compiler implementation that translates Hinglish SQL queries to standard SQL and executes them using SQLite.

## 📋 Features

- **Complete Compiler Pipeline**: Lexer → Parser → Semantic Analyzer → Optimizer → Code Generator → Executor
- **Hinglish Keywords**: All SQL keywords in Hinglish for better accessibility
- **All SQL Categories**: DDL, DQL, DML, DCL support
- **Query Optimization**: Predicate pushdown, join reordering, index selection
- **Interactive Mode**: REPL with help and statistics
- **Error Handling**: Comprehensive error reporting with line numbers
- **Multiple Interfaces**: CLI and web interface

## 🛠️ Installation

```bash
git clone <repository-url>
cd BhashaQL
pip install -r requirements.txt