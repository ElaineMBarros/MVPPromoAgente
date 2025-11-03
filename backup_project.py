"""
Script de Backup Completo do PromoAgente
Cria backup de todos os arquivos importantes do projeto
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
import zipfile

def create_backup():
    # Nome do backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"PromoAgente_Backup_{timestamp}"
    backup_dir = Path(f"../{backup_name}")
    
    print("🔄 Iniciando backup do PromoAgente...")
    print(f"📁 Destino: {backup_dir}")
    
    # Cria diretório de backup
    backup_dir.mkdir(exist_ok=True)
    
    # Arquivos e pastas para incluir
    items_to_backup = [
        # Backend Python
        "src/",
        "prompts/",
        "main.py",
        "requirements.txt",
        ".env.example",
        ".env.production",
        "start.bat",
        "start.sh",
        
        # Frontend
        "frontend/src/",
        "frontend/public/",
        "frontend/index.html",
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/tsconfig.json",
        "frontend/tsconfig.node.json",
        "frontend/vite.config.ts",
        
        # Documentação
        "README.md",
        "GITHUB_SETUP.md",
        
        # Banco de dados
        "promoagente_local.db",
        "agno.db",
        
        # Outros arquivos
        "logo_gera.png",
        ".gitignore",
    ]
    
    # Diretórios para excluir
    exclude_dirs = {
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".git",
        "dist",
        "build",
        ".pytest_cache",
        ".mypy_cache",
        "frontend/node_modules",
        "frontend/dist",
    }
    
    # Copia arquivos
    copied_count = 0
    for item in items_to_backup:
        src = Path(item)
        if not src.exists():
            print(f"⚠️ Não encontrado: {item}")
            continue
            
        dst = backup_dir / item
        
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied_count += 1
            print(f"✅ Copiado: {item}")
        elif src.is_dir():
            # Copia diretório excluindo pastas indesejadas
            def ignore_patterns(dir, files):
                return [f for f in files if f in exclude_dirs]
            
            shutil.copytree(src, dst, ignore=ignore_patterns, dirs_exist_ok=True)
            copied_count += 1
            print(f"📂 Copiado: {item}")
    
    # Cria arquivo de informações do backup
    info_file = backup_dir / "BACKUP_INFO.txt"
    with open(info_file, "w", encoding="utf-8") as f:
        f.write(f"PromoAgente - Backup\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Versão: Sistema Completo\n")
        f.write(f"Arquivos copiados: {copied_count}\n\n")
        f.write(f"Conteúdo:\n")
        f.write(f"- Backend Python (FastAPI + OpenAI + Agno)\n")
        f.write(f"- Frontend React + TypeScript + Vite\n")
        f.write(f"- Banco de dados SQLite\n")
        f.write(f"- Prompts de IA otimizados\n")
        f.write(f"- Documentação completa\n\n")
        f.write(f"Para restaurar:\n")
        f.write(f"1. Copie todos os arquivos para um diretório\n")
        f.write(f"2. No backend: pip install -r requirements.txt\n")
        f.write(f"3. No frontend: cd frontend && npm install\n")
        f.write(f"4. Configure .env com suas chaves\n")
        f.write(f"5. Execute: python main.py\n")
        f.write(f"6. Em outro terminal: cd frontend && npm run dev\n")
    
    print(f"\n✅ Backup concluído!")
    print(f"📁 Localização: {backup_dir.absolute()}")
    print(f"📊 Total de itens: {copied_count}")
    
    # Pergunta se quer criar ZIP
    print("\n📦 Deseja criar arquivo ZIP? (S/n): ", end="")
    create_zip = input().strip().lower()
    
    if create_zip != 'n':
        zip_file = Path(f"../{backup_name}.zip")
        print(f"\n🔄 Criando arquivo ZIP...")
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                # Exclui diretórios indesejados
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(backup_dir.parent)
                    zipf.write(file_path, arcname)
        
        zip_size = zip_file.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ ZIP criado: {zip_file.absolute()}")
        print(f"📦 Tamanho: {zip_size:.2f} MB")
        
        # Pergunta se quer remover pasta descompactada
        print(f"\n🗑️ Remover pasta descompactada? (s/N): ", end="")
        remove_folder = input().strip().lower()
        
        if remove_folder == 's':
            shutil.rmtree(backup_dir)
            print(f"✅ Pasta removida")
    
    print("\n🎉 Backup finalizado com sucesso!")
    print(f"💾 Seus dados estão seguros!")

if __name__ == "__main__":
    try:
        create_backup()
    except Exception as e:
        print(f"\n❌ Erro durante backup: {e}")
        import traceback
        traceback.print_exc()
