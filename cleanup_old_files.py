#!/usr/bin/env python3
"""
Script de Limpeza de Arquivos Duplicados - PromoAgente
Remove arquivos e pastas antigas que foram migrados para /src/
"""
import os
import shutil
from pathlib import Path

def cleanup_old_files():
    """Remove arquivos e pastas antigas"""
    
    print("🧹 Iniciando limpeza de arquivos duplicados...\n")
    
    # Define o diretório raiz do projeto
    root = Path(__file__).parent
    
    # Lista de pastas a remover
    folders_to_remove = [
        root / "agents",
        root / "core",
    ]
    
    # Lista de arquivos a remover
    files_to_remove = [
        root / "main_old.py",
        root / "main_old2.py",
        root / "test_chat.db",
    ]
    
    removed_count = 0
    errors = []
    
    # Remove pastas
    print("📂 Removendo pastas antigas...")
    for folder in folders_to_remove:
        if folder.exists() and folder.is_dir():
            try:
                shutil.rmtree(folder)
                print(f"  ✅ Removido: {folder.name}/")
                removed_count += 1
            except Exception as e:
                error_msg = f"  ❌ Erro ao remover {folder.name}/: {e}"
                print(error_msg)
                errors.append(error_msg)
        else:
            print(f"  ⏭️  Não encontrado: {folder.name}/ (já removido ou não existe)")
    
    # Remove arquivos
    print("\n📄 Removendo arquivos antigos...")
    for file in files_to_remove:
        if file.exists() and file.is_file():
            try:
                file.unlink()
                print(f"  ✅ Removido: {file.name}")
                removed_count += 1
            except Exception as e:
                error_msg = f"  ❌ Erro ao remover {file.name}: {e}"
                print(error_msg)
                errors.append(error_msg)
        else:
            print(f"  ⏭️  Não encontrado: {file.name} (já removido ou não existe)")
    
    # Resumo
    print(f"\n{'='*50}")
    print(f"✨ Limpeza concluída!")
    print(f"📊 Itens removidos: {removed_count}")
    
    if errors:
        print(f"⚠️  Erros encontrados: {len(errors)}")
        for error in errors:
            print(f"   {error}")
    else:
        print("✅ Nenhum erro encontrado!")
    
    print(f"{'='*50}\n")
    
    # Verifica se /src/ existe
    src_folder = root / "src"
    if src_folder.exists():
        print("✅ Pasta /src/ confirmada (nova estrutura)")
    else:
        print("⚠️  ATENÇÃO: Pasta /src/ não encontrada!")
    
    print("\n🎉 Projeto limpo e organizado!")
    return removed_count, len(errors)


if __name__ == "__main__":
    try:
        removed, errors = cleanup_old_files()
        
        if errors > 0:
            print("\n⚠️  Alguns arquivos não puderam ser removidos.")
            print("   Tente fechar o VS Code e executar novamente.")
            exit(1)
        else:
            print("\n✅ Limpeza bem-sucedida!")
            exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Limpeza cancelada pelo usuário.")
        exit(130)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        exit(1)
