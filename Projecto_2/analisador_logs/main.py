from pathlib import Path
from io_utils import read_lines_auto
from parser import parse_records
from analytics import analyze
from report import console_summary, export_reports


def main():
    # Caminhos padrão
    base_dir = Path(__file__).parent
    input_path = base_dir / "logs_exemplo.csv"
    out_dir = base_dir / "out"

    # Verifica se o ficheiro existe
    if not input_path.exists():
        print(f"Ficheiro de logs não encontrado: {input_path}")
        return

    # Executa análise
    fmt, iterator = read_lines_auto(input_path)
    parsed = list(parse_records(iterator))
    stats = analyze(parsed)

    # Mostra resultados
    print(f"Formato detetado: {fmt}")
    print(console_summary(stats))

    # Exporta relatórios
    outputs = export_reports(stats, out_dir)
    print("\nRelatórios gerados:")
    for k, v in outputs.items():
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()