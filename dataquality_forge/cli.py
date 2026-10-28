import sys
import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from dataquality_forge import __version__
from dataquality_forge.storage import load_dataset_dataframe
from dataquality_forge.profiler import profile_dataset
from dataquality_forge.validator import execute_validation_run
from dataquality_forge.schema import extract_schema_from_file, compare_schemas
from dataquality_forge.reports import generate_json_report, generate_csv_report, generate_html_report

app = typer.Typer(help="DataQuality Forge - Open-Source Data Quality Profiling & Validation CLI")
console = Console()


@app.command()
def version():
    """Display DataQuality Forge version."""
    console.print(f"[bold green]DataQuality Forge[/bold green] version: {__version__}")


@app.command(name="inspect")
def inspect(file_path: str):
    """Inspect basic metadata and first 5 rows of a dataset file."""
    p = Path(file_path)
    if not p.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        sys.exit(2)
    try:
        df = load_dataset_dataframe(file_path, limit=5)
        console.print(f"[bold blue]File:[/bold blue] {p.name} ({p.stat().st_size} bytes)")
        console.print(f"[bold blue]Columns ({len(df.columns)}):[/bold blue] {list(df.columns)}")
        table = Table(title="Dataset Preview (First 5 Rows)")
        for col in df.columns:
            table.add_column(str(col))
        for _, row in df.iterrows():
            table.add_row(*[str(val) for val in row.values])
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Inspection failed:[/bold red] {e}")
        sys.exit(1)


@app.command(name="profile")
def profile(
    file_path: str,
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    sample: Optional[int] = typer.Option(None, "--sample", help="Sample row limit"),
):
    """Profile a dataset and generate quality summary and column statistics."""
    p = Path(file_path)
    if not p.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        sys.exit(2)
    try:
        results = profile_dataset(file_path, sample_limit=sample)
        if json_output:
            print(json.dumps(results, indent=2))
            return

        console.print(f"\n[bold green]=== Data Profiling: {p.name} ===[/bold green]")
        console.print(f"Total Rows: [bold]{results['total_rows']}[/bold] | Columns: [bold]{results['total_columns']}[/bold] | Mode: {results['mode']}")
        console.print(f"Duplicate Rows: {results['duplicate_rows']} ({results['duplicate_row_percentage']}%)")
        console.print(f"Missing Cells: {results['missing_cells']} ({results['missing_cell_percentage']}%)")
        console.print(f"Complete Rows: {results['complete_rows']} ({results['complete_row_percentage']}%)")
        console.print(f"Duration: {results['duration_ms']} ms\n")

        table = Table(title="Column Profiles")
        table.add_column("Column")
        table.add_column("Inferred Type")
        table.add_column("Nulls (%)")
        table.add_column("Distinct")
        table.add_column("Details")

        for cp in results["column_profiles"]:
            det = []
            if cp.get("numeric_stats"):
                ns = cp["numeric_stats"]
                det.append(f"min={ns.get('min')}, max={ns.get('max')}, mean={ns.get('mean')}")
            elif cp.get("string_stats") or cp.get("min_length") is not None:
                det.append(f"len=[{cp.get('min_length')}-{cp.get('max_length')}], whitespaces={cp.get('whitespace_count')}")
            top_v = ", ".join([f"{tv['value']}({tv['count']})" for tv in cp.get("top_values", [])[:2]])
            if top_v:
                det.append(f"top=[{top_v}]")
            table.add_row(
                cp["name"],
                cp["inferred_type"],
                f"{cp['null_count']} ({cp['null_percentage']}%)",
                str(cp["distinct_count"]),
                "; ".join(det),
            )
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Profiling failed:[/bold red] {e}")
        sys.exit(1)


