# BhashaQL - Hinglish SQL Compiler

A revolutionary SQL compiler that allows you to write database queries in Hinglish (Hindi + English)!

## About

BhashaQL is a complete SQL compiler that translates Hinglish queries into standard SQL and executes them. It makes database operations accessible to Hindi-speaking developers by providing familiar Hinglish keywords.

## Features

- **Complete SQL Support**: DDL, DQL, DML, and DCL operations
- **Web Interface**: Interactive web-based query editor
- **Real-time Compilation**: Instant query parsing and execution
- **Error Handling**: Comprehensive error messages in Hinglish
- **Database Backend**: SQLite database integration
- **REST API**: Full API for integration with other tools

## Supported Operations

### DDL (Data Definition Language)
```bql
-- Create table
banaye table students (id number, name text, age number);

-- Drop table  
hataye table students;

-- Alter table
badliye table students add column grade text;
```

### DQL (Data Query Language)
```bql
-- Select all
laye * se students;

-- Select with condition
laye name, age se students jahan age > 18;

-- Order by
laye * se students kram dwara age desc;

-- Aggregate functions
laye count(*) se students;
laye avg(age) se students;
```

### DML (Data Manipulation Language)
```bql
-- Insert data
daalen mein students values (1, "Aman", 20);

-- Update data
badlein students set karein age = 21 jahan id = 1;

-- Delete data
mitayein se students jahan age < 18;
```

### DCL (Data Control Language)
```bql
-- Grant permissions
deejaye select, insert on students to user1;

-- Revoke permissions
wapas insert on students from user1;
```

## Installation

```bash
git clone <repository-url>
cd BhashaQL
pip install -r requirements.txt
```

## Quick Start

1. **Run the backend server:**
```bash
python app.py
```

2. **Open the web interface:**
Navigate to `http://localhost:3000` in your browser

3. **Try a sample query:**
```bql
banaye table students (id number, name text, age number);
daalen mein students values (1, "Aman", 20);
laye * se students;
```

## Project Structure

```
BhashaQL/
├── compiler/           # Core compiler components
│   ├── lexer.py       # Lexical analysis
│   ├── parser.py      # Parsing and AST generation
│   ├── semantic.py    # Semantic analysis
│   ├── ir.py          # Intermediate representation
│   ├── optimizer.py   # IR optimization
│   ├── codegen.py     # SQL code generation
│   └── tokens.py      # Token definitions
├── web/               # Web interface
│   └── index.html     # Frontend application
├── tests/             # Test cases
│   ├── sample_queries.bql
│   └── error_cases.bql
├── app.py             # Flask web server
├── main.py            # Command line interface
└── requirements.txt   # Python dependencies
```

## Web Interface Features

- **Syntax Highlighting**: Color-coded Hinglish keywords
- **Auto-completion**: Intelligent query suggestions
- **Error Highlighting**: Real-time error detection
- **Results Display**: Formatted table results
- **Query History**: Track previous queries
- **Export Results**: Download query results

## API Endpoints

### Compile Query
```http
POST /api/compile
Content-Type: application/json

{
    "query": "laye * se students jahan age > 18;"
}
```

### Get Examples
```http
GET /api/examples
```

### Get Tables
```http
GET /api/tables
```

### Health Check
```http
GET /api/health
```

## Language Reference

| Hinglish Keyword | English Equivalent | Purpose |
|------------------|-------------------|---------|
| `banaye` | CREATE | Create tables |
| `hataye` | DROP | Drop tables |
| `badliye` | ALTER | Modify tables |
| `laye` | SELECT | Query data |
| `se` | FROM | Specify table |
| `jahan` | WHERE | Filter conditions |
| `daalen` | INSERT | Insert data |
| `mein` | INTO | Target table |
| `badlein` | UPDATE | Update data |
| `mitayein` | DELETE | Delete data |
| `deejaye` | GRANT | Grant permissions |
| `wapas` | REVOKE | Revoke permissions |

## Examples

### Basic Operations
```bql
-- Create and populate table
banaye table employees (id number, name text, department text, salary number);
daalen mein employees values (1, "Rahul", "IT", 50000);
daalen mein employees values (2, "Priya", "HR", 45000);

-- Query data
laye * se employees jahan department = "IT";
laye avg(salary) se employees group dwara department;
```

### Advanced Queries
```bql
-- Subquery
laye * se employees jahan salary in (
    laye max(salary) se employees group dwara department
);

-- Complex conditions
laye * se employees 
jahan department = "IT" aur salary >= 40000 aur salary <= 60000;
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

---

**Happy Querying in Hinglish! 