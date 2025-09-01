# 🚀 Mark Foot - Scripts de Desenvolvimento## 🔄 Opções extras:

```powershell
# Windows - Reset completo (apaga tudo e recria)
.\scripts\start-dev.ps1 -Reset

# Linux/Mac - Reset completo
./scripts/start-dev.sh --reset

# Ver ajuda
.\scripts\start-dev.ps1 -Help     # Windows
./scripts/start-dev.sh --help     # Linux/Mac
``` super simples para levantar o ambiente de desenvolvimento em segundos!**

## 🖥️ Windows

```powershell
# Executar uma vez e pronto!
.\scripts\start-dev.ps1
```

## 🐧 Linux/Mac

```bash
# Dar permissão (só na primeira vez)
chmod +x scripts/start-dev.sh

# Executar uma vez e pronto!
./scripts/start-dev.sh
```

## 🎯 O que acontece automaticamente:

1. ✅ Verifica se Docker está rodando
2. ✅ Para containers antigos 
3. ✅ Sobe todos os containers necessários
4. ✅ Aguarda banco de dados ficar pronto
5. ✅ Aplica migrations automaticamente
6. ✅ Popula dados de teste (se necessário)
7. ✅ Cria superuser admin (se não existir)
8. ✅ Mostra URLs de acesso

## 🌐 Depois do script rodar:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/api/v1/
- **Django Admin**: http://localhost:8001/admin/

## 👤 Login padrão:

- **Usuário**: admin
- **Senha**: admin123

## � Opções extras:

```powershell
# Windows - Reset completo (apaga tudo e recria)
.\start-dev.ps1 -Reset

# Linux/Mac - Reset completo
./start-dev.sh --reset

# Ver ajuda
.\start-dev.ps1 -Help     # Windows
./start-dev.sh --help     # Linux/Mac
```

## 🛠️ Comandos úteis após setup:

```bash
# Ver logs em tempo real
docker-compose -f docker/docker-compose.dev.yml logs -f

# Parar tudo
docker-compose -f docker/docker-compose.dev.yml down

# Ver status dos containers
docker ps
```

## ⚠️ Se algo der errado:

1. **Execute com reset**: `.\scripts\start-dev.ps1 -Reset` (Windows) ou `./scripts/start-dev.sh --reset` (Linux/Mac)
2. **Verifique se Docker está rodando**: Docker Desktop deve estar aberto
3. **Verifique portas ocupadas**: Pare outros serviços nas portas 3000, 8001, 3307, 6380

## 🎉 Isso é tudo!

Não precisa mais decorar comandos Docker complexos. É só rodar o script e começar a desenvolver!

---

**💡 Dica**: Adicione o script aos seus favoritos ou crie um alias para ficar ainda mais fácil!