@app.command(name="validate")
def validate(
    file_path: str,
    rules: str = typer.Option(..., "--rules", "-r", help="Path to rules JSON file"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    export_html: Optional[str] = typer.Option(None, "--export-html", help="Path to save HTML report"),
):
    """Validate a dataset file against rules defined in a JSON file."""
    p = Path(file_path)
    rp = Path(rules)
    if not p.exists():
        console.print(f"[bold red]Error:[/bold red] Dataset not found: {file_path}")
        sys.exit(2)
    if not rp.exists():
        console.print(f"[bold red]Error:[/bold red] Rules file not found: {rules}")
        sys.exit(2)

    try:
        with open(rp, "r", encoding="utf-8") as rf:
            rule_defs = json.load(rf)
            if isinstance(rule_defs, dict) and "rules" in rule_defs:
                rule_defs = rule_defs["rules"]
    except Exception as e:
        console.print(f"[bold red]Invalid rules file syntax:[/bold red] {e}")
        sys.exit(2)

    try:
        result = execute_validation_run(file_path, rule_defs)
        if export_html:
            html = generate_html_report(result, dataset_name=p.name)
            Path(export_html).write_text(html, encoding="utf-8")
            console.print(f"[bold green]HTML report exported to:[/bold green] {export_html}")

        if json_output:
            print(json.dumps(result, indent=2))
        else:
            console.print(f"\n[bold green]=== Validation Results: {p.name} ===[/bold green]")
            console.print(f"Overall Quality Score: [bold cyan]{result['quality_score']}%[/bold cyan]")
            console.print(f"Rules Executed: {result['rules_executed']} | Passed: [green]{result['passed_rules']}[/green] | Failed: [red]{result['failed_rules']}[/red]")
            console.print(f"Duration: {result['duration_ms']} ms\n")

            table = Table(title="Rule Outcomes")
            table.add_column("Status")
            table.add_column("Rule Name")
            table.add_column("Severity")
            table.add_column("Pass Rate")
            table.add_column("Failed Recs")

            for rr in result["rule_results"]:
                stat = "[green]PASS[/green]" if rr["passed"] else "[red]FAIL[/red]"
                table.add_row(
                    stat,
                    rr["rule_name"],
                    rr["severity"],
                    f"{rr['pass_percentage']}%",
                    str(rr["failed_records"]),
                )
            console.print(table)

        # Exit code 3 if any error/critical rule failed
        if result["error_count"] > 0:
            sys.exit(3)
        sys.exit(0)

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[bold red]Validation failed:[/bold red] {e}")
        sys.exit(1)


@app.command(name="schema")
def schema_cmd(
    action: str = typer.Argument(..., help="Action: 'extract' or 'compare'"),
    file_a: str = typer.Argument(..., help="Dataset file or expected schema JSON"),
    file_b: Optional[str] = typer.Argument(None, help="Actual schema JSON or dataset file (for compare)"),
):
    """Schema inspection and expected vs actual comparison."""
    if action == "extract":
        s = extract_schema_from_file(file_a)
        print(json.dumps(s, indent=2))
    elif action == "compare":
        if not file_b:
            console.print("[bold red]Compare requires two files: <expected.json> <actual>[/bold red]")
            sys.exit(2)
        # Load expected
        with open(file_a, "r", encoding="utf-8") as f:
            expected = json.load(f)
        # Load actual
        pb = Path(file_b)
        if pb.suffix.lower() == ".json":
            with open(pb, "r", encoding="utf-8") as f:
                actual = json.load(f)
        else:
            actual = extract_schema_from_file(file_b)

        diff = compare_schemas(expected, actual)
        console.print(f"Compatible: [bold]{diff['is_compatible']}[/bold]")
        console.print(f"Summary: {diff['summary']}")
        if diff["breaking_changes"]:
            console.print("[bold red]Breaking changes:[/bold red]")
            for bc in diff["breaking_changes"]:
                console.print(f" - {bc}")
            sys.exit(3)
        sys.exit(0)
    else:
        console.print(f"[bold red]Unknown action:[/bold red] {action}")
        sys.exit(2)


if __name__ == "__main__":
    app()
